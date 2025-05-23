from app import create_app, db
import os

app = create_app()

# Inicializar la base de datos con el contexto de la aplicación
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)