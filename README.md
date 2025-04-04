# Basket Duel 🏀

Projet universitaire réalisé à l'Université Paris-Saclay (Évry-Val-d'Essonne)

**Auteurs :**
- Amari Augustin
- Annadoure Souriya
- Samy Benaïssa

Basket Duel est un jeu de basket-ball compétitif en 2D où deux joueurs s'affrontent au tour par tour. Le jeu propose un mode multijoueur en réseau local et un mode contre l'IA.

## 🎮 Fonctionnalités

- Mode multijoueur en réseau local
- Mode contre l'IA
- Terrain de jeu 2D avec vue depuis les gradins
- Position aléatoire du panier et des joueurs
- Système de tir avec angle et force
- Trajectoire parabolique réaliste
- Points bonus flottants pour des effets spéciaux
- Interface graphique intuitive

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd Basket-Duel
```

2. Assurez-vous d'avoir Python 3.x installé sur votre machine

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## 🎯 Comment jouer

### Démarrage du jeu

1. Lancez le serveur :
```bash
python src/main.py
```

2. Pour le mode multijoueur, connectez-vous avec le client sur la même machine ou sur le réseau local.

### Règles du jeu

- Les joueurs tirent à tour de rôle
- Chaque tir nécessite de choisir :
  - L'angle du tir
  - La force du tir
- La balle suit une trajectoire parabolique influencée par la gravité
- Un panier est marqué si la balle passe à travers le cercle
- Des bonus flottants peuvent modifier les points ou la trajectoire

## 📁 Structure du projet

```
Basket-Duel/
├── src/
│   ├── main.py          # Point d'entrée du jeu
│   ├── partie.py        # Logique principale du jeu
│   ├── Terrain.py       # Gestion du terrain
│   ├── Joueur.py        # Classe du joueur
│   ├── balle.py         # Physique de la balle
│   ├── serveur.py       # Serveur de jeu
│   ├── client.py        # Client de jeu
│   └── assets/          # Ressources graphiques
├── server_config.txt    # Configuration du serveur
└── client_config.txt    # Configuration du client
```

## 🛠️ Configuration

### Serveur
Modifiez `server_config.txt` pour configurer :
- L'adresse IP du serveur
- Le port d'écoute

### Client
Modifiez `client_config.txt` pour configurer :
- L'adresse IP du serveur à rejoindre
- Le port de connexion

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence [À DÉFINIR]. Voir le fichier `LICENSE` pour plus de détails. 