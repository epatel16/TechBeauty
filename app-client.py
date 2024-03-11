"""
Student name(s): Eshani Patel, Rachael Kim
Student email(s): ejpatel@caltech.edu, subinkim@caltech.edu
High-level program overview
"""
import sys  # to print error messages to sys.stderr
import os
import mysql.connector
# check if mysql.connector is installed
# if not, run pip3 install to install
# try:
#     import mysql.connector
# except ImportError as e:
#     os.system('pip3 install mysql-connector-python')
# To get error codes from the connector, useful for user-friendly
# error-handling
import mysql.connector.errorcode as errorcode

# Debugging flag to print errors when debugging that shouldn't be visible
# to an actual client. ***Set to False when done testing.***
DEBUG = True

# to keep track of whether the user is logged in or not
system_var = {
    "loggedin": False,
    "username": ""
}

# ----------------------------------------------------------------------
# SQL Utility Functions
# ----------------------------------------------------------------------
# TODO: we can work on adding username/password input feature
def get_conn():
    """"
    Returns a connected MySQL connector instance, if connection is successful.
    If unsuccessful, exits.
    """
    try:
        conn = mysql.connector.connect(
          host='localhost',
          # TODO: change this
          user='admin', # TODO: maybe take username input?
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
def browse_products(sql = ''):
    cursor = conn.cursor()
    sql = 'SELECT product_id, brand_name, product_name, product_type, rating FROM product \
            NATURAL JOIN store NATURAL JOIN brand %s;' % sql
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        if cursor.rowcount == 0:
            print("Your query returned no result.")
            show_options()
        else:
            print("-----------------------------------------------------------------------------------------------------------------------------")
            for (product_id, brand_name, product_name, product_type, rating) in rows:
                print(f"{product_id} {brand_name}")
                print("{product_name:100s} | {product_type:15s} | {rating:.1f}"
                    .format(product_name=product_name, product_type=product_type, rating=rating))
                print("-----------------------------------------------------------------------------------------------------------------------------")
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('ERROR: unable to fetch all products..')
    return None

def handle_brand():
    cursor = conn.cursor()
    sql = 'SELECT brand_id, brand_name FROM brand;'
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        print("Choose the brand you want: ")
        for (brand_id, brand_name) in rows:
            print(f"    ({brand_id}){brand_name}")
        ans = input("Enter your option: ").lower()
        sql = f"WHERE brand_id = {ans}"
        browse_products(sql)
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('ERROR: unable to get the list of all brands')
    return None

def handle_skintype():
    print("What is your skin type?")
    print("    (a) combination")
    print("    (b) dry")
    print("    (c) oily")
    print("    (d) sensitive")
    ans = input("Enter an option: ").lower()
    query = ''
    if ans == "a":
        query = 'WHERE is_combination = 1'
    elif ans == "b":
        query = 'WHERE is_dry = 1'
    elif ans == "c":
        query = "WHERE is_oily = 1"
    elif ans == "d":
        query = "WHERE is_sensitive = 1"
    browse_products(query)

def handle_product_type():
    print("Choose the type of product you want to browse: ")
    print("    (a) Moisturizer")
    print("    (b) Cleanser")
    print("    (c) Treatment")
    print("    (d) Face Mask")
    print("    (e) Eye cream")
    print("    (f) Sun protect")
    ans = input("Enter your option: ").lower()
    valid = "abcdef"
    query = ''
    if ans not in valid:
        print("Invalid input. Re-enter.")
        handle_product_type()
    elif ans == "a":
        query = 'Moisturizer'
    elif ans == "b":
        query = 'Cleanser'
    elif ans == "c":
        query = 'Treatment'
    elif ans == "d":
        query = 'Face Mask'
    elif ans == "e":
        query = 'Eye cream'
    elif ans == "f":
        query = "Sun protect"
    browse_products(query)

def handle_price():
    print("Choose your price range: ")
    print("    (a) Under $10")
    print("    (b) $10 - $50")
    print("    (c) $50 - $75")
    print("    (d) $75 - $100")
    print("    (e) $100 +")
    ans = input("Enter an option: ").lower()
    valid = "abcde"
    query = ""
    if ans not in valid:
        print("Invalid input! Would you like to see the list of all products? \
              (y) for yes and other keys for no.")
        ans = input("Enter an option: ").lower()
        if ans == "y":
            browse_products()
        else:
            filter_products()
    elif ans == "a":
        query = "WHERE price < 10"
    elif ans == "b":
        query = "WHERE price < 50 AND price >= 10"
    elif ans == "c":
        query = "WHERE price < 75 AND price >= 50"
    elif ans == "d":
        query = "WHERE price < 100 AND price >= 75"
    elif ans == "e":
        query = "WHERE price >= 100"
    browse_products(query)

def filter_products():
    print("What do you want to filter your product on?")
    print("    (b) brand name")
    print("    (s) skin type")
    print("    (p) product type")
    print("    (e) price range")
    ans = input("Enter an option: ").lower()
    if ans == "b":
        handle_brand()
    elif ans == "s":
        handle_skintype()
    elif ans == "p":
        handle_product_type()
    elif ans == "e":
        handle_price()
    else:
        print("Invalid input! Would you like to see the list of all products? (y) for yes and other keys for no.")
        ans = input("Enter an option: ").lower()
        if ans == "y":
            browse_products()
        else:
            filter_products()
    

# ----------------------------------------------------------------------
# Functions for Logging Users In
# ----------------------------------------------------------------------
# Note: There's a distinction between database users (admin and client)
# and application users (e.g. members registered to a store). You can
# choose how to implement these depending on whether you have app.py or
# app-client.py vs. app-admin.py (in which case you don't need to
# support any prompt functionality to conditionally login to the sql database)
def login():
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    print("Enter your credentials.")
    username = input("What is your username: ").lower()
    password = input("What is your password: ").lower()
    func = "SELECT authenticate(%s, %s);"
    try:
        cursor.execute(func, (username, password))
        rows = cursor.fetchone()
        if cursor.rowcount == 0:
            print("Unable to authenticate the user. Start using our service by signing up:")
            signup()
        else:
            system_var["loggedin"] = True
            system_var["username"] = username
            print("Successully signed you in!")
            show_mod_options()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('ERROR: unable to log user in..')

def check_username(username):
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    sql = "SELECT * FROM user_info WHERE username = \'%s\';" % username
    try:
        cursor.execute(sql)
        return cursor.rowcount == 1
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('ERROR: unable to check if user exists..')

def signup():
    cursor = conn.cursor()
    # Remember to pass arguments as a tuple like so to prevent SQL
    # injection.
    print("Let's create your account!")
    username = input("What would you want your username to be: ")
    password = input("And your password?: ")
    while check_username(username):
        username = input("Username is already taken! Choose a different username: ")
        password = input("And password: ")
    sql = "CALL sp_add_user(%s, %s);"
    try:
        cursor.execute(sql, (username, password))
        cursor.commit()
        system_var["loggedin"] = True
        system_var["username"] = username
        show_mod_options()
    except mysql.connector.Error as err:
        # If you're testing, it's helpful to see more details printed.
        if DEBUG:
            sys.stderr(err)
            sys.exit(1)
        else:
            sys.stderr('ERROR: unable to add a new user..')
# ----------------------------------------------------------------------
# Command-Line Functionality
# ----------------------------------------------------------------------
def show_options():
    """
    Displays options users can choose in the application, such as
    viewing <x>, filtering results with a flag (e.g. -s to sort),
    sending a request to do <x>, etc.
    """
    print('What would you like to do? ')
    print('  (a) - see all products')
    print('  (f) - filter products')
    print('  (l) - login to your account')
    print('  (s) - sign up for an account')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'a':
        browse_products()
    elif ans == 'f':
        filter_products()
    elif ans == 'l':
        login()
    elif ans == 's':
        signup()
    else:
        print("Error: invalid input for option. Please choose from the given set of options.")
        show_options()

# this is only for users who have already logged in
def show_mod_options():
    """
    Displays options users can choose in the application, such as
    viewing <x>, filtering results with a flag (e.g. -s to sort),
    sending a request to do <x>, etc.
    """
    print('What would you like to do? ')
    print('  (a) - see all products')
    print('  (f) - filter products')
    print('  (q) - quit')
    print()
    ans = input('Enter an option: ').lower()
    if ans == 'q':
        quit_ui()
    elif ans == 'a':
        browse_products()
    elif ans == 'f':
        filter_products()
    else:
        print("Error: invalid input for option. Please choose from the given set of options.")
        show_mod_options()

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
    show_options()


if __name__ == '__main__':
    # This conn is a global object that other functions can access.
    # You'll need to use cursor = conn.cursor() each time you are
    # about to execute a query with cursor.execute(<sqlquery>)
    # username = input("Your MySQL username: ")
    # password = input("Your MySQL password: ")
    conn = get_conn()
    main()
