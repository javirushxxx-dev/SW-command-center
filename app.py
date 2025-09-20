# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# --- Configuration ---
# Create the Flask app instance
app = Flask(__name__)

# Set the database location. It will create a file named 'database.db' in the same folder.
# For deployment, this will be replaced by the hosting service's database URL.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)


# --- Database Model ---
# This defines the structure of your 'Client' table in the database.
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Unique ID for each client
    alias = db.Column(db.String(100), nullable=False) # Client's name/alias
    contact_info = db.Column(db.String(200), unique=True, nullable=False) # Phone, email, etc.
    notes = db.Column(db.Text, nullable=True) # General notes
    is_verified = db.Column(db.Boolean, default=False) # A simple flag for verification
    is_blacklisted = db.Column(db.Boolean, default=False) # A flag for blacklisting

    def to_dict(self):
        """Converts the client object to a dictionary for easier use with the API."""
        return {
            'id': self.id,
            'alias': self.alias,
            'contact_info': self.contact_info,
            'notes': self.notes,
            'is_verified': self.is_verified,
            'is_blacklisted': self.is_blacklisted
        }


# --- API Routes ---
# This is the "front door" to your backend.

# Route to add a new client
@app.route('/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    new_client = Client(
        alias=data['alias'],
        contact_info=data['contact_info'],
        notes=data.get('notes', ''),
        is_verified=data.get('is_verified', False)
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify(new_client.to_dict()), 201

# Route to get all clients
@app.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

# Route to get a single client by their ID
@app.route('/clients/<int:id>', methods=['GET'])
def get_client(id):
    client = Client.query.get_or_404(id)
    return jsonify(client.to_dict())


# A simple command to create the database table the first time you run it.
with app.app_context():
    db.create_all()
