from flask import Flask
from flask_cors import CORS

from .routes import routes


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(routes)

    CORS(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)
