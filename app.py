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

@app.route('/search',methods=['POST'])
def search_products():
    try:
        # Retrieve the keyword from the request body
        keyword = request.json['keyword']

        # Perform the search operation and retrieve the HTML content
        url = f'https://www.amazon.in/s?k={keyword}'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        content = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Extract the relevant information from the parsed HTML
        products = []
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for result in results:
            title_elem = result.find('span', {'class': 'a-size-medium'})
            price_elem = result.find('span', {'class': 'a-price-whole'})
            image_elem = result.find('img', {'class': 's-image'})
            product_elem = 'https://www.amazon.in' + result.find('a', class_='a-link-normal')['href']
            rating_elem = result.find('span', {'class': 'a-icon-alt'})
            
            if title_elem and price_elem and image_elem:
                product = {
                    'title': title_elem.text.strip(),
                    'price': price_elem.text.strip(),
                    'image_url': image_elem.get('src'),
                    'product_url':product_elem,
                    'rating':rating_elem.text.strip(),
                }
                products.append(product)

        # Return the results as a JSON response
        return jsonify(products)

    except Exception as e:
        # Log the error message
        print('Error:', str(e))

        # Return an error response
        return jsonify({'error': 'An error occurred during the search.'}), 500



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


