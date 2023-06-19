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
    url = f'https://www.amazon.in/s?k={keyword.replace}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for result in results:
            title_elem = result.find('span', {'class': 'a-size-medium'})
            price_elem = result.find('span', {'class': 'a-price-whole'})
            image_elem = result.find('img', {'class': 's-image'})
            product = {
                'title': title_elem,
                'price': price_elem,
                'image_url': image_elem,
            }
            products.append(product)

        return products
    
    return None


#def scrape_flipkart(keyword):
    url = f'https://www.flipkart.com/search?q={keyword.replace(" ", "+")}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        products = []
        
        results = soup.find_all('div', {'class': '_1YokD2 _3Mn1Gg'})

        for result in results:
            title = result.find('a', {'class': '_4rR01T'}).text.strip()
            price = result.find('div', {'class': '_30jeq3 _1_WHN1'}).text.strip()
            image_url = result.find('img', {'class': '_396cs4'}).get('src')

            product = {
                'title': title,
                'price': price,
                'image_url': image_url
            }
            products.append(product)

        return products
    
    return None


@app.route('/search', methods=['POST'])
def search():
    keyword = request.json['keyword']

    amazon_products = scrape_amazon(keyword)
    #flipkart_products = scrape_flipkart(keyword)

    if amazon_products is not None: #and flipkart_products is not None:
        return jsonify({
            'amazon': amazon_products,
            #'flipkart': flipkart_products
        })
    else:
        return jsonify({'error': 'Error fetching search results'}), 500







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
   
@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user ID from the session to log the user out
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/user', methods=['GET'])
def get_user_info():
    user_id = session.get('user_id')

    if user_id:
        user = User.query.get(user_id)

        if user:
            return jsonify({
                'id': user.id,
                'email': user.email
            })

    return jsonify({'message': 'User not found'}), 404


if __name__ == "__main__":
    app.run(debug=True)


