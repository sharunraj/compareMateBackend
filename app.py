from flask import Flask, request, jsonify, session, render_template, make_response
from flask_bcrypt import Bcrypt
from flask_cors import CORS, cross_origin
from models import db, User
from bs4 import BeautifulSoup
import os
import requests



app = Flask(__name__)
CORS(app)
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

def scrape_amazon(keyword):
    url = f'https://www.amazon.in/s?k={keyword}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []
    results = soup.find_all('div', {'data-component-type': 's-search-result'})

    for result in results:
        title = result.find('span', class_='a-text-normal').text.strip()
        price = result.find('span', class_='a-offscreen').text.strip()
        image_url = result.find('img')['src']
        product_url = result.find('a', class_='a-link-normal')['href']
        rating = result.find('span', {'class': 'a-icon-alt'}).text.strip()

        product = {
            'title': title,
            'price': price,
            'image_url': image_url,
            'product_url': product_url,
            'rating': rating
        }
        products.append(product)

    return products

def scrape_reliance_digital(keyword):
    url = f'https://www.reliancedigital.in/search?q={keyword}'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []
    results = soup.find_all('div', {'class': 'product-card'})

    for result in results:
        title = result.find('div', {'class': 'product-title'}).text.strip()
        price = result.find('div', {'class': 'product-price'}).text.strip()
        image_url = result.find('img', {'class': 'product-img'})['src']
        product_url = result.find('a')['href']
        rating = result.find('div', {'class': 'rating-value'}).text.strip()

        product = {
            'title': title,
            'price': price,
            'image_url': image_url,
            'product_url': product_url,
            'rating': rating
        }
        products.append(product)

    return products

@app.route('/search', methods=['POST'])
def search_products():
    keyword = request.json.get('keyword')
    
    amazon_results = scrape_amazon(keyword)
    reliance_results = scrape_reliance_digital(keyword)
    
    results = {
        'amazon': amazon_results,
        'reliance': reliance_results
    }
    
    return jsonify(results)

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


