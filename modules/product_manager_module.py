# modules/product_manager_module.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
from config.translations import get_text
from views.product_dialogs import CategoryForm, ProductForm, VariantForm, ModifierForm
# from models.category import Category # Asumo que tienes estos modelos
# from models.product import Product
# from models.variant import Variant
# from models.modifier import Modifier
# from utils.db_manager import DBManager # Ya importado en main

class ProductManagerModule(ttk.Frame):
    def __init__(self, parent, db_manager, icons): # Recibe el diccionario de iconos
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.parent = parent
        self.icons = icons # Guarda la referencia a los iconos

        # Configurar grid para que el contenido del módulo se expanda
        self.grid_rowconfigure(1, weight=1) # La PanedWindow en la fila 1
        self.grid_columnconfigure(0, weight=1) # La PanedWindow en la columna 0

        self.current_form_frame = None # Para mantener la referencia al formulario actual
        self.selected_item = None # Para el elemento seleccionado en el treeview (categoría, producto, etc.)
        self.selected_item_type = None # 'category', 'product', 'variant', 'modifier'

        self.create_widgets()
        self.load_categories_and_products()


    def create_widgets(self):
        # Frame para botones de acción en la parte superior
        action_frame = ttk.Frame(self)
        action_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        # Configura las columnas para que los botones estén justificados a la izquierda
        for i in range(4): # Ajusta según la cantidad de botones
            action_frame.grid_columnconfigure(i, weight=0) # No se expanden
        action_frame.grid_columnconfigure(4, weight=1) # Una columna vacía al final para empujar

        # Botones con iconos y texto
        ttk.Button(action_frame, text=get_text("btn_add_category"), image=self.icons["add_category"], compound=tk.LEFT, command=self.add_category).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text=get_text("btn_add_product"), image=self.icons["add_product"], compound=tk.LEFT, command=self.add_product).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text=get_text("btn_add_variant"), image=self.icons["add_variant"], compound=tk.LEFT, command=self.add_variant).grid(row=0, column=2, padx=5)
        ttk.Button(action_frame, text=get_text("btn_add_modifier"), image=self.icons["add_modifier"], compound=tk.LEFT, command=self.add_modifier).grid(row=0, column=3, padx=5)


        # PanedWindow para la estructura de árbol y los detalles
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=1, column=0, sticky="nsew") # Ocupa todo el espacio restante

        # --- Lado izquierdo: Treeview ---
        self.tree_frame = ttk.Frame(self.paned_window, padding="5")
        self.paned_window.add(self.tree_frame, weight=1) # El tree_frame se expande horizontalmente
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Name_ES", "Name_EN", "Price"), show="headings")
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading("#0", text=get_text("tree_col_category_product")) # Columna principal para jerarquía
        self.tree.column("#0", width=250, stretch=tk.YES) # Ancho inicial razonable
        self.tree.heading("ID", text=get_text("tree_col_id"))
        self.tree.column("ID", width=50, stretch=tk.NO, anchor="center")
        self.tree.heading("Name_ES", text=get_text("tree_col_name_es"))
        self.tree.column("Name_ES", width=150, stretch=tk.YES)
        self.tree.heading("Name_EN", text=get_text("tree_col_name_en"))
        self.tree.column("Name_EN", width=150, stretch=tk.YES)
        self.tree.heading("Price", text=get_text("tree_col_price"))
        self.tree.column("Price", width=80, stretch=tk.NO, anchor="e")

        # Scrollbar para el treeview
        tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scrollbar.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu) # Botón derecho para menú contextual

        # --- Lado derecho: Área de detalles para editar ---
        self.detail_frame = ttk.Frame(self.paned_window, padding="10")
        self.paned_window.add(self.detail_frame, weight=1) # El detail_frame también se expande

        # Título del formulario de detalles
        self.detail_title_label = ttk.Label(self.detail_frame, text="", font=('Arial', 12, 'bold'))
        self.detail_title_label.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Frame para el formulario dinámico (categoría, producto, etc.)
        self.form_container_frame = ttk.Frame(self.detail_frame)
        self.form_container_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.form_container_frame.grid_rowconfigure(0, weight=1) # El formulario dentro se expande
        self.form_container_frame.grid_columnconfigure(0, weight=1) # El formulario dentro se expande

        # Botones de acción del formulario de detalles (Guardar, Eliminar, Limpiar)
        form_action_frame = ttk.Frame(self.detail_frame)
        form_action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        form_action_frame.columnconfigure(0, weight=1) # Columna izquierda vacía para empujar botones a la derecha

        ttk.Button(form_action_frame, text=get_text("btn_save"), image=self.icons["save"], compound=tk.LEFT, command=self.save_item).grid(row=0, column=1, padx=5, sticky="e")
        ttk.Button(form_action_frame, text=get_text("btn_delete"), image=self.icons["delete"], compound=tk.LEFT, command=self.delete_item).grid(row=0, column=2, padx=5, sticky="e")
        ttk.Button(form_action_frame, text=get_text("btn_clear_form"), image=self.icons["clear"], compound=tk.LEFT, command=self.clear_detail_form).grid(row=0, column=3, padx=5, sticky="e")

        # Configurar la última fila de detail_frame para que se expanda y empuje los botones al final
        self.detail_frame.grid_rowconfigure(self.detail_frame.grid_size()[1], weight=1)

        self.create_context_menu()

    def create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label=get_text("context_edit"), image=self.icons["edit"], compound=tk.LEFT, command=self.edit_selected_item)
        self.context_menu.add_command(label=get_text("context_delete"), image=self.icons["delete"], compound=tk.LEFT, command=self.delete_item)
        self.context_menu.add_separator()
        self.context_menu.add_command(label=get_text("context_add_product"), image=self.icons["add_product"], compound=tk.LEFT, command=self.add_product_to_selected_category)
        self.context_menu.add_command(label=get_text("context_add_variant"), image=self.icons["add_variant"], compound=tk.LEFT, command=self.add_variant_to_selected_product)
        self.context_menu.add_command(label=get_text("context_add_modifier"), image=self.icons["add_modifier"], compound=tk.LEFT, command=self.add_modifier_to_selected_item)

    def show_context_menu(self, event):
        try:
            self.tree.identify_row(event.y) # Identify row under mouse
            self.context_menu.post(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def add_category(self):
        self.display_form(CategoryForm, title_key="dialog_add_category_title")
        self.selected_item = None
        self.selected_item_type = None

    def add_product(self):
        selected_iid = self.tree.selection()
        if not selected_iid:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_category_for_product"))
            return

        item_data = self.tree.item(selected_iid, "values")
        item_id = item_data[0] # The ID of the selected item
        item_level = self.get_item_level(selected_iid)

        if item_level == 0: # Is a category
            category_id = item_id
            category_name_es = self.tree.item(selected_iid, "text") # Get category name from #0 column
            self.display_form(ProductForm, title_key="dialog_add_product_title", initial_data={'category_id': category_id, 'category_name_es': category_name_es})
            self.selected_item = None
            self.selected_item_type = None
        else:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_category_for_product"))

    def add_product_to_selected_category(self):
        selected_iid = self.tree.selection()
        if not selected_iid:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_no_selection"))
            return

        item_level = self.get_item_level(selected_iid)
        if item_level == 0: # It's a category
            item_data = self.tree.item(selected_iid, "values")
            category_id = item_data[0]
            category_name_es = self.tree.item(selected_iid, "text")
            self.display_form(ProductForm, title_key="dialog_add_product_title", initial_data={'category_id': category_id, 'category_name_es': category_name_es})
            self.selected_item = None
            self.selected_item_type = None
        else:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_category_for_product"))


    def add_variant(self):
        selected_iid = self.tree.selection()
        if not selected_iid:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_for_variant"))
            return

        item_data = self.tree.item(selected_iid, "values")
        item_id = item_data[0] # The ID of the selected item
        item_level = self.get_item_level(selected_iid)

        if item_level == 1: # Is a product
            product_id = item_id
            product_name_es = self.tree.item(selected_iid, "text")
            self.display_form(VariantForm, title_key="dialog_add_variant_title", initial_data={'product_id': product_id, 'product_name_es': product_name_es})
            self.selected_item = None
            self.selected_item_type = None
        else:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_for_variant"))

    def add_variant_to_selected_product(self):
        selected_iid = self.tree.selection()
        if not selected_iid:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_no_selection"))
            return

        item_level = self.get_item_level(selected_iid)
        if item_level == 1: # It's a product
            item_data = self.tree.item(selected_iid, "values")
            product_id = item_data[0]
            product_name_es = self.tree.item(selected_iid, "text")
            self.display_form(VariantForm, title_key="dialog_add_variant_title", initial_data={'product_id': product_id, 'product_name_es': product_name_es})
            self.selected_item = None
            self.selected_item_type = None
        else:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_for_variant"))


    def add_modifier(self):
        # By default, add a global modifier, or allow selection
        self.display_form(ModifierForm, title_key="dialog_add_modifier_title")
        self.selected_item = None
        self.selected_item_type = None

    def add_modifier_to_selected_item(self):
        selected_iid = self.tree.selection()
        if not selected_iid:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_no_selection"))
            return

        item_data = self.tree.item(selected_iid, "values")
        item_id = item_data[0]
        item_level = self.get_item_level(selected_iid)

        initial_data = {}
        if item_level == 1: # Product selected
            initial_data['applies_to'] = 'product'
            initial_data['product_id'] = item_id
            initial_data['product_name_es'] = self.tree.item(selected_iid, "text")
        elif item_level == 2: # Variant selected
            initial_data['applies_to'] = 'variant'
            initial_data['variant_id'] = item_id
            initial_data['variant_name_es'] = self.tree.item(selected_iid, "text")
        else:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_or_variant_for_modifier")) # NEW translation key needed
            return

        self.display_form(ModifierForm, title_key="dialog_add_modifier_title", initial_data=initial_data)
        self.selected_item = None
        self.selected_item_type = None


    def edit_selected_item(self):
        if not self.selected_item or not self.selected_item_type:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_no_selection"))
            return

        item_id = self.selected_item
        item_type = self.selected_item_type

        if item_type == "category":
            data = self.db_manager.get_category_by_id(item_id)
            if data:
                self.display_form(CategoryForm, title_key="dialog_edit_category_title", initial_data=data)
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_item_not_found"))
        elif item_type == "product":
            data = self.db_manager.get_product_by_id(item_id)
            if data:
                # Add category info to initial_data for ProductForm
                category_name_es = self.db_manager.get_category_by_id(data['category_id'])['name_es']
                data['category_name_es'] = category_name_es
                self.display_form(ProductForm, title_key="dialog_edit_product_title", initial_data=data)
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_item_not_found"))
        elif item_type == "variant":
            data = self.db_manager.get_variant_by_id(item_id)
            if data:
                # Add product info to initial_data for VariantForm
                product_name_es = self.db_manager.get_product_by_id(data['product_id'])['name_es']
                data['product_name_es'] = product_name_es
                self.display_form(VariantForm, title_key="dialog_edit_variant_title", initial_data=data)
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_item_not_found"))
        elif item_type == "modifier":
            data = self.db_manager.get_modifier_by_id(item_id)
            if data:
                # Add product/variant info if applies_to is not global
                if data['applies_to'] == 'product' and data['product_id']:
                    data['product_name_es'] = self.db_manager.get_product_by_id(data['product_id'])['name_es']
                elif data['applies_to'] == 'variant' and data['variant_id']:
                    data['variant_name_es'] = self.db_manager.get_variant_by_id(data['variant_id'])['name_es']
                self.display_form(ModifierForm, title_key="dialog_edit_modifier_title", initial_data=data)
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_item_not_found"))

    def delete_item(self):
        if not self.selected_item or not self.selected_item_type:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_no_selection"))
            return

        item_id = self.selected_item
        item_type = self.selected_item_type

        if messagebox.askyesno(get_text("confirm_delete_title"), get_text("confirm_delete_message")):
            success = False
            if item_type == "category":
                # Check for associated products
                if self.db_manager.get_products_by_category(item_id):
                    messagebox.showwarning(get_text("msg_warning"), get_text("msg_category_has_products"))
                    return
                success = self.db_manager.delete_category(item_id)
            elif item_type == "product":
                # Check for associated variants
                if self.db_manager.get_variants_by_product(item_id):
                    messagebox.showwarning(get_text("msg_warning"), get_text("msg_product_has_variants"))
                    return
                success = self.db_manager.delete_product(item_id)
            elif item_type == "variant":
                # Check for associated modifiers
                if self.db_manager.get_modifiers_by_variant(item_id):
                    messagebox.showwarning(get_text("msg_warning"), get_text("msg_variant_has_modifiers"))
                    return
                success = self.db_manager.delete_variant(item_id)
            elif item_type == "modifier":
                # Assuming no complex sales associations for now, or handled by DB CASCADE
                success = self.db_manager.delete_modifier(item_id)
                # You might need a check here like msg_modifier_associated_with_sales

            if success:
                messagebox.showinfo(get_text("msg_success"), get_text("msg_item_deleted_successfully"))
                self.load_categories_and_products()
                self.clear_detail_form()
            else:
                messagebox.showerror(get_text("msg_error"), get_text("msg_delete_failed"))

    def display_form(self, form_class, title_key, initial_data=None):
        if self.current_form_frame:
            self.current_form_frame.destroy()

        self.detail_title_label.config(text=get_text(title_key))

        # Pass icons to forms if they need them (e.g., ProductForm for browse button)
        if form_class == ProductForm:
            self.current_form_frame = form_class(self.form_container_frame, self.db_manager, self.icons["browse"])
        else:
            self.current_form_frame = form_class(self.form_container_frame, self.db_manager)

        self.current_form_frame.grid(row=0, column=0, sticky="nsew") # Place form in container

        if initial_data:
            if hasattr(self.current_form_frame, 'load_category_data') and form_class == CategoryForm:
                self.current_form_frame.load_category_data(initial_data)
            elif hasattr(self.current_form_frame, 'load_product_data') and form_class == ProductForm:
                self.current_form_frame.load_product_data(initial_data)
            elif hasattr(self.current_form_frame, 'load_variant_data') and form_class == VariantForm:
                self.current_form_frame.load_variant_data(initial_data)
            elif hasattr(self.current_form_frame, 'load_modifier_data') and form_class == ModifierForm:
                self.current_form_frame.load_modifier_data(initial_data)

    def clear_detail_form(self):
        if self.current_form_frame:
            self.current_form_frame.destroy()
        self.detail_title_label.config(text="")
        self.selected_item = None
        self.selected_item_type = None
        self.tree.selection_remove(self.tree.selection()) # Deselect item in treeview


    def save_item(self):
        if not self.current_form_frame:
            messagebox.showwarning(get_text("msg_warning"), get_text("msg_no_selection"))
            return

        if not hasattr(self.current_form_frame, 'validate_form') or not self.current_form_frame.validate_form():
            return # Validation failed in the form itself

        data = self.current_form_frame.get_data() # Assuming all forms have get_data()

        success = False
        message_key_success = ""
        message_key_error = ""

        if isinstance(self.current_form_frame, CategoryForm):
            if data['id'] is None: # New category
                success = self.db_manager.add_category(data)
                message_key_success = "msg_category_added"
                message_key_error = "msg_error_adding_category"
            else: # Existing category
                success = self.db_manager.update_category(data)
                message_key_success = "msg_category_updated"
                message_key_error = "msg_error_updating_category"
        elif isinstance(self.current_form_frame, ProductForm):
            # ProductForm needs category_id. Ensure it's passed or selected.
            if not data['category_id']:
                messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_category_for_product_save")) # NEW
                return
            if data['id'] is None:
                success = self.db_manager.add_product(data)
                message_key_success = "msg_product_added"
                message_key_error = "msg_error_adding_product"
            else:
                success = self.db_manager.update_product(data)
                message_key_success = "msg_product_updated"
                message_key_error = "msg_error_updating_product"
        elif isinstance(self.current_form_frame, VariantForm):
            if not data['product_id']:
                messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_for_variant_save")) # NEW
                return
            if data['id'] is None:
                success = self.db_manager.add_variant(data)
                message_key_success = "msg_variant_added"
                message_key_error = "msg_error_adding_variant"
            else:
                success = self.db_manager.update_variant(data)
                message_key_success = "msg_variant_updated"
                message_key_error = "msg_error_updating_variant"
        elif isinstance(self.current_form_frame, ModifierForm):
            # Special validation for modifier applies_to
            if data['applies_to'] == 'product' and not data['product_id']:
                messagebox.showwarning(get_text("msg_warning"), get_text("msg_modifier_product_variant_required"))
                return
            if data['applies_to'] == 'variant' and not data['variant_id']:
                messagebox.showwarning(get_text("msg_warning"), get_text("msg_modifier_product_variant_required"))
                return
            if data['applies_to'] == 'global' and (data['product_id'] or data['variant_id']):
                 messagebox.showwarning(get_text("msg_warning"), get_text("msg_global_modifier_no_association"))
                 return

            if data['id'] is None:
                success = self.db_manager.add_modifier(data)
                message_key_success = "msg_modifier_added"
                message_key_error = "msg_error_adding_modifier"
            else:
                success = self.db_manager.update_modifier(data)
                message_key_success = "msg_modifier_updated"
                message_key_error = "msg_error_updating_modifier"

        if success:
            messagebox.showinfo(get_text("msg_success"), get_text(message_key_success))
            self.load_categories_and_products() # Reload treeview
            self.clear_detail_form() # Clear form after successful save
        else:
            messagebox.showerror(get_text("msg_error"), get_text(message_key_error))


    def on_tree_select(self, event):
        selected_iid = self.tree.selection()
        if not selected_iid:
            self.clear_detail_form()
            return

        selected_iid = selected_iid[0] # Get the first selected item
        item_data = self.tree.item(selected_iid, "values")
        item_id = item_data[0] # Assuming ID is the first value in tuple

        parent_iid = self.tree.parent(selected_iid)
        if not parent_iid: # Root item (Category) or Global Modifiers
            if selected_iid == "global_modifiers_root":
                self.clear_detail_form()
                self.selected_item = None
                self.selected_item_type = None
                self.detail_title_label.config(text=get_text("tree_global_modifiers"))
                # You might want to display a list of global modifiers here
                return

            self.selected_item_type = "category"
            self.selected_item = item_id
            data = self.db_manager.get_category_by_id(item_id)
            if data:
                self.display_form(CategoryForm, title_key="dialog_edit_category_title", initial_data=data)
        else: # Child item (Product, Variant, Modifier)
            grandparent_iid = self.tree.parent(parent_iid)
            if not grandparent_iid: # Product or Modifier under Global Modifiers
                if parent_iid == "global_modifiers_root": # Modifier under Global Modifiers
                    self.selected_item_type = "modifier"
                    self.selected_item = item_id
                    data = self.db_manager.get_modifier_by_id(item_id)
                    if data:
                        self.display_form(ModifierForm, title_key="dialog_edit_modifier_title", initial_data=data)
                else: # Product under a Category
                    self.selected_item_type = "product"
                    self.selected_item = item_id
                    data = self.db_manager.get_product_by_id(item_id)
                    if data:
                        category_name_es = self.db_manager.get_category_by_id(data['category_id'])['name_es']
                        data['category_name_es'] = category_name_es
                        self.display_form(ProductForm, title_key="dialog_edit_product_title", initial_data=data)
            else: # Variant or Modifier under Product/Variant
                great_grandparent_iid = self.tree.parent(grandparent_iid)
                if not great_grandparent_iid: # Variant under Product
                    self.selected_item_type = "variant"
                    self.selected_item = item_id
                    data = self.db_manager.get_variant_by_id(item_id)
                    if data:
                        product_name_es = self.db_manager.get_product_by_id(data['product_id'])['name_es']
                        data['product_name_es'] = product_name_es
                        self.display_form(VariantForm, title_key="dialog_edit_variant_title", initial_data=data)
                else: # Modifier under Variant
                    self.selected_item_type = "modifier"
                    self.selected_item = item_id
                    data = self.db_manager.get_modifier_by_id(item_id)
                    if data:
                        variant_name_es = self.db_manager.get_variant_by_id(data['variant_id'])['name_es']
                        data['variant_name_es'] = variant_name_es
                        self.display_form(ModifierForm, title_key="dialog_edit_modifier_title", initial_data=data)


    def get_item_level(self, iid):
        level = 0
        while self.tree.parent(iid):
            iid = self.tree.parent(iid)
            level += 1
        return level

    def load_categories_and_products(self):
        # Clear existing items
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # Insert global modifiers root
        self.tree.insert("", "end", iid="global_modifiers_root", text=get_text("tree_global_modifiers"), open=True,
                         values=("", "", "", "")) # Placeholder values

        # Load Global Modifiers
        global_modifiers = self.db_manager.get_global_modifiers()
        for mod in global_modifiers:
            self.tree.insert("global_modifiers_root", "end", iid=f"modifier_{mod['id']}", text=mod['name_es'], open=False,
                             values=(mod['id'], mod['name_es'], mod['name_en'], f"{mod['price']:.2f}"))

        # Load Categories
        categories = self.db_manager.get_all_categories()
        for cat in categories:
            category_iid = self.tree.insert("", "end", iid=f"category_{cat['id']}", text=cat['name_es'], open=False,
                                            values=(cat['id'], cat['name_es'], cat['name_en'], ""))
            # Load Products for each Category
            products = self.db_manager.get_products_by_category(cat['id'])
            for prod in products:
                product_iid = self.tree.insert(category_iid, "end", iid=f"product_{prod['id']}", text=prod['name_es'], open=False,
                                                values=(prod['id'], prod['name_es'], prod['name_en'], f"{prod['base_price']:.2f}"))
                # Load Variants for each Product
                variants = self.db_manager.get_variants_by_product(prod['id'])
                for var in variants:
                    variant_iid = self.tree.insert(product_iid, "end", iid=f"variant_{var['id']}", text=var['name_es'], open=False,
                                                    values=(var['id'], var['name_es'], var['name_en'], f"{var['price_adjustment']:.2f}"))
                    # Load Modifiers for each Variant
                    modifiers = self.db_manager.get_modifiers_by_variant(var['id'])
                    for mod in modifiers:
                        self.tree.insert(variant_iid, "end", iid=f"modifier_{mod['id']}", text=mod['name_es'], open=False,
                                        values=(mod['id'], mod['name_es'], mod['name_en'], f"{mod['price']:.2f}"))

                # Load Modifiers for each Product
                product_modifiers = self.db_manager.get_modifiers_by_product(prod['id'])
                for mod in product_modifiers:
                    self.tree.insert(product_iid, "end", iid=f"modifier_{mod['id']}", text=mod['name_es'], open=False,
                                    values=(mod['id'], mod['name_es'], mod['name_en'], f"{mod['price']:.2f}"))

        # Expand all categories by default for easier viewing
        for iid in self.tree.get_children(""): # Get top-level items
            self.tree.item(iid, open=True) # Expand them
            # Also expand global modifiers
            if iid == "global_modifiers_root":
                self.tree.item(iid, open=True)