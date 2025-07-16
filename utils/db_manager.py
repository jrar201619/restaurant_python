# utils/db_manager.py

class db_manager: # Fíjate en la 'd' minúscula aquí
    def __init__(self, db_name):
        self.conn = None
        self.db_name = db_name
        self.connect()
    # ... el resto de tu código de la clase ...