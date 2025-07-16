# utils/db_manager.py

import sqlite3

class DBManager:
    def __init__(self, db_name):
        self.conn = None
        self.cursor = None
        self.db_name = db_name
        self.connect()

    def connect(self):
        """Establece una conexión a la base de datos SQLite."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def init_db(self):
        """Inicializa la base de datos, creando las tablas si no existen."""
        if self.conn:
            try:
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        price REAL NOT NULL,
                        category TEXT
                    )
                ''')
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE
                    )
                ''')
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS global_modifiers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE,
                        value REAL NOT NULL,
                        type TEXT NOT NULL
                    )
                ''')
                self.conn.commit()
                print("Database initialized (tables created/checked).")
            except sqlite3.Error as e:
                print(f"Error initializing database: {e}")
        else:
            print("Cannot initialize DB: No active connection.")

    def get_global_modifiers(self):
        """
        Recupera los modificadores globales de la base de datos.
        Retorna una lista de diccionarios con los modificadores.
        """
        if not self.conn:
            print("No database connection to get global modifiers.")
            return []
        try:
            self.cursor.execute("SELECT name, value, type FROM global_modifiers")
            modifiers = [{"name": row[0], "value": row[1], "type": row[2]} for row in self.cursor.fetchall()]
            return modifiers
        except sqlite3.Error as e:
            print(f"Error fetching global modifiers: {e}")
            return []

    def get_all_categories(self):
        """
        Recupera todas las categorías de la base de datos.
        Retorna una lista de cadenas (los nombres de las categorías).
        """
        if not self.conn:
            print("No database connection to get categories.")
            return []
        try:
            self.cursor.execute("SELECT name FROM categories ORDER BY name ASC")
            categories = [row[0] for row in self.cursor.fetchall()]
            return categories
        except sqlite3.Error as e:
            print(f"Error fetching categories: {e}")
            return []

    def add_category(self, category_name):
        """
        Añade una nueva categoría a la base de datos.
        Retorna True si la categoría se añadió con éxito, False en caso contrario.
        """
        if not self.conn:
            print("No database connection to add category.")
            return False
        try:
            # Aseguramos que el nombre de la categoría sea un string antes de intentar insertar
            if not isinstance(category_name, str):
                print(f"Invalid category name type: {type(category_name)}. Expected string.")
                return False

            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))
            self.conn.commit()
            print(f"Category '{category_name}' added successfully.")
            return True
        except sqlite3.IntegrityError:
            print(f"Category '{category_name}' already exists.")
            return False # Retorna False si la categoría ya existe (UNIQUE constraint)
        except sqlite3.Error as e:
            print(f"Error adding category '{category_name}': {e}")
            return False

    # Otros métodos (insert_product, get_all_products, etc.) irían aquí.