"""Point d'entree : lance le serveur web GestionPro."""
from gestionpro import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
