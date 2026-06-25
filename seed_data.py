"""Remplit la base avec quelques taches d'exemple (a lancer une fois)."""
from datetime import date, timedelta
from gestionpro import create_app
from gestionpro.database import db
from gestionpro.models import Tache

app = create_app()

EXEMPLES = [
    ("Cadrage du projet de digitalisation", "Safoura", "Termine", "Haute", 100, -10),
    ("Recueil des besoins utilisateurs", "Safoura", "Termine", "Haute", 100, -5),
    ("Maquette du tableau de bord", "Equipe data", "En cours", "Moyenne", 60, 7),
    ("Automatisation du reporting mensuel", "Safoura", "En cours", "Haute", 40, 14),
    ("Migration des donnees vers la base", "Equipe IT", "A faire", "Haute", 0, 21),
    ("Rediger la documentation", "Safoura", "A faire", "Basse", 0, 30),
    ("Formation des utilisateurs", "RH", "A faire", "Moyenne", 0, 35),
]

with app.app_context():
    db.drop_all()
    db.create_all()
    for titre, resp, statut, prio, av, jours in EXEMPLES:
        db.session.add(Tache(
            titre=titre, responsable=resp, statut=statut, priorite=prio,
            avancement=av, date_echeance=date.today() + timedelta(days=jours),
        ))
    db.session.commit()
    print(f"{len(EXEMPLES)} taches d'exemple ajoutees.")
