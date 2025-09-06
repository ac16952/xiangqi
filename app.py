from flask import Flask
from flask_cors import CORS
from api.routes import api as api_blueprint

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    
    # Enable CORS for all domains on all routes
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register the API blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
