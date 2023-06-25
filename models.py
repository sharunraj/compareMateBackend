from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

db = SQLAlchemy()

def get_uuid():
    return uuid4().hex

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(6), primary_key = True, unique = True, default=get_uuid)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.Text, nullable = False)
    
class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(200))
    user_id = db.Column(db.String(6), db.ForeignKey('users.id'), nullable=False)