from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
import requests

# SQLAlchemy for Interactions with MySQL
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text


app = Flask(__name__)

DEBUG = 1

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
## TODO: check permissions - client doesn't have access to authenticate procedure
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:adminpwd@localhost/cosmeticsdb'

# Start MySQL session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = scoped_session(sessionmaker(bind=engine))

########################################
#           Helper Functions           #
########################################

# execute a MySQL query to get the list of
# all available products on the storefront
def get_all_products():
    product = db.execute(text("SELECT brand_id, product_id, product_name, brand_name, price, rating FROM product \
                              NATURAL JOIN store NATURAL JOIN brand ORDER BY product_name ASC")).fetchall()
    return product

# execute a MySQL query to get the list of all `brand_id`s 
# and `brand_name`s from database 
def get_all_brands():
    brand = db.execute(text("SELECT brand_id, brand_name FROM brand ORDER BY brand_name ASC")).fetchall()
    return brand

# attempt to authenticate user given username and password, return the result
def authenticate(username, password) -> bool:
    # execute our pre-loaded MySQL procedure `authenticate`
    # to authenticate a user given username and password
    auth = "SELECT authenticate(\'%s\', \'%s\');" % (username, password)
    rows = db.execute(text(auth)).fetchone()
    # if the query returns no result, or if the returned result
    # is False, then return False
    if len(rows) == 0 or rows[0] == 0:
        return 0
    # else, set the session variable `loggedin` to True and set
    # the session variable `username` to the username of the user
    session["loggedin"] = True
    session["username"] = username
    return 1

# execute a query to check if the username exists in the database
def check_username(username) -> bool:
    # select users who have a matching username
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
        return 1
    else: 
        return 0

# execute a query to get a list of products given the query
# note that this function is ONLY used for the case where we browse
# a list of products, for which we will always return same set of
# attributes 
def browse_products(sql = ''):
    sql = 'SELECT product_id, brand_name, product_name, product_type, rating FROM product \
            NATURAL JOIN store NATURAL JOIN brand %s;' % sql
    db.execute(sql)
    rows = db.fetchall()
    return rows    


########################################
#          Handling Requests           #
########################################
#Index page where new users can register
@app.route("/")
def index():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    return render_template("index.html", login = session.get("logged_in",), username = session.get('username'))
        
#Login
@app.route("/login", methods=["POST", "GET"])
def login():
    if session.get("logged_in"):
        return redirect(url_for('home'))
    if request.method == "GET":
        return render_template("auth/login.html", login=session.get("logged_in"), username=session.get("username"))
    else:
        username = request.form.get('username')
        password = request.form.get('password')

        #Check if the user entered username and password
        if (username is None) or (password is None):
            return render_template("auth/login.html", message = "Please fill in all the required fields.", 
                                    login = session.get("logged_in"))

        #Check if credentials are correct
        if not authenticate(username, password):
            return render_template("auth/login.html", message="Wrong credentials. Try again.",
                                    login=session.get("logged_in"),username=session.get("username"))
        else:
            return redirect(url_for('home'), login=session.get("logged_in"),username=session.get("username"))

#Logout - clear the session when users log out
@app.route("/log_out")
def log_out():
    session["logged_in"] = False
    session.clear()
    return redirect(url_for('index'))

#Register - make an account
@app.route("/register", methods=["POST", "GET"])
def register():
    if session.get("logged_in"):
        return redirect(url_for('home'))
    if request.method == "GET":
        return render_template("auth/register.html", login=session.get("logged_in"), username=session.get("username"))
    if request.method == "POST":
        #Get data from the form
        username = request.form.get('username').lower()
        password = request.form.get('password')

        # Check if inputs match the criteria
        if username is None or password is None:
            return render_template("auth/register.html", message = "Please fill in all the required fields.", 
                                   login=session.get("logged_in"), username = session.get("username"))
        elif len(username) < 6:
            return render_template("auth/register.html", message="Your username has to be 6 characters or longer.", 
                                   login = session.get("logged_in"), username = session.get("username"))
        elif len(password) < 8:
            return render_template("auth/register.html", message="Your password has to be 8 characters or longer.", 
                                   login=session.get("logged_in"), username = session.get("username"))

        # Insert new user into database
        if check_username(username):
            return render_template("auth/register.html",  message = "Username already exists :(", 
                                   login=session.get("logged_in"), username = session.get("username"))
        else:
            db.execute("CALL sp_add_users(:username, :pwd)",{"username": username, "pwd":password})
            db.commit()
            return render_template("auth/login.html", message = "Please sign in.",
                                   login = session.get("logged_in"), username = session.get("username"))

#Search page for users to filter all products
@app.route("/products", methods=["POST", "GET"])
def products():
   product = get_all_products()
   return render_template("main/products.html", products=product, login=session.get("logged_in"), username=session.get("username"))

# SUBROUTES of Products
#Detailed information about the selected product
@app.route("/products/product_id=<product_id>", methods=["GET"])
def product(product_id):
   return None

#Show all brands
@app.route("/brands", methods=["POST", "GET"])
def brands():
    brand = get_all_brands()
    alphabets = {}
    for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        alphabets[l] = []
    for (_, brand_name) in brand:
        alphabets[brand_name[0].upper()].append(brand_name)
    return render_template("main/brands.html", brands=alphabets, login=session.get("logged_in"), username=session.get("username"))

# SUBROUTES of Brands
@app.route("/brand/brand_id=<brand_id>", methods=["GET"])
def brand(brand_id):
    return None

#Adding product to shopping cart
@app.route("/addToCart")
def addToCart():
    return None

#Checking shopping cart
@app.route("/cart")
def cart():
    return None