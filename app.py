from flask import Flask, request, jsonify, session, render_template
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from models import db, User
from bs4 import BeautifulSoup
import os
import requests



app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'srn-raj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasj.db'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return "<p>Test page</p>"

@app.route("/api/search")
def search():
    keyword = request.args.get('keyword')
    url = f'https://www.amazon.com/s?k={keyword}'

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    results = soup.select('.s-result-item')

    for result in results:
        title_element = result.select_one('.a-text-normal')
        price_element = result.select_one('.a-price-whole')
        image_element = result.select_one('.s-image')

        if title_element and price_element and image_element:
            title = title_element.get_text(strip=True)
            price = price_element.get_text(strip=True)
            image_url = image_element.get('src')

            products.append({
                'title': title,
                'price': price,
                'image_url': image_url
            })

    return jsonify(products)


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


