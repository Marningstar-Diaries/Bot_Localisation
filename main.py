from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import Coord, Base  # Réutilise le modèle SQLAlchemy

TOKEN = "8226133133:AAHWSAsfJjJ2E1l6crXnQ-haHhqBF1XhPEM"
BASE_URL = "http://127.0.0.1:5000"  # URL de ton serveur Flask

# Base de données
engine = create_engine("sqlite:///bot_data.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# ===========================
# COMMANDES BOT
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message de bienvenue avec menu"""
    keyboard = ReplyKeyboardMarkup([["Lien 🌐", "Coordonnées 📍"]], resize_keyboard=True)
    await update.message.reply_text(
        f"👋 Salut {update.effective_user.first_name} !\n"
        "Bienvenue sur le bot de géolocalisation.\n"
        "Utilise les boutons ci-dessous pour accéder aux fonctions :",
        reply_markup=keyboard
    )

async def lien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🌐 {BASE_URL}/")

async def coordonnees(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coords = session.query(Coord).order_by(Coord.created_at.desc()).limit(5).all()
    if not coords:
        await update.message.reply_text("Aucune coordonnée pour le moment 🕓")
        return
    msg = "🗺️ **Dernières coordonnées :**\n\n"
    for c in coords:
        msg += f"📍 {c.username} — Lat: {c.latitude:.5f}, Lon: {c.longitude:.5f} ({c.created_at.strftime('%d/%m/%Y %H:%M')})\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gère les clics sur le menu clavier"""
    text = update.message.text
    if text == "Lien 🌐":
        await lien(update, context)
    elif text == "Coordonnées 📍":
        await coordonnees(update, context)
    else:
        await update.message.reply_text("Commande non reconnue. Utilise le menu ci-dessous.")

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
    app_tg.add_handler(CommandHandler("echo", echo))
    # Pour gérer les clics sur le clavier
    from telegram.ext import MessageHandler, filters
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("🤖 Bot Telegram en ligne...")
    app_tg.run_polling()
