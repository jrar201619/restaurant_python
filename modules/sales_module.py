# modules/sales_module.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk # Asegúrate de tener Pillow instalado
import os
import shutil # Para copiar imágenes

from config.translations import get_text, set_language, current_language
from models import Category, Product, Variant, Modifier, Sale, SaleItem, SaleItemModifier

# Directorio donde se guardarán las imágenes de productos
IMAGE_DIR = "assets/product_images"

class SalesModule(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.current_order_items = [] # Lista para almacenar los ítems del pedido actual
        self.selected_product = None # Almacena el objeto Product seleccionado
        self.selected_variant = None # Almacena el objeto Variant seleccionado
        self.selected_modifiers = {} # {modifier_id: quantity}

        self.create_widgets()
        self.load_categories()
        self.update_order_summary() # Inicializa el resumen del pedido

    def create_widgets(self):
        # Título del módulo
        self.title_label = ttk.Label(self, text=get_text("sales_title"), font=("Arial", 16, "bold"))
        self.title_label.pack(pady=10)

        # Frame principal para la disposición de 3 columnas
        self.main_content_frame = ttk.Frame(self)
        self.main_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Columna 1: Categorías ---
        self.category_frame = ttk.LabelFrame(self.main_content_frame, text=get_text("lbl_category"))
        self.category_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5, expand=True)

        self.category_tree = ttk.Treeview(self.category_frame, columns=("name",), show="headings")
        self.category_tree.heading("name", text=get_text("tree_col_category"))
        self.category_tree.pack(fill=tk.BOTH, expand=True)
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)

        # --- Columna 2: Productos y Detalles (Variantes/Modificadores) ---
        self.product_details_frame = ttk.Frame(self.main_content_frame)
        self.product_details_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5, expand=True)

        # Frame para productos (parte superior de Columna 2)
        self.product_frame = ttk.LabelFrame(self.product_details_frame, text=get_text("tree_col_product"))
        self.product_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        self.product_tree = ttk.Treeview(self.product_frame, columns=("name", "price"), show="headings")
        self.product_tree.heading("name", text=get_text("tree_col_product"))
        self.product_tree.heading("price", text=get_text("tree_col_price"))
        self.product_tree.column("price", width=80, anchor=tk.E)
        self.product_tree.pack(fill=tk.BOTH, expand=True)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)

        # Frame para detalles (variantes y modificadores) (parte inferior de Columna 2)
        self.details_frame = ttk.LabelFrame(self.product_details_frame, text="Detalles del Producto") # Esto también se traducirá
        self.details_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        # Sub-frame para variantes
        self.variant_frame = ttk.LabelFrame(self.details_frame, text=get_text("lbl_variants"))
        self.variant_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.variant_tree = ttk.Treeview(self.variant_frame, columns=("name", "adjustment"), show="headings")
        self.variant_tree.heading("name", text=get_text("tree_col_variant"))
        self.variant_tree.heading("adjustment", text=get_text("lbl_price_adjustment"))
        self.variant_tree.column("adjustment", width=80, anchor=tk.E)
        self.variant_tree.pack(fill=tk.BOTH, expand=True)
        self.variant_tree.bind("<<TreeviewSelect>>", self.on_variant_select)

        # Sub-frame para modificadores
        self.modifier_frame = ttk.LabelFrame(self.details_frame, text=get_text("lbl_modifiers"))
        self.modifier_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.modifier_tree = ttk.Treeview(self.modifier_frame, columns=("name", "price"), show="headings")
        self.modifier_tree.heading("name", text=get_text("tree_col_modifier"))
        self.modifier_tree.heading("price", text=get_text("tree_col_price"))
        self.modifier_tree.column("price", width=80, anchor=tk.E)
        self.modifier_tree.pack(fill=tk.BOTH, expand=True)
        self.modifier_tree.bind("<<TreeviewSelect>>", self.on_modifier_select)


        # Área de información y añadir al pedido
        self.add_to_order_frame = ttk.LabelFrame(self.product_details_frame, text=get_text("dialog_add_to_order_title"))
        self.add_to_order_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.add_to_order_frame, text=get_text("lbl_selected_product")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.lbl_current_product = ttk.Label(self.add_to_order_frame, text="")
        self.lbl_current_product.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.add_to_order_frame, text=get_text("lbl_selected_variant")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.lbl_current_variant = ttk.Label(self.add_to_order_frame, text="")
        self.lbl_current_variant.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(self.add_to_order_frame, text=get_text("lbl_selected_modifiers")).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.lbl_current_modifiers = ttk.Label(self.add_to_order_frame, text="")
        self.lbl_current_modifiers.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(self.add_to_order_frame, text=get_text("lbl_item_quantity")).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.quantity_entry = ttk.Entry(self.add_to_order_frame, width=5)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        self.btn_add_to_order = ttk.Button(self.add_to_order_frame, text=get_text("btn_add_to_order"), command=self.add_item_to_order)
        self.btn_add_to_order.grid(row=4, column=0, columnspan=2, pady=5)


        # --- Columna 3: Resumen del Pedido ---
        self.order_summary_frame = ttk.LabelFrame(self.main_content_frame, text=get_text("lbl_order_summary"))
        self.order_summary_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5, pady=5, expand=True)

        self.order_tree = ttk.Treeview(self.order_summary_frame, columns=("item", "quantity", "price_unit", "price_total"), show="headings")
        self.order_tree.heading("item", text=get_text("tree_col_item"))
        self.order_tree.heading("quantity", text=get_text("tree_col_item_quantity"))
        self.order_tree.heading("price_unit", text=get_text("tree_col_item_price"))
        self.order_tree.heading("price_total", text=get_text("tree_col_item_total"))
        self.order_tree.column("quantity", width=50, anchor=tk.CENTER)
        self.order_tree.column("price_unit", width=80, anchor=tk.E)
        self.order_tree.column("price_total", width=80, anchor=tk.E)
        self.order_tree.pack(fill=tk.BOTH, expand=True)

        self.order_tree.bind("<Delete>", lambda event: self.remove_selected_order_item())
        self.order_tree.bind("<<TreeviewSelect>>", self.on_order_item_select) # Para el botón de eliminar

        self.total_frame = ttk.Frame(self.order_summary_frame)
        self.total_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.total_frame, text=get_text("lbl_total"), font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        self.lbl_total_amount = ttk.Label(self.total_frame, text="0.00", font=("Arial", 12, "bold"))
        self.lbl_total_amount.pack(side=tk.RIGHT, padx=5)

        self.checkout_buttons_frame = ttk.Frame(self.order_summary_frame)
        self.checkout_buttons_frame.pack(fill=tk.X, pady=5)

        self.btn_checkout = ttk.Button(self.checkout_buttons_frame, text=get_text("btn_checkout"), command=self.process_checkout)
        self.btn_checkout.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_clear_order = ttk.Button(self.checkout_buttons_frame, text=get_text("btn_clear_order"), command=self.clear_order)
        self.btn_clear_order.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)
        
        self.btn_remove_item = ttk.Button(self.checkout_buttons_frame, text=get_text("btn_remove_from_order"), command=self.remove_selected_order_item)
        self.btn_remove_item.pack(side=tk.BOTTOM, expand=True, fill=tk.X, padx=2, pady=5)
        self.btn_remove_item.state(['disabled']) # Deshabilitado al inicio


    def load_categories(self):
        self.category_tree.delete(*self.category_tree.get_children())
        categories = Category.get_all()
        for cat in categories:
            self.category_tree.insert("", tk.END, iid=cat.id, values=(cat.get_localized_name(current_language),))

    def on_category_select(self, event):
        selected_item = self.category_tree.focus()
        if selected_item:
            category_id = int(selected_item)
            self.load_products_by_category(category_id)
        else:
            self.clear_products()
            self.clear_details()
            self.clear_selection_labels()

    def load_products_by_category(self, category_id):
        self.clear_products()
        self.clear_details()
        self.clear_selection_labels()
        products = Product.get_products_by_category(category_id)
        for prod in products:
            self.product_tree.insert("", tk.END, iid=prod.id, values=(prod.get_localized_name(current_language), f"{prod.base_price:.2f}"))

    def on_product_select(self, event):
        selected_item = self.product_tree.focus()
        if selected_item:
            product_id = int(selected_item)
            self.selected_product = Product.get_by_id(product_id)
            self.selected_variant = None
            self.selected_modifiers = {}
            
            self.update_selection_labels()
            self.load_product_details(self.selected_product)
        else:
            self.selected_product = None
            self.selected_variant = None
            self.selected_modifiers = {}
            self.clear_details()
            self.clear_selection_labels()

    def load_product_details(self, product):
        self.clear_details()
        if product:
            # Cargar variantes
            variants = Variant.get_variants_by_product(product.id)
            for var in variants:
                self.variant_tree.insert("", tk.END, iid=var.id, values=(var.get_localized_name(current_language), f"{var.price_adjustment:+.2f}")) # + para mostrar signo

            # Cargar modificadores (globales, de producto y de variante)
            # Simplificado: Por ahora cargamos todos los modificadores aplicables al producto.
            # En una app real, podrías filtrar más o tener un sistema de "modificadores por grupo".
            # Aquí, obtenemos los globales y los específicos del producto.
            modifiers = Modifier.get_global_modifiers() + Modifier.get_modifiers_by_product(product.id)
            # Asegúrate de no duplicar si un modificador es global y también se asocia a un producto por error.
            seen_modifier_ids = set()
            for mod in modifiers:
                if mod.id not in seen_modifier_ids:
                    self.modifier_tree.insert("", tk.END, iid=mod.id, values=(mod.get_localized_name(current_language), f"{mod.price:.2f}"))
                    seen_modifier_ids.add(mod.id)
        
        # Resetear las selecciones de variantes y modificadores
        self.selected_variant = None
        self.selected_modifiers = {}
        self.update_selection_labels()


    def on_variant_select(self, event):
        selected_item = self.variant_tree.focus()
        if selected_item:
            variant_id = int(selected_item)
            self.selected_variant = Variant.get_by_id(variant_id)
            # Si seleccionas una variante, deberías también cargar modificadores específicos de esa variante
            # Por ahora, los modificadores ya cargados (globales/de producto) son suficientes,
            # pero aquí podrías añadir lógica para sumar modificadores de variante.
            
            # Limpiar cualquier selección previa de modificadores si la variante cambia
            self.modifier_tree.selection_set([])
            self.selected_modifiers = {} # Resetear los modificadores seleccionados al cambiar de variante
            # Recargar modificadores para incluir los específicos de la variante si aplica
            self.load_product_details(self.selected_product) # Esto recargará todo, incluyendo los modificadores.
                                                            # Considera optimizar si hay muchos.
            
            self.update_selection_labels()
        else:
            self.selected_variant = None
            self.update_selection_labels()

    def on_modifier_select(self, event):
        # Maneja selecciones MÚLTIPLES de modificadores
        selected_items = self.modifier_tree.selection()
        self.selected_modifiers = {} # Resetear para la nueva selección
        
        for item_id in selected_items:
            modifier_id = int(item_id)
            modifier = Modifier.get_by_id(modifier_id)
            if modifier:
                # Permitir al usuario especificar la cantidad de cada modificador
                qty_dialog = simpledialog.askinteger(get_text("lbl_modifier_quantity"), 
                                                     f"{get_text('lbl_quantity')} {modifier.get_localized_name(current_language)}:", 
                                                     parent=self, initialvalue=1, minvalue=1)
                if qty_dialog is not None and qty_dialog > 0:
                    self.selected_modifiers[modifier_id] = qty_dialog
                else:
                    # Si el usuario cancela o introduce 0, deseleccionar el modificador
                    self.modifier_tree.selection_remove(item_id)
        self.update_selection_labels()

    def add_item_to_order(self):
        if not self.selected_product:
            messagebox.showwarning(get_text("msg_error"), get_text("msg_select_product"))
            return

        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                messagebox.showwarning(get_text("msg_error"), get_text("msg_quantity_positive"))
                return
        except ValueError:
            messagebox.showwarning(get_text("msg_error"), get_text("msg_invalid_quantity"))
            return

        # Calcular el precio base del ítem (producto + variante si aplica)
        item_base_price = self.selected_product.base_price
        if self.selected_variant:
            item_base_price += self.selected_variant.price_adjustment

        # Crear un diccionario para el ítem del pedido
        order_item = {
            "product": self.selected_product,
            "variant": self.selected_variant,
            "modifiers": [], # Almacenará {modifier_obj, quantity_selected}
            "quantity": quantity,
            "price_at_sale": item_base_price, # Este será el precio unitario del producto/variante
        }

        # Añadir modificadores seleccionados y ajustar el precio total del ítem
        for mod_id, mod_qty in self.selected_modifiers.items():
            modifier_obj = Modifier.get_by_id(mod_id)
            if modifier_obj:
                order_item["modifiers"].append({"modifier": modifier_obj, "quantity": mod_qty})
                # El precio del modificador se suma al precio_at_sale por cada unidad de modificador
                order_item["price_at_sale"] += (modifier_obj.price * mod_qty)

        self.current_order_items.append(order_item)
        self.update_order_summary()
        self.clear_current_selection() # Limpia la selección después de añadir al pedido

    def update_order_summary(self):
        # Limpiar el Treeview del pedido
        self.order_tree.delete(*self.order_tree.get_children())
        total_amount = 0.0

        for item_data in self.current_order_items:
            product_name = item_data["product"].get_localized_name(current_language)
            variant_name = item_data["variant"].get_localized_name(current_language) if item_data["variant"] else ""

            display_name = product_name
            if variant_name:
                display_name += f" ({variant_name})"

            item_unit_price = item_data["product"].base_price
            if item_data["variant"]:
                item_unit_price += item_data["variant"].price_adjustment

            item_total = (item_unit_price * item_data["quantity"])

            # Insertar el producto/variante principal
            parent_iid = self.order_tree.insert("", tk.END, values=(
                display_name,
                item_data["quantity"],
                f"{item_unit_price:.2f}",
                f"{item_total:.2f}"
            ))

            # Insertar los modificadores como ítems secundarios
            for mod_info in item_data["modifiers"]:
                modifier_obj = mod_info["modifier"]
                mod_qty = mod_info["quantity"]
                mod_price_at_sale = modifier_obj.price # El precio del modificador individual
                mod_total = mod_price_at_sale * mod_qty # El total para este modificador * su cantidad
                
                # Sumar el total de los modificadores al total del item
                item_total += mod_total

                self.order_tree.insert(parent_iid, tk.END, values=(
                    f"  + {modifier_obj.get_localized_name(current_language)}",
                    mod_qty,
                    f"{mod_price_at_sale:.2f}",
                    f"{mod_total:.2f}"
                ))

            # Actualizar el total de la fila principal con los modificadores
            self.order_tree.item(parent_iid, values=(
                display_name,
                item_data["quantity"],
                f"{item_unit_price:.2f}", # Precio unitario del producto/variante sin modificadores
                f"{item_total:.2f}" # Total del item CON modificadores
            ))
            
            total_amount += item_total # Sumar el total de este item (con modificadores) al total general

        self.lbl_total_amount.config(text=f"{total_amount:.2f}")

        # Habilitar/deshabilitar botón de eliminar si hay elementos seleccionados
        if self.order_tree.selection():
            self.btn_remove_item.state(['!disabled'])
        else:
            self.btn_remove_item.state(['disabled'])

    def on_order_item_select(self, event):
        # Este método se llama cuando se selecciona un elemento en el árbol de pedidos
        # Simplemente habilita/deshabilita el botón de eliminar.
        if self.order_tree.selection():
            self.btn_remove_item.state(['!disabled'])
        else:
            self.btn_remove_item.state(['disabled'])

    def remove_selected_order_item(self):
        selected_item_iid = self.order_tree.focus() # Obtiene el IID del elemento seleccionado
        if not selected_item_iid:
            messagebox.showwarning(get_text("msg_error"), get_text("msg_no_selection"))
            return

        # Para poder eliminar un ítem del pedido, debemos tener en cuenta si es un ítem padre o un modificador hijo.
        # Si es un modificador hijo, obtenemos el padre y lo eliminamos junto con el padre.
        # Si es un padre, eliminamos ese padre y sus hijos.

        # Obtener el padre del elemento seleccionado
        parent_iid = self.order_tree.parent(selected_item_iid)

        if parent_iid: # Si tiene un padre, es un modificador o un sub-item de un producto/variante
            item_to_remove_iid = parent_iid # Quitar el item principal
        else: # Si no tiene padre, es un item principal (producto/variante)
            item_to_remove_iid = selected_item_iid
        
        # Obtener el índice del ítem a eliminar en current_order_items
        # El IID de los ítems principales del pedido es el índice en current_order_items
        try:
            item_index = self.order_tree.index(item_to_remove_iid)
            if 0 <= item_index < len(self.current_order_items):
                del self.current_order_items[item_index]
                self.update_order_summary()
            else:
                # Esto no debería ocurrir si la lógica del IID es correcta
                messagebox.showerror(get_text("msg_error"), get_text("msg_item_not_found"))
        except tk.TclError:
            # Esto puede pasar si el IID no existe (ej. ya fue eliminado)
            messagebox.showerror(get_text("msg_error"), get_text("msg_item_not_found"))


    def process_checkout(self):
        if not self.current_order_items:
            messagebox.showwarning(get_text("msg_error"), get_text("msg_no_items_in_order"))
            return

        total_amount = float(self.lbl_total_amount.cget("text"))

        # Crear la venta
        sale = Sale(total_amount=total_amount)
        if not sale.save():
            messagebox.showerror(get_text("msg_error"), get_text("msg_save_failed") + " (Venta)")
            return

        sale_id = sale.id

        # Guardar cada SaleItem y sus SaleItemModifiers
        for item_data in self.current_order_items:
            product_id = item_data["product"].id
            variant_id = item_data["variant"].id if item_data["variant"] else None
            quantity = item_data["quantity"]
            # El price_at_sale en SaleItem es el precio unitario del producto/variante sin modificadores
            # Los modificadores se guardan por separado
            item_base_price = item_data["product"].base_price
            if item_data["variant"]:
                item_base_price += item_data["variant"].price_adjustment

            sale_item = SaleItem(
                sale_id=sale_id,
                product_id=product_id,
                variant_id=variant_id,
                quantity=quantity,
                price_at_sale=item_base_price # Precio base del item (prod+var)
            )
            if not sale_item.save():
                messagebox.showerror(get_text("msg_error"), get_text("msg_save_failed") + f" (Item de venta para {item_data['product'].get_localized_name(current_language)})")
                # Considerar rollback de la venta si un item falla
                return

            sale_item_id = sale_item.id

            # Guardar los modificadores del SaleItem
            for mod_info in item_data["modifiers"]:
                modifier_obj = mod_info["modifier"]
                mod_qty = mod_info["quantity"]
                
                sale_item_modifier = SaleItemModifier(
                    sale_item_id=sale_item_id,
                    modifier_id=modifier_obj.id,
                    quantity=mod_qty,
                    price_at_sale=modifier_obj.price # Precio del modificador en el momento de la venta
                )
                if not sale_item_modifier.save():
                    messagebox.showerror(get_text("msg_error"), get_text("msg_save_failed") + f" (Modificador {modifier_obj.get_localized_name(current_language)})")
                    # Considerar rollback
                    return
        
        messagebox.showinfo(get_text("msg_success"), get_text("msg_sale_successful"))
        self.clear_order() # Limpiar el pedido después de una venta exitosa

    def clear_order(self):
        self.current_order_items = []
        self.update_order_summary()
        self.clear_current_selection()

    def clear_products(self):
        self.product_tree.delete(*self.product_tree.get_children())

    def clear_details(self):
        self.variant_tree.delete(*self.variant_tree.get_children())
        self.modifier_tree.delete(*self.modifier_tree.get_children())
        self.modifier_tree.selection_set([]) # Asegurarse de deseleccionar

    def clear_selection_labels(self):
        self.lbl_current_product.config(text="")
        self.lbl_current_variant.config(text="")
        self.lbl_current_modifiers.config(text="")
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")
        self.selected_product = None
        self.selected_variant = None
        self.selected_modifiers = {}
        # Deseleccionar árboles
        self.product_tree.selection_set([])
        self.variant_tree.selection_set([])
        self.modifier_tree.selection_set([])

    def update_selection_labels(self):
        product_text = self.selected_product.get_localized_name(current_language) if self.selected_product else "N/A"
        variant_text = self.selected_variant.get_localized_name(current_language) if self.selected_variant else "N/A"
        
        modifiers_names = [
            f"{Modifier.get_by_id(mod_id).get_localized_name(current_language)} (x{qty})" 
            for mod_id, qty in self.selected_modifiers.items()
        ]
        modifiers_text = ", ".join(modifiers_names) if modifiers_names else "N/A"

        self.lbl_current_product.config(text=product_text)
        self.lbl_current_variant.config(text=variant_text)
        self.lbl_current_modifiers.config(text=modifiers_text)

    def clear_current_selection(self):
        # Deseleccionar todos los árboles de selección de productos/variantes/modificadores
        self.category_tree.selection_set([])
        self.product_tree.selection_set([])
        self.variant_tree.selection_set([])
        self.modifier_tree.selection_set([])
        
        self.clear_products()
        self.clear_details()
        self.clear_selection_labels()


    def update_language(self):
        """Actualiza el texto de todos los widgets del módulo de ventas al cambiar el idioma."""
        self.title_label.config(text=get_text("sales_title"))
        self.category_frame.config(text=get_text("lbl_category"))
        self.category_tree.heading("name", text=get_text("tree_col_category"))
        
        self.product_frame.config(text=get_text("tree_col_product"))
        self.product_tree.heading("name", text=get_text("tree_col_product"))
        self.product_tree.heading("price", text=get_text("tree_col_price"))

        self.details_frame.config(text="Detalles del Producto") # Esto se traduciría mejor con una clave
        self.variant_frame.config(text=get_text("lbl_variants"))
        self.variant_tree.heading("name", text=get_text("tree_col_variant"))
        self.variant_tree.heading("adjustment", text=get_text("lbl_price_adjustment"))

        self.modifier_frame.config(text=get_text("lbl_modifiers"))
        self.modifier_tree.heading("name", text=get_text("tree_col_modifier"))
        self.modifier_tree.heading("price", text=get_text("tree_col_price"))

        self.add_to_order_frame.config(text=get_text("dialog_add_to_order_title"))
        self.btn_add_to_order.config(text=get_text("btn_add_to_order"))
        self.lbl_current_product.config(text=get_text("lbl_selected_product") + self.lbl_current_product.cget("text").split(':')[-1])
        self.lbl_current_variant.config(text=get_text("lbl_selected_variant") + self.lbl_current_variant.cget("text").split(':')[-1])
        self.lbl_current_modifiers.config(text=get_text("lbl_selected_modifiers") + self.lbl_current_modifiers.cget("text").split(':')[-1])
        ttk.Label(self.add_to_order_frame, text=get_text("lbl_item_quantity")).grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)


        self.order_summary_frame.config(text=get_text("lbl_order_summary"))
        self.order_tree.heading("item", text=get_text("tree_col_item"))
        self.order_tree.heading("quantity", text=get_text("tree_col_item_quantity"))
        self.order_tree.heading("price_unit", text=get_text("tree_col_item_price"))
        self.order_tree.heading("price_total", text=get_text("tree_col_item_total"))
        
        # Actualizar el texto del total (la cantidad ya está en el label, solo el prefijo)
        self.total_frame.winfo_children()[0].config(text=get_text("lbl_total")) # Asumiendo que el label del total es el primer hijo

        self.btn_checkout.config(text=get_text("btn_checkout"))
        self.btn_clear_order.config(text=get_text("btn_clear_order"))
        self.btn_remove_item.config(text=get_text("btn_remove_from_order"))

        # Volver a cargar los datos para que los nombres localizados se actualicen en los Treeviews
        self.load_categories()
        # Si un producto o categoría ya estaba seleccionado, recargarlos para mostrar nombres localizados
        # Esto es más complejo, ya que implicaría recordar la selección actual.
        # Por simplicidad, solo recargamos las categorías.
        # Puedes mejorar esto almacenando los IDs seleccionados antes de recargar y volviéndolos a seleccionar.
        if self.selected_product:
            self.load_products_by_category(self.selected_product.category_id)
            self.product_tree.selection_set(self.selected_product.id) # Re-selecciona el producto
            self.load_product_details(self.selected_product)
            self.update_selection_labels() # Re-renderiza las etiquetas de selección

        self.update_order_summary() # Actualiza los nombres de los ítems en el resumen del pedido