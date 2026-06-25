"""
API REST de l'application (operations CRUD + statistiques).

Toutes les routes renvoient du JSON. Elles sont regroupees dans un "blueprint"
Flask, monte sous le prefixe /api (voir __init__.py).

Routes :
    GET    /api/taches            -> liste des taches (filtre ?statut=...)
    POST   /api/taches            -> creation d'une tache
    GET    /api/taches/<id>       -> detail d'une tache
    PUT    /api/taches/<id>       -> mise a jour d'une tache
    DELETE /api/taches/<id>       -> suppression d'une tache
    GET    /api/stats             -> indicateurs pour le tableau de bord
"""

from flask import Blueprint, request, jsonify, abort

from .database import db
from .models import Tache, STATUTS, PRIORITES

api = Blueprint("api", __name__)


@api.get("/taches")
def lister_taches():
    """Renvoie la liste des taches, avec filtre optionnel par statut."""
    statut = request.args.get("statut")
    requete = Tache.query
    if statut in STATUTS:
        requete = requete.filter_by(statut=statut)
    taches = requete.order_by(Tache.date_creation.desc()).all()
    return jsonify([t.to_dict() for t in taches])


@api.post("/taches")
def creer_tache():
    """Cree une nouvelle tache a partir du JSON recu."""
    donnees = request.get_json(silent=True) or {}
    if not donnees.get("titre"):
        abort(400, description="Le champ 'titre' est obligatoire.")
    tache = Tache.depuis_dict(donnees)
    db.session.add(tache)
    db.session.commit()
    return jsonify(tache.to_dict()), 201


@api.get("/taches/<int:tache_id>")
def detail_tache(tache_id: int):
    """Renvoie le detail d'une tache."""
    tache = db.session.get(Tache, tache_id)
    if tache is None:
        abort(404, description="Tache introuvable.")
    return jsonify(tache.to_dict())


@api.put("/taches/<int:tache_id>")
def modifier_tache(tache_id: int):
    """Met a jour une tache existante."""
    tache = db.session.get(Tache, tache_id)
    if tache is None:
        abort(404, description="Tache introuvable.")
    donnees = request.get_json(silent=True) or {}
    tache.appliquer(donnees)
    db.session.commit()
    return jsonify(tache.to_dict())


@api.delete("/taches/<int:tache_id>")
def supprimer_tache(tache_id: int):
    """Supprime une tache."""
    tache = db.session.get(Tache, tache_id)
    if tache is None:
        abort(404, description="Tache introuvable.")
    db.session.delete(tache)
    db.session.commit()
    return jsonify({"message": "Tache supprimee", "id": tache_id})


@api.get("/stats")
def statistiques():
    """Calcule les indicateurs affiches sur le tableau de bord."""
    taches = Tache.query.all()
    total = len(taches)

    # Repartition par statut et par priorite
    par_statut = {s: 0 for s in STATUTS}
    par_priorite = {p: 0 for p in PRIORITES}
    for t in taches:
        par_statut[t.statut] = par_statut.get(t.statut, 0) + 1
        par_priorite[t.priorite] = par_priorite.get(t.priorite, 0) + 1

    terminees = par_statut.get("Termine", 0)
    taux_completion = round(100 * terminees / total) if total else 0
    avancement_moyen = round(sum(t.avancement for t in taches) / total) if total else 0

    return jsonify({
        "total": total,
        "terminees": terminees,
        "taux_completion": taux_completion,
        "avancement_moyen": avancement_moyen,
        "par_statut": par_statut,
        "par_priorite": par_priorite,
    })
