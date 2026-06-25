# GestionPro — Application web de suivi de projets

**GestionPro** est une application web complète de **gestion et de suivi de tâches de projet**,
construite autour d'une **API REST** et d'une **base de données**, avec un **tableau de bord**
(indicateurs et graphiques) et une interface pour créer, filtrer, modifier et supprimer les tâches.

Ce projet illustre une architecture **back-end + base de données + front-end** complète.

---

## Aperçu des fonctionnalités

- **Tableau de bord** : indicateurs clés (KPI) — total, tâches terminées, taux d'achèvement,
  avancement moyen — et **graphiques** (répartition par statut et par priorité)
- **Gestion des tâches (CRUD)** : ajout, modification, suppression
- **Recherche** et **filtre par statut**
- **API REST** documentée (JSON)
- **Base de données** relationnelle via un ORM (SQLAlchemy)
- **Tests automatisés** de l'API (pytest)

## Technologies

Python · Flask · Flask-SQLAlchemy (ORM) · SQLite · JavaScript (fetch) · Chart.js · pytest

---

## Installation

```bash
git clone https://github.com/Safoura3/gestionpro.git
cd gestionpro
pip install -r requirements.txt
```

## Lancement

```bash
python seed_data.py     # (optionnel) remplit la base avec des exemples
python run.py           # démarre le serveur
```

Puis ouvrir **http://127.0.0.1:5000**.

---

## L'API REST

| Méthode | Route                | Rôle                                  |
|---------|----------------------|---------------------------------------|
| GET     | `/api/taches`        | Liste des tâches (filtre `?statut=`)  |
| POST    | `/api/taches`        | Créer une tâche                       |
| GET     | `/api/taches/<id>`   | Détail d'une tâche                    |
| PUT     | `/api/taches/<id>`   | Modifier une tâche                    |
| DELETE  | `/api/taches/<id>`   | Supprimer une tâche                   |
| GET     | `/api/stats`         | Indicateurs du tableau de bord        |

Exemple (création d'une tâche) :

```bash
curl -X POST http://127.0.0.1:5000/api/taches \
     -H "Content-Type: application/json" \
     -d '{"titre": "Préparer la démo", "priorite": "Haute", "responsable": "Safoura"}'
```

---

## Architecture du projet

```
gestionpro/
├── gestionpro/
│   ├── __init__.py     # fabrique de l'application (create_app)
│   ├── database.py     # objet base de données (SQLAlchemy)
│   ├── models.py       # modèle de données (table Tache)
│   └── api.py          # API REST (CRUD + statistiques)
├── templates/index.html  # interface web
├── static/
│   ├── style.css
│   └── app.js          # logique front (consomme l'API)
├── tests/test_api.py   # tests de l'API (pytest)
├── seed_data.py        # jeu de données d'exemple
├── run.py              # point d'entrée
├── requirements.txt
└── README.md
```

> **Choix d'architecture** : le code est séparé par responsabilité (base de données, modèle,
> API, interface). L'« application factory » (`create_app`) permet de lancer une instance
> isolée pour les tests, avec une base en mémoire.

## Tests

```bash
pytest
```

---

## Auteure

Projet réalisé par **Safoura Mamboune Ndam** — étudiante en ingénierie informatique
(spécialité Transformation Digitale & Innovation).
