🤖 Telegram Bot avec Système d'Invitation

Un bot Telegram sécurisé avec système d'invitation et interface de gestion des utilisateurs.

📋 Description

Ce bot Telegram permet une gestion sécurisée des utilisateurs via un système d'invitation. Il communique avec un serveur Node.js pour stocker les données des utilisateurs, les codes d'invitation et les coordonnées géographiques.

✨ Fonctionnalités

· 🔐 Système d'autorisation basé sur les invitations
· 👥 Gestion des utilisateurs via serveur Node.js
· 🔗 Génération de liens d'invitation uniques
· 📍 Récupération de coordonnées géographiques
· 📊 Statistiques d'utilisation en temps réel
· ⌨️ Interface clavier intuitive

🛠️ Installation

Prérequis

· Python 3.8+
· Compte Telegram avec Bot créé via @BotFather
· Serveur Node.js fonctionnel (port 3000)

Configuration

1. Cloner le dépôt

```bash
git clone <votre-repo>
cd <votre-repo>
```

1. Installer les dépendances

```bash
pip install python-telegram-bot requests python-dotenv
```

1. Configurer les variables d'environnement

```bash
cp .env.example .env
```

Editez le fichier .env :

```env
TELEGRAM_BOT_TOKEN=votre_token_bot_telegram
SERVER_URL=http://localhost:3000
```

1. Démarrer le bot

```bash
python bot.py
```

🎯 Utilisation

Commandes disponibles

· /start - Démarrer le bot (avec code d'invitation si nécessaire)
· /invite - Générer un lien d'invitation
· /stats - Afficher les statistiques

Menu clavier

· 📎 Lien - Afficher un lien prédéfini
· 🖼️ Image - Afficher une URL d'image
· 📍 Coordonnées récupéré - Récupérer les coordonnées stockées
· 👥 Inviter - Générer une invitation
· 📊 Stats - Afficher les statistiques

🔧 Structure du projet

```
├── bot.py                 # Script principal du bot
├── .env                   # Variables d'environnement
├── requirements.txt       # Dépendances Python
└── README.md             # Documentation
```

🔄 API Endpoints utilisés

Le bot communique avec un serveur Node.js sur les endpoints suivants :

· GET /users - Récupérer la liste des utilisateurs
· POST /users - Ajouter un nouvel utilisateur
· GET /invitations - Récupérer les invitations
· POST /invitations - Créer/Mettre à jour une invitation
· GET /coords - Récupérer les coordonnées

🛡️ Sécurité

· Vérification des autorisations à chaque commande
· Codes d'invitation uniques et à usage unique
· Validation des utilisateurs via serveur externe

📦 Dépendances

· python-telegram-bot - Interface Telegram Bot API
· requests - Requêtes HTTP vers le serveur Node.js
· python-dotenv - Gestion des variables d'environnement
· secrets - Génération de codes sécurisés

🚀 Déploiement

Local

```bash
python bot.py
```

Production

Recommandé d'utiliser avec :

· Docker pour containerisation
· Supervisor pour gestion des processus
· Nginx comme reverse proxy (si nécessaire)

🤝 Contribution

1. Fork le projet
2. Créer une branche feature (git checkout -b feature/AmazingFeature)
3. Commit les changements (git commit -m 'Add AmazingFeature')
4. Push vers la branche (git push origin feature/AmazingFeature)
5. Ouvrir une Pull Request

📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

⚠️ Notes importantes

· Assurez-vous que le serveur Node.js est opérationnel avant de démarrer le bot
· Gardez le token du bot sécurisé et ne le commitez jamais
· Le bot nécessite une connexion Internet stable pour fonctionner
· Les données sont stockées sur le serveur Node.js externe

📞 Support

Pour toute question ou problème, ouvrez une issue sur le dépôt GitHub.