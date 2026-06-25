"""
Modele de donnees de l'application.

On definit ici la table principale : une "Tache" (ou action de projet).
SQLAlchemy fait le lien entre cet objet Python et la table de la base de donnees.
"""

from datetime import datetime, date, timezone

from .database import db


def _maintenant() -> datetime:
    """Renvoie la date/heure actuelle (UTC), de maniere compatible futur."""
    return datetime.now(timezone.utc)


# Valeurs autorisees (servent a valider et a alimenter le tableau de bord)
STATUTS = ["A faire", "En cours", "Termine"]
PRIORITES = ["Basse", "Moyenne", "Haute"]


class Tache(db.Model):
    """Une tache de projet a suivre."""

    __tablename__ = "taches"

    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    responsable = db.Column(db.String(120), nullable=False, default="")
    statut = db.Column(db.String(20), nullable=False, default="A faire")
    priorite = db.Column(db.String(20), nullable=False, default="Moyenne")
    avancement = db.Column(db.Integer, nullable=False, default=0)  # pourcentage 0-100
    date_echeance = db.Column(db.Date, nullable=True)
    date_creation = db.Column(db.DateTime, nullable=False, default=_maintenant)

    def to_dict(self) -> dict:
        """Convertit la tache en dictionnaire (pour la reponse JSON de l'API)."""
        return {
            "id": self.id,
            "titre": self.titre,
            "responsable": self.responsable,
            "statut": self.statut,
            "priorite": self.priorite,
            "avancement": self.avancement,
            "date_echeance": self.date_echeance.isoformat() if self.date_echeance else None,
            "date_creation": self.date_creation.isoformat(),
        }

    @staticmethod
    def depuis_dict(donnees: dict) -> "Tache":
        """Cree une tache a partir d'un dictionnaire (donnees recues de l'API)."""
        tache = Tache()
        tache.appliquer(donnees)
        return tache

    def appliquer(self, donnees: dict) -> None:
        """Met a jour les champs de la tache a partir d'un dictionnaire valide."""
        if "titre" in donnees:
            self.titre = str(donnees["titre"]).strip()
        if "responsable" in donnees:
            self.responsable = str(donnees.get("responsable", "")).strip()
        if "statut" in donnees and donnees["statut"] in STATUTS:
            self.statut = donnees["statut"]
        if "priorite" in donnees and donnees["priorite"] in PRIORITES:
            self.priorite = donnees["priorite"]
        if "avancement" in donnees:
            # On borne la valeur entre 0 et 100
            try:
                self.avancement = max(0, min(100, int(donnees["avancement"])))
            except (TypeError, ValueError):
                self.avancement = 0
        if "date_echeance" in donnees and donnees["date_echeance"]:
            try:
                self.date_echeance = date.fromisoformat(donnees["date_echeance"])
            except (TypeError, ValueError):
                self.date_echeance = None
