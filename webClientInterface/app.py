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

########################################
#     1. Helpers for login/register    #
########################################

# attempt to authenticate user given username and password, return the result
def authenticate(username, password) -> bool:
    # execute our pre-loaded MySQL procedure `authenticate`
    # to authenticate a user given username and password
    auth = "SELECT authenticate(\'%s\', \'%s\');" % (username, password)
    # when there is a database error and the execution
    # doesn't go as expected
    try:
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
    except exc.DatabaseError as e:
        # if for some reason MySQL authenticate has returned an error
        # we give details of error to the user and return -1
        sys.stderr("MySQL Error: procedure authenticate errored.")
        sys.stderr("Error detail: %s" % e.detail)
        return -1

# execute a query to check if the username exists in the database
def check_username(username) -> bool:
    # select users who have a matching username
    try:
        rows = db.execute(text("SELECT * FROM user_info WHERE username = :username;"), 
                      {"username": username})
    except exc.DatabaseError as e:
        # if for some reason MySQL authenticate has returned an error
        # we give details of error to the user and return -1
        sys.stderr("MySQL Error: procedure authenticate errored.")
        sys.stderr("Error detail: %s" % e.detail)
        return -1
    
    # if the execution results in at least one row, return True
    if rows.rowcount != 0:
        return 1
    else: 
        return 0

########################################
#   2. Helpers for cart and purchases  #
########################################
    
# execute a procedure to add an item to a cart
def add_item(product_id):
    # execute our pre-loaded MySQL procedure `add_item_cart`
    # which adds an item to the given user's cart
    add_cart = "CALL add_item_cart(\'%s\', \'%s\');" % (session.get("username"), product_id)
    try:
        db.execute(text(add_cart))
        db.commit()
        return 1
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error calling add_item_cart: %s" % e.detail)
        return -1

# execute a procedure to decrease the number of an item to a cart
def decrease_item(product_id):
    # execute our pre-loaded MySQL procedure `decrease_item_cart`
    # which decreases the number of the given product in the user's cart
    remove_item = "CALL decrease_item_cart(\'%s\', \'%s\');" % (session.get("username"), product_id)
    try:
        db.execute(text(remove_item))
        db.commit()
        return 1
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error calling decrease_item_cart: %s" % e.detail)
        return 0
    
# execute a procedure to delete an item to a cart
def delete_from_cart(product_id):
    # execute our pre-loaded MySQL procedure `delete_item_cart`
    # which deletes the item completely from the user's cart
    delete = "CALL delete_item_cart(\'%s\', \'%s\');" % (session.get("username"), product_id)
    try:
        db.execute(text(delete))
        db.commit()
        return 1
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error calling delete_item_cart: %s" % e.detail)
        return 0
    
# get all items in the cart for the user
def get_cart():
    try:
        items = db.execute(text("SELECT product_id, price, num_items, \
            brand_name, product_name FROM cart NATURAL JOIN product \
            NATURAL JOIN store NATURAL JOIN brand WHERE username=\'%s\'" % 
            session.get("username"))).fetchall()
        return items
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error while getting all cart items: %s" % e.detail)
        return -1

# get the total value of the cart
def get_cart_total():
    try:
        # call procedure `calculate_cart_total` to compute the total value
        # of items in the user's cart
        total = db.execute(text("SELECT calculate_cart_total(\'%s\')" 
                                % session.get("username"))).fetchone()
        if not total[0]:
            return 0
        return total[0]
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error while getting cart total: %s" % e.detail)
        return -1

# get all the relevant purchase histories
def get_purchase_history():
    # selects every tuple from purchase_history associated with the user
    # also return product information to use for front-end display
    purchases = db.execute(text("SELECT * FROM purchase_history \
                     NATURAL JOIN product WHERE username=\'%s\'" % 
                      session.get("username"))).fetchall()
    # we will group purchase history by timestamp
    # so purchases made together can be shown as a singular purchase
    # this is because one purchase appears as multiple entries
    # due to our DDL design
    history = defaultdict(list)
    for purchase in purchases:
        history[purchase.purchase_time].append(purchase)
    return history

########################################
#3. Helper for querying products/brands#
########################################
# execute a MySQL query to get the list of
# all available products on the storefront
def get_all_products():
    # query to get all the products available on the website
    # order by product name ascending for readability
    try:
        product = db.execute(text("SELECT brand_id, product_id, product_name,\
                brand_name, price, rating, inventory FROM product \
                NATURAL JOIN store NATURAL JOIN brand \
                ORDER BY product_name ASC")).fetchall()
        return product
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error in get_all_products: %s" % e.detail)
        return -1

# execute a MySQL query to get the list of all `brand_id`s 
# and `brand_name`s from database 
def get_all_brands():
    try:
        # get brand_id and brand_name from brand table
        # to retrieve a list of all available brands
        brand = db.execute(text("SELECT * FROM \
                            brand ORDER BY brand_name ASC")).fetchall()
        # we won't check for the length of return value, because if
        # there is no brand to show, we can simply show an empty page
        return brand
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error in get_all_products: %s" % e.detail)
        return -1

# execute a MySQL query to get all the ingredients of a given product
def get_ingredients_of_product(product_id):
    try:
        # get all the ingredient names contained in the given product
        ingredients = db.execute(text("SELECT ingredient_name FROM \
                    has_ingredient NATURAL JOIN ingredient WHERE \
                    product_id=%s" % product_id)).fetchall()
        res = []
        for ing in ingredients:
            res.append(ing[0].capitalize())
        return res
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error in get_ingredients_of_product: %s" % e.detail)
        return -1

# search products by ingredient
# input `ingredient` is the user's regex input for ingredient name
# e.g. ingredient=beta will return any products with ingredients
# that contain beta in their names (e.g. beta-carotene)
def search_by_ingredient(ingredient, additional_query=""):
    # search by ingredient
    # we first select products that contain ingredients that match
    # the input regex. we then return all the information regarding
    # the product to the users
    query = "SELECT product_id, brand_name, product_name, product_type, \
            price, rating FROM product NATURAL JOIN (SELECT product_id FROM \
            has_ingredient NATURAL JOIN ingredient WHERE \
            ingredient_name LIKE \'%%%s%%\') AS p NATURAL JOIN store \
            NATURAL JOIN brand %s;" % (ingredient, additional_query)
    try:
        products = db.execute(text(query)).fetchall()
        return products
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error in search_by_ingredient: %s" % e.detail)
        return -1

# execute a query to get a list of products given the query
# note that this function is ONLY used for the case where we browse
# a list of products, for which we will always return same set of
# attributes 
def browse_products(sql = ''):
    sql = 'SELECT product_id, brand_name, product_name, product_type, \
            price, rating, inventory FROM product \
            NATURAL JOIN store NATURAL JOIN brand %s;' % sql
    try:
        rows = db.execute(text(sql)).fetchall()
        return rows
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error in browse_products: %s" % e.detail)
        return -1

# execute a query to get singular product given the query
def browse_one_products(sql = ''):
    sql = 'SELECT * FROM product NATURAL JOIN store NATURAL JOIN brand %s;' % sql
    try:
        rows = db.execute(text(sql)).fetchone()
        return rows
    except exc.DatabaseError as e:
        sys.stderr("MySQL Error in browse_one_product: %s" % e.detail)
        return -1


########################################
#          Handling Requests           #
########################################
    
#Index page where new users can register
@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", login = session.get("logged_in",), username = session.get('username'))
      
# Login page
# POST = when the login request is submitted
# GET = when the user tries to reach login page
@app.route("/login", methods=["POST", "GET"])
def login():
    ## is the user is already logged in
    if session.get("logged_in"):
        return redirect(url_for('index'))
    
    # if the request method is GET, open login page for users
    if request.method == "GET":
        # render_template will render html file with the given paramters
        # and redirect users to the html
        return render_template("auth/login.html", login=session.get("logged_in"), username=session.get("username"))
    
    # if the request method is POST
    # get username and password from the form
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if the user entered username and password
    if username is None or password is None:
        return render_template("auth/login.html", message = "Please fill in all the required fields.", 
                                login = session.get("logged_in"))

    # Check if credentials are correct
    if not authenticate(username, password):
        return render_template("auth/login.html", message="Wrong credentials. Try again.",
                                login=session.get("logged_in"),username=session.get("username"))
    
    # set session variables to maintain login status
    else:
        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for('index'))

# Logout page
# When user attemps to log out
@app.route("/logout")
def logout():
    # flushout session variables and redirect user to homepage
    session["logged_in"] = False
    session["username"] = ""
    session.clear()
    return redirect(url_for('index'))

# Signup page
# When user registers for a new account
# POST = user submits registration request
# GET = user tries to access registration page
@app.route("/register", methods=["POST", "GET"])
def register():
    # if the user is already logged in, take them to home
    if session.get("logged_in"):
        return redirect(url_for('index'))
    
    # if request method is "GET", take them to register.html
    if request.method == "GET":
        return render_template("auth/register.html", login=session.get("logged_in"), username=session.get("username"))
    
    # if request method is "POST"
    # Get data from the form
    username = request.form.get('username').lower()
    password = request.form.get('password')

    # Check if inputs match the criteria
    if username is None or password is None:
        return render_template("auth/register.html", message = "Missing required fields", 
                                login=session.get("logged_in"), username = session.get("username"))
    # note that both username and characters have length constraint
    # upper-bound is consistent with our DDL (VARCHAR(20) for both)
    elif len(username) < 6 or len(username) > 20:
        return render_template("auth/register.html", message="Username must be between 6 and 20 characters", 
                                login = session.get("logged_in"), username = session.get("username"))
    elif len(password) < 8 or len(password) > 20:
        return render_template("auth/register.html", message="Password must be between 8 and 20 characters", 
                                login=session.get("logged_in"), username = session.get("username"))

    # Insert new user into database
    # check if the username already exists
    if check_username(username):
        return render_template("auth/register.html", message = "Username already exists :(", 
                                login=session.get("logged_in"), username = session.get("username"))
    # if not add a new user to our database by calling
    # our pre-loaded procedure, `sp_add_user`
    # then redirect the users to login page
    else:
        db.execute(text("CALL sp_add_user(:username, :pwd)"),{"username": username, "pwd":password})
        db.commit()
        return render_template("auth/login.html", message = "Please sign in.",
                                login = session.get("logged_in"), username = session.get("username"))

# Products page
# Page for users to see the entire list of products
@app.route("/products", methods=["GET"])
def products():
   product = get_all_products()
   brands = get_all_brands()
   return render_template("main/products.html", products=product, brands=brands,
                          login=session.get("logged_in"), username=session.get("username"))

# SUBROUTES of Products
# Product page
# Provides detailed information about the selected product
@app.route("/products/product_id=<product_id>", methods=["GET"])
def product(product_id):
   # call `browse_one_product` with optional condition
   result = browse_one_products("WHERE product_id=%s" % product_id)
   ingredients = get_ingredients_of_product(product_id)
   return render_template('main/product.html', product=result, ingredients=ingredients,
                          login=session.get("logged_in"), username=session.get('username'))

# Product_filter route
# POST = when the user submits a request to filter the list 
# of products by their chosen criteria
# Users may not submit a "GET" request to this route as it
# doesn't render any page
@app.route("/product_filter", methods=["POST"])
def product_filter():
    # get filter form inputs from the page on request submit
    brand = request.form.get('brand')
    product_type = request.form.get('prod_type')
    ingredient = request.form.get('ingredients')
    price = int(request.form.get('price'))
    rating = int(request.form.get("rating"))
    # build a string query based on the submitted filters
    sql_query_list = []
    if brand != "-1":
        sql_query_list.append("brand_id=%s" % brand)
    if product_type != "-1":
        sql_query_list.append("product_type=\'%s\'" % product_type)
    if price != -1:
        if price == 76:
            sql_query_list.append("price >= 75")
        else:
            sql_query_list.append("price <= %d AND price >= %d" % (price, price - 25))
    if rating != -1:
        sql_query_list.append("rating >= %d" % rating)
    sql = "WHERE " + (" AND ".join(sql_query_list))

    # ingredient filter must be handled slightly differently
    # as the MySQL query for this task also involves has_ingredients
    # and ingredient tables
    if ingredient:
        if sql_query_list:
            result = search_by_ingredient(ingredient, sql)
        else:
            result = search_by_ingredient(ingredient)
    # if no ingredient filter is submitted, we can filter based on
    # the other two
    else:
        if sql_query_list:
            result = browse_products(sql)
        else:
            return redirect(url_for("products"))
    # return to products page with the resulting products list
    # and the entire list of brands
    brands = get_all_brands()
    return render_template("main/products.html", products=result, brands=brands,
                        login=session.get("logged_in"), username=session.get("username"))

# Brands page
# Page to show all brands
@app.route("/brands", methods=["GET"])
def brands():
    # Processing the list of brands here - we created a dictionary
    # of brand names by matching them to an alphabet that
    # corresponds to the first letter of their names
    brand = get_all_brands()
    alphabets = {}
    for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        alphabets[l] = []
    for (_, brand_name) in brand:
        alphabets[brand_name[0].upper()].append(brand_name)
    return render_template("main/brands.html", brands=alphabets, login=session.get("logged_in"), username=session.get("username"))

# SUBROUTES of Brands
# Brand page
# Page to show a brand and all of its products
@app.route("/brands/brand_name=<brand_name>", methods=["GET"])
def brand(brand_name = None):
    # submit a query with optional condition
    prods = browse_products('WHERE brand_name=\'%s\''% brand_name)
    return render_template("main/brand.html", products=prods, login=session.get("logged_in"), username=session.get("username"))

# Product type page
# Search by Product Type - this is built into nav bar
@app.route("/products/product_type=<product_type>", methods=['GET'])
def product_type(product_type):
    prods = browse_products('WHERE product_type=\'%s\'' % product_type)
    brands = get_all_brands()
    return render_template("main/products.html", products=prods, brands=brands,
                           login=session.get("logged_in"), username=session.get("username"))

# Add to Cart route
# POST = adds item to user's shopping cart when the user
# clicks on 'Add To Cart' buttons
@app.route("/add_to_cart/product_id=<product_id>", methods=["POST"])
def add_to_cart(product_id):
    # user must be logged in to add to their cart
    # if not, redirect them to login page
    if not session.get("logged_in"):
        return redirect(url_for('login'))
    if request.method == "POST":
        # add item by calling our procedure
        if add_item(product_id):
            return redirect(url_for('cart'))
        # if adding item has not been successful, return to product
        # with an error message
        else:
            result = browse_one_products("WHERE product_id=%s" % product_id)
            ingredients = get_ingredients_of_product(product_id)
            return render_template('main/product.html', product=result, ingredients=ingredients,
                                   message="Item cannot be added right now. Item sold out on website!",
                                   login=session.get("logged_in"), username=session.get('username'))
    # if request method is 'GET' for whatever reason, return to cart
    else:
        return redirect(url_for('cart'))

# Cart page
# Shows the user's shopping cart
@app.route("/cart", methods=['GET'])
def cart():
    # can only access if the user is logged in
    # if not, redirect them to the login page
    if session.get("logged_in"):
        # gets all the items in user's cart and also computes
        # the total for the items in the cart
        items = get_cart()
        total_cart = get_cart_total()
        return render_template('cart/cart.html', cart_items=items, total_value=total_cart,
                               login=session.get("logged_in"), username=session.get('username'))
    else:
        return redirect(url_for('login'))

# Update cart route
# POST = updates the number of an item in one's cart,
# either by incrementing or decrementing the number of that item
# is_increase flag tells us whether we should increment or decrement
@app.route("/update_cart/product_id=<product_id>&is_increase=<is_increase>", methods=["POST"])
def update_cart(product_id, is_increase=False):
    if is_increase == "1":
        add_item(product_id)
    else:
        decrease_item(product_id)
    return redirect(url_for('cart'))

# Delete item route
# POST = deletes an item entirely from the user's cart
@app.route("/delete_item/product_id=<product_id>", methods=["POST"])
def delete_item(product_id):
    delete_from_cart(product_id)
    return redirect(url_for('cart'))

# Checkout route
# POST = check out items in your cart
@app.route("/checkout", methods=["POST"])
def checkout():
    # user may only check out if they are logged in
    if session.get("logged_in"):
        # get all items and the cart total for front-end
        # (we want to show these values on our purchase_complete page)
        items = get_cart()
        total_cart = get_cart_total()
        # call move_cart_to_purchase_history procedure on the username
        # which will insert all the cart tuples associated with the user's username
        # into purchase_history and delete the original entries from the cart
        # (thereby "checking out"). This will trigger our after_cart_checkout trigger
        # which should decrement the inventory as needed
        sql = "CALL move_cart_to_purchase_history(\'%s\')" % session.get("username")
        try:
            db.execute(text(sql))
            db.commit()
            return render_template('cart/purchase_complete.html', items=items, order_date=date.today(),
                           total_price = total_cart, login=session.get("logged_in"), 
                           username=session.get("username"))
        except exc.DatabaseError as _:
            return render_template('cart/cart.html', cart_items=items, total_value=total_cart,
                               message="We are currently unable to check out your order.",
                               login=session.get("logged_in"), username=session.get('username'))
    else:
        return redirect(url_for('login'))
    
# MyPage page
# my page to see order history, etc.
@app.route("/mypage", methods=['GET'])
def mypage():
    # should only be accessible when the user is logged in
    # if not, direct them to the login page
    if session.get("logged_in"):
        # get user's purchase history by making a MySQL query
        history = get_purchase_history()
        return render_template('auth/mypage.html', history=history,
                               login=session.get("logged_in"), username=session.get("username"))
    else:
        return redirect(url_for("login"))