"""Initialisation de la base de donnees (SQLAlchemy)."""

from flask_sqlalchemy import SQLAlchemy

# Objet base de donnees partage par toute l'application
db = SQLAlchemy()
