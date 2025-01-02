# app.py
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create API instance
api = Api(app)

# Ensure database tables exist
@app.before_request
def create_tables():
    #db.create_all()
    pass

# CRUD Operations
class UserAPI(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404
            return user.as_dict(), 200
        else:
            users = User.query.all()
            return [user.as_dict() for user in users], 200

    def post(self):
        data = request.get_json()
        try:
            new_user = User(name=data['name'], email=data['email'])
            db.session.add(new_user)
            db.session.commit()
            return {"message": "User created successfully"}, 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        data = request.get_json()
        try:
            user.name = data.get('name', user.name)
            user.email = data.get('email', user.email)
            db.session.commit()
            return {"message": "User updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        try:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

# API Routes
api.add_resource(UserAPI, '/users', '/users/<int:user_id>')

if __name__ == '__main__':
    app.run(debug=True)
