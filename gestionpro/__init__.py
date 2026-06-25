"""
Fabrique d'application (pattern "application factory").

La fonction create_app() construit et configure l'application Flask :
elle relie la base de donnees, enregistre l'API REST et la page web.
Ce pattern facilite les tests (on peut creer une app isolee avec une base
en memoire).
"""

from pathlib import Path

from flask import Flask, render_template

from .database import db
from .api import api


def create_app(config: dict | None = None) -> Flask:
    """Cree et configure l'application Flask.

    Args:
        config: dictionnaire de configuration optionnel (utile pour les tests,
            par exemple pour utiliser une base SQLite en memoire).
    """
    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    # Configuration par defaut : base SQLite dans un fichier local
    chemin_base = Path(app.root_path).parent / "gestionpro.db"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{chemin_base}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Surcharge eventuelle (tests)
    if config:
        app.config.update(config)

    # Initialisation de la base et creation des tables
    db.init_app(app)
    with app.app_context():
        from . import models  # import pour enregistrer les tables
        db.create_all()

    # Enregistrement de l'API sous /api
    app.register_blueprint(api, url_prefix="/api")

    # Page web principale
    @app.route("/")
    def accueil():
        return render_template("index.html")

    return app
