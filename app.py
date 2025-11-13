from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# === Variables d'environnement ===
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
LOCATION_URL = os.environ.get("LOCATION_URL")

# ===========================
# COMMANDES BOT
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message de bienvenue avec menu"""
    keyboard = ReplyKeyboardMarkup([["Lien 🌐", "Coordonnées 📍"]], resize_keyboard=True)
    await update.message.reply_text(
        f"👋 Salut {update.effective_user.first_name} !\n"
        "Bienvenue sur le bot de géolocalisation.\n"
        "Utilise les boutons ci-dessous pour accéder aux fonctions 👇 :",
        reply_markup=keyboard
    )

async def lien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envoie le lien du site Flask (Render)"""
    await update.message.reply_text(
        f"🌐 Clique ici pour envoyer ta position :\n{LOCATION_URL}/"
    )

async def coordonnees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Récupère les coordonnées depuis le serveur Flask"""
    try:
        response = requests.get(f"{LOCATION_URL}/coords")
        if response.status_code == 200:
            data = response.json()
            if not data:
                await update.message.reply_text("⚠️ Aucune coordonnée enregistrée pour le moment.")
                return

            msg = "🗺️ **Dernières coordonnées enregistrées :**\n\n"
            for c in reversed(data[-5:]):  # affiche les 5 dernières
                username = c.get("username", "Utilisateur inconnu")
                lat = c.get("latitude")
                lon = c.get("longitude")
                created = c.get("created_at")
                msg += f"👤 {username}\n📍 Lat: {lat:.5f}, Lon: {lon:.5f}\n🕒 {created}\n\n"

            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Erreur lors de la récupération des données.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Impossible de contacter le serveur.\nErreur : {e}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur le menu clavier"""
    text = update.message.text
    if text == "Lien 🌐":
        await lien(update, context)
    elif text == "Coordonnées 📍":
        await coordonnees(update, context)
    else:
        await update.message.reply_text("Commande non reconnue. Utilise le menu ci-dessous 👇")

# ===========================
# LANCEMENT DU BOT
# ===========================
if __name__ == "__main__":
    app_tg = ApplicationBuilder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("lien", lien))
    app_tg.add_handler(CommandHandler("coordonnees", coordonnees))
    app_tg.add_handler(CommandHandler("help", start))
    app_tg.add_handler(CommandHandler("menu", start))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot Telegram connecté et en ligne...")
    app_tg.run_polling()

