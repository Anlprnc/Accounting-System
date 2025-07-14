from flask import Flask
from models import db
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.accounting_routes import accounting_bp
from routes.invoice_routes import invoice_bp
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///accounting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

db.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(accounting_bp)
app.register_blueprint(invoice_bp)

with app.app_context():
    db.create_all()

@app.route('/')
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/api/health')
def health_check():
    return {
        'status': 'healthy',
        'message': 'Accounting API is running'
    }

if __name__ == '__main__':
    app.run(debug=True)