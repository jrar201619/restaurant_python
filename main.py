# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import os
from config.translations import set_language, get_text, TRANSLATIONS
from modules.product_manager_module import ProductManagerModule
from utils.db_manager import DBManager
from utils.helpers import load_icon # Importa la función de ayuda

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(get_text("app_title"))
        self.geometry("1200x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configurar la grid de la ventana principal para que los elementos se expandan
        self.grid_rowconfigure(0, weight=1) # Fila para el main_frame
        self.grid_columnconfigure(0, weight=1) # Columna para el main_frame

        self.style = ttk.Style(self)
        self.load_styles()

        self.db_manager = DBManager("restaurant_data.db")
        self.db_manager.init_db()

        self.current_module_frame = None
        self.icons = {} # Diccionario para guardar referencias a los iconos

        self.load_all_icons() # Cargar todos los iconos al inicio

        self.create_menu()
        self.create_main_frame()
        self.show_module("products") # Muestra el módulo de productos por defecto

    def load_all_icons(self):
        """Loads all necessary icons for the application."""
        icon_size = (24, 24) # Define un tamaño estándar para los iconos del menú

        self.icons["products"] = load_icon("products.png", icon_size)
        self.icons["sales"] = load_icon("sales.png", icon_size)
        self.icons["reports"] = load_icon("reports.png", icon_size)
        self.icons["settings"] = load_icon("settings.png", icon_size)
        self.icons["add_category"] = load_icon("add_category.png", icon_size)
        self.icons["add_product"] = load_icon("add_product.png", icon_size)
        self.icons["add_variant"] = load_icon("add_variant.png", icon_size)
        self.icons["add_modifier"] = load_icon("add_modifier.png", icon_size)
        self.icons["save"] = load_icon("save.png", icon_size)
        self.icons["delete"] = load_icon("delete.png", icon_size)
        self.icons["clear"] = load_icon("clear.png", icon_size)
        self.icons["edit"] = load_icon("edit.png", icon_size)
        self.icons["browse"] = load_icon("browse.png", icon_size)


    def load_styles(self):
        # Configuración de estilo global
        self.style.theme_use("clam") # Un tema moderno de ttk

        self.style.configure("TFrame", background="#f8f8f8")
        self.style.configure("TLabel", font=('Arial', 10), background="#f8f8f8")
        self.style.configure("TButton", font=('Arial', 10, 'bold'), padding=6, background="#e0e0e0", foreground="#333333")
        self.style.map("TButton",
                       background=[('active', '#c0c0c0'), ('pressed', '#a0a0a0')],
                       foreground=[('active', '#000000')])
        self.style.configure("TEntry", padding=5, font=('Arial', 10))
        self.style.configure("TText", font=('Arial', 10))
        self.style.configure("TCombobox", padding=5, font=('Arial', 10))
        self.style.configure("TCheckbutton", background="#f8f8f8", font=('Arial', 10))

        # Estilo para Treeview
        self.style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background="#e9e9e9", foreground="#333333")
        self.style.configure("Treeview", rowheight=25, font=('Arial', 9), background="#ffffff", fieldbackground="#ffffff", foreground="#333333")
        self.style.map('Treeview',
                       background=[('selected', '#3f51b5')], # Color azul para selección
                       foreground=[('selected', 'white')])

        # Estilo para PanedWindow (divisor)
        self.style.configure("TPanedwindow", background="#e0e0e0")
        self.style.configure("Panedwindow", background="#e0e0e0") # Para el borde del divisor


    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        modules_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label=get_text("modules_menu_label"), menu=modules_menu)

        # Añadir botones con iconos al menú
        modules_menu.add_command(label=get_text("menu_products"), image=self.icons["products"], compound=tk.LEFT, command=lambda: self.show_module("products"))
        modules_menu.add_command(label=get_text("menu_sales"), image=self.icons["sales"], compound=tk.LEFT, command=lambda: self.show_module("sales"))
        modules_menu.add_command(label=get_text("menu_reports"), image=self.icons["reports"], compound=tk.LEFT, command=lambda: self.show_module("reports"))
        modules_menu.add_command(label=get_text("menu_settings"), image=self.icons["settings"], compound=tk.LEFT, command=lambda: self.show_module("settings"))

        language_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label=get_text("menu_language"), menu=language_menu)
        language_menu.add_command(label=get_text("menu_language_es"), command=lambda: self.set_app_language("es"))
        language_menu.add_command(label=get_text("menu_language_en"), command=lambda: self.set_app_language("en"))

        menu_bar.add_command(label=get_text("menu_logout"), command=self.on_closing) # Placeholder for logout


    def create_main_frame(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def show_module(self, module_name):
        if self.current_module_frame:
            self.current_module_frame.destroy()

        if module_name == "products":
            self.current_module_frame = ProductManagerModule(self.main_frame, self.db_manager, self.icons)
        elif module_name == "sales":
            # self.current_module_frame = SalesModule(self.main_frame, self.db_manager)
            self.current_module_frame = ttk.Label(self.main_frame, text=get_text("msg_not_implemented") + " " + get_text("sales_title"), anchor="center")
        elif module_name == "reports":
            # self.current_module_frame = ReportsModule(self.main_frame, self.db_manager)
            self.current_module_frame = ttk.Label(self.main_frame, text=get_text("msg_not_implemented") + " " + get_text("reports_title"), anchor="center")
        elif module_name == "settings":
            # self.current_module_frame = SettingsModule(self.main_frame, self.db_manager)
            self.current_module_frame = ttk.Label(self.main_frame, text=get_text("msg_not_implemented") + " " + get_text("settings_title"), anchor="center")

        if self.current_module_frame:
            self.current_module_frame.grid(row=0, column=0, sticky="nsew")

    def set_app_language(self, lang_code):
        set_language(lang_code)
        self.title(get_text("app_title"))
        self.create_menu() # Recrear el menú para actualizar las etiquetas
        # Aquí también deberías recargar los módulos activos si tienen texto interno
        if self.current_module_frame:
            # Una forma simple es recrear el módulo actual
            # Una forma más avanzada sería que el módulo tenga un método .update_language()
            current_module_name = ""
            if isinstance(self.current_module_frame, ProductManagerModule):
                current_module_name = "products"
            # ... (para otros módulos)
            if current_module_name:
                self.show_module(current_module_name)
            else: # Fallback for placeholder modules
                 messagebox.showinfo(get_text("msg_success"), get_text("msg_not_implemented")) # Just a dummy update

    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir?"):
            self.db_manager.close_connection()
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()