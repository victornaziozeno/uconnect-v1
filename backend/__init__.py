from flask import Flask

def create_app():
    app = Flask(__name__)

    # Configurações
    app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

    # Importando rotas
    from .routes import main
    app.register_blueprint(main)

    return app
