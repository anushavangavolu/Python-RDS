import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flasgger import Swagger

# Initialize Flask app and configure
app = Flask(__name__)

def read_secret(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None
    except UnicodeDecodeError as e:
        raise ValueError(f"Error reading secret file {file_path}: {e}")


# Construct DATABASE_URL from environment variables
username = os.getenv('DB_USERNAME', '<username>')
password = read_secret(os.getenv('DB_PASSWORD_FILE', 'default_password'))
rds_endpoint = os.getenv('DB_ENDPOINT', '<rds_endpoint>')
database = os.getenv('DB_NAME', '<database>')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{rds_endpoint}/{database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
Swagger(app, template_file='swagger.yaml')


# Define User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

# Routes
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data['username'] == 'admin' and data['password'] == 'password':
        token = create_access_token(identity={'username': data['username']})
        return jsonify({'token': token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([{'id': user.id, 'name': user.name, 'email': user.email} for user in users])

@app.route('/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.json
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'name': new_user.name, 'email': new_user.email}), 201

@app.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json
    user.name = data['name']
    user.email = data['email']
    db.session.commit()
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Run the app
if __name__ == '__main__':
    # Use '127.0.0.1' to bind to localhost, or '0.0.0.0' for external access
    app.run(host='127.0.0.1', port=5000, debug=True)