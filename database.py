import sqlite3
import os

DB_FILE = "data/sales_db.db"
DB_DIR = "data"

# Global variable to hold the database connection and cursor
# It's generally better to pass these around, but for simplicity in a small app,
# a global approach with proper open/close can work if managed carefully.
conn = None
cursor = None

def get_db_connection():
    """
    Establishes and returns a database connection and cursor.
    If the connection already exists, it returns the existing one.
    """
    global conn, cursor
    if conn is None:
        if not os.path.exists(DB_DIR):
            os.makedirs(DB_DIR)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
    return conn, cursor

def close_db_connection():
    """Closes the database connection if it's open."""
    global conn, cursor
    if conn:
        conn.close()
        conn = None
        cursor = None
    print("Database connection closed.")


def create_tables():
    """
    Creates the necessary tables if they don't already exist.
    This function should be called once at application startup.
    """
    conn, cursor = get_db_connection() # Get an active connection

    # Table for Categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_es TEXT NOT NULL UNIQUE,
            name_en TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for Products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name_es TEXT NOT NULL,
            name_en TEXT NOT NULL,
            description_es TEXT,
            description_en TEXT,
            base_price REAL NOT NULL,
            image_path TEXT,
            is_available INTEGER DEFAULT 1, -- 1 for true, 0 for false
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
        )
    """)

    # Table for Variants (e.g., Small, Medium, Large for a coffee)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            name_es TEXT NOT NULL,
            name_en TEXT NOT NULL,
            price_adjustment REAL NOT NULL DEFAULT 0.0, -- How much to add/subtract from product base price
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
        )
    """)

    # Table for Modifiers (e.g., Extra Cheese, No Onion, Add Sugar)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS modifiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_es TEXT NOT NULL,
            name_en TEXT NOT NULL,
            price REAL NOT NULL,
            product_id INTEGER, -- NULL for global modifier, otherwise specific to a product
            variant_id INTEGER, -- NULL for global or product-specific modifier, otherwise specific to a variant
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
            FOREIGN KEY (variant_id) REFERENCES variants (id) ON DELETE CASCADE
        )
    """)

    # Table for Sales (main transaction)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table for Sale Items (products and their variants in a sale)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            variant_id INTEGER, -- NULL if no variant selected
            quantity INTEGER NOT NULL,
            item_price REAL NOT NULL, -- Price of the product/variant at time of sale
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT, -- Don't delete product if in old sale
            FOREIGN KEY (variant_id) REFERENCES variants (id) ON DELETE RESTRICT
        )
    """)

    # Table for Sale Item Modifiers (modifiers applied to a specific sale item)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_item_modifiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_item_id INTEGER NOT NULL,
            modifier_id INTEGER NOT NULL,
            modifier_price REAL NOT NULL, -- Price of the modifier at time of sale
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sale_item_id) REFERENCES sale_items (id) ON DELETE CASCADE,
            FOREIGN KEY (modifier_id) REFERENCES modifiers (id) ON DELETE RESTRICT
        )
    """)

    # Table for Users (for login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL, -- In a real app, hash this!
            role TEXT NOT NULL DEFAULT 'cashier', -- e.g., 'admin', 'cashier'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    # The connection is NOT closed here. It will remain open for the app.
    print("Tables created/verified.")

# New: Add a function to get the current active cursor for models
def get_cursor():
    """Returns the globally active database cursor."""
    global cursor
    if cursor is None:
        # If cursor is None, try to get a connection.
        # This acts as a safeguard, though get_db_connection should be called at app start.
        get_db_connection()
    return cursor

# Initial call to create_tables will also establish the connection
# create_tables() # Do not call this directly here. Call it from main.py.