# mi_sistema_ventas/models.py

import sqlite3
import datetime
# Importamos get_db_connection y get_cursor para usar la conexión global
from database import get_db_connection, get_cursor

class BaseModel:
    _table_name = ""
    _fields = [] # Lista de tuplas (nombre_columna, tipo_python)
    _primary_key = "id"

    def __init__(self, **kwargs):
        # Inicializa los atributos del objeto con los valores proporcionados o None
        # Incluye el primary key en la inicialización
        setattr(self, self._primary_key, kwargs.get(self._primary_key))
        for field_name, _ in self._fields:
            # Para campos que no tienen un valor en kwargs, se inicializan a None
            setattr(self, field_name, kwargs.get(field_name))

        # Manejar created_at y updated_at si existen en la tabla pero no en _fields
        # Asumiendo que la DB los gestiona automáticamente (DEFAULT CURRENT_TIMESTAMP)
        # Si NO están en _fields, entonces kwargs.get() es la forma correcta.
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')


    @classmethod
    def _execute_query(cls, query, params=(), fetch_result=False):
        """Método de clase para ejecutar consultas SQL y manejar la conexión."""
        conn, cursor = get_db_connection()

        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                # Para SELECTs, necesitamos los nombres de las columnas para crear diccionarios
                col_names = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                # Retorna una lista de diccionarios para facilitar la inicialización del modelo
                return [dict(zip(col_names, row)) for row in rows] if fetch_result else rows
            else:
                conn.commit() # Solo commitea si no es un SELECT
                return cursor
        except sqlite3.Error as e:
            print(f"Error de base de datos en {cls._table_name}: {e}")
            conn.rollback() # Solo rollback si no es un SELECT
            return None # Retorna None en caso de error
        # No hay finally: conn.close() aquí, la conexión permanece abierta

    @classmethod
    def get_by_id(cls, item_id):
        """Obtiene una instancia del modelo por su ID."""
        query = f"SELECT * FROM {cls._table_name} WHERE {cls._primary_key} = ?"
        # Pasamos fetch_result=True para obtener un diccionario
        rows = cls._execute_query(query, (item_id,), fetch_result=True)
        if rows: # Si se encontró al menos una fila (debería ser solo una para ID)
            return cls(**rows[0]) # rows[0] es el diccionario de la primera fila
        return None

    @classmethod
    def get_all(cls):
        """Obtiene todas las instancias del modelo."""
        query = f"SELECT * FROM {cls._table_name}"
        # Pasamos fetch_result=True para obtener una lista de diccionarios
        rows = cls._execute_query(query, fetch_result=True)
        if rows:
            return [cls(**row) for row in rows]
        return []

    def save(self):
        """Guarda la instancia actual en la base de datos (INSERT o UPDATE)."""
        # Filtra los campos que tienen un valor en el objeto y que son parte de _fields
        # No incluir 'id' en los campos a insertar ya que es AUTOINCREMENT
        fields_to_process = []
        values_to_process = []
        for field_name, _ in self._fields:
            value = getattr(self, field_name)
            fields_to_process.append(field_name)
            values_to_process.append(value)

        # Si tu DB maneja created_at/updated_at automáticamente, no los incluyas aquí.
        # Si los gestionas manualmente, asegúrate de que estén en _fields y se les asigne un valor.

        if getattr(self, self._primary_key) is None:
            # INSERT nuevo registro
            field_names_str = ", ".join(fields_to_process)
            placeholders = ", ".join(["?"] * len(fields_to_process))
            query = f"INSERT INTO {self._table_name} ({field_names_str}) VALUES ({placeholders})"
            cursor = self._execute_query(query, values_to_process)
            if cursor: # Si la ejecución fue exitosa
                setattr(self, self._primary_key, cursor.lastrowid) # Asigna el ID generado
                return True
        else:
            # UPDATE registro existente
            # Solo actualizamos los campos que están en _fields
            set_clauses = ", ".join([f"{f[0]} = ?" for f in self._fields])
            # SQLite puede actualizar updated_at con ON UPDATE CURRENT_TIMESTAMP en el CREATE TABLE
            # Si no lo tienes, añade 'updated_at = CURRENT_TIMESTAMP' aquí
            query = f"UPDATE {self._table_name} SET {set_clauses} WHERE {self._primary_key} = ?"
            values_to_process.append(getattr(self, self._primary_key)) # Añade el ID al final
            if self._execute_query(query, values_to_process):
                return True
        return False

    def delete(self):
        """Elimina la instancia actual de la base de datos."""
        if getattr(self, self._primary_key) is not None:
            query = f"DELETE FROM {self._table_name} WHERE {self._primary_key} = ?"
            # No se necesita fetch_result para DELETE
            if self._execute_query(query, (getattr(self, self._primary_key),)):
                return True
        return False

    def to_dict(self):
        """Convierte el objeto del modelo a un diccionario."""
        data = {self._primary_key: getattr(self, self._primary_key)}
        for field_name, _ in self._fields:
            data[field_name] = getattr(self, field_name)
        # Incluir created_at y updated_at si existen
        if hasattr(self, 'created_at'):
            data['created_at'] = self.created_at
        if hasattr(self, 'updated_at'):
            data['updated_at'] = self.updated_at
        return data

    def __repr__(self):
        return f"<{self.__class__.__name__} ID={getattr(self, self._primary_key)} {self.to_dict()}>"

# --- Modelos Específicos ---

class Category(BaseModel):
    _table_name = "categories"
    _fields = [
        ("name_es", str),
        ("name_en", str),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_name(self, lang="es"):
        """Devuelve el nombre de la categoría en el idioma especificado."""
        return self.name_en if lang == "en" else self.name_es

    def get_localized_name(self, lang_code):
        """Devuelve el nombre de la categoría según el idioma actual."""
        if lang_code == "es":
            return self.name_es
        elif lang_code == "en":
            return self.name_en
        return self.name_es # Fallback to Spanish or a default

class Product(BaseModel):
    _table_name = "products"
    _fields = [
        ("category_id", int),
        ("name_es", str),
        ("name_en", str),
        ("description_es", str),
        ("description_en", str),
        ("base_price", float),
        ("image_path", str),
        ("is_available", int), # Asegúrate de que este campo también exista en tu tabla
    ]

    def __init__(self, **kwargs):
        # Asegúrate de que 'is_available' tenga un valor por defecto si no se proporciona
        if 'is_available' not in kwargs:
            kwargs['is_available'] = 1 # Por defecto disponible
        super().__init__(**kwargs)

    def get_name(self, lang="es"):
        return self.name_en if lang == "en" else self.name_es

    def get_description(self, lang="es"):
        return self.description_en if lang == "en" else self.description_es

    def get_variants(self):
        """Obtiene todas las variantes asociadas a este producto."""
        return Variant.get_variants_by_product(self.id)

    def get_applicable_modifiers(self):
        """
        Obtiene los modificadores aplicables a este producto.
        Esto incluirá modificadores globales y modificadores asociados específicamente a este producto.
        """
        global_modifiers = Modifier.get_global_modifiers()
        product_specific_modifiers = Modifier.get_modifiers_by_product(self.id)
        return global_modifiers + product_specific_modifiers

    def get_localized_name(self, lang_code):
        """Devuelve el nombre del producto según el idioma actual."""
        if lang_code == "es":
            return self.name_es
        elif lang_code == "en":
            return self.name_en
        return self.name_es # Fallback to Spanish or a default

    @classmethod
    def get_products_by_category(cls, category_id):
        """Obtiene todos los productos asociados a una categoría específica."""
        query = "SELECT * FROM products WHERE category_id = ?"
        rows = cls._execute_query(query, (category_id,), fetch_result=True)
        if rows:
            return [cls(**row) for row in rows]
        return []


class Variant(BaseModel):
    _table_name = "variants"
    _fields = [
        ("product_id", int),
        ("name_es", str),
        ("name_en", str),
        ("price_adjustment", float),
    ]

    def __init__(self, **kwargs):
        # Asegúrate de que 'price_adjustment' tenga un valor por defecto
        if 'price_adjustment' not in kwargs:
            kwargs['price_adjustment'] = 0.0
        super().__init__(**kwargs)

    def get_name(self, lang="es"):
        return self.name_en if lang == "en" else self.name_es

    def get_localized_name(self, lang_code):
        """Devuelve el nombre de la variante según el idioma actual."""
        if lang_code == "es":
            return self.name_es
        elif lang_code == "en":
            return self.name_en
        return self.name_es # Fallback to Spanish or a default

    @classmethod
    def get_variants_by_product(cls, product_id):
        """Obtiene todas las variantes asociadas a un producto específico."""
        query = "SELECT * FROM variants WHERE product_id = ?"
        rows = cls._execute_query(query, (product_id,), fetch_result=True)
        if rows:
            return [cls(**row) for row in rows]
        return []

class Modifier(BaseModel):
    _table_name = "modifiers"
    _fields = [
        ("name_es", str),
        ("name_en", str),
        ("price", float),
        ("product_id", int),  # Puede ser NULL si es un modificador global
        ("variant_id", int),  # Puede ser NULL si es un modificador global o de producto
    ]

    def __init__(self, **kwargs):
        # Asegúrate de que 'price' tenga un valor por defecto
        if 'price' not in kwargs:
            kwargs['price'] = 0.0
        super().__init__(**kwargs)

    def get_name(self, lang="es"):
        return self.name_en if lang == "en" else self.name_es

    def get_localized_name(self, lang_code):
        """Devuelve el nombre del modificador según el idioma actual."""
        if lang_code == "es":
            return self.name_es
        elif lang_code == "en":
            return self.name_en
        return self.name_es # Fallback to Spanish or a default

    @classmethod
    def get_modifiers_by_product(cls, product_id):
        """Obtiene todos los modificadores asociados a un producto específico."""
        query = "SELECT * FROM modifiers WHERE product_id = ? AND variant_id IS NULL"
        rows = cls._execute_query(query, (product_id,), fetch_result=True)
        if rows:
            return [cls(**row) for row in rows]
        return []

    @classmethod
    def get_modifiers_by_variant(cls, variant_id):
        """Obtiene todos los modificadores asociados a una variante específica."""
        query = "SELECT * FROM modifiers WHERE variant_id = ?"
        rows = cls._execute_query(query, (variant_id,), fetch_result=True)
        if rows:
            return [cls(**row) for row in rows]
        return []

    @classmethod
    def get_global_modifiers(cls):
        """Obtiene todos los modificadores que no están asociados a ningún producto ni variante."""
        query = "SELECT * FROM modifiers WHERE product_id IS NULL AND variant_id IS NULL"
        rows = cls._execute_query(query, fetch_result=True)
        if rows:
            return [cls(**row) for row in rows]
        return []

class Sale(BaseModel):
    _table_name = "sales"
    _fields = [
        ("sale_date", str),
        ("total_amount", float),
    ]

    def __init__(self, **kwargs):
        # Si sale_date no se proporciona, usa la fecha y hora actual
        if kwargs.get('sale_date') is None:
            kwargs['sale_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        super().__init__(**kwargs)

    def get_items(self):
        """Obtiene todos los ítems de venta asociados a esta venta."""
        query = "SELECT * FROM sale_items WHERE sale_id = ?"
        rows = SaleItem._execute_query(query, (self.id,), fetch_result=True)
        if rows:
            return [SaleItem(**row) for row in rows]
        return []

class SaleItem(BaseModel):
    _table_name = "sale_items"
    _fields = [
        ("sale_id", int),
        ("product_id", int),
        ("variant_id", int), # Puede ser None
        ("quantity", int),
        ("price_at_sale", float),
    ]

    def __init__(self, **kwargs):
        # Asegúrate de que 'quantity' tenga un valor por defecto
        if 'quantity' not in kwargs:
            kwargs['quantity'] = 1
        super().__init__(**kwargs)

    def get_product(self):
        """Obtiene el objeto Producto asociado a este ítem de venta."""
        return Product.get_by_id(self.product_id)

    def get_variant(self):
        """Obtiene el objeto Variante asociado a este ítem de venta (si existe)."""
        return Variant.get_by_id(self.variant_id) if self.variant_id else None

    def get_modifiers(self):
        """Obtiene los modificadores aplicados a este ítem de venta."""
        query = """
            SELECT sim.modifier_id, sim.quantity, sim.price_at_sale, m.name_es, m.name_en
            FROM sale_item_modifiers sim
            JOIN modifiers m ON sim.modifier_id = m.id
            WHERE sim.sale_item_id = ?
        """
        # Usamos _execute_query del SaleItemModifier para este fetch
        # Y manejamos la conversión a dicts manualmente para asegurar la estructura deseada
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (self.id,))
        
        col_names = [description[0] for description in cursor.description]
        modifiers_data = []
        for row_tuple in cursor.fetchall():
            row_dict = dict(zip(col_names, row_tuple))
            modifiers_data.append({
                "id": row_dict["modifier_id"],
                "name_es": row_dict["name_es"],
                "name_en": row_dict["name_en"],
                "price": row_dict["price_at_sale"], # Precio del modificador individual al momento de la venta
                "quantity": row_dict["quantity"]
            })
        return modifiers_data # Retorna una lista de diccionarios


class SaleItemModifier(BaseModel):
    _table_name = "sale_item_modifiers"
    _fields = [
        ("sale_item_id", int),
        ("modifier_id", int),
        ("quantity", int),
        ("price_at_sale", float),
    ]

    def __init__(self, **kwargs):
        # Asegúrate de que 'quantity' y 'price_at_sale' tengan valores por defecto
        if 'quantity' not in kwargs:
            kwargs['quantity'] = 1
        if 'price_at_sale' not in kwargs:
            kwargs['price_at_sale'] = 0.0 # O un valor más apropiado si se conoce
        super().__init__(**kwargs)

    def get_modifier(self):
        """Obtiene el objeto Modifier asociado a este modificador de ítem de venta."""
        return Modifier.get_by_id(self.modifier_id)