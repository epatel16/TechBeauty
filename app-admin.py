"""
Student name(s): Eshani Patel, Rachael Kim
Student email(s): ejpatel@caltech.edu, subinkim@caltech.edu
High-level program overview:
- `app-admin.py` allows the admin user of our service to manage the store.
- admin user will be allowed to perform following operations:
1) add or delete product
2) update inventory
3) 

"""
import sys  # to print error messages to sys.stderr
import os
# check if mysql.connector is installed
# if not, run pip3 install to install
try:
    import mysql.connector
except ImportError as e:
    os.system('pip3 install mysql.connector')
# To get error codes from the connector, useful for user-friendly
# error-handling
import mysql.connector.errorcode as errorcode

# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = True


# ----------------------------------------------------------------------
# SQL Utility Functions
# ----------------------------------------------------------------------
def get_conn():
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          user='admin',
          # Find port in MAMP or MySQL Workbench GUI or with
          # SHOW VARIABLES WHERE variable_name LIKE 'port';
          port='3306',  # this may change!
          password='adminpwd',
          database='cosmeticsdb' # replace this with your database name
        )
        print('Successfully connected.')
        return conn
    except mysql.connector.Error as err:
        # Remember that this is specific to _database_ users, not
        # application users. So is probably irrelevant to a client in your
        # simulated program. Their user information would be in a users table
        # specific to your database; hence the DEBUG use.
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR and DEBUG:
            sys.stderr('Incorrect username or password when connecting to DB.')
        elif err.errno == errorcode.ER_BAD_DB_ERROR and DEBUG:
            sys.stderr('Database does not exist.')
        elif DEBUG:
            sys.stderr(err)
        else:
            # A fine catchall client-facing message.
            sys.stderr('An error occurred, please contact the administrator.')
        sys.exit(1)

# ----------------------------------------------------------------------
# Functions for Command-Line Options/Query Execution
# ----------------------------------------------------------------------
def execute_query(sql):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            # returns -1 here if the execution of the query fails
            # so we can handle error separately at the caller
            sys.stderr('Error! Unable to execute SQL query. Check your inputs again.')
            return -1

# used when we have to do .fetchone() instead of .fetchall()
def execute_query_single(sql):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    try:
        cursor.execute(sql)
        row = cursor.fetchone()
        return row
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            # returns -1 here if the execution of the query fails
            # so we can handle error separately at the caller
            sys.stderr('Error! Unable to execute SQL query. Check your inputs again.')
            return -1

# used when we have to commit changes
# insert/delete/update queries
def execute_insert_delete_update(sql):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    try:
        # commit the result, and if successful, return 1
        cursor.execute(sql)
        conn.commit()
        return 1
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            # returns -1 here if the execution of the query fails
            # so we can handle error separately at the caller
            sys.stderr('Error! Unable to execute SQL query. Check your inputs again.')
            return -1

# Runs the SELECT query to get the list of product_id and
# product_name from product table with an optional condition

def get_products(cond = ''):
    sql = 'SELECT product_id, product_name FROM product %s;' %cond
    rows = execute_query(sql)
    return rows

def get_brands(cond = ''):
    sql = 'SELECT brand_id, brand_name FROM brand %s;' % cond
    rows = execute_query(sql)
    return rows

def get_curr_inventory(conds = ''):
    sql = 'SELECT brand_name, product_name, inventory FROM brand \
            JOIN store ON brand.brand_id = store.brand_id \
            JOIN product ON product.product_id = store.product_id %s;' % conds
    rows = execute_query(sql)
    return rows

def get_inventory_per_brand(limits = ''):
    sql = 'SELECT brand_name, SUM(calculate_inventory_value(product_id))\
            AS total_inventory_value FROM brand NATURAL JOIN store \
            NATURAL JOIN product GROUP BY brand_name %s;' % limits
    rows = execute_query(sql)
    return rows

def get_curr_store(conds = ''):
    sql = 'SELECT brand_name, product.product_id, \
            product_name FROM product NATURAL JOIN store \
            NATURAL JOIN (SELECT * FROM brand %s) AS p;' % conds
    rows = execute_query(sql)
    return rows

def get_all_sales():
    sql = 'SELECT SUM(num_items * price) \
            AS total_sales FROM purchase_history AS h \
            NATURAL JOIN product;'
    rows = execute_query(sql)
    return rows

def get_brand_sales(brand_id):
    sql = 'SELECT brand.brand_name, SUM(num_items * price) \
            AS total_sales FROM purchase_history AS h \
            JOIN product AS p ON h.product_id = p.product_id \
            JOIN store AS s ON p.product_id = s.product_id \
            JOIN brand ON brand.brand_id = s.brand_id\
            WHERE brand.brand_id = %s\
            GROUP BY brand.brand_id ORDER BY brand.brand_name ASC;'\
            % brand_id
    rows = execute_query(sql)
    return rows

def get_product_sales(prod_id):
    sql = 'SELECT product.product_name, SUM(num_items * price) \
            AS total_sales FROM purchase_history JOIN product \
            ON purchase_history.product_id = product.product_id \
            WHERE product.product_id = %s\
            GROUP BY product.product_id \
            ORDER BY product.product_name ASC;' % prod_id
    rows = execute_query(sql)
    return rows

def get_all_brand_sales():
    sql = 'SELECT brand.brand_name, SUM(num_items * price) \
            AS total_sales FROM purchase_history AS h \
            JOIN product AS p ON h.product_id = p.product_id \
            JOIN store AS s ON p.product_id = s.product_id \
            JOIN brand ON brand.brand_id = s.brand_id\
            GROUP BY brand.brand_id ORDER BY brand.brand_name ASC;'
    rows = execute_query(sql)
    return rows

def get_all_product_sales():
    sql = 'SELECT product.product_name, SUM(num_items * price) \
            AS total_sales FROM purchase_history JOIN product \
            ON purchase_history.product_id = product.product_id \
            GROUP BY product.product_id ORDER BY product.product_name ASC;'
    rows = execute_query(sql)
    return rows

# Get the top 5 highest-sales brands
# "top selling" here is determined by the dollar amount of total sales
def get_top_selling_brand():
    sql = 'SELECT brand.brand_name, SUM(num_items * price) \
            AS total_sales FROM purchase_history AS h \
            JOIN product AS p ON h.product_id = p.product_id \
            JOIN store AS s ON p.product_id = s.product_id \
            JOIN brand ON brand.brand_id = s.brand_id\
            GROUP BY brand.brand_id ORDER BY total_sales \
            DESC LIMIT 5;'
    rows = execute_query(sql)
    return rows

# Get the top 5 highest-sales products for the given brand
# "top selling" here is determined by the dollar amount of total sales
def get_top_selling_prod_per_brand(brand_id):
    sql = 'SELECT p.product_name, SUM(num_items * price) \
            AS total_sales FROM purchase_history AS h \
            JOIN product AS p ON h.product_id = p.product_id \
            JOIN store AS s ON p.product_id = s.product_id \
            JOIN brand ON brand.brand_id = s.brand_id\
            WHERE brand.brand_id = %s\
            GROUP BY p.product_name ORDER BY total_sales \
            DESC LIMIT 5;' % brand_id
    rows = execute_query(sql)
    return rows

# Get the top 5 highest-sales products
# "top selling" here is determined by the dollar amount of total sales
def get_top_selling_product():
    sql = 'SELECT product.product_name, SUM(num_items * price) \
            AS total_sales FROM purchase_history JOIN product \
            ON purchase_history.product_id = product.product_id \
            GROUP BY product.product_id \
            ORDER BY total_sales DESC LIMIT 5;' 
    rows = execute_query(sql)
    return rows

# Get the top 5 best-selling products for the given product type
# "best selling" here is determined by the units sold
def get_product_type_best_sale(prod_type):
    sql = 'SELECT product_name, SUM(num_items) AS total_units_sold\
            FROM purchase_history NATURAL JOIN product \
            WHERE product_type=\'%s\' GROUP BY product_name\
            ORDER BY total_units_sold DESC, product_name ASC LIMIT 5;'\
            % prod_type
    rows = execute_query(sql)
    return rows

# Get the top 5 best-selling products for the given brand
# "best selling" here is determined by the units sold
def get_brand_best_sale(brand_id):
    sql = 'SELECT product_name, SUM(num_items) AS total_units_sold\
            FROM purchase_history NATURAL JOIN product NATURAL JOIN store\
            NATURAL JOIN brand WHERE brand_id=%s GROUP BY product_name\
            ORDER BY total_units_sold DESC, product_name ASC LIMIT 5;' % brand_id
    rows = execute_query(sql)
    return rows

def get_best_selling_product():
    sql = 'SELECT p.product_name, SUM(num_items) AS total_units_sold\
            FROM purchase_history AS h JOIN product AS p ON \
            h.product_id = p.product_id GROUP BY p.product_name\
            ORDER BY total_units_sold DESC, p.product_name ASC LIMIT 5;'
    rows = execute_query(sql)
    return rows

def get_best_selling_brand():
    sql = 'SELECT brand_name, SUM(num_items) AS total_units_sold \
            FROM purchase_history AS h NATURAL JOIN product \
            NATURAL JOIN store NATURAL JOIN brand \
            GROUP BY brand_id ORDER BY total_units_sold \
            DESC LIMIT 5;'
    rows = execute_query(sql)
    return rows
# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------
def format_brand_list(brands):
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (brand_id, brand_name) in brands:
        print(f"{brand_id}: {brand_name}")
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

#############################
#     Result formatters     #
#############################

# Formats the result of SELECT query on product
# Prints the list of product id and product name
def format_product_list(products):
    print("Product ID | Product Name")
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (product_id, product_name) in products:
        print("{product_id:10d}: {product_name:100s}"
            .format(product_id=product_id, product_name=product_name))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

# Formats the result of SELECT query on the joined
# table of store and product
# Prints the list of product id and product name
def format_store_products(stores):
    print("Product ID | Product Name")
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (_, product_id, product_name) in stores:
        print("{product_id:10d} | {product_name:100s}"
            .format(product_id=product_id,product_name=product_name))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

# Formats the result of SELECT query on the joined
# table of store, product, and brand
# Prints the list of product names and the
# names for the corresponding brands
def format_store(inventory):
    print("{b:30s} | {name:100s}".format(b="Brand Name", name="Product Name"))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (brand_name, product_name, _) in inventory:
        print("{brand_name:30s} | {product_name:100s}"
            .format(brand_name=brand_name, product_name=product_name))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

# Formats the result of SELECT query on the joined
# table of store, product, and brand
# Prints the list of product names and the
# names for the corresponding brands
def format_inventory_res(curr_inventory):
    print("{b_name:20s} | {p_name:80s} | Inventory"
          .format(b_name="Brand Name", p_name="Product Name"))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (brand_name, product_name, inventory) in curr_inventory:
        print("{brand_name:20s} | {product_name:80s} | {inventory:.0f}"
            .format(brand_name=brand_name, product_name=product_name, inventory=inventory))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

# Formats the list of tuples (brand_name, inventory_value)
# where inventory_value is the total value of inventory
# owned by each brand, computed by doing
# inventory (amount of the given product available on store) *
# the price of each item
def format_inventory_val(inventory_val):
    print("{name:30s} | Inventory Value".format(name="Brand Name"))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (brand_name, inventory_value) in inventory_val:
        print("{brand_name:30s} | ${inventory_value:.2f}"
            .format(brand_name=brand_name, inventory_value=inventory_value))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

# Formats the list of tuples (name, sales_value)
# where name might be either product_name or brand_name
# and sales_value is the sum of all products that are sold
def format_sales(sales):
    print("{n:100s} | Total Sales Value".format(n="Name"))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (name, sales_value) in sales:
        print("{name:100s} | ${sales_value:.2f}"
            .format(name=name, sales_value=sales_value))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

def format_sales_units(sales):
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (name, num_units) in sales:
        print("{name:100s} | {num_units:.0f}"
            .format(name=name, num_units=num_units))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

def format_recent_sales(sales):
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for (name, num_units, purchase_time) in sales:
        print("{name:100s} | {num_units:.0f} | {purchase_time}"
            .format(name=name, num_units=num_units, purchase_time=purchase_time))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

def format_user(users):
    print("-----------------------------------------------------------------------------------------------------------------------------")
    for user in users:
        print("{username:20s} ".format(username=user[0]))
    print("-----------------------------------------------------------------------------------------------------------------------------")
    print()

#############################
#     Helper functions      #
#############################
    
def product_id_is_valid(product_id):
    if not product_id.isnumeric():
        return format_sales_units
    sql = 'SELECT * FROM product WHERE product_id=%s;' % product_id
    rows = execute_query(sql)
    return len(rows) > 0

def brand_id_is_valid(brand_id):
    if not brand_id.isnumeric():
        return format_sales_units
    sql = 'SELECT * FROM brand WHERE brand_id=%s;' % brand_id
    rows = execute_query(sql)
    return len(rows) > 0

def get_product_id():
    def get_prod_id_from_brand_list():
        ans = input("Enter brand_id: ")
        while not brand_id_is_valid(ans):
            print("Your brand_id is not valid.")
            ans = input("Enter your brand_id again: ")
        rows = get_curr_store("WHERE brand_id=%s" % ans)
        format_store_products(rows)
        ans = input("Now, enter your product_id: ")
        while not product_id_is_valid(ans):
            print("Your product_id is not valid.")
            ans = input("Enter your product_id again: ")
        return ans
    
    print("Choose an option")
    print("   (a) I know a precise product_id I want")
    print("   (b) I want to see the list of products")
    ans = input("Enter: ").lower()
    if ans == "a":
        ans = input("Enter product_id: ")
        while not product_id_is_valid(ans):
            print("Your product_id is not valid.")
            ans = input("Enter your product_id again: ")
        return ans
    elif ans == "b":
        print("What products would you want to see?")
        print("   (a) products of specific brand")
        print("   (b) full list of products")
        print()
        ans = input("Enter: ").lower()
        if ans == "a":
            print("Do you know the exact brand_id?")
            print("   (y) - yes, I do")
            print("   (n) - maybe, I know part (or all) of the name")
            ans = input("Enter: ").lower()
            if ans == "y":
                return get_prod_id_from_brand_list()
            elif ans == "n":
                ans = input("Enter (part of) the name of the brand: ").lower()
                sql = f'WHERE brand_name LIKE \'%{ans}%\''
                rows = get_brands(sql)
                if len(rows) < 1:
                    print("Invalid input. Let's start this again.")
                    get_product_id()
                else:
                    format_brand_list(rows)
                    return get_prod_id_from_brand_list()
            else:
                print("Invalid input. Let's retry.")
                return get_product_id()
        elif ans == "b":
            rows = get_brands()
            max_len = len(rows)
            ans = "n"
            range = [0, 25]
            print(f"Brands from id={range[0]+1} to id={range[1]+1}")
            while ans == "n" and range[0] < max_len:
                format_brand_list(rows[range[0]:range[1]])
                range[0] += 25
                range[1] += 25
                ans = input("Would you like to choose from the given list? \
                            Enter (y) for yes, (n) for no.").lower()
            return get_prod_id_from_brand_list()
        else:
            print("Invalid input. Let's retry.")
            return get_product_id()
    else:
        print("Invalid input. Let's retry.")
        return get_product_id()

def get_brand_id():
    print("Choose an option")
    print("   (a) I know a precise brand_id I want")
    print("   (b) I want to see the list of brands")
    ans = input("Enter: ").lower()
    if ans == "a":
        ans = input("Enter brand_id: ")
        while not brand_id_is_valid(ans):
            print("Your brand_id is not valid.")
            ans = input("Enter your brand_id again: ")
        return ans
    elif ans == "b":
        rows = get_brands()
        format_brand_list(rows)
        ans = input("Now, enter a brand_id you want: ")
        while not brand_id_is_valid(ans):
            print("Your brand_id is not valid.")
            ans = input("Enter your brand_id again: ")
        return ans
    else:
        print("Invalid input. Let's try again.")
        return get_brand_id()

def get_prod_type():
        print("Choose product type")
        print("   (a) Moisturizer")
        print("   (b) Cleanser")
        print("   (c) Treatment")
        print("   (d) Face Mask")
        print("   (e) Eye Cream")
        print("   (f) Sun Protect")
        prod_type = input("Enter: ").lower()
        while prod_type not in "abcdef":
            prod_type = input("Invalid option. Re-enter: ").lower()
        mapping = {
            "a": "Moisturizer",
            "b": "Cleanser",
            "c": "Treatment",
            "d": "Face Mask",
            "e": "Eye cream",
            "f": "Sun protect"
        }
        return mapping[prod_type]

def get_skin_type():
        print("Choose skin type")
        print("   (a) Combination")
        print("   (b) Dry")
        print("   (c) Normal")
        print("   (d) Oily")
        print("   (e) Sensitive")
        skin_type = input("Enter: ").lower()
        while skin_type not in "abcde":
            skin_type = input("Invalid option. Re-enter: ").lower()
        mapping = {
            "a": 0,
            "b": 1,
            "c": 2,
            "d": 3,
            "e": 4
        }
        res = [0 for _ in range(5)]
        res[mapping[skin_type]] = 1
        return res

#############################
#  (a) Inventory Functions  #
#############################
    
def check_inventory():
    print("What would you want to do?")
    print('   (a) View all inventory [NOT RECOMMENDED]')
    print('   (b) View inventory for given product')
    print('   (c) View inventory for given brand')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        rows = get_curr_inventory()
        format_inventory_res(rows)
    elif ans == 'b':
        prod_id = get_product_id()
        sql = 'SELECT brand_name, product_name, inventory FROM product \
                JOIN store ON product.product_id = store.product_id \
                JOIN brand ON store.brand_id = brand.brand_id WHERE product.product_id=%s;' \
                % prod_id
        rows = execute_query(sql)
        if rows == -1:
            print("Invalid product_id.")
            check_inventory()
        else:
            format_inventory_res(rows)
    elif ans == 'c':
        brand_id = get_brand_id()
        sql = 'SELECT brand_name, product_name, inventory FROM product \
                JOIN store ON product.product_id = store.product_id \
                JOIN brand ON store.brand_id = brand.brand_id WHERE brand.brand_id=%s;' \
                % brand_id
        rows = execute_query(sql)
        if rows == -1:
            print("Invalid brand_id.")
            check_inventory()
        else:
            format_inventory_res(rows)
    else:
        print("INVALID INPUT! Choose from the given options")
        check_inventory()

def update_inventory():
    print("What would you want to do?")
    print("   (a) Update inventory of a product")
    print("   (b) Update inventory of all products of a brand")
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        prod_id = get_product_id()
        (_, _, curr_inv)  = get_curr_inventory('WHERE product.product_id=%s' 
                                            % prod_id)[0]
        print(f"The current inventory of {prod_id} is {curr_inv}")
        print("What would you want to update this inventory to?")
        new_inv = int(input('Enter a number: '))
        sql = 'UPDATE store SET inventory=%s WHERE product_id=%s'\
                % (new_inv, prod_id)
        rows = execute_insert_delete_update(sql)
        if rows == -1:
            print("Invalid inputs. Retry.")
            update_inventory()
        else:
            print("Success!")
    elif ans == 'b':
        brand_id = get_brand_id()
        curr_inv = get_curr_inventory('WHERE brand.brand_id=%s' % brand_id)
        print(f"The current inventory of products of {brand_id} is:")
        format_inventory_res(curr_inv)
        print("How many products would you like to add or subtract?")
        new_inv = int(input('Enter a number: '))
        if new_inv > 0:
            sql = 'UPDATE store SET inventory=inventory+%s WHERE brand_id=%s'\
                    % (new_inv, brand_id)
        else:
            sql = 'UPDATE store SET inventory=inventory-%s WHERE brand_id=%s'\
                    % (abs(new_inv), brand_id)
        rows = execute_query(sql)
        if rows == -1:
            print("Invalid inputs. Retry.")
            update_inventory()
        else:
            print("Success!")
    else:
        print("INVALID INPUT! Choose from the given options")
        update_inventory()

def handle_update_inventory():
    print("What would you want to do?")
    print('   (a) Check inventory')
    print('   (b) Update inventory')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        check_inventory()
    elif ans == 'b':
        update_inventory()
    else:
        print("INVALID INPUT! Choose from the given options")
        show_options()

#############################
#  (b) Product List Funcs   #
#############################

def get_largest_product_id():
    sql = 'SELECT MAX(product_id) FROM product ORDER BY product_id DESC;'
    res = execute_query_single(sql)
    return int(res[0])

def handle_update_product():
    print("What would you want to do?")
    print('   (a) Add more products')
    print('   (b) Delete products')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        print("Ok! Then we need the following information from you:")
        name = input("First, enter the name of this new product: ")
        print("Now, what type is this new product?")
        prod_type = get_prod_type()
        print("What is the brand of this product?") 
        print("Follow the instructions to input correct brand.")
        print("If the brand doesn't exist, create a new brand first.")
        brand_id = get_brand_id()
        price = float(input("What is the price of your new product? Enter number:"))
        skin_type = get_skin_type()
        product_id = get_largest_product_id() + 1
        sql = f'INSERT INTO product (product_id, product_name, product_type, \
                price, rating, is_combination, is_dry, is_normal, is_oily, \
                is_sensitive) VALUES ({product_id}, \'{name}\', \'{prod_type}\',\
                {price}, 0.0, {skin_type[0]}, {skin_type[1]}, {skin_type[2]}, \
                {skin_type[3]}, {skin_type[4]});'
        execute_insert_delete_update(sql)
        sql2 = 'INSERT INTO store (product_id, brand_id, inventory) \
                VALUES (%d, %s, %d);' % (product_id, brand_id, 0)
        execute_insert_delete_update(sql2)
    elif ans == 'b':
        product_id = int(get_product_id())
        print("hey!")
        print(f"Confirming that you want to delete product with id {product_id}")
        # get user confirmation, since this cannot be undone
        ans = input("Enter (y) for yes, other keys for no: ").lower()
        if ans == "y":
            sql = 'DELETE FROM product WHERE product_id=%d' % product_id
            execute_insert_delete_update(sql)
            print("Successfully removed the product!")
        else:
            print("Ok! Taking you back to main page.")
            print()
            show_options()
    else:
        print("INVALID INPUT! Choose from the given options")
        handle_update_product()

#############################
#   (c) Brand List Funcs    #
#############################    

def get_largest_brand_id():
    sql = 'SELECT MAX(brand_id) FROM brand ORDER BY brand_id DESC;'
    res = execute_query_single(sql)
    return int(res[0])

def handle_update_brand():
    print("What would you want to do?")
    print('   (a) Add a brand')
    print('   (b) Delete a brand')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        print("Ok! Then we need one more piece of information from you:")
        name = input("First, enter the name of this new brand: ")
        brand_id = get_largest_brand_id() + 1
        sql = f'INSERT INTO brand (brand_id, brand_name) VALUES \
                ({brand_id}, \'{name}\');'
        execute_insert_delete_update(sql)
        print("Successfully executed the query!")
        print()
        show_options()
    elif ans == 'b':
        brand_id = int(get_brand_id())
        print(f"Confirming that you want to delete brand with id {brand_id}")
        # get user confirmation, since this cannot be undone
        ans = input("Enter (y) for yes, other keys for no: ").lower()
        if ans == "y":
            sql = 'DELETE FROM brand WHERE brand_id=%d' % brand_id
            execute_insert_delete_update(sql)
            print("Successfully removed the product!")
        else:
            print("Ok! Taking you back to main page.")
            print()
            show_options()
    else:
        print("INVALID INPUT! Choose from the given options")
        handle_update_brand()

#############################
#    (d) User Info Funcs    #
#############################
def username_exists(username):
    sql = 'SELECT * FROM user_info WHERE username = \'%s\'' % username
    result = execute_query_single(sql)
    if result[0] != None:
        return True
    return False

def handle_update_user():
    print("What would you want to do?")
    print('   (a) Add a user')
    print('   (b) Delete a user')
    print('   (c) View a list of all users')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        print("Ok! Then we need a couple more information from you: ")
        name = input("First, enter username of this new user: ")
        password = input("Now, enter the user's password: ")
        sql = f'CALL sp_add_user(\'{name}\', \'{password}\');'
        execute_insert_delete_update(sql)
        print("Successfully executed the query!")
        print()
        show_options()
    elif ans == 'b':
        name = input("Enter username of the user you would like to remove: ")
        while not username_exists(name):
            name = input("Username doesn't exist in our database. Re-enter: ")
        print(f"Confirming that you want to delete user: {name}")
        # get user confirmation, since this cannot be undone
        ans = input("Enter (y) for yes, other keys for no: ").lower()
        if ans == "y":
            sql = 'DELETE FROM user_info WHERE username=\'%s\'' % name
            execute_insert_delete_update(sql)
            print("Successfully removed the user!")
        else:
            print("Ok! Taking you back to main page.")
            print()
            show_options()
    elif ans == 'c':
        sql = 'SELECT username FROM user_info;'
        rows = execute_query(sql)
        format_user(rows)
        print()
        show_options()
    else:
        print("INVALID INPUT! Choose from the given options")
        handle_update_brand()

#############################
# (e) Statistics for Admin  #
#############################

def check_inventory_value():
    print("What would you want to do?")
    print('   (a) - Total inventory value per brand')
    print('   (b) - 5 brands with the highest remaining inventory')
    print('   (c) - 5 brands with the least remaining inventory')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        rows = get_inventory_per_brand()
        if len(rows) > 0:
            format_inventory_val(rows)
        else:
            print('No data to show.')
            handle_view_statistics()
    elif ans == 'b':
        rows = get_inventory_per_brand('ORDER BY total_inventory_value DESC LIMIT 5')
        if len(rows) > 0:
            format_inventory_val(rows)
        else:
            print('No data to show.')
            handle_view_statistics()
    elif ans == 'c':
        rows = get_inventory_per_brand('ORDER BY total_inventory_value ASC LIMIT 5')
        if len(rows) > 0:
            format_inventory_val(rows)
        else:
            print('No data to show.')
            handle_view_statistics()
    else:
        print('INVALID INPUT! Retry.')
        handle_view_statistics()

# handles all statistics options related to
# the sales of products and brands
def check_sales():
    print("What would you want to do?")
    print('   (a) - Check total sales')
    print('   (b) - Check top sales (i.e. highest dollar amount in sales)')
    print('   (c) - Check best sales (i.e. highest number of units sold)')
    print('   (d) - Check the most recent sales')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        print("Would you want to check the total sales of...")
        print("   (a) a brand?")
        print("   (b) a product?")
        print("   (c) each brand?")
        print("   (d) each product?")
        print("   (e) overall?")
        print("Any brand/product with no sales will not be shown.")
        ans = input("Enter an option: ").lower()
        if ans not in "abcde":
            print("Invalid input. Retry.")
            check_sales()
        else:
            if ans == "a":
                brand_id = get_brand_id()
                rows = get_brand_sales(brand_id)     
            elif ans == "b":
                prod_id = get_product_id()
                rows = get_product_sales(prod_id)
            elif ans =="c":
                rows = get_all_brand_sales()
            elif ans == "d":
                rows = get_all_product_sales()
            elif ans == "e":
                rows = get_all_sales()
            # handle the case where we have not enough data
            if len(rows) == 0:
                print("Not enough sales info yet! :(")
            else:
                format_sales(rows)
            print()
            show_options()

    elif ans == 'b':
        print("Would you want to see the top selling")
        print("   (a) brand?")
        print("   (b) product?")
        print("   (c) products for a brand?")
        print("Any brand/product with no sales will not be shown.")
        ans = input("Enter an option: ").lower()
        if ans not in "abc":
            print("Invalid input given. Retry.")
            check_sales()
        else:
            if ans == "a":
                rows = get_top_selling_brand()
            elif ans == "b":
                rows = get_top_selling_product()
            elif ans == "c":
                brand_id = get_brand_id()
                rows = get_top_selling_prod_per_brand(brand_id)
            # handle the case where we don't get any data back
            # due to lack of data in purchase_history table
            if len(rows) < 1:
                print("No sales data to be shown yet!")
            else:
                format_sales(rows)
            print()
            show_options()
            
    elif ans == 'c':
        print("Would you want to see the best selling")
        print("   (a) brand?")
        print("   (b) product?")
        print("   (c) products for a brand?")
        print("   (d) product by product type?")
        print("Any brand/product with no sales will not be shown.")
        ans = input("Enter an option: ").lower()
        if ans not in "abcd":
            print("Invalid input given. Retry.")
            check_sales()
        else:
            if ans == "a":
                rows = get_best_selling_brand()
            elif ans == "b":
                rows = get_best_selling_product()
            elif ans == "c":
                brand_id = get_brand_id()
                rows = get_brand_best_sale(brand_id)
            elif ans == "d":
                prod_type = get_prod_type()
                rows = get_product_type_best_sale(prod_type)
            # handle the case where we don't get any data back
            # due to lack of data in purchase_history table
            if len(rows) < 1:
                print("No sales data to be shown yet!")
            else:
                format_sales_units(rows)
            print()
            show_options()
    
    elif ans == 'd':
        print("Would you want to the most recent sales")
        print("   (a) for a brand?")
        print("   (b) for a given product type?")
        print("   (c) of all available products?")
        print("Any brand/product with no sales will not be shown.")
        ans = input("Enter an option: ").lower()
        if ans not in "abc":
            print("Invalid input given. Retry.")
            check_sales()
        else:
            if ans == "a":
                brand_id = get_brand_id()
                sql = 'SELECT product_name, num_items, purchase_time \
                        FROM purchase_history NATURAL JOIN product \
                        NATURAL JOIN store NATURAL JOIN brand \
                        WHERE brand_id = %s\
                        ORDER BY purchase_time DESC, product_name ASC LIMIT 5;'\
                        % brand_id     
                rows = execute_query(sql)
            elif ans == "b":
                prod_type = get_prod_type()
                sql = 'SELECT product_name, num_items, purchase_time \
                        FROM purchase_history NATURAL JOIN product \
                        WHERE product_type=\'%s\' ORDER BY purchase_time DESC,\
                        product_name ASC LIMIT 5;' % prod_type
                rows = execute_query(sql)
                
            elif ans == "c":
                sql = 'SELECT product_name, num_items, purchase_time \
                        FROM purchase_history NATURAL JOIN product \
                        ORDER BY purchase_time DESC, product_name ASC LIMIT 5;'
                rows = execute_query(sql)

            # handle the case where we don't get any data back
            # due to lack of data in purchase_history table
            if len(rows) < 1:
                print("No sales data to be shown yet!")
            else:
                format_recent_sales(rows)
            print()
            show_options()

    else:
        print('INVALID INPUT! Retry.')
        handle_view_statistics()

def handle_view_statistics():
    print('What statistics would you want to look up?')
    print('   (a) - Inventory')
    print('   (b) - Sales')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'a':
        check_inventory_value()
    elif ans == 'b':
        check_sales()
    else:
        print('INVALID INPUT! Retry.')
        handle_view_statistics()

# A function to show all the available options for admin users
def show_options():
    """
    Displays options specific for admins, such as adding new data <x>,
    modifying <x> based on a given id, removing <x>, etc.
    """
    print('What would you like to do?')
    print('  (a) - Check/Update inventory')
    print('  (b) - Check/Update product list')
    print('  (c) - Check/Update brand list')
    print('  (d) - Check/Update user list')
    print('  (e) - View statistics')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'a':
        handle_update_inventory()
    elif ans == 'b':
        handle_update_product()
    elif ans == 'c':
        handle_update_brand()
    elif ans == 'd':
        handle_update_user()
    elif ans == 'e':
        handle_view_statistics()
    else:
        print("INVALID INPUT! Choose from the given options")
    show_options()


def quit_ui():
    """
    Quits the program, printing a good bye message to the user.
    """
    print('Good bye!')
    exit()


def main():
    """
    Main function for starting things up.
    """
    print('ADMIN CONTROL PANEL')
    show_options()


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    conn = get_conn()
    main()
