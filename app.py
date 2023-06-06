from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from flask_session import Session
from models import db, User
import redis
import os


app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'srn-raj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasj.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

SESSION_TYPE = "redis"
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True
SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")


bcrypt = Bcrypt(app)
server_session = Session(app)


CORS(app, supports_credentials=True)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return "<p>Hello, World</p>"

@app.route("/signup", methods=["POST"])
def signup():
    
   email = request.json["email"]
   password = request.json["password"]
   
   user_exists = User.query.filter_by(email=email).first() is not None
   
   if user_exists:
       return jsonify({"Error": "Email alreay Exists "}), 409
   
   
   hashed_password = bcrypt.generate_password_hash(password)
   new_user = User(email=email, password=hashed_password)
   db.session.add(new_user)
   db.session.commit()
   
   session["user_id"] = new_user.id
   
   return jsonify({
        
        "id": new_user.id,
        "email": new_user.email
    })
    
@app.route("/login", methods = ["POST"])
def login_user():
   email = request.json["email"]
   password = request.json["password"]
   
   user = User.query.filter_by(email=email).first() 
   
   if user is None:
       return jsonify({"Error": "Unauthorized Access"}), 401
   
   if not bcrypt.check_password_hash(user.password, password):
       return jsonify({"Error": "Unaithorized"}), 401
   
   session["user_id"] = user.id
   
   return jsonify({
       "id": user.id,
       "email": user.email
   })
if __name__ == "__main__":
    app.run(debug=True)


