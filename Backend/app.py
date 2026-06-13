import os
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import Config
from database import db, bcrypt
from auth import auth_bp
from routes import api_bp


def create_app():
    frontend_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "Frontend")
    )
    app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    Limiter(get_remote_address, app=app, default_limits=["200 per minute"])

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    def root():
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/<path:path>")
    def static_proxy(path):
        full = os.path.join(frontend_dir, path)
        if os.path.isfile(full):
            return send_from_directory(frontend_dir, path)
        return send_from_directory(frontend_dir, "index.html")

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(_):
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise  # still raise so Render shows the real error in logs

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)