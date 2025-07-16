# views/product_dialogs.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from config.translations import get_text
from utils.helpers import load_image_for_preview, copy_image_to_assets, load_icon

# --- Base Form Class (Optional but Recommended for shared logic) ---
class BaseForm(ttk.Frame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, padding="10")
        self.db_manager = db_manager
        self.item_id = None # Will store the ID of the item being edited

        # Configure columns for consistent layout
        self.columnconfigure(0, weight=0) # Labels column
        self.columnconfigure(1, weight=1) # Entry/Widget column

    def get_data(self):
        """Returns a dictionary of the form's data."""
        raise NotImplementedError("Subclasses must implement get_data()")

    def load_data(self, data):
        """Loads data into the form fields."""
        raise NotImplementedError("Subclasses must implement load_data()")

    def clear_form(self):
        """Clears all form fields."""
        raise NotImplementedError("Subclasses must implement clear_form()")

    def validate_form(self):
        """Validates the form inputs. Returns True if valid, False otherwise."""
        return True # Default to true, override in subclasses

# --- CategoryForm ---
class CategoryForm(BaseForm):
    def __init__(self, parent, db_manager):
        super().__init__(parent, db_manager)

        row_idx = 0

        ttk.Label(self, text=get_text("lbl_name_es")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_es_entry = ttk.Entry(self)
        self.name_es_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_name_en")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_en_entry = ttk.Entry(self)
        self.name_en_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_description_es")).grid(row=row_idx, column=0, sticky="nw", padx=5, pady=5)
        self.description_es_text = tk.Text(self, height=4, width=40) # Specify width for initial size
        self.description_es_text.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_description_en")).grid(row=row_idx, column=0, sticky="nw", padx=5, pady=5)
        self.description_en_text = tk.Text(self, height=4, width=40)
        self.description_en_text.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        self.grid_rowconfigure(row_idx, weight=1) # Pushes content to top

    def load_data(self, category_data):
        self.item_id = category_data["id"]
        self.name_es_entry.delete(0, tk.END)
        self.name_es_entry.insert(0, category_data["name_es"])
        self.name_en_entry.delete(0, tk.END)
        self.name_en_entry.insert(0, category_data["name_en"])
        self.description_es_text.delete(1.0, tk.END)
        self.description_es_text.insert(1.0, category_data["description_es"])
        self.description_en_text.delete(1.0, tk.END)
        self.description_en_text.insert(1.0, category_data["description_en"])

    def get_data(self):
        return {
            "id": self.item_id,
            "name_es": self.name_es_entry.get().strip(),
            "name_en": self.name_en_entry.get().strip(),
            "description_es": self.description_es_text.get(1.0, tk.END).strip(),
            "description_en": self.description_en_text.get(1.0, tk.END).strip(),
        }

    def clear_form(self):
        self.item_id = None
        self.name_es_entry.delete(0, tk.END)
        self.name_en_entry.delete(0, tk.END)
        self.description_es_text.delete(1.0, tk.END)
        self.description_en_text.delete(1.0, tk.END)

    def validate_form(self):
        if not self.name_es_entry.get().strip() or not self.name_en_entry.get().strip():
            messagebox.showerror(get_text("msg_error"), get_text("msg_fields_required"))
            return False
        return True

# --- ProductForm ---
class ProductForm(BaseForm):
    def __init__(self, parent, db_manager, browse_icon=None): # Pass browse_icon
        super().__init__(parent, db_manager)
        self.category_id = None
        self.image_filename = None
        self.photo_image = None # To hold reference to the image for Tkinter

        row_idx = 0

        # Category (Read-only or Combobox for selection)
        ttk.Label(self, text=get_text("lbl_category")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.category_name_label = ttk.Label(self, text="") # Displays selected category name
        self.category_name_label.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        # You might want a button to select/change category
        # Or a Combobox to select from all categories
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_name_es")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_es_entry = ttk.Entry(self)
        self.name_es_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_name_en")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_en_entry = ttk.Entry(self)
        self.name_en_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_description_es")).grid(row=row_idx, column=0, sticky="nw", padx=5, pady=5)
        self.description_es_text = tk.Text(self, height=4, width=40)
        self.description_es_text.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_description_en")).grid(row=row_idx, column=0, sticky="nw", padx=5, pady=5)
        self.description_en_text = tk.Text(self, height=4, width=40)
        self.description_en_text.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_base_price")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.base_price_entry = ttk.Entry(self)
        self.base_price_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        self.is_available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text=get_text("lbl_is_available"), variable=self.is_available_var).grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        row_idx += 1

        # Image Section
        image_select_frame = ttk.Frame(self)
        image_select_frame.grid(row=row_idx, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        image_select_frame.columnconfigure(1, weight=1) # Entry for path expands

        ttk.Label(image_select_frame, text=get_text("lbl_image_path")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.image_path_entry = ttk.Entry(image_select_frame, state="readonly")
        self.image_path_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Use the passed browse_icon
        self.browse_button = ttk.Button(image_select_frame, text=get_text("btn_select_image"), image=browse_icon, compound=tk.LEFT, command=self.select_image)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)
        row_idx += 1

        self.image_preview_frame = ttk.Frame(self, relief="solid", borderwidth=1)
        self.image_preview_frame.grid(row=row_idx, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.image_preview_frame.grid_rowconfigure(0, weight=1)
        self.image_preview_frame.grid_columnconfigure(0, weight=1)

        self.image_preview_label = ttk.Label(self.image_preview_frame, text=get_text("no_image_preview"), anchor="center")
        self.image_preview_label.grid(row=0, column=0, sticky="nsew")
        row_idx += 1

        self.grid_rowconfigure(row_idx, weight=1) # Pushes content to top

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title=get_text("dialog_select_image"),
            filetypes=[(get_text("image_files"), "*.png *.jpg *.jpeg *.gif"),
                       (get_text("all_files"), "*.*")]
        )
        if file_path:
            # Copy image to assets and get relative path
            relative_path = copy_image_to_assets(file_path, "assets/images/products")
            if relative_path:
                self.image_filename = relative_path
                self.image_path_entry.config(state="normal")
                self.image_path_entry.delete(0, tk.END)
                self.image_path_entry.insert(0, self.image_filename)
                self.image_path_entry.config(state="readonly")
                self.update_image_preview(self.image_filename)
            else:
                self.image_filename = None # Clear if copy failed

    def update_image_preview(self, image_path):
        self.photo_image = load_image_for_preview(image_path)
        if self.photo_image:
            self.image_preview_label.config(image=self.photo_image, text="")
        else:
            self.image_preview_label.config(image="", text=get_text("no_image_preview"))


    def load_data(self, product_data):
        self.item_id = product_data["id"]
        self.category_id = product_data["category_id"]
        self.category_name_label.config(text=product_data.get("category_name_es", get_text("msg_category_not_found")))

        self.name_es_entry.delete(0, tk.END)
        self.name_es_entry.insert(0, product_data["name_es"])
        self.name_en_entry.delete(0, tk.END)
        self.name_en_entry.insert(0, product_data["name_en"])
        self.description_es_text.delete(1.0, tk.END)
        self.description_es_text.insert(1.0, product_data["description_es"])
        self.description_en_text.delete(1.0, tk.END)
        self.description_en_text.insert(1.0, product_data["description_en"])
        self.base_price_entry.delete(0, tk.END)
        self.base_price_entry.insert(0, str(product_data["base_price"]))
        self.is_available_var.set(bool(product_data["is_available"]))

        self.image_filename = product_data["image_path"]
        self.image_path_entry.config(state="normal")
        self.image_path_entry.delete(0, tk.END)
        self.image_path_entry.insert(0, self.image_filename if self.image_filename else "")
        self.image_path_entry.config(state="readonly")
        self.update_image_preview(os.path.join("assets", self.image_filename) if self.image_filename else None) # Assuming image_path is relative to assets

    def get_data(self):
        try:
            base_price = float(self.base_price_entry.get())
            if base_price < 0:
                messagebox.showerror(get_text("msg_error"), get_text("msg_price_positive"))
                return None
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price"))
            return None

        return {
            "id": self.item_id,
            "category_id": self.category_id, # This must be set from selection logic in ProductManager
            "name_es": self.name_es_entry.get().strip(),
            "name_en": self.name_en_entry.get().strip(),
            "description_es": self.description_es_text.get(1.0, tk.END).strip(),
            "description_en": self.description_en_text.get(1.0, tk.END).strip(),
            "base_price": base_price,
            "image_path": self.image_filename,
            "is_available": self.is_available_var.get(),
        }

    def clear_form(self):
        self.item_id = None
        self.category_id = None
        self.category_name_label.config(text="")
        self.name_es_entry.delete(0, tk.END)
        self.name_en_entry.delete(0, tk.END)
        self.description_es_text.delete(1.0, tk.END)
        self.description_en_text.delete(1.0, tk.END)
        self.base_price_entry.delete(0, tk.END)
        self.is_available_var.set(True)
        self.image_filename = None
        self.image_path_entry.config(state="normal")
        self.image_path_entry.delete(0, tk.END)
        self.image_path_entry.config(state="readonly")
        self.image_preview_label.config(image="", text=get_text("no_image_preview"))
        self.photo_image = None

    def validate_form(self):
        if not self.name_es_entry.get().strip() or not self.name_en_entry.get().strip():
            messagebox.showerror(get_text("msg_error"), get_text("msg_fields_required"))
            return False
        try:
            float(self.base_price_entry.get())
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price"))
            return False
        # category_id must be set by the calling module before saving new product
        if not self.category_id: # For new products, category must be known
             messagebox.showerror(get_text("msg_error"), get_text("msg_select_category_for_product_save"))
             return False
        return True

# --- VariantForm ---
class VariantForm(BaseForm):
    def __init__(self, parent, db_manager):
        super().__init__(parent, db_manager)
        self.product_id = None

        row_idx = 0

        ttk.Label(self, text=get_text("lbl_product_name")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.product_name_label = ttk.Label(self, text="")
        self.product_name_label.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_variant_name")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_es_entry = ttk.Entry(self)
        self.name_es_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_name_en")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_en_entry = ttk.Entry(self)
        self.name_en_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_price_adjustment")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.price_adjustment_entry = ttk.Entry(self)
        self.price_adjustment_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        self.grid_rowconfigure(row_idx, weight=1)

    def load_data(self, variant_data):
        self.item_id = variant_data["id"]
        self.product_id = variant_data["product_id"]
        self.product_name_label.config(text=variant_data.get("product_name_es", get_text("msg_item_not_found")))

        self.name_es_entry.delete(0, tk.END)
        self.name_es_entry.insert(0, variant_data["name_es"])
        self.name_en_entry.delete(0, tk.END)
        self.name_en_entry.insert(0, variant_data["name_en"])
        self.price_adjustment_entry.delete(0, tk.END)
        self.price_adjustment_entry.insert(0, str(variant_data["price_adjustment"]))

    def get_data(self):
        try:
            price_adjustment = float(self.price_adjustment_entry.get())
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price_adjustment"))
            return None

        return {
            "id": self.item_id,
            "product_id": self.product_id,
            "name_es": self.name_es_entry.get().strip(),
            "name_en": self.name_en_entry.get().strip(),
            "price_adjustment": price_adjustment,
        }

    def clear_form(self):
        self.item_id = None
        self.product_id = None
        self.product_name_label.config(text="")
        self.name_es_entry.delete(0, tk.END)
        self.name_en_entry.delete(0, tk.END)
        self.price_adjustment_entry.delete(0, tk.END)

    def validate_form(self):
        if not self.name_es_entry.get().strip() or not self.name_en_entry.get().strip():
            messagebox.showerror(get_text("msg_error"), get_text("msg_fields_required"))
            return False
        try:
            float(self.price_adjustment_entry.get())
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price_adjustment"))
            return False
        if not self.product_id:
             messagebox.showerror(get_text("msg_error"), get_text("msg_select_product_for_variant_save"))
             return False
        return True

# --- ModifierForm ---
class ModifierForm(BaseForm):
    def __init__(self, parent, db_manager):
        super().__init__(parent, db_manager)
        self.product_id = None
        self.variant_id = None

        row_idx = 0

        ttk.Label(self, text=get_text("lbl_modifier_name")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_es_entry = ttk.Entry(self)
        self.name_es_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_name_en")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.name_en_entry = ttk.Entry(self)
        self.name_en_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_modifier_price")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.price_entry = ttk.Entry(self)
        self.price_entry.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        row_idx += 1

        ttk.Label(self, text=get_text("lbl_modifier_applies_to")).grid(row=row_idx, column=0, sticky="w", padx=5, pady=5)
        self.applies_to_var = tk.StringVar(value="global")
        self.applies_to_combobox = ttk.Combobox(self, textvariable=self.applies_to_var,
                                                values=["global", "product", "variant"], state="readonly")
        self.applies_to_combobox.grid(row=row_idx, column=1, sticky="ew", padx=5, pady=5)
        self.applies_to_combobox.bind("<<ComboboxSelected>>", self.on_applies_to_change)
        row_idx += 1

        # Product selection widgets (initially hidden)
        self.product_label = ttk.Label(self, text=get_text("lbl_product_selection"))
        self.product_combobox = ttk.Combobox(self, state="readonly")
        self.product_combobox.bind("<<ComboboxSelected>>", self.on_product_select_for_modifier)
        self.product_combobox_data = {} # To map display name to ID

        # Variant selection widgets (initially hidden)
        self.variant_label = ttk.Label(self, text=get_text("lbl_variant_selection"))
        self.variant_combobox = ttk.Combobox(self, state="readonly")
        self.variant_combobox_data = {} # To map display name to ID

        # Initial call to set visibility
        self.on_applies_to_change()
        self.grid_rowconfigure(row_idx, weight=1)


    def on_applies_to_change(self, event=None):
        selected_option = self.applies_to_var.get()
        current_row = 4 # Start placing after initial fields

        # Hide product and variant widgets
        self.product_label.grid_forget()
        self.product_combobox.grid_forget()
        self.variant_label.grid_forget()
        self.variant_combobox.grid_forget()

        if selected_option == "product":
            self.product_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
            self.product_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
            self.load_products_for_combobox()
            current_row += 1
        elif selected_option == "variant":
            self.product_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
            self.product_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
            self.load_products_for_combobox() # Load products first
            current_row += 1

            self.variant_label.grid(row=current_row, column=0, sticky="w", padx=5, pady=5)
            self.variant_combobox.grid(row=current_row, column=1, sticky="ew", padx=5, pady=5)
            # Variants will be loaded after product selection
            current_row += 1

        self.grid_rowconfigure(current_row, weight=1) # Ensure spacing at the bottom

    def load_products_for_combobox(self):
        products = self.db_manager.get_all_products()
        product_names = []
        self.product_combobox_data = {"": None} # Add empty option
        for p in products:
            display_name = f"{p['name_es']} ({p['base_price']:.2f})"
            product_names.append(display_name)
            self.product_combobox_data[display_name] = p['id']
        self.product_combobox['values'] = sorted(product_names)
        self.product_combobox.set("") # Clear selection

        # Clear variant combo as product changes
        self.variant_combobox.set("")
        self.variant_combobox['values'] = []
        self.variant_combobox_data = {"": None}
        self.product_id = None
        self.variant_id = None


    def on_product_select_for_modifier(self, event=None):
        selected_product_name = self.product_combobox.get()
        self.product_id = self.product_combobox_data.get(selected_product_name)

        # Clear previous variant selection and data
        self.variant_combobox.set("")
        self.variant_combobox['values'] = []
        self.variant_combobox_data = {"": None}
        self.variant_id = None

        if self.applies_to_var.get() == "variant" and self.product_id:
            variants = self.db_manager.get_variants_by_product(self.product_id)
            variant_names = []
            for v in variants:
                display_name = f"{v['name_es']} ({v['price_adjustment']:.2f})"
                variant_names.append(display_name)
                self.variant_combobox_data[display_name] = v['id']
            self.variant_combobox['values'] = sorted(variant_names)

    def load_data(self, modifier_data):
        self.item_id = modifier_data["id"]
        self.name_es_entry.delete(0, tk.END)
        self.name_es_entry.insert(0, modifier_data["name_es"])
        self.name_en_entry.delete(0, tk.END)
        self.name_en_entry.insert(0, modifier_data["name_en"])
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, str(modifier_data["price"]))
        self.applies_to_var.set(modifier_data["applies_to"])
        self.on_applies_to_change() # Update UI based on applies_to

        if modifier_data["applies_to"] == "product":
            self.product_id = modifier_data["product_id"]
            if self.product_id:
                product_data = self.db_manager.get_product_by_id(self.product_id)
                if product_data:
                    display_name = f"{product_data['name_es']} ({product_data['base_price']:.2f})"
                    self.product_combobox.set(display_name)
                    # Ensure product_combobox_data is populated
                    self.load_products_for_combobox() # Reload to ensure data is there
                    self.product_combobox.set(display_name) # Set again after reload
        elif modifier_data["applies_to"] == "variant":
            self.variant_id = modifier_data["variant_id"]
            if self.variant_id:
                variant_data = self.db_manager.get_variant_by_id(self.variant_id)
                if variant_data:
                    # Need product info to set product combobox first
                    product_data = self.db_manager.get_product_by_id(variant_data['product_id'])
                    if product_data:
                        product_display_name = f"{product_data['name_es']} ({product_data['base_price']:.2f})"
                        self.product_combobox.set(product_display_name)
                        self.load_products_for_combobox() # Reload products
                        self.product_combobox.set(product_display_name) # Set product
                        self.on_product_select_for_modifier() # This will load variants

                    variant_display_name = f"{variant_data['name_es']} ({variant_data['price_adjustment']:.2f})"
                    self.variant_combobox.set(variant_display_name)
                    # Ensure variant_combobox_data is populated
                    if product_data: # If product was found and set
                         self.on_product_select_for_modifier() # Recarga para asegurar que las variantes están en la lista
                         self.variant_combobox.set(variant_display_name) # Set variant again

    def get_data(self):
        try:
            price = float(self.price_entry.get())
            if price < 0:
                messagebox.showerror(get_text("msg_error"), get_text("msg_price_positive"))
                return None
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price"))
            return None

        applies_to = self.applies_to_var.get()
        product_id = self.product_id
        variant_id = self.variant_id

        # Update product_id/variant_id based on current combobox selection for new modifiers or re-saving
        if applies_to == 'product':
            selected_product_name = self.product_combobox.get()
            product_id = self.product_combobox_data.get(selected_product_name)
            variant_id = None # Ensure variant_id is None if applies_to product
        elif applies_to == 'variant':
            selected_variant_name = self.variant_combobox.get()
            variant_id = self.variant_combobox_data.get(selected_variant_name)
            # product_id is already set by on_product_select_for_modifier
        elif applies_to == 'global':
            product_id = None
            variant_id = None

        return {
            "id": self.item_id,
            "name_es": self.name_es_entry.get().strip(),
            "name_en": self.name_en_entry.get().strip(),
            "price": price,
            "applies_to": applies_to,
            "product_id": product_id,
            "variant_id": variant_id,
        }

    def clear_form(self):
        self.item_id = None
        self.product_id = None
        self.variant_id = None
        self.name_es_entry.delete(0, tk.END)
        self.name_en_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.applies_to_var.set("global")
        self.on_applies_to_change()
        self.product_combobox.set("")
        self.variant_combobox.set("")

    def validate_form(self):
        if not self.name_es_entry.get().strip() or not self.name_en_entry.get().strip():
            messagebox.showerror(get_text("msg_error"), get_text("msg_fields_required"))
            return False
        try:
            price = float(self.price_entry.get())
            if price < 0:
                messagebox.showerror(get_text("msg_error"), get_text("msg_price_positive"))
                return False
        except ValueError:
            messagebox.showerror(get_text("msg_error"), get_text("msg_invalid_price"))
            return False

        applies_to = self.applies_to_var.get()
        if applies_to == "product":
            selected_product_name = self.product_combobox.get()
            if not selected_product_name or selected_product_name not in self.product_combobox_data or self.product_combobox_data[selected_product_name] is None:
                messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_for_modifier"))
                return False
        elif applies_to == "variant":
            selected_variant_name = self.variant_combobox.get()
            if not selected_variant_name or selected_variant_name not in self.variant_combobox_data or self.variant_combobox_data[selected_variant_name] is None:
                messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_variant_for_modifier"))
                return False
            # Also ensure product is selected if variant is selected
            selected_product_name = self.product_combobox.get()
            if not selected_product_name or selected_product_name not in self.product_combobox_data or self.product_combobox_data[selected_product_name] is None:
                messagebox.showwarning(get_text("msg_warning"), get_text("msg_select_product_for_modifier")) # Need to select product first
                return False

        return True