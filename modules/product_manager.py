import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import io

# Asegúrate de importar get_text y current_language desde la configuración
from config.translations import get_text, current_language

# Asegúrate de importar los modelos necesarios
from models import Category, Product, Variant, Modifier


class ProductManagerModule(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_selected_category_id = None
        self.current_selected_product_id = None
        self.current_selected_variant_id = None
        self.current_selected_modifier_id = None
        self.selected_item_type = None # 'category', 'product', 'variant', 'modifier'

        self.image_path_var = tk.StringVar() # Para almacenar la ruta de la imagen
        self.modifier_applies_to_var = tk.StringVar(value="global") # 'global', 'product', 'variant'
        self.modifier_applies_to_var.trace_add("write", self.on_modifier_applies_to_change)

        self.create_widgets()
        self.load_categories() # Carga las categorías al inicio
        self.clear_product_details() # Limpia los campos al inicio

        # Cargar imágenes predeterminadas (si es necesario, ajusta las rutas)
        # self.default_image = ImageTk.PhotoImage(Image.open("assets/default_product.png").resize((100, 100)))


    def create_widgets(self):
        # Frame principal para el gestor de productos
        self.main_panel = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Panel Izquierdo: Treeview para categorías, productos, variantes, modificadores ---
        self.left_panel = ttk.Frame(self.main_panel, width=300)
        self.main_panel.add(self.left_panel, weight=1)

        # Botones de añadir
        self.add_buttons_frame = ttk.Frame(self.left_panel)
        self.add_buttons_frame.pack(pady=5, fill=tk.X)

        self.btn_add_category = ttk.Button(self.add_buttons_frame, text=get_text("btn_add_category"), command=self.add_category)
        self.btn_add_category.pack(side=tk.LEFT, expand=True, padx=2)
        self.btn_add_product = ttk.Button(self.add_buttons_frame, text=get_text("btn_add_product"), command=self.add_product)
        self.btn_add_product.pack(side=tk.LEFT, expand=True, padx=2)
        self.btn_add_variant = ttk.Button(self.add_buttons_frame, text=get_text("btn_add_variant"), command=self.add_variant, state=tk.DISABLED)
        self.btn_add_variant.pack(side=tk.LEFT, expand=True, padx=2)
        self.btn_add_modifier = ttk.Button(self.add_buttons_frame, text=get_text("btn_add_modifier"), command=self.add_modifier)
        self.btn_add_modifier.pack(side=tk.LEFT, expand=True, padx=2)


        # Treeview para mostrar la jerarquía
        self.tree = ttk.Treeview(self.left_panel, selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.heading("#0", text=get_text("tree_item")) # Columna principal
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu) # Botón derecho para menú contextual

        # --- Panel Derecho: Formulario de detalles y acciones ---
        self.right_panel = ttk.Frame(self.main_panel, width=700)
        self.main_panel.add(self.right_panel, weight=2)

        # Frame para el título del formulario
        self.form_title_frame = ttk.Frame(self.right_panel)
        self.form_title_frame.pack(pady=5, fill=tk.X)
        self.form_title_label = ttk.Label(self.form_title_frame, text=get_text("title_details"), font=("Helvetica", 16, "bold"))
        self.form_title_label.pack()

        # Canvas para el formulario con scrollbar
        self.canvas = tk.Canvas(self.right_panel)
        self.scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame para los campos del formulario
        self.form_frame = ttk.LabelFrame(self.scrollable_frame, text=get_text("form_details"))
        self.form_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Configurar columnas para que se expandan
        self.form_frame.columnconfigure(1, weight=1)

        # --- Campos del formulario (Inicialmente genéricos, se actualizan al seleccionar) ---
        row_idx = 0

        # Campo ID (solo lectura)
        ttk.Label(self.form_frame, text="ID:").grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.entry_id = ttk.Entry(self.form_frame, state="readonly")
        self.entry_id.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Nombre (Español)
        self.lbl_name_es = ttk.Label(self.form_frame, text=get_text("label_name_es"))
        self.lbl_name_es.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_es = ttk.Entry(self.form_frame)
        self.entry_name_es.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Nombre (Inglés)
        self.lbl_name_en = ttk.Label(self.form_frame, text=get_text("label_name_en"))
        self.lbl_name_en.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_en = ttk.Entry(self.form_frame)
        self.entry_name_en.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Descripción (Español) - Para Productos
        self.lbl_description_es = ttk.Label(self.form_frame, text=get_text("label_description_es"))
        self.lbl_description_es.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.text_description_es = tk.Text(self.form_frame, height=3, width=40)
        self.text_description_es.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Descripción (Inglés) - Para Productos
        self.lbl_description_en = ttk.Label(self.form_frame, text=get_text("label_description_en"))
        self.lbl_description_en.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.text_description_en = tk.Text(self.form_frame, height=3, width=40)
        self.text_description_en.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Precio Base - Para Productos
        self.lbl_base_price = ttk.Label(self.form_frame, text=get_text("label_base_price"))
        self.lbl_base_price.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.entry_base_price = ttk.Entry(self.form_frame)
        self.entry_base_price.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Ajuste de Precio - Para Variantes
        self.lbl_price_adjustment = ttk.Label(self.form_frame, text=get_text("label_price_adjustment"))
        self.lbl_price_adjustment.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.entry_price_adjustment = ttk.Entry(self.form_frame)
        self.entry_price_adjustment.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Precio (para Modificadores)
        self.lbl_modifier_price = ttk.Label(self.form_frame, text=get_text("label_modifier_price"))
        self.lbl_modifier_price.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.entry_modifier_price = ttk.Entry(self.form_frame)
        self.entry_modifier_price.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Campo Imagen - Para Productos
        self.lbl_image = ttk.Label(self.form_frame, text=get_text("label_image"))
        self.lbl_image.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.entry_image_path = ttk.Entry(self.form_frame, textvariable=self.image_path_var)
        self.entry_image_path.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        self.btn_browse_image = ttk.Button(self.form_frame, text=get_text("btn_browse"), command=self.browse_image)
        self.btn_browse_image.grid(row=row_idx, column=2, sticky="ew", padx=5, pady=2)
        row_idx += 1

        # Es Disponible - Para Productos (Checkbox)
        self.is_available_var = tk.BooleanVar(value=True)
        self.chk_is_available = ttk.Checkbutton(self.form_frame, text=get_text("label_is_available"), variable=self.is_available_var)
        self.chk_is_available.grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        row_idx += 1

        # Aplicable a (para Modificadores)
        self.lbl_applies_to = ttk.Label(self.form_frame, text=get_text("label_applies_to"))
        self.lbl_applies_to.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.rb_applies_global = ttk.Radiobutton(self.form_frame, text=get_text("option_global"), variable=self.modifier_applies_to_var, value="global")
        self.rb_applies_global.grid(row=row_idx, column=1, sticky="w", padx=5, pady=2)
        row_idx += 1
        self.rb_applies_product = ttk.Radiobutton(self.form_frame, text=get_text("option_product"), variable=self.modifier_applies_to_var, value="product")
        self.rb_applies_product.grid(row=row_idx, column=1, sticky="w", padx=5, pady=2)
        row_idx += 1
        self.rb_applies_variant = ttk.Radiobutton(self.form_frame, text=get_text("option_variant"), variable=self.modifier_applies_to_var, value="variant")
        self.rb_applies_variant.grid(row=row_idx, column=1, sticky="w", padx=5, pady=2)
        row_idx += 1

        # Campos de selección de producto/variante para modificadores
        # Estos se ocultarán/mostrarán dinámicamente.
        # Es crucial que se creen y se les asigne una posición inicial (aunque sea oculta)
        # para que grid_slaves pueda encontrarlos.
        self.lbl_modifier_product = ttk.Label(self.form_frame, text=get_text("label_product"))
        self.lbl_modifier_product.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.cb_modifier_product = ttk.Combobox(self.form_frame, state="readonly")
        self.cb_modifier_product.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        self.cb_modifier_product.bind("<<ComboboxSelected>>", self.on_modifier_product_selected)
        row_idx += 1

        self.lbl_modifier_variant = ttk.Label(self.form_frame, text=get_text("label_variant"))
        self.lbl_modifier_variant.grid(row=row_idx, column=0, sticky="w", padx=5, pady=2)
        self.cb_modifier_variant = ttk.Combobox(self.form_frame, state="readonly")
        self.cb_modifier_variant.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=2)
        row_idx += 1


        # Frame para botones de acción (Guardar, Eliminar, Limpiar)
        self.form_buttons_frame = ttk.Frame(self.right_panel)
        self.form_buttons_frame.pack(pady=10, fill=tk.X)

        self.btn_save = ttk.Button(self.form_buttons_frame, text=get_text("btn_save"), command=self.clear_product_details) # Asigna un comando por defecto seguro
        self.btn_save.pack(side=tk.LEFT, expand=True, padx=5)

        self.btn_delete = ttk.Button(self.form_buttons_frame, text=get_text("btn_delete"), command=self.delete_item, state=tk.DISABLED)
        self.btn_delete.pack(side=tk.LEFT, expand=True, padx=5)

        self.btn_clear = ttk.Button(self.form_buttons_frame, text=get_text("btn_clear"), command=self.clear_product_details)
        self.btn_clear.pack(side=tk.LEFT, expand=True, padx=5)

        # Cargar productos y modificadores para los comboboxes (si aplica)
        self.load_all_products_for_combobox()
        #self.load_all_modifiers_for_combobox() # No es necesario aquí, se carga en on_modifier_product_selected


    def load_all_products_for_combobox(self):
        """Carga todos los productos en el combobox de selección de producto para modificadores."""
        products = Product.get_all()
        self.product_map = {p.get_localized_name(current_language): p.id for p in products}
        self.cb_modifier_product['values'] = list(self.product_map.keys())
        self.cb_modifier_product.set("") # Limpiar selección


    def on_modifier_product_selected(self, event=None):
        """Carga las variantes del producto seleccionado en el combobox de variantes."""
        selected_product_name = self.cb_modifier_product.get()
        product_id = self.product_map.get(selected_product_name)
        if product_id:
            variants = Variant.get_variants_by_product(product_id)
            self.variant_map = {v.get_localized_name(current_language): v.id for v in variants}
            self.cb_modifier_variant['values'] = list(self.variant_map.keys())
        else:
            self.cb_modifier_variant['values'] = []
        self.cb_modifier_variant.set("") # Limpiar selección de variante


    def clear_product_details(self):
        # Deseleccionar el Treeview
        self.tree.selection_remove(self.tree.selection())

        # Limpiar campos de entrada
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, tk.END)
        self.entry_id.config(state="readonly")

        self.entry_name_es.delete(0, tk.END)
        self.entry_name_en.delete(0, tk.END)
        self.text_description_es.delete("1.0", tk.END)
        self.text_description_en.delete("1.0", tk.END)
        self.entry_base_price.delete(0, tk.END)
        self.entry_price_adjustment.delete(0, tk.END)
        self.entry_modifier_price.delete(0, tk.END)
        self.entry_image_path.delete(0, tk.END)
        self.is_available_var.set(True) # Marcar como disponible por defecto
        self.cb_modifier_product.set("")
        self.cb_modifier_variant.set("")
        self.cb_modifier_variant['values'] = [] # Limpiar variantes

        self.btn_save.config(text=get_text("btn_save"), command=self.clear_product_details) # Restablecer comando
        self.btn_delete.config(state=tk.DISABLED)

        # Restablecer la selección de tipo de elemento
        self.current_selected_category_id = None
        self.current_selected_product_id = None
        self.current_selected_variant_id = None
        self.current_selected_modifier_id = None
        self.selected_item_type = None

        # Resetear radio buttons de modificador y llamar a su handler
        self.modifier_applies_to_var.set("global") # Esto disparará on_modifier_applies_to_change

        # Esconder todos los campos por defecto (manejo en on_modifier_applies_to_change)
        self.hide_all_form_fields()

        self.update_language() # Para actualizar labels en el formulario si se cambió el idioma


    def hide_all_form_fields(self):
        """Oculta todos los campos del formulario para mostrarlos selectivamente."""
        # Categoría
        self.lbl_name_es.grid_remove()
        self.entry_name_es.grid_remove()
        self.lbl_name_en.grid_remove()
        self.entry_name_en.grid_remove()

        # Producto
        self.lbl_description_es.grid_remove()
        self.text_description_es.grid_remove()
        self.lbl_description_en.grid_remove()
        self.text_description_en.grid_remove()
        self.lbl_base_price.grid_remove()
        self.entry_base_price.grid_remove()
        self.lbl_image.grid_remove()
        self.entry_image_path.grid_remove()
        self.btn_browse_image.grid_remove()
        self.chk_is_available.grid_remove()

        # Variante
        self.lbl_price_adjustment.grid_remove()
        self.entry_price_adjustment.grid_remove()

        # Modificador
        self.lbl_modifier_price.grid_remove()
        self.entry_modifier_price.grid_remove()
        self.lbl_applies_to.grid_remove()
        self.rb_applies_global.grid_remove()
        self.rb_applies_product.grid_remove()
        self.rb_applies_variant.grid_remove()

        # Estos son manejados por on_modifier_applies_to_change, pero los quitamos aquí también
        self.lbl_modifier_product.grid_remove()
        self.cb_modifier_product.grid_remove()
        self.lbl_modifier_variant.grid_remove()
        self.cb_modifier_variant.grid_remove()


    def show_category_fields(self, category=None):
        self.hide_all_form_fields()
        self.form_title_label.config(text=get_text("title_category_details"))

        # Campos de categoría
        self.lbl_name_es.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_es.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_name_en.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_en.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        if category:
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, category.id)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_es.insert(0, category.name_es)
            self.entry_name_en.delete(0, tk.END)
            self.entry_name_en.insert(0, category.name_en)
            self.btn_save.config(command=lambda: self.save_category(category.id))
            self.btn_delete.config(state=tk.NORMAL)
        else: # Para añadir nueva categoría
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_en.delete(0, tk.END)
            self.btn_save.config(command=lambda: self.save_category(None))
            self.btn_delete.config(state=tk.DISABLED)

        self.selected_item_type = 'category'
        self.update_language() # Actualizar los textos de los labels


    def show_product_fields(self, product=None):
        self.hide_all_form_fields()
        self.form_title_label.config(text=get_text("title_product_details"))

        # Campos de producto
        self.lbl_name_es.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_es.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_name_en.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_en.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_description_es.grid(row=3, column=0, sticky="nw", padx=5, pady=2)
        self.text_description_es.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_description_en.grid(row=4, column=0, sticky="nw", padx=5, pady=2)
        self.text_description_en.grid(row=4, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_base_price.grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.entry_base_price.grid(row=5, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_image.grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.entry_image_path.grid(row=6, column=1, sticky="ew", padx=5, pady=2)
        self.btn_browse_image.grid(row=6, column=2, sticky="ew", padx=5, pady=2)
        self.chk_is_available.grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=2)

        if product:
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, product.id)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_es.insert(0, product.name_es)
            self.entry_name_en.delete(0, tk.END)
            self.entry_name_en.insert(0, product.name_en)
            self.text_description_es.delete("1.0", tk.END)
            self.text_description_es.insert("1.0", product.description_es if product.description_es else "")
            self.text_description_en.delete("1.0", tk.END)
            self.text_description_en.insert("1.0", product.description_en if product.description_en else "")
            self.entry_base_price.delete(0, tk.END)
            self.entry_base_price.insert(0, str(product.base_price))
            self.image_path_var.set(product.image_path if product.image_path else "")
            self.is_available_var.set(bool(product.is_available)) # Convierte 0/1 a False/True
            self.btn_save.config(command=lambda: self.save_product(product.id))
            self.btn_delete.config(state=tk.NORMAL)
        else: # Para añadir nuevo producto
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_en.delete(0, tk.END)
            self.text_description_es.delete("1.0", tk.END)
            self.text_description_en.delete("1.0", tk.END)
            self.entry_base_price.delete(0, tk.END)
            self.image_path_var.set("")
            self.is_available_var.set(True)
            self.btn_save.config(command=lambda: self.save_product(None))
            self.btn_delete.config(state=tk.DISABLED)

        self.selected_item_type = 'product'
        self.update_language() # Actualizar los textos de los labels


    def show_variant_fields(self, variant=None):
        self.hide_all_form_fields()
        self.form_title_label.config(text=get_text("title_variant_details"))

        # Campos de variante
        self.lbl_name_es.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_es.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_name_en.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_en.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_price_adjustment.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.entry_price_adjustment.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        if variant:
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, variant.id)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_es.insert(0, variant.name_es)
            self.entry_name_en.delete(0, tk.END)
            self.entry_name_en.insert(0, variant.name_en)
            self.entry_price_adjustment.delete(0, tk.END)
            self.entry_price_adjustment.insert(0, str(variant.price_adjustment))
            self.btn_save.config(command=lambda: self.save_variant(variant.id))
            self.btn_delete.config(state=tk.NORMAL)
        else: # Para añadir nueva variante
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_en.delete(0, tk.END)
            self.entry_price_adjustment.delete(0, tk.END)
            self.entry_price_adjustment.insert(0, "0.0") # Valor por defecto
            self.btn_save.config(command=lambda: self.save_variant(None))
            self.btn_delete.config(state=tk.DISABLED)

        self.selected_item_type = 'variant'
        self.update_language()


    def show_modifier_fields(self, modifier=None):
        self.hide_all_form_fields()
        self.form_title_label.config(text=get_text("title_modifier_details"))

        # Campos de modificador
        self.lbl_name_es.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_es.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_name_en.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_name_en.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.lbl_modifier_price.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.entry_modifier_price.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        self.lbl_applies_to.grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.rb_applies_global.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        self.rb_applies_product.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        self.rb_applies_variant.grid(row=6, column=1, sticky="w", padx=5, pady=2)


        if modifier:
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.insert(0, modifier.id)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_es.insert(0, modifier.name_es)
            self.entry_name_en.delete(0, tk.END)
            self.entry_name_en.insert(0, modifier.name_en)
            self.entry_modifier_price.delete(0, tk.END)
            self.entry_modifier_price.insert(0, str(modifier.price))

            # Determinar qué opción de "aplica a" está seleccionada
            if modifier.product_id is None and modifier.variant_id is None:
                self.modifier_applies_to_var.set("global")
            elif modifier.product_id is not None and modifier.variant_id is None:
                self.modifier_applies_to_var.set("product")
                # Establecer el producto en el combobox
                product = Product.get_by_id(modifier.product_id)
                if product:
                    self.cb_modifier_product.set(product.get_localized_name(current_language))
            elif modifier.variant_id is not None:
                self.modifier_applies_to_var.set("variant")
                # Establecer la variante en el combobox
                variant = Variant.get_by_id(modifier.variant_id)
                if variant:
                    # Necesitamos cargar los productos primero para que la variante se pueda encontrar
                    product = Product.get_by_id(variant.product_id)
                    if product:
                        self.cb_modifier_product.set(product.get_localized_name(current_language))
                        self.on_modifier_product_selected() # Cargar las variantes
                        self.cb_modifier_variant.set(variant.get_localized_name(current_language))

            self.btn_save.config(command=lambda: self.save_modifier(modifier.id))
            self.btn_delete.config(state=tk.NORMAL)
        else: # Para añadir nuevo modificador
            self.entry_id.config(state="normal")
            self.entry_id.delete(0, tk.END)
            self.entry_id.config(state="readonly")
            self.entry_name_es.delete(0, tk.END)
            self.entry_name_en.delete(0, tk.END)
            self.entry_modifier_price.delete(0, tk.END)
            self.entry_modifier_price.insert(0, "0.0") # Valor por defecto
            self.modifier_applies_to_var.set("global") # Por defecto a global
            self.btn_save.config(command=lambda: self.save_modifier(None))
            self.btn_delete.config(state=tk.DISABLED)

        self.selected_item_type = 'modifier'
        self.load_all_products_for_combobox() # Asegurar que los productos están cargados
        self.on_modifier_applies_to_change() # Asegurar que los campos correctos se muestran/ocultan
        self.update_language()


    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            self.clear_product_details()
            return

        item_id = self.tree.item(selected_item, "text")
        item_type = self.tree.item(selected_item, "tags")[0] if self.tree.item(selected_item, "tags") else None

        self.current_selected_category_id = None
        self.current_selected_product_id = None
        self.current_selected_variant_id = None
        self.current_selected_modifier_id = None

        if item_type == "category":
            category = Category.get_by_id(int(item_id))
            if category:
                self.current_selected_category_id = category.id
                self.show_category_fields(category)
                self.btn_add_product.config(state=tk.NORMAL)
                self.btn_add_variant.config(state=tk.DISABLED)
                # Modificadores siempre disponibles, pero para este caso, pueden ser globales o de producto/variante
                # self.btn_add_modifier.config(state=tk.NORMAL)
            else:
                self.clear_product_details()

        elif item_type == "product":
            product = Product.get_by_id(int(item_id))
            if product:
                self.current_selected_product_id = product.id
                # Obtener la categoría padre del producto
                parent_iid = self.tree.parent(selected_item)
                if parent_iid:
                    self.current_selected_category_id = int(self.tree.item(parent_iid, "text"))
                self.show_product_fields(product)
                self.btn_add_product.config(state=tk.NORMAL) # Siempre se puede añadir otro producto
                self.btn_add_variant.config(state=tk.NORMAL) # Se puede añadir variante a este producto
                # self.btn_add_modifier.config(state=tk.NORMAL)
            else:
                self.clear_product_details()

        elif item_type == "variant":
            variant = Variant.get_by_id(int(item_id))
            if variant:
                self.current_selected_variant_id = variant.id
                # Obtener el producto padre de la variante
                parent_iid = self.tree.parent(selected_item)
                if parent_iid:
                    self.current_selected_product_id = int(self.tree.item(parent_iid, "text"))
                    # Obtener la categoría padre del producto
                    grandparent_iid = self.tree.parent(parent_iid)
                    if grandparent_iid:
                        self.current_selected_category_id = int(self.tree.item(grandparent_iid, "text"))

                self.show_variant_fields(variant)
                self.btn_add_product.config(state=tk.NORMAL)
                self.btn_add_variant.config(state=tk.NORMAL) # Se puede añadir otra variante al mismo producto
                # self.btn_add_modifier.config(state=tk.NORMAL)
            else:
                self.clear_product_details()

        elif item_type == "modifier":
            modifier = Modifier.get_by_id(int(item_id))
            if modifier:
                self.current_selected_modifier_id = modifier.id
                # El modificador puede no tener padre o tener un producto/variante como padre
                parent_iid = self.tree.parent(selected_item)
                if parent_iid:
                    parent_type = self.tree.item(parent_iid, "tags")[0]
                    parent_id = int(self.tree.item(parent_iid, "text"))
                    if parent_type == "product":
                        self.current_selected_product_id = parent_id
                    elif parent_type == "variant":
                        self.current_selected_variant_id = parent_id
                self.show_modifier_fields(modifier)
                self.btn_add_product.config(state=tk.NORMAL)
                self.btn_add_variant.config(state=tk.NORMAL)
                # self.btn_add_modifier.config(state=tk.NORMAL)
            else:
                self.clear_product_details()
        else:
            self.clear_product_details()


    def load_categories(self):
        # Limpiar Treeview existente
        for item in self.tree.get_children():
            self.tree.delete(item)

        categories = Category.get_all()
        for category in categories:
            category_name = category.get_localized_name(current_language)
            category_iid = self.tree.insert("", "end", text=category.id, values=(category_name,), tags=("category",))
            self.tree.item(category_iid, open=True) # Abrir la categoría por defecto

            # Cargar productos para cada categoría
            products = Product.get_products_by_category(category.id)
            for product in products:
                product_name = product.get_localized_name(current_language)
                product_iid = self.tree.insert(category_iid, "end", text=product.id, values=(product_name,), tags=("product",))
                self.tree.item(product_iid, open=True) # Abrir el producto por defecto

                # Cargar variantes para cada producto
                variants = Variant.get_variants_by_product(product.id)
                for variant in variants:
                    variant_name = variant.get_localized_name(current_language)
                    variant_iid = self.tree.insert(product_iid, "end", text=variant.id, values=(variant_name,), tags=("variant",))

                # Cargar modificadores asociados directamente a este producto
                product_modifiers = Modifier.get_modifiers_by_product(product.id)
                for modifier in product_modifiers:
                    modifier_name = modifier.get_localized_name(current_language)
                    modifier_iid = self.tree.insert(product_iid, "end", text=modifier.id, values=(modifier_name,), tags=("modifier",))

        # Cargar modificadores globales
        global_modifiers = Modifier.get_global_modifiers()
        if global_modifiers:
            global_mod_iid = self.tree.insert("", "end", text=get_text("tree_global_modifiers"), values=("",), tags=("global_modifier_group",))
            self.tree.item(global_mod_iid, open=True)
            for modifier in global_modifiers:
                modifier_name = modifier.get_localized_name(current_language)
                self.tree.insert(global_mod_iid, "end", text=modifier.id, values=(modifier_name,), tags=("modifier",))

        # Recargar productos en el combobox para modificadores
        self.load_all_products_for_combobox()


    def add_category(self):
        self.clear_product_details()
        self.show_category_fields(None)
        self.form_title_label.config(text=get_text("title_add_category"))
        self.btn_save.config(command=lambda: self.save_category(None))
        self.btn_add_variant.config(state=tk.DISABLED)


    def add_product(self):
        # Asegúrate de que haya una categoría seleccionada para añadir un producto
        if not self.current_selected_category_id and not self.tree.selection():
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_category_for_product"))
            return

        self.clear_product_details()
        self.show_product_fields(None)
        self.form_title_label.config(text=get_text("title_add_product"))
        self.btn_save.config(command=lambda: self.save_product(None))
        self.btn_add_variant.config(state=tk.DISABLED) # No se puede añadir variante si no hay producto guardado


    def add_variant(self):
        # Asegúrate de que haya un producto seleccionado para añadir una variante
        if not self.current_selected_product_id and not self.tree.selection():
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_for_variant"))
            return

        self.clear_product_details()
        self.show_variant_fields(None)
        self.form_title_label.config(text=get_text("title_add_variant"))
        self.btn_save.config(command=lambda: self.save_variant(None))


    def add_modifier(self):
        self.clear_product_details()
        self.show_modifier_fields(None)
        self.form_title_label.config(text=get_text("title_add_modifier"))
        self.btn_save.config(command=lambda: self.save_modifier(None))
        # No deshabilitamos los botones de añadir producto/variante aquí,
        # ya que un modificador puede no tener un padre directamente "seleccionable" en el treeview


    def save_category(self, category_id):
        name_es = self.entry_name_es.get().strip()
        name_en = self.entry_name_en.get().strip()

        if not name_es or not name_en:
            messagebox.showerror(get_text("msg_error"), get_text("msg_name_required"))
            return

        if category_id:
            category = Category.get_by_id(category_id)
            if category:
                category.name_es = name_es
                category.name_en = name_en
                if category.save():
                    messagebox.showinfo(get_text("msg_success"), get_text("msg_category_updated"))
                    self.load_categories()
                    self.clear_product_details()
                else:
                    messagebox.showerror(get_text("msg_error"), get_text("msg_error_updating_category"))
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_category_not_found"))
        else:
            category = Category(name_es=name_es, name_en=name_en)
            if category.save():
                messagebox.showinfo(get_text("msg_success"), get_text("msg_category_added"))
                self.load_categories()
                self.clear_product_details()
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_error_adding_category"))


    def save_product(self, product_id):
        name_es = self.entry_name_es.get().strip()
        name_en = self.entry_name_en.get().strip()
        description_es = self.text_description_es.get("1.0", tk.END).strip()
        description_en = self.text_description_en.get("1.0", tk.END).strip()
        base_price_str = self.entry_base_price.get().strip()
        image_path = self.image_path_var.get().strip()
        is_available = 1 if self.is_available_var.get() else 0

        if not name_es or not name_en or not base_price_str:
            messagebox.showerror(get_text("msg_error"), get_text("msg_required_product_fields"))
            return

        try:
            base_price = float(base_price_str)
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price"))
            return

        # Para un nuevo producto, necesitamos una categoría seleccionada
        if product_id is None and self.current_selected_category_id is None:
            messagebox.showerror(get_text("msg_error"), get_text("msg_select_category_for_product_save"))
            return

        category_id_to_use = self.current_selected_category_id


        if product_id:
            product = Product.get_by_id(product_id)
            if product:
                product.name_es = name_es
                product.name_en = name_en
                product.description_es = description_es if description_es else None
                product.description_en = description_en if description_en else None
                product.base_price = base_price
                product.image_path = image_path if image_path else None
                product.is_available = is_available
                if product.save():
                    messagebox.showinfo(get_text("msg_success"), get_text("msg_product_updated"))
                    self.load_categories()
                    self.clear_product_details()
                else:
                    messagebox.showerror(get_text("msg_error"), get_text("msg_error_updating_product"))
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_product_not_found"))
        else:
            product = Product(
                category_id=category_id_to_use,
                name_es=name_es,
                name_en=name_en,
                description_es=description_es if description_es else None,
                description_en=description_en if description_en else None,
                base_price=base_price,
                image_path=image_path if image_path else None,
                is_available=is_available
            )
            if product.save():
                messagebox.showinfo(get_text("msg_success"), get_text("msg_product_added"))
                self.load_categories()
                self.clear_product_details()
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_error_adding_product"))


    def save_variant(self, variant_id):
        name_es = self.entry_name_es.get().strip()
        name_en = self.entry_name_en.get().strip()
        price_adjustment_str = self.entry_price_adjustment.get().strip()

        if not name_es or not name_en or not price_adjustment_str:
            messagebox.showerror(get_text("msg_error"), get_text("msg_required_variant_fields"))
            return

        try:
            price_adjustment = float(price_adjustment_str)
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price_adjustment"))
            return

        # Para una nueva variante, necesitamos un producto seleccionado
        if variant_id is None and self.current_selected_product_id is None:
            messagebox.showerror(get_text("msg_error"), get_text("msg_select_product_for_variant_save"))
            return

        product_id_to_use = self.current_selected_product_id

        if variant_id:
            variant = Variant.get_by_id(variant_id)
            if variant:
                variant.name_es = name_es
                variant.name_en = name_en
                variant.price_adjustment = price_adjustment
                if variant.save():
                    messagebox.showinfo(get_text("msg_success"), get_text("msg_variant_updated"))
                    self.load_categories()
                    self.clear_product_details()
                else:
                    messagebox.showerror(get_text("msg_error"), get_text("msg_error_updating_variant"))
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_variant_not_found"))
        else:
            variant = Variant(
                product_id=product_id_to_use,
                name_es=name_es,
                name_en=name_en,
                price_adjustment=price_adjustment
            )
            if variant.save():
                messagebox.showinfo(get_text("msg_success"), get_text("msg_variant_added"))
                self.load_categories()
                self.clear_product_details()
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_error_adding_variant"))


    def save_modifier(self, modifier_id):
        name_es = self.entry_name_es.get().strip()
        name_en = self.entry_name_en.get().strip()
        price_str = self.entry_modifier_price.get().strip()
        applies_to = self.modifier_applies_to_var.get()

        product_id = None
        variant_id = None

        if not name_es or not name_en or not price_str:
            messagebox.showerror(get_text("msg_error"), get_text("msg_required_modifier_fields"))
            return

        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price_modifier"))
            return

        if applies_to == "product":
            selected_product_name = self.cb_modifier_product.get()
            if not selected_product_name:
                messagebox.showerror(get_text("msg_error"), get_text("msg_select_product_for_modifier"))
                return
            product_id = self.product_map.get(selected_product_name)
            if product_id is None:
                messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_product_selection"))
                return
        elif applies_to == "variant":
            selected_variant_name = self.cb_modifier_variant.get()
            if not selected_variant_name:
                messagebox.showerror(get_text("msg_error"), get_text("msg_select_variant_for_modifier"))
                return
            variant_id = self.variant_map.get(selected_variant_name)
            if variant_id is None:
                messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_variant_selection"))
                return
            # Si es un modificador de variante, también necesitamos el product_id del padre para la lógica interna si fuera necesario
            # Aunque la tabla solo lo pide para product_id o variant_id, no ambos
            if self.cb_modifier_product.get():
                 product_id = self.product_map.get(self.cb_modifier_product.get())


        if modifier_id:
            modifier = Modifier.get_by_id(modifier_id)
            if modifier:
                modifier.name_es = name_es
                modifier.name_en = name_en
                modifier.price = price
                modifier.product_id = product_id
                modifier.variant_id = variant_id
                if modifier.save():
                    messagebox.showinfo(get_text("msg_success"), get_text("msg_modifier_updated"))
                    self.load_categories()
                    self.clear_product_details()
                else:
                    messagebox.showerror(get_text("msg_error"), get_text("msg_error_updating_modifier"))
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_modifier_not_found"))
        else:
            modifier = Modifier(
                name_es=name_es,
                name_en=name_en,
                price=price,
                product_id=product_id,
                is_available=1, # Los modificadores son siempre 'disponibles' por ahora
                variant_id=variant_id
            )
            if modifier.save():
                messagebox.showinfo(get_text("msg_success"), get_text("msg_modifier_added"))
                self.load_categories()
                self.clear_product_details()
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_error_adding_modifier"))


    def delete_item(self):
        if not self.selected_item_type:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_no_item_selected_delete"))
            return

        item_id = int(self.entry_id.get())
        confirm = messagebox.askyesno(
            get_text("confirm_delete_title"),
            f"{get_text('confirm_delete_message')} {self.selected_item_type} (ID: {item_id})?"
        )

        if confirm:
            success = False
            if self.selected_item_type == 'category':
                success = Category.delete(item_id)
            elif self.selected_item_type == 'product':
                success = Product.delete(item_id)
            elif self.selected_item_type == 'variant':
                success = Variant.delete(item_id)
            elif self.selected_item_type == 'modifier':
                success = Modifier.delete(item_id)

            if success:
                messagebox.showinfo(get_text("msg_success"), get_text("msg_item_deleted"))
                self.load_categories()
                self.clear_product_details()
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_error_deleting_item"))


    def browse_image(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title=get_text("dialog_select_image"),
            filetypes=(
                (get_text("file_type_image_files"), "*.png *.jpg *.jpeg *.gif"),
                (get_text("file_type_all_files"), "*.*")
            )
        )
        if file_path:
            # Aquí podrías copiar el archivo a una carpeta de activos de la app
            # Por ahora, solo guardamos la ruta
            self.image_path_var.set(file_path)


    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        self.tree.selection_set(item_id) # Seleccionar el ítem clickeado
        self.on_tree_select(None) # Cargar detalles del ítem seleccionado

        context_menu = tk.Menu(self.tree, tearoff=0)
        item_type = self.tree.item(item_id, "tags")[0] if self.tree.item(item_id, "tags") else None

        if item_type == "category":
            context_menu.add_command(label=get_text("menu_add_product"), command=self.add_product)
            context_menu.add_command(label=get_text("menu_edit_category"), command=lambda: self.on_tree_select(None)) # Re-trigger select to show form
            context_menu.add_command(label=get_text("menu_delete_category"), command=self.delete_item)
        elif item_type == "product":
            context_menu.add_command(label=get_text("menu_add_variant"), command=self.add_variant)
            context_menu.add_command(label=get_text("menu_add_modifier"), command=self.add_modifier)
            context_menu.add_command(label=get_text("menu_edit_product"), command=lambda: self.on_tree_select(None))
            context_menu.add_command(label=get_text("menu_delete_product"), command=self.delete_item)
        elif item_type == "variant":
            context_menu.add_command(label=get_text("menu_add_modifier"), command=self.add_modifier)
            context_menu.add_command(label=get_text("menu_edit_variant"), command=lambda: self.on_tree_select(None))
            context_menu.add_command(label=get_text("menu_delete_variant"), command=self.delete_item)
        elif item_type == "modifier":
            context_menu.add_command(label=get_text("menu_edit_modifier"), command=lambda: self.on_tree_select(None))
            context_menu.add_command(label=get_text("menu_delete_modifier"), command=self.delete_item)

        if context_menu.winfo_children(): # Mostrar solo si hay opciones
            context_menu.tk_popup(event.x_root, event.y_root)


    def on_modifier_applies_to_change(self, *args):
        selected_option = self.modifier_applies_to_var.get()

        # Las filas donde están los campos de producto y variante para modificadores
        # Asegurarse de que los widgets existan y estén grid() al menos una vez en create_widgets()
        # para que grid_slaves pueda encontrarlos.
        # En este punto, 'row' es relativo al form_frame.
        
        # Estos son los widgets que se ocultan/muestran
        # Modificar las filas según tu layout final
        # Actualmente están en la última parte de create_widgets
        # lbl_modifier_product en row=X, column=0
        # cb_modifier_product en row=X, column=1
        # lbl_modifier_variant en row=Y, column=0
        # cb_modifier_variant en row=Y, column=1
        
        # A partir del código de create_widgets, están en la siguiente secuencia después de radio buttons
        # Los radio buttons ocupan 3 filas empezando en row=4.
        # Por lo tanto, lbl_modifier_product estaría en row=4+3 = 7
        # y lbl_modifier_variant estaría en row=7+1 = 8

        product_label_widgets = self.form_frame.grid_slaves(row=7, column=0)
        product_combo_widgets = self.form_frame.grid_slaves(row=7, column=1)
        variant_label_widgets = self.form_frame.grid_slaves(row=8, column=0)
        variant_combo_widgets = self.form_frame.grid_slaves(row=8, column=1)

        product_label = product_label_widgets[0] if product_label_widgets else None
        product_combo = product_combo_widgets[0] if product_combo_widgets else None
        variant_label = variant_label_widgets[0] if variant_combo_widgets else None # Corregido de product_combo_widgets a variant_combo_widgets
        variant_combo = variant_combo_widgets[0] if variant_combo_widgets else None


        # Ocultar todos por defecto
        if product_label: product_label.grid_remove()
        if product_combo: product_combo.grid_remove()
        if variant_label: variant_label.grid_remove()
        if variant_combo: variant_combo.grid_remove()

        # Mostrar según la opción seleccionada
        if selected_option == "product":
            if product_label: product_label.grid(row=7, column=0, sticky="w", padx=5, pady=2)
            if product_combo: product_combo.grid(row=7, column=1, sticky="ew", padx=5, pady=2)
            self.load_all_products_for_combobox() # Asegurarse de que los productos estén cargados
            self.cb_modifier_variant.set("") # Limpiar la selección de variante si cambia a producto
            self.cb_modifier_variant['values'] = [] # Vaciar las variantes

        elif selected_option == "variant":
            if product_label: product_label.grid(row=7, column=0, sticky="w", padx=5, pady=2)
            if product_combo: product_combo.grid(row=7, column=1, sticky="ew", padx=5, pady=2)
            if variant_label: variant_label.grid(row=8, column=0, sticky="w", padx=5, pady=2)
            if variant_combo: variant_combo.grid(row=8, column=1, sticky="ew", padx=5, pady=2)
            self.load_all_products_for_combobox() # Asegurarse de que los productos estén cargados
            # La carga de variantes se realiza en on_modifier_product_selected cuando se selecciona un producto


    def update_language(self):
        # Actualizar textos de los botones en el panel izquierdo
        self.btn_add_category.config(text=get_text("btn_add_category"))
        self.btn_add_product.config(text=get_text("btn_add_product"))
        self.btn_add_variant.config(text=get_text("btn_add_variant"))
        self.btn_add_modifier.config(text=get_text("btn_add_modifier"))

        # Actualizar el encabezado del treeview
        self.tree.heading("#0", text=get_text("tree_item"))

        # Actualizar título del formulario
        if self.selected_item_type == 'category':
            self.form_title_label.config(text=get_text("title_category_details"))
        elif self.selected_item_type == 'product':
            self.form_title_label.config(text=get_text("title_product_details"))
        elif self.selected_item_type == 'variant':
            self.form_title_label.config(text=get_text("title_variant_details"))
        elif self.selected_item_type == 'modifier':
            self.form_title_label.config(text=get_text("title_modifier_details"))
        else:
            self.form_title_label.config(text=get_text("title_details"))

        # Actualizar el texto del LabelFrame del formulario
        self.form_frame.config(text=get_text("form_details"))

        # Actualizar labels de los campos del formulario
        self.lbl_name_es.config(text=get_text("label_name_es"))
        self.lbl_name_en.config(text=get_text("label_name_en"))
        self.lbl_description_es.config(text=get_text("label_description_es"))
        self.lbl_description_en.config(text=get_text("label_description_en"))
        self.lbl_base_price.config(text=get_text("label_base_price"))
        self.lbl_price_adjustment.config(text=get_text("label_price_adjustment"))
        self.lbl_modifier_price.config(text=get_text("label_modifier_price"))
        self.lbl_image.config(text=get_text("label_image"))
        self.btn_browse_image.config(text=get_text("btn_browse"))
        self.chk_is_available.config(text=get_text("label_is_available"))
        self.lbl_applies_to.config(text=get_text("label_applies_to"))
        self.rb_applies_global.config(text=get_text("option_global"))
        self.rb_applies_product.config(text=get_text("option_product"))
        self.rb_applies_variant.config(text=get_text("option_variant"))
        self.lbl_modifier_product.config(text=get_text("label_product"))
        self.lbl_modifier_variant.config(text=get_text("label_variant"))


        # Actualizar textos de los botones de acción
        self.btn_save.config(text=get_text("btn_save"))
        self.btn_delete.config(text=get_text("btn_delete"))
        self.btn_clear.config(text=get_text("btn_clear"))

        # Recargar el Treeview para actualizar nombres localizados
        self.load_categories()

        # Si hay un producto/variante seleccionado en los comboboxes de modificadores, actualizarlos
        if self.cb_modifier_product.get():
            current_product_id = self.product_map.get(self.cb_modifier_product.get())
            if current_product_id:
                product = Product.get_by_id(current_product_id)
                if product:
                    self.cb_modifier_product.set(product.get_localized_name(current_language))
                    self.on_modifier_product_selected() # Recargar variantes con nuevo idioma
        
        # También actualiza el texto de los modificadores globales en el treeview
        # Esto se maneja automáticamente por load_categories()