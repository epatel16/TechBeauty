from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
import sys
from collections import defaultdict
from datetime import date

# SQLAlchemy for Interactions with MySQL
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import exc

app = Flask(__name__)

DEBUG = 1

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://client:clientpwd@localhost/cosmeticsdb'

# Start MySQL session
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db = scoped_session(sessionmaker(bind=engine))

########################################
#           Helper Functions           #
########################################

###### 1. Helpers for authentication and new user registrations
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
    if db.execute(text("SELECT * FROM user_info WHERE username = :username;"), 
                      {"username": username}).rowcount != 0:
        return 1
    else: 
        return 0

###### 2. Helpers for cart and purchases
# execute a procedure to add an item to a cart
def add_item(product_id):
    ## execute our pre-loaded MySQL procedure `add_item_cart`
    add_cart = "CALL add_item_cart(\'%s\', \'%s\');" % (session.get("username"), product_id)
    try:
        db.execute(text(add_cart))
        db.commit()
        return 1
    except exc.DatabaseError as e:
        return 0

# execute a procedure to decrease the number of an item to a cart
def decrease_item(product_id):
    ## execute our pre-loaded MySQL procedure `decrease_item`
    remove_item = "CALL decrease_item_cart(\'%s\', \'%s\');" % (session.get("username"), product_id)
    try:
        db.execute(text(remove_item))
        db.commit()
        return 1
    except exc.DatabaseError as e:
        return 0
    
# execute a procedure to delete an item to a cart
def delete_from_cart(product_id):
    ## execute our pre-loaded MySQL procedure `delete_item_cart`
    delete = "CALL delete_item_cart(\'%s\', \'%s\');" % (session.get("username"), product_id)
    try:
        db.execute(text(delete))
        db.commit()
        return 1
    except exc.DatabaseError as e:
        return 0
    
# get all items in the cart for the user
def get_cart():
    items = db.execute(text("SELECT product_id, price, num_items, brand_name, product_name \
                            FROM cart NATURAL LEFT JOIN product \
                            NATURAL JOIN store NATURAL JOIN brand WHERE username=\'%s\'" % 
                            session.get("username"))).fetchall()
    return items

# get the total value of the cart
def get_cart_total():
    total = db.execute(text("SELECT calculate_cart_total(\'%s\')" % session.get("username"))).fetchone()
    if not total[0]:
        return 0
    return total[0]

# get all the relevant purchase histories
def get_purchase_history():
    purchases = db.execute(text("SELECT * FROM purchase_history NATURAL JOIN product WHERE \
                             username=\'%s\'" % session.get("username"))).fetchall()
    # we will group purchase history by timestamp
    # so purchases made together can be shown as a singular purchase
    history = defaultdict(list)
    for purchase in purchases:
        history[purchase.purchase_time].append(purchase)
    return history

####### 3. Helpers for querying products and brands
# execute a MySQL query to get the list of
# all available products on the storefront
def get_all_products():
    product = db.execute(text("SELECT brand_id, product_id, product_name, brand_name,\
                               price, rating, inventory FROM product \
                               NATURAL JOIN store NATURAL JOIN brand ORDER BY product_name ASC")).fetchall()
    return product

# execute a MySQL query to get the list of all `brand_id`s 
# and `brand_name`s from database 
def get_all_brands():
    brand = db.execute(text("SELECT brand_id, brand_name FROM brand ORDER BY brand_name ASC")).fetchall()
    return brand

# execute a MySQL query to get all the ingredients of a given product
def get_ingredients_of_product(product_id):
    ingredients = db.execute(text("SELECT ingredient_name FROM has_ingredient \
                                  NATURAL JOIN ingredient WHERE product_id=%s" % product_id)).fetchall()
    res = []
    for ing in ingredients:
        res.append(ing[0].capitalize())
    return res

def search_by_ingredient(ingredient, additional_query=""):
    query = "SELECT product_id, brand_name, product_name, product_type, \
            price, rating FROM product NATURAL JOIN (SELECT product_id FROM \
            has_ingredient NATURAL JOIN ingredient WHERE \
            ingredient_name LIKE \'%%%s%%\') AS p NATURAL JOIN store \
            NATURAL JOIN brand %s;" % (ingredient, additional_query)
    products = db.execute(text(query)).fetchall()
    return products

# execute a query to get a list of products given the query
# note that this function is ONLY used for the case where we browse
# a list of products, for which we will always return same set of
# attributes 
def browse_products(sql = ''):
    sql = 'SELECT product_id, brand_name, product_name, product_type, \
            price, rating, inventory FROM product \
            NATURAL JOIN store NATURAL JOIN brand %s;' % sql
    rows = db.execute(text(sql)).fetchall()
    return rows    

# execute a query to get singular product given the query
def browse_one_products(sql = ''):
    sql = 'SELECT * FROM product NATURAL JOIN store NATURAL JOIN brand %s;' % sql
    rows = db.execute(text(sql)).fetchone()
    return rows    


########################################
#          Handling Requests           #
########################################
#Index page where new users can register
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", login = session.get("logged_in",), username = session.get('username'))
      
# User attemps to log in
@app.route("/login", methods=["POST", "GET"])
def login():
    ## is the user is already logged in
    if session.get("logged_in"):
        return redirect(url_for('index'))
    
    ## if the request method is GET
    if request.method == "GET":
        return render_template("auth/login.html", login=session.get("logged_in"), username=session.get("username"))
    
    ## if the request method is POST
    # get username and password from the form
    username = request.form.get('username')
    password = request.form.get('password')

    #Check if the user entered username and password
    if username is None or password is None:
        return render_template("auth/login.html", message = "Please fill in all the required fields.", 
                                login = session.get("logged_in"))

    #Check if credentials are correct
    if not authenticate(username, password):
        return render_template("auth/login.html", message="Wrong credentials. Try again.",
                                login=session.get("logged_in"),username=session.get("username"))
    # set session variables
    else:
        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for('index'))

# When user attemps to log out
@app.route("/logout")
def logout():
    # reset session variables and flush out session
    session["logged_in"] = False
    session["username"] = ""
    session.clear()
    return redirect(url_for('index'))

# When user registers for a new account
@app.route("/register", methods=["POST", "GET"])
def register():
    ## if the user is already logged in, take them to home
    if session.get("logged_in"):
        return redirect(url_for('index'))
    
    ## if request method is "GET"
    if request.method == "GET":
        return render_template("auth/register.html", login=session.get("logged_in"), username=session.get("username"))
    
    ## if request method is "POST"
    #Get data from the form
    username = request.form.get('username').lower()
    password = request.form.get('password')

    # Check if inputs match the criteria
    if username is None or password is None:
        return render_template("auth/register.html", message = "Missing required fields", 
                                login=session.get("logged_in"), username = session.get("username"))
    elif len(username) < 6 or len(username) > 20:
        return render_template("auth/register.html", message="Username must be between 6 and 20 characters", 
                                login = session.get("logged_in"), username = session.get("username"))
    elif len(password) < 8 or len(password) > 20:
        return render_template("auth/register.html", message="Password must be between 8 and 20 characters", 
                                login=session.get("logged_in"), username = session.get("username"))

    # Insert new user into database
    if check_username(username):
        return render_template("auth/register.html", message = "Username already exists :(", 
                                login=session.get("logged_in"), username = session.get("username"))
    else:
        db.execute(text("CALL sp_add_user(:username, :pwd)"),{"username": username, "pwd":password})
        db.commit()
        return render_template("auth/login.html", message = "Please sign in.",
                                login = session.get("logged_in"), username = session.get("username"))

# When user forgets password and tries to reset
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    return None

# Search page for users to filter all products
@app.route("/products", methods=["POST", "GET"])
def products():
   product = get_all_products()
   brands = get_all_brands()
   return render_template("main/products.html", products=product, brands=brands,
                          login=session.get("logged_in"), username=session.get("username"))

## SUBROUTES of Products
# Detailed information about the selected product
@app.route("/products/product_id=<product_id>", methods=["GET"])
def product(product_id):
   result = browse_one_products("WHERE product_id=%s" % product_id)
   ingredients = get_ingredients_of_product(product_id)
   return render_template('main/product.html', product=result, ingredients=ingredients,
                          login=session.get("logged_in"), username=session.get('username'))

@app.route("/product_filter", methods=["POST"])
def product_filter():
    brand = request.form.get('brand')
    product_type = request.form.get('prod_type')
    ingredient = request.form.get('ingredients')
    sql_query_list = []
    if brand != "-1":
        sql_query_list.append("brand_id=%s" % brand)
    if product_type != "-1":
        sql_query_list.append("product_type=\'%s\'" % product_type)
    sql = "WHERE " + (" AND ".join(sql_query_list))
    if ingredient:
        if sql_query_list:
            result = search_by_ingredient(ingredient, sql)
        else:
            result = search_by_ingredient(ingredient)
    else:
        if sql_query_list:
            result = browse_products(sql)
        else:
            return redirect(url_for("products"))
    brands = get_all_brands()
    return render_template("main/products.html", products=result, brands=brands,
                        login=session.get("logged_in"), username=session.get("username"))

# Page to show all brands
@app.route("/brands", methods=["POST", "GET"])
def brands():
    brand = get_all_brands()
    alphabets = {}
    for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        alphabets[l] = []
    for (_, brand_name) in brand:
        alphabets[brand_name[0].upper()].append(brand_name)
    return render_template("main/brands.html", brands=alphabets, login=session.get("logged_in"), username=session.get("username"))

## SUBROUTES of Brands
# Page to show a brand and all of its products
@app.route("/brands/brand_name=<brand_name>", methods=["GET"])
def brand(brand_name = None):
    prods = browse_products('WHERE brand_name=\'%s\''% brand_name)
    return render_template("main/brand.html", products=prods, login=session.get("logged_in"), username=session.get("username"))

# Search by Product Type
@app.route("/products/product_type=<product_type>", methods=['GET'])
def product_type(product_type):
    prods = browse_products('WHERE product_type=\'%s\'' % product_type)
    return render_template("main/products.html", products=prods, login=session.get("logged_in"), username=session.get("username"))

# add to shopping cart
@app.route("/add_to_cart/product_id=<product_id>", methods=["POST"])
def add_to_cart(product_id):
    if not session.get("logged_in"):
        return redirect(url_for('login'))
    if request.method == "POST":
        if add_item(product_id):
            return redirect(url_for('cart'))
        else:
            result = browse_one_products("WHERE product_id=%s" % product_id)
            ingredients = get_ingredients_of_product(product_id)
            return render_template('main/product.html', product=result, ingredients=ingredients,
                                   message="Item cannot be added right now. Item sold out on website!",
                                   login=session.get("logged_in"), username=session.get('username'))
    else:
        return redirect(url_for('cart'))

# check shopping cart
@app.route("/cart", methods=['GET'])
def cart():
    if session.get("logged_in"):
        items = get_cart()
        total_cart = get_cart_total()
        return render_template('cart/cart.html', cart_items=items, total_value=total_cart,
                               login=session.get("logged_in"), username=session.get('username'))
    else:
        return redirect(url_for('login'))

# update the number of an item in one's cart
@app.route("/update_cart/product_id=<product_id>&is_increase=<is_increase>", methods=["POST"])
def update_cart(product_id, is_increase=False):
    if is_increase == "1":
        add_item(product_id)
    else:
        decrease_item(product_id)
    return redirect(url_for('cart'))

# deletes an item from the user's cart
@app.route("/delete_item/product_id=<product_id>", methods=["POST"])
def delete_item(product_id):
    delete_from_cart(product_id)
    return redirect(url_for('cart'))

# check out items in your cart
@app.route("/checkout", methods=["POST"])
def checkout():
    if session.get("logged_in"):
        items = get_cart()
        total_cart = get_cart_total()
        sql = "CALL move_cart_to_purchase_history(\'%s\')" % session.get("username")
        try:
            db.execute(text(sql))
            db.commit()
            return render_template('cart/purchase_complete.html', items=items, order_date=date.today(),
                           total_price = total_cart, login=session.get("logged_in"), 
                           username=session.get("username"))
        except exc.DatabaseError as e:
            return render_template('cart/cart.html', cart_items=items, total_value=total_cart,
                               message="We are currently unable to check out your order.",
                               login=session.get("logged_in"), username=session.get('username'))
    else:
        return redirect(url_for('login'))
    

# my page to see order history, etc.
@app.route("/mypage")
def mypage():
    if session.get("logged_in"):
        history = get_purchase_history()
        return render_template('auth/mypage.html', history=history,
                               login=session.get("logged_in"), username=session.get("username"))
    else:
        return redirect(url_for("login"))