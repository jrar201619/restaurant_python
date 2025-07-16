# mi_sistema_ventas/ui/product_manager_ui.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os

# Importar tus modelos y traducciones
from models import Category, Product, Variant, Modifier, Sale, SaleItem, SaleItemModifier
from config.translations import get_text, set_language, current_language

class ProductManagerUI(ttk.Frame):
    def __init__(self, parent, app_instance):
        super().__init__(parent)
        self.parent = parent
        self.app_instance = app_instance
        self.current_lang = current_language

        # Asegúrate de que las carpetas de imágenes existan
        if not os.path.exists('assets/product_images'):
            os.makedirs('assets/product_images')

        self.create_widgets()
        self.update_texts()
        self.load_categories() # Cargar categorías al inicio
        self.load_products() # Cargar productos al inicio
        self.load_variants() # Cargar variantes al inicio
        self.load_modifiers() # Cargar modificadores al inicio (NUEVO)


    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Pestaña de Categorías ---
        self.category_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.category_frame, text=get_text("tree_col_category"))
        self.setup_category_tab()

        # --- Pestaña de Productos ---
        self.product_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.product_frame, text=get_text("tree_col_product"))
        self.setup_product_tab()

        # --- Pestaña de Variantes ---
        self.variant_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.variant_frame, text=get_text("tree_col_variant"))
        self.setup_variant_tab()

        # --- Pestaña de Modificadores ---
        self.modifier_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.modifier_frame, text=get_text("tree_col_modifier"))
        self.setup_modifier_tab() # LLAMADA AL NUEVO MÉTODO

        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)


    def _on_tab_change(self, event):
        selected_tab_id = self.notebook.select()
        tab_index = self.notebook.index(selected_tab_id)

        if tab_index == 0: # Categories tab
            self.app_instance.set_main_title("product_manager_title")
        elif tab_index == 1: # Products tab
            self.app_instance.set_main_title("product_manager_title")
        elif tab_index == 2: # Variants tab
            self.app_instance.set_main_title("product_manager_title")
        elif tab_index == 3: # Modifiers tab
            self.app_instance.set_main_title("product_manager_title")


    def update_texts(self):
        self.current_lang = current_language
        self.notebook.tab(0, text=get_text("tree_col_category"))
        self.notebook.tab(1, text=get_text("tree_col_product"))
        self.notebook.tab(2, text=get_text("tree_col_variant"))
        self.notebook.tab(3, text=get_text("tree_col_modifier"))

        if hasattr(self, 'category_tree'):
            self._update_category_texts()
        if hasattr(self, 'product_tree'):
            self._update_product_texts()
        if hasattr(self, 'variant_tree'):
            self._update_variant_texts()
        if hasattr(self, 'modifier_tree'): # ACTUALIZACIÓN DE TEXTOS DE MODIFICADOR
            self._update_modifier_texts()

        self._on_tab_change(None)


    # --- Métodos de la Pestaña de Categorías ---
    def setup_category_tab(self):
        button_frame = ttk.Frame(self.category_frame)
        button_frame.pack(pady=10, fill="x")

        self.add_category_btn = ttk.Button(button_frame, text=get_text("btn_add_category"), command=self.add_category)
        self.add_category_btn.pack(side="left", padx=5)

        self.edit_category_btn = ttk.Button(button_frame, text=get_text("btn_edit"), command=self.edit_category)
        self.edit_category_btn.pack(side="left", padx=5)

        self.delete_category_btn = ttk.Button(button_frame, text=get_text("btn_delete"), command=self.delete_category)
        self.delete_category_btn.pack(side="left", padx=5)

        columns = ("id", "name_es", "name_en")
        self.category_tree = ttk.Treeview(self.category_frame, columns=columns, show="headings")
        self.category_tree.pack(expand=True, fill="both")

        self.category_tree.heading("id", text="ID", anchor="center")
        self.category_tree.heading("name_es", text=get_text("lbl_name") + " (ES)", anchor="w")
        self.category_tree.heading("name_en", text=get_text("lbl_name") + " (EN)", anchor="w")

        self.category_tree.column("id", width=50, anchor="center")
        self.category_tree.column("name_es", width=200, anchor="w")
        self.category_tree.column("name_en", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(self.category_frame, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.category_tree.bind("<<TreeviewSelect>>", self._on_category_select)
        self._on_category_select()

    def _update_category_texts(self):
        self.add_category_btn.config(text=get_text("btn_add_category"))
        self.edit_category_btn.config(text=get_text("btn_edit"))
        self.delete_category_btn.config(text=get_text("btn_delete"))

        self.category_tree.heading("name_es", text=get_text("lbl_name") + " (ES)")
        self.category_tree.heading("name_en", text=get_text("lbl_name") + " (EN)")

        self.load_categories()

    def _on_category_select(self, event=None):
        selected_item = self.category_tree.selection()
        if selected_item:
            self.edit_category_btn.config(state="normal")
            self.delete_category_btn.config(state="normal")
        else:
            self.edit_category_btn.config(state="disabled")
            self.delete_category_btn.config(state="disabled")

    def load_categories(self):
        self._clear_treeview(self.category_tree)
        categories = Category.get_all()
        for cat in categories:
            self.category_tree.insert("", "end", iid=cat.id, values=(cat.id, cat.name_es, cat.name_en))
        self._on_category_select()

    def add_category(self):
        self._open_category_dialog("add")

    def edit_category(self):
        selected_item = self.category_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return
        category_id = self.category_tree.item(selected_item[0], "iid")
        category = Category.get_by_id(category_id)
        if category:
            self._open_category_dialog("edit", category)
        else:
            self._show_error(get_text("msg_item_not_found"))

    def delete_category(self):
        selected_item = self.category_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return

        category_id = self.category_tree.item(selected_item[0], "iid")
        category = Category.get_by_id(category_id)

        if not category:
            self._show_error(get_text("msg_item_not_found"))
            return

        associated_products = Product.get_products_by_category(category_id)
        if associated_products:
            self._show_error(get_text("msg_category_has_products"))
            return

        if self._ask_confirm(get_text("confirm_delete_message")):
            if category.delete():
                self._show_info(get_text("msg_success"))
                self.load_categories()
                self.load_products() # Recargar productos si una categoría se elimina para reflejar cambios
            else:
                self._show_error(get_text("msg_error") + get_text("msg_delete_failed"))

    def _open_category_dialog(self, mode, category=None):
        dialog = tk.Toplevel(self.parent)
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        if mode == "add":
            dialog.title(get_text("dialog_add_category_title"))
        else:
            dialog.title(get_text("dialog_edit_category_title"))

        lbl_name_es = ttk.Label(dialog, text=get_text("lbl_name") + " (ES):")
        lbl_name_es.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry_name_es = ttk.Entry(dialog, width=40)
        entry_name_es.grid(row=0, column=1, padx=10, pady=5)

        lbl_name_en = ttk.Label(dialog, text=get_text("lbl_name") + " (EN):")
        lbl_name_en.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        entry_name_en = ttk.Entry(dialog, width=40)
        entry_name_en.grid(row=1, column=1, padx=10, pady=5)

        if mode == "edit" and category:
            entry_name_es.insert(0, category.name_es)
            entry_name_en.insert(0, category.name_en)

        def save_category():
            name_es = entry_name_es.get().strip()
            name_en = entry_name_en.get().strip()

            if not name_es or not name_en:
                self._show_error(get_text("msg_error") + get_text("msg_fields_required"))
                return

            try:
                if mode == "add":
                    new_category = Category(name_es=name_es, name_en=name_en)
                    if new_category.save():
                        self._show_info(get_text("msg_success"))
                        self.load_categories()
                        self.load_products() # Recargar productos si se añade/edita una categoría
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
                else: # mode == "edit"
                    category.name_es = name_es
                    category.name_en = name_en
                    if category.save():
                        self._show_info(get_text("msg_success"))
                        self.load_categories()
                        self.load_products() # Recargar productos si se añade/edita una categoría
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
            except Exception as e:
                self._show_error(f"{get_text('msg_error')}: {e}")


        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        save_btn = ttk.Button(button_frame, text=get_text("btn_save"), command=save_category)
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(button_frame, text=get_text("btn_cancel"), command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)

        dialog.wait_window(dialog)


    # --- Métodos de la Pestaña de Productos ---
    def setup_product_tab(self):
        button_frame = ttk.Frame(self.product_frame)
        button_frame.pack(pady=10, fill="x")

        self.add_product_btn = ttk.Button(button_frame, text=get_text("btn_add_product"), command=self.add_product)
        self.add_product_btn.pack(side="left", padx=5)

        self.edit_product_btn = ttk.Button(button_frame, text=get_text("btn_edit"), command=self.edit_product)
        self.edit_product_btn.pack(side="left", padx=5)

        self.delete_product_btn = ttk.Button(button_frame, text=get_text("btn_delete"), command=self.delete_product)
        self.delete_product_btn.pack(side="left", padx=5)

        columns = ("id", "name_es", "name_en", "category_name", "base_price", "image_path")
        self.product_tree = ttk.Treeview(self.product_frame, columns=columns, show="headings")
        self.product_tree.pack(expand=True, fill="both")

        self.product_tree.heading("id", text="ID", anchor="center")
        self.product_tree.heading("name_es", text=get_text("lbl_product_name") + " (ES)", anchor="w")
        self.product_tree.heading("name_en", text=get_text("lbl_product_name") + " (EN)", anchor="w")
        self.product_tree.heading("category_name", text=get_text("lbl_category"), anchor="w")
        self.product_tree.heading("base_price", text=get_text("lbl_base_price"), anchor="e")
        self.product_tree.heading("image_path", text=get_text("lbl_image_path"), anchor="w")

        self.product_tree.column("id", width=50, anchor="center")
        self.product_tree.column("name_es", width=150, anchor="w")
        self.product_tree.column("name_en", width=150, anchor="w")
        self.product_tree.column("category_name", width=100, anchor="w")
        self.product_tree.column("base_price", width=80, anchor="e")
        self.product_tree.column("image_path", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(self.product_frame, orient="vertical", command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.product_tree.bind("<<TreeviewSelect>>", self._on_product_select)
        self._on_product_select()

    def _update_product_texts(self):
        self.add_product_btn.config(text=get_text("btn_add_product"))
        self.edit_product_btn.config(text=get_text("btn_edit"))
        self.delete_product_btn.config(text=get_text("btn_delete"))

        self.product_tree.heading("name_es", text=get_text("lbl_product_name") + " (ES)")
        self.product_tree.heading("name_en", text=get_text("lbl_product_name") + " (EN)")
        self.product_tree.heading("category_name", text=get_text("lbl_category"))
        self.product_tree.heading("base_price", text=get_text("lbl_base_price"))
        self.product_tree.heading("image_path", text=get_text("lbl_image_path"))

        self.load_products()

    def _on_product_select(self, event=None):
        selected_item = self.product_tree.selection()
        if selected_item:
            self.edit_product_btn.config(state="normal")
            self.delete_product_btn.config(state="normal")
        else:
            self.edit_product_btn.config(state="disabled")
            self.delete_product_btn.config(state="disabled")

    def load_products(self):
        self._clear_treeview(self.product_tree)
        products = Product.get_all()
        for prod in products:
            category = Category.get_by_id(prod.category_id)
            category_name = category.get_localized_name(self.current_lang) if category else "N/A"
            self.product_tree.insert("", "end", iid=prod.id,
                                     values=(prod.id, prod.name_es, prod.name_en,
                                             category_name, f"{prod.base_price:.2f}",
                                             os.path.basename(prod.image_path) if prod.image_path else ""))
        self._on_product_select()

    def add_product(self):
        self._open_product_dialog("add")

    def edit_product(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return
        product_id = self.product_tree.item(selected_item[0], "iid")
        product = Product.get_by_id(product_id)
        if product:
            self._open_product_dialog("edit", product)
        else:
            self._show_error(get_text("msg_item_not_found"))

    def delete_product(self):
        selected_item = self.product_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return

        product_id = self.product_tree.item(selected_item[0], "iid")
        product = Product.get_by_id(product_id)

        if not product:
            self._show_error(get_text("msg_item_not_found"))
            return

        associated_variants = Variant.get_variants_by_product(product_id)
        if associated_variants:
            self._show_error(get_text("msg_product_has_variants"))
            return

        # Check for associated modifiers
        associated_modifiers = Modifier.get_modifiers_by_product(product_id)
        if associated_modifiers:
            self._show_error(get_text("msg_product_has_modifiers")) # Assuming you'll add this key
            return

        if self._ask_confirm(get_text("confirm_delete_message")):
            if product.delete():
                if product.image_path and os.path.exists(product.image_path):
                    try:
                        os.remove(product.image_path)
                    except OSError as e:
                        print(f"Error al eliminar la imagen {product.image_path}: {e}")
                self._show_info(get_text("msg_success"))
                self.load_products()
                self.load_variants() # Recargar variantes si un producto se elimina (afecta a las variantes de ese producto)
                self.load_modifiers() # Recargar modificadores si un producto se elimina (afecta a los modificadores de ese producto)
            else:
                self._show_error(get_text("msg_error") + get_text("msg_delete_failed"))

    def _open_product_dialog(self, mode, product=None):
        dialog = tk.Toplevel(self.parent)
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        if mode == "add":
            dialog.title(get_text("dialog_add_product_title"))
        else:
            dialog.title(get_text("dialog_edit_product_title"))

        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=10)

        ttk.Label(form_frame, text=get_text("lbl_product_name") + " (ES):").grid(row=0, column=0, sticky="w", pady=2)
        entry_name_es = ttk.Entry(form_frame, width=40)
        entry_name_es.grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text=get_text("lbl_product_name") + " (EN):").grid(row=1, column=0, sticky="w", pady=2)
        entry_name_en = ttk.Entry(form_frame, width=40)
        entry_name_en.grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text=get_text("lbl_description") + " (ES):").grid(row=2, column=0, sticky="w", pady=2)
        entry_description_es = ttk.Entry(form_frame, width=40)
        entry_description_es.grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text=get_text("lbl_description") + " (EN):").grid(row=3, column=0, sticky="w", pady=2)
        entry_description_en = ttk.Entry(form_frame, width=40)
        entry_description_en.grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(form_frame, text=get_text("lbl_base_price") + ":").grid(row=4, column=0, sticky="w", pady=2)
        entry_base_price = ttk.Entry(form_frame, width=40)
        entry_base_price.grid(row=4, column=1, sticky="ew", pady=2)
        vcmd = (self.register(self._validate_numeric_input), '%P')
        entry_base_price.config(validate="key", validatecommand=vcmd)

        ttk.Label(form_frame, text=get_text("lbl_category") + ":").grid(row=5, column=0, sticky="w", pady=2)
        self.product_dialog_category_names = [cat.get_localized_name(self.current_lang) for cat in Category.get_all()]
        self.product_dialog_category_ids_map = {cat.get_localized_name(self.current_lang): cat.id for cat in Category.get_all()}
        combo_category = ttk.Combobox(form_frame, values=self.product_dialog_category_names, state="readonly")
        combo_category.grid(row=5, column=1, sticky="ew", pady=2)
        if self.product_dialog_category_names:
            combo_category.set(self.product_dialog_category_names[0])

        ttk.Label(form_frame, text=get_text("lbl_image_path") + ":").grid(row=6, column=0, sticky="w", pady=2)
        entry_image_path = ttk.Entry(form_frame, width=30)
        entry_image_path.grid(row=6, column=1, sticky="ew", pady=2)
        btn_select_image = ttk.Button(form_frame, text=get_text("btn_select_image"),
                                      command=lambda: self._select_image_file(entry_image_path, self.image_preview_label))
        btn_select_image.grid(row=6, column=2, padx=5, pady=2)

        self.image_preview_label = ttk.Label(form_frame, compound="image")
        self.image_preview_label.grid(row=7, column=0, columnspan=3, pady=5)
        self.tk_image = None

        if mode == "edit" and product:
            entry_name_es.insert(0, product.name_es)
            entry_name_en.insert(0, product.name_en)
            entry_description_es.insert(0, product.description_es)
            entry_description_en.insert(0, product.description_en)
            entry_base_price.insert(0, str(product.base_price))
            
            if product.category_id:
                current_category = Category.get_by_id(product.category_id)
                if current_category:
                    combo_category.set(current_category.get_localized_name(self.current_lang))
            
            entry_image_path.insert(0, product.image_path if product.image_path else "")
            self._load_and_display_image(product.image_path, self.image_preview_label)

        def save_product():
            name_es = entry_name_es.get().strip()
            name_en = entry_name_en.get().strip()
            description_es = entry_description_es.get().strip()
            description_en = entry_description_en.get().strip()
            base_price_str = entry_base_price.get().strip()
            selected_category_name = combo_category.get()
            image_path = entry_image_path.get().strip()

            if not name_es or not name_en or not base_price_str or not selected_category_name:
                self._show_error(get_text("msg_error") + get_text("msg_fields_required"))
                return

            try:
                base_price = float(base_price_str)
                if base_price < 0:
                    self._show_error(get_text("msg_error") + get_text("msg_price_positive"))
                    return
            except ValueError:
                self._show_error(get_text("msg_error") + get_text("msg_invalid_price"))
                return

            category_id = self.product_dialog_category_ids_map.get(selected_category_name)
            if category_id is None:
                self._show_error(get_text("msg_error") + get_text("msg_select_category"))
                return

            try:
                if mode == "add":
                    new_product = Product(
                        name_es=name_es, name_en=name_en,
                        description_es=description_es, description_en=description_en,
                        base_price=base_price, category_id=category_id,
                        image_path=image_path
                    )
                    if new_product.save():
                        self._show_info(get_text("msg_success"))
                        self.load_products()
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
                else: # mode == "edit"
                    if product.image_path and product.image_path != image_path and os.path.exists(product.image_path):
                        try:
                            os.remove(product.image_path)
                        except OSError as e:
                            print(f"Advertencia: No se pudo eliminar la imagen antigua {product.image_path}: {e}")

                    product.name_es = name_es
                    product.name_en = name_en
                    product.description_es = description_es
                    product.description_en = description_en
                    product.base_price = base_price
                    product.category_id = category_id
                    product.image_path = image_path
                    if product.save():
                        self._show_info(get_text("msg_success"))
                        self.load_products()
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
            except Exception as e:
                self._show_error(f"{get_text('msg_error')}: {e}")

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        save_btn = ttk.Button(button_frame, text=get_text("btn_save"), command=save_product)
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(button_frame, text=get_text("btn_cancel"), command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)

        dialog.wait_window(dialog)


    # --- Métodos de la Pestaña de Variantes ---

    def setup_variant_tab(self):
        """Configura la interfaz para la gestión de variantes."""
        # Frame para botones
        button_frame = ttk.Frame(self.variant_frame)
        button_frame.pack(pady=10, fill="x")

        self.add_variant_btn = ttk.Button(button_frame, text=get_text("btn_add_variant"), command=self.add_variant)
        self.add_variant_btn.pack(side="left", padx=5)

        self.edit_variant_btn = ttk.Button(button_frame, text=get_text("btn_edit"), command=self.edit_variant)
        self.edit_variant_btn.pack(side="left", padx=5)

        self.delete_variant_btn = ttk.Button(button_frame, text=get_text("btn_delete"), command=self.delete_variant)
        self.delete_variant_btn.pack(side="left", padx=5)

        # Treeview para mostrar variantes
        columns = ("id", "product_name", "name_es", "name_en", "price_adjustment")
        self.variant_tree = ttk.Treeview(self.variant_frame, columns=columns, show="headings")
        self.variant_tree.pack(expand=True, fill="both")

        # Configuración de las columnas (el texto se actualizará en _update_variant_texts)
        self.variant_tree.heading("id", text="ID", anchor="center")
        self.variant_tree.heading("product_name", text=get_text("lbl_product_name"), anchor="w")
        self.variant_tree.heading("name_es", text=get_text("lbl_variant_name") + " (ES)", anchor="w")
        self.variant_tree.heading("name_en", text=get_text("lbl_variant_name") + " (EN)", anchor="w")
        self.variant_tree.heading("price_adjustment", text=get_text("lbl_price_adjustment"), anchor="e")

        # Ancho de las columnas
        self.variant_tree.column("id", width=50, anchor="center")
        self.variant_tree.column("product_name", width=150, anchor="w")
        self.variant_tree.column("name_es", width=150, anchor="w")
        self.variant_tree.column("name_en", width=150, anchor="w")
        self.variant_tree.column("price_adjustment", width=100, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.variant_frame, orient="vertical", command=self.variant_tree.yview)
        self.variant_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Evento de selección para habilitar/deshabilitar botones de edición/eliminación
        self.variant_tree.bind("<<TreeviewSelect>>", self._on_variant_select)
        self._on_variant_select() # Deshabilitar inicialmente los botones

    def _update_variant_texts(self):
        """Actualiza los textos específicos de la pestaña de variantes."""
        self.add_variant_btn.config(text=get_text("btn_add_variant"))
        self.edit_variant_btn.config(text=get_text("btn_edit"))
        self.delete_variant_btn.config(text=get_text("btn_delete"))

        # Actualizar encabezados del Treeview
        self.variant_tree.heading("product_name", text=get_text("lbl_product_name"))
        self.variant_tree.heading("name_es", text=get_text("lbl_variant_name") + " (ES)")
        self.variant_tree.heading("name_en", text=get_text("lbl_variant_name") + " (EN)")
        self.variant_tree.heading("price_adjustment", text=get_text("lbl_price_adjustment"))

        self.load_variants() # Recargar datos para que se muestren los nombres traducidos si hay cambios relevantes

    def _on_variant_select(self, event=None):
        """Habilita o deshabilita los botones de editar/eliminar según la selección del Treeview."""
        selected_item = self.variant_tree.selection()
        if selected_item:
            self.edit_variant_btn.config(state="normal")
            self.delete_variant_btn.config(state="normal")
        else:
            self.edit_variant_btn.config(state="disabled")
            self.delete_variant_btn.config(state="disabled")

    def load_variants(self):
        """Carga y muestra las variantes de la base de datos en el Treeview."""
        self._clear_treeview(self.variant_tree)
        variants = Variant.get_all()
        for var in variants:
            product = Product.get_by_id(var.product_id)
            product_name = product.get_localized_name(self.current_lang) if product else "N/A"
            self.variant_tree.insert("", "end", iid=var.id,
                                     values=(var.id, product_name, var.name_es, var.name_en, f"{var.price_adjustment:.2f}"))
        self._on_variant_select() # Re-evaluar el estado de los botones

    def add_variant(self):
        """Abre un diálogo para añadir una nueva variante."""
        self._open_variant_dialog("add")

    def edit_variant(self):
        """Abre un diálogo para editar la variante seleccionada."""
        selected_item = self.variant_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return
        variant_id = self.variant_tree.item(selected_item[0], "iid")
        variant = Variant.get_by_id(variant_id)
        if variant:
            self._open_variant_dialog("edit", variant)
        else:
            self._show_error(get_text("msg_item_not_found"))

    def delete_variant(self):
        """Elimina la variante seleccionada."""
        selected_item = self.variant_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return

        variant_id = self.variant_tree.item(selected_item[0], "iid")
        variant = Variant.get_by_id(variant_id)

        if not variant:
            self._show_error(get_text("msg_item_not_found"))
            return
        
        # Check for associated modifiers (if modifiers can be linked to variants)
        # This assumes your Modifier model has a way to get modifiers by variant_id
        associated_modifiers = Modifier.get_modifiers_by_variant(variant_id) # Assuming this method exists
        if associated_modifiers:
            self._show_error(get_text("msg_variant_has_modifiers"))
            return

        if self._ask_confirm(get_text("confirm_delete_message")):
            if variant.delete():
                self._show_info(get_text("msg_success"))
                self.load_variants()
                self.load_modifiers() # Recargar modificadores si una variante se elimina
            else:
                self._show_error(get_text("msg_error") + get_text("msg_delete_failed"))

    def _open_variant_dialog(self, mode, variant=None):
        """
        Abre un diálogo para añadir o editar una variante.
        :param mode: "add" o "edit"
        :param variant: Objeto Variant si el modo es "edit"
        """
        dialog = tk.Toplevel(self.parent)
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        if mode == "add":
            dialog.title(get_text("dialog_add_variant_title"))
        else:
            dialog.title(get_text("dialog_edit_variant_title"))

        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=10)

        # Producto asociado (Combobox)
        ttk.Label(form_frame, text=get_text("lbl_product_name") + ":").grid(row=0, column=0, sticky="w", pady=2)
        # Asegúrate de que solo los productos con ID estén disponibles
        self.variant_dialog_product_names = [
            prod.get_localized_name(self.current_lang) for prod in Product.get_all() if prod.id is not None
        ]
        self.variant_dialog_product_ids_map = {
            prod.get_localized_name(self.current_lang): prod.id for prod in Product.get_all() if prod.id is not None
        }
        combo_product = ttk.Combobox(form_frame, values=self.variant_dialog_product_names, state="readonly")
        combo_product.grid(row=0, column=1, sticky="ew", pady=2)
        if self.variant_dialog_product_names:
            combo_product.set(self.variant_dialog_product_names[0]) # Select first product by default


        # Nombre de Variante (ES)
        ttk.Label(form_frame, text=get_text("lbl_variant_name") + " (ES):").grid(row=1, column=0, sticky="w", pady=2)
        entry_name_es = ttk.Entry(form_frame, width=40)
        entry_name_es.grid(row=1, column=1, sticky="ew", pady=2)

        # Nombre de Variante (EN)
        ttk.Label(form_frame, text=get_text("lbl_variant_name") + " (EN):").grid(row=2, column=0, sticky="w", pady=2)
        entry_name_en = ttk.Entry(form_frame, width=40)
        entry_name_en.grid(row=2, column=1, sticky="ew", pady=2)

        # Ajuste de Precio
        ttk.Label(form_frame, text=get_text("lbl_price_adjustment") + ":").grid(row=3, column=0, sticky="w", pady=2)
        entry_price_adjustment = ttk.Entry(form_frame, width=40)
        entry_price_adjustment.grid(row=3, column=1, sticky="ew", pady=2)
        vcmd = (self.register(self._validate_numeric_input_with_negative), '%P') # Puede ser negativo
        entry_price_adjustment.config(validate="key", validatecommand=vcmd)


        # Cargar datos si es modo edición
        if mode == "edit" and variant:
            # Seleccionar producto actual de la variante
            if variant.product_id:
                current_product = Product.get_by_id(variant.product_id)
                if current_product:
                    combo_product.set(current_product.get_localized_name(self.current_lang))
            
            entry_name_es.insert(0, variant.name_es)
            entry_name_en.insert(0, variant.name_en)
            entry_price_adjustment.insert(0, str(variant.price_adjustment))


        def save_variant():
            selected_product_name = combo_product.get()
            name_es = entry_name_es.get().strip()
            name_en = entry_name_en.get().strip()
            price_adjustment_str = entry_price_adjustment.get().strip()

            if not selected_product_name or not name_es or not name_en or not price_adjustment_str:
                self._show_error(get_text("msg_error") + get_text("msg_fields_required"))
                return

            try:
                price_adjustment = float(price_adjustment_str)
            except ValueError:
                self._show_error(get_text("msg_error") + get_text("msg_invalid_price_adjustment", default="Ajuste de precio inválido. Introduce un número válido."))
                return

            product_id = self.variant_dialog_product_ids_map.get(selected_product_name)
            if product_id is None:
                self._show_error(get_text("msg_error") + get_text("msg_select_product", default="Por favor, selecciona un producto válido."))
                return
            
            try:
                if mode == "add":
                    new_variant = Variant(
                        product_id=product_id,
                        name_es=name_es, name_en=name_en,
                        price_adjustment=price_adjustment
                    )
                    if new_variant.save():
                        self._show_info(get_text("msg_success"))
                        self.load_variants()
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
                else: # mode == "edit"
                    variant.product_id = product_id
                    variant.name_es = name_es
                    variant.name_en = name_en
                    variant.price_adjustment = price_adjustment
                    if variant.save():
                        self._show_info(get_text("msg_success"))
                        self.load_variants()
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
            except Exception as e:
                self._show_error(f"{get_text('msg_error')}: {e}")

        # Botones de acción
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        save_btn = ttk.Button(button_frame, text=get_text("btn_save"), command=save_variant)
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(button_frame, text=get_text("btn_cancel"), command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)

        dialog.wait_window(dialog)


    # --- Métodos de la Pestaña de Modificadores (NUEVO) ---

    def setup_modifier_tab(self):
        """Configura la interfaz para la gestión de modificadores."""
        # Frame para botones
        button_frame = ttk.Frame(self.modifier_frame)
        button_frame.pack(pady=10, fill="x")

        self.add_modifier_btn = ttk.Button(button_frame, text=get_text("btn_add_modifier"), command=self.add_modifier)
        self.add_modifier_btn.pack(side="left", padx=5)

        self.edit_modifier_btn = ttk.Button(button_frame, text=get_text("btn_edit"), command=self.edit_modifier)
        self.edit_modifier_btn.pack(side="left", padx=5)

        self.delete_modifier_btn = ttk.Button(button_frame, text=get_text("btn_delete"), command=self.delete_modifier)
        self.delete_modifier_btn.pack(side="left", padx=5)

        # Treeview para mostrar modificadores
        columns = ("id", "associated_item", "name_es", "name_en", "price")
        self.modifier_tree = ttk.Treeview(self.modifier_frame, columns=columns, show="headings")
        self.modifier_tree.pack(expand=True, fill="both")

        # Configuración de las columnas
        self.modifier_tree.heading("id", text="ID", anchor="center")
        self.modifier_tree.heading("associated_item", text=get_text("lbl_product_name") + "/" + get_text("tree_col_variant"), anchor="w") # Ajustar encabezado
        self.modifier_tree.heading("name_es", text=get_text("lbl_modifier_name") + " (ES)", anchor="w")
        self.modifier_tree.heading("name_en", text=get_text("lbl_modifier_name") + " (EN)", anchor="w")
        self.modifier_tree.heading("price", text=get_text("lbl_modifier_price"), anchor="e")

        # Ancho de las columnas
        self.modifier_tree.column("id", width=50, anchor="center")
        self.modifier_tree.column("associated_item", width=200, anchor="w")
        self.modifier_tree.column("name_es", width=150, anchor="w")
        self.modifier_tree.column("name_en", width=150, anchor="w")
        self.modifier_tree.column("price", width=80, anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.modifier_frame, orient="vertical", command=self.modifier_tree.yview)
        self.modifier_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Evento de selección
        self.modifier_tree.bind("<<TreeviewSelect>>", self._on_modifier_select)
        self._on_modifier_select()

    def _update_modifier_texts(self):
        """Actualiza los textos específicos de la pestaña de modificadores."""
        self.add_modifier_btn.config(text=get_text("btn_add_modifier"))
        self.edit_modifier_btn.config(text=get_text("btn_edit"))
        self.delete_modifier_btn.config(text=get_text("btn_delete"))

        # Actualizar encabezados del Treeview
        self.modifier_tree.heading("associated_item", text=get_text("lbl_product_name") + "/" + get_text("tree_col_variant"))
        self.modifier_tree.heading("name_es", text=get_text("lbl_modifier_name") + " (ES)")
        self.modifier_tree.heading("name_en", text=get_text("lbl_modifier_name") + " (EN)")
        self.modifier_tree.heading("price", text=get_text("lbl_modifier_price"))

        self.load_modifiers()

    def _on_modifier_select(self, event=None):
        """Habilita o deshabilita los botones de editar/eliminar según la selección del Treeview."""
        selected_item = self.modifier_tree.selection()
        if selected_item:
            self.edit_modifier_btn.config(state="normal")
            self.delete_modifier_btn.config(state="normal")
        else:
            self.edit_modifier_btn.config(state="disabled")
            self.delete_modifier_btn.config(state="disabled")

    def load_modifiers(self):
        """Carga y muestra los modificadores de la base de datos en el Treeview."""
        self._clear_treeview(self.modifier_tree)
        modifiers = Modifier.get_all()
        for mod in modifiers:
            associated_item_name = get_text("global_modifier_label", default="Global") # Default for global modifiers

            if mod.product_id:
                product = Product.get_by_id(mod.product_id)
                if product:
                    associated_item_name = product.get_localized_name(self.current_lang)
            elif mod.variant_id: # If modifiers can be associated with variants
                variant = Variant.get_by_id(mod.variant_id)
                if variant:
                    product = Product.get_by_id(variant.product_id)
                    product_name = product.get_localized_name(self.current_lang) if product else "N/A"
                    associated_item_name = f"{product_name} ({variant.get_localized_name(self.current_lang)})"

            self.modifier_tree.insert("", "end", iid=mod.id,
                                     values=(mod.id, associated_item_name, mod.name_es, mod.name_en, f"{mod.price:.2f}"))
        self._on_modifier_select()

    def add_modifier(self):
        """Abre un diálogo para añadir un nuevo modificador."""
        self._open_modifier_dialog("add")

    def edit_modifier(self):
        """Abre un diálogo para editar el modificador seleccionado."""
        selected_item = self.modifier_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return
        modifier_id = self.modifier_tree.item(selected_item[0], "iid")
        modifier = Modifier.get_by_id(modifier_id)
        if modifier:
            self._open_modifier_dialog("edit", modifier)
        else:
            self._show_error(get_text("msg_item_not_found"))

    def delete_modifier(self):
        """Elimina el modificador seleccionado."""
        selected_item = self.modifier_tree.selection()
        if not selected_item:
            self._show_info(get_text("msg_no_selection"))
            return

        modifier_id = self.modifier_tree.item(selected_item[0], "iid")
        modifier = Modifier.get_by_id(modifier_id)

        if not modifier:
            self._show_error(get_text("msg_item_not_found"))
            return

        # Check for associated SaleItemModifiers (if applicable)
        # This would require a method in SaleItemModifier or a direct query.
        # For simplicity, not checking for existing sales items linked to this modifier.

        if self._ask_confirm(get_text("confirm_delete_message")):
            if modifier.delete():
                self._show_info(get_text("msg_success"))
                self.load_modifiers()
            else:
                self._show_error(get_text("msg_error") + get_text("msg_delete_failed"))

    def _open_modifier_dialog(self, mode, modifier=None):
        """
        Abre un diálogo para añadir o editar un modificador.
        :param mode: "add" o "edit"
        :param modifier: Objeto Modifier si el modo es "edit"
        """
        dialog = tk.Toplevel(self.parent)
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)

        if mode == "add":
            dialog.title(get_text("dialog_add_modifier_title"))
        else:
            dialog.title(get_text("dialog_edit_modifier_title"))

        form_frame = ttk.Frame(dialog)
        form_frame.pack(padx=20, pady=10)

        # Nombre de Modificador (ES)
        ttk.Label(form_frame, text=get_text("lbl_modifier_name") + " (ES):").grid(row=0, column=0, sticky="w", pady=2)
        entry_name_es = ttk.Entry(form_frame, width=40)
        entry_name_es.grid(row=0, column=1, sticky="ew", pady=2)

        # Nombre de Modificador (EN)
        ttk.Label(form_frame, text=get_text("lbl_modifier_name") + " (EN):").grid(row=1, column=0, sticky="w", pady=2)
        entry_name_en = ttk.Entry(form_frame, width=40)
        entry_name_en.grid(row=1, column=1, sticky="ew", pady=2)

        # Precio de Modificador
        ttk.Label(form_frame, text=get_text("lbl_modifier_price") + ":").grid(row=2, column=0, sticky="w", pady=2)
        entry_price = ttk.Entry(form_frame, width=40)
        entry_price.grid(row=2, column=1, sticky="ew", pady=2)
        vcmd = (self.register(self._validate_numeric_input_with_negative), '%P') # Precio puede ser 0 o negativo para descuentos
        entry_price.config(validate="key", validatecommand=vcmd)
        
        # Asociación a Producto o Variante (Simplificado: solo a Producto por ahora, o Global)
        ttk.Label(form_frame, text=get_text("lbl_product_name") + "/" + get_text("tree_col_variant") + ":").grid(row=3, column=0, sticky="w", pady=2)
        
        # Opciones para el combobox: "Global", y luego todos los productos y variantes.
        # Simplificación: Dejaremos la opción para asociarlo a un PRODUCTO o GLOBAL
        # Si se quiere asociar a variantes, la lista de `combo_values` sería más compleja.
        combo_values = [get_text("global_modifier_label", default="Global")] + [
            prod.get_localized_name(self.current_lang) for prod in Product.get_all() if prod.id is not None
        ]
        self.modifier_dialog_item_ids_map = {
            get_text("global_modifier_label", default="Global"): (None, None) # (product_id, variant_id)
        }
        for prod in Product.get_all():
            if prod.id is not None:
                self.modifier_dialog_item_ids_map[prod.get_localized_name(self.current_lang)] = (prod.id, None)
        # Puedes añadir variantes aquí si lo necesitas:
        # for var in Variant.get_all():
        #     if var.id is not None:
        #         product = Product.get_by_id(var.product_id)
        #         product_name = product.get_localized_name(self.current_lang) if product else "N/A"
        #         self.modifier_dialog_item_ids_map[f"{product_name} ({var.get_localized_name(self.current_lang)})"] = (var.product_id, var.id)
        #         combo_values.append(f"{product_name} ({var.get_localized_name(self.current_lang)})")


        combo_associated_item = ttk.Combobox(form_frame, values=combo_values, state="readonly")
        combo_associated_item.grid(row=3, column=1, sticky="ew", pady=2)
        combo_associated_item.set(get_text("global_modifier_label", default="Global")) # Default a Global


        # Cargar datos si es modo edición
        if mode == "edit" and modifier:
            entry_name_es.insert(0, modifier.name_es)
            entry_name_en.insert(0, modifier.name_en)
            entry_price.insert(0, str(modifier.price))
            
            if modifier.product_id:
                product = Product.get_by_id(modifier.product_id)
                if product:
                    combo_associated_item.set(product.get_localized_name(self.current_lang))
            elif modifier.variant_id:
                # Si se implementara la asociación a variantes, se debería buscar aquí
                pass
            else: # Global modifier
                combo_associated_item.set(get_text("global_modifier_label", default="Global"))


        def save_modifier():
            name_es = entry_name_es.get().strip()
            name_en = entry_name_en.get().strip()
            price_str = entry_price.get().strip()
            selected_item_name = combo_associated_item.get()

            if not name_es or not name_en or not price_str:
                self._show_error(get_text("msg_error") + get_text("msg_fields_required"))
                return

            try:
                price = float(price_str)
            except ValueError:
                self._show_error(get_text("msg_error") + get_text("msg_invalid_price", default="Precio inválido. Introduce un número válido."))
                return
            
            # Obtener product_id y variant_id de la selección
            product_id = None
            variant_id = None
            if selected_item_name != get_text("global_modifier_label", default="Global"):
                product_id, variant_id = self.modifier_dialog_item_ids_map.get(selected_item_name, (None, None))
                if product_id is None and variant_id is None: # Should not happen if combo_values are correct
                    self._show_error(get_text("msg_error") + get_text("msg_select_product", default="Por favor, selecciona un elemento válido."))
                    return

            try:
                if mode == "add":
                    new_modifier = Modifier(
                        name_es=name_es, name_en=name_en,
                        price=price,
                        product_id=product_id,
                        variant_id=variant_id # Esto se usará si se implementa la asociación a variantes
                    )
                    if new_modifier.save():
                        self._show_info(get_text("msg_success"))
                        self.load_modifiers()
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
                else: # mode == "edit"
                    modifier.name_es = name_es
                    modifier.name_en = name_en
                    modifier.price = price
                    modifier.product_id = product_id
                    modifier.variant_id = variant_id
                    if modifier.save():
                        self._show_info(get_text("msg_success"))
                        self.load_modifiers()
                        dialog.destroy()
                    else:
                        self._show_error(get_text("msg_error") + get_text("msg_save_failed"))
            except Exception as e:
                self._show_error(f"{get_text('msg_error')}: {e}")

        # Botones de acción
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        save_btn = ttk.Button(button_frame, text=get_text("btn_save"), command=save_modifier)
        save_btn.pack(side="left", padx=5)

        cancel_btn = ttk.Button(button_frame, text=get_text("btn_cancel"), command=dialog.destroy)
        cancel_btn.pack(side="left", padx=5)

        dialog.wait_window(dialog)


    # --- Métodos auxiliares generales ---

    def _clear_treeview(self, tree):
        for item in tree.get_children():
            tree.delete(item)

    def _show_info(self, message):
        messagebox.showinfo(get_text("app_title"), message)

    def _show_error(self, message):
        messagebox.showerror(get_text("app_title"), message)

    def _ask_confirm(self, message):
        return messagebox.askyesno(get_text("confirm_delete_title"), message)

    def _select_image_file(self, entry_widget, preview_label):
        """Abre un diálogo de archivo para seleccionar una imagen y copia a assets/product_images."""
        file_path = filedialog.askopenfilename(
            title=get_text("btn_select_image"),
            filetypes=[(get_text("image_files"), "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            base_name = os.path.basename(file_path)
            new_file_path = os.path.join("assets", "product_images", base_name)
            
            counter = 1
            original_name, ext = os.path.splitext(base_name)
            while os.path.exists(new_file_path):
                new_file_path = os.path.join("assets", "product_images", f"{original_name}_{counter}{ext}")
                counter += 1

            try:
                import shutil
                shutil.copy(file_path, new_file_path)
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, new_file_path)
                self._load_and_display_image(new_file_path, preview_label) # Muestra la vista previa
            except Exception as e:
                self._show_error(f"{get_text('msg_error')}: {get_text('msg_image_copy_failed')}\n{e}")

    def _load_and_display_image(self, image_path, label_widget, size=(100, 100)):
        """Carga una imagen y la muestra en un QLabel."""
        self.tk_image = None # Limpiar referencia anterior
        label_widget.config(image='', text=get_text("no_image_preview"))

        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail(size, Image.Resampling.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(img) # Guarda la referencia
                label_widget.config(image=self.tk_image, text="")
            except Exception as e:
                label_widget.config(image='', text=get_text("error_loading_image"))
                print(f"Error al cargar imagen {image_path}: {e}")

    def _validate_numeric_input(self, P):
        """Valida que la entrada sea un número flotante válido y positivo (para precios base)."""
        if P == "" or P == ".":
            return True
        try:
            val = float(P)
            return val >= 0
        except ValueError:
            return False

    def _validate_numeric_input_with_negative(self, P):
        """Valida que la entrada sea un número flotante válido (puede ser positivo o negativo para ajustes)."""
        if P == "" or P == "." or P == "-": # Permitir '-' al inicio para números negativos
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False