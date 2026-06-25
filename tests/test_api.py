"""
Tests de l'API REST de GestionPro.

On utilise une base SQLite EN MEMOIRE (rien n'est ecrit sur le disque),
recreee a chaque test grace a la fixture 'client'. On verifie le cycle
complet : creation, lecture, mise a jour, suppression et statistiques.

Lancement :  pytest
"""

import pytest

from gestionpro import create_app
from gestionpro.database import db


@pytest.fixture
def client():
    """Cree une application de test avec une base en memoire."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client


def test_liste_vide_au_depart(client):
    reponse = client.get("/api/taches")
    assert reponse.status_code == 200
    assert reponse.get_json() == []


def test_creation_tache(client):
    reponse = client.post("/api/taches", json={"titre": "Ma tache", "priorite": "Haute"})
    assert reponse.status_code == 201
    data = reponse.get_json()
    assert data["titre"] == "Ma tache"
    assert data["priorite"] == "Haute"
    assert data["id"] is not None


def test_creation_sans_titre_refusee(client):
    reponse = client.post("/api/taches", json={"responsable": "X"})
    assert reponse.status_code == 400


def test_modification_tache(client):
    cree = client.post("/api/taches", json={"titre": "A modifier"}).get_json()
    reponse = client.put(f"/api/taches/{cree['id']}", json={"statut": "Termine", "avancement": 100})
    assert reponse.status_code == 200
    data = reponse.get_json()
    assert data["statut"] == "Termine"
    assert data["avancement"] == 100


def test_suppression_tache(client):
    cree = client.post("/api/taches", json={"titre": "A supprimer"}).get_json()
    suppression = client.delete(f"/api/taches/{cree['id']}")
    assert suppression.status_code == 200
    # La tache ne doit plus exister
    assert client.get(f"/api/taches/{cree['id']}").status_code == 404


def test_statistiques(client):
    client.post("/api/taches", json={"titre": "T1", "statut": "Termine", "avancement": 100})
    client.post("/api/taches", json={"titre": "T2", "statut": "En cours", "avancement": 50})
    stats = client.get("/api/stats").get_json()
    assert stats["total"] == 2
    assert stats["terminees"] == 1
    assert stats["taux_completion"] == 50
