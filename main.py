# main.py

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk # Asegúrate de tener Pillow instalado (pip install Pillow)
import os

# Importar las funciones de la base de datos
from database import create_tables, get_db_connection, close_db_connection

# Importar las configuraciones de idioma
from config.translations import get_text, set_language, current_language

# Importar los módulos de la aplicación
from modules.product_manager import ProductManagerModule # Asegúrate de que este existe
from modules.sales_module import SalesModule # Asegúrate de que este existe
from modules.reports_module import ReportsModule # Asegúrate de que este existe
from modules.settings_module import SettingsModule # Asegúrate de que este existe

class SalesApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(get_text("app_title"))
        self.geometry("1200x800")
        self.current_module_frame = None
        self.user_role = "admin" # Temporal para pruebas, luego se establecerá al iniciar sesión

        self.create_main_frame()
        self.create_menu_bar()
        self.load_module("products") # Carga el módulo de productos por defecto

        # Bind the window close event to close the database connection
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_main_frame(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def create_menu_bar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_file"), menu=file_menu)
        file_menu.add_command(label=get_text("menu_exit"), command=self.on_closing)

        # Menú Módulos
        modules_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_modules"), menu=modules_menu)
        modules_menu.add_command(label=get_text("menu_products"), command=lambda: self.load_module("products"))
        modules_menu.add_command(label=get_text("menu_sales"), command=lambda: self.load_module("sales"))
        modules_menu.add_command(label=get_text("menu_reports"), command=lambda: self.load_module("reports"))

        # Menú Configuración
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_settings"), menu=settings_menu)
        settings_menu.add_command(label=get_text("menu_language"), command=self.show_language_selection)
        settings_menu.add_command(label=get_text("menu_users"), command=lambda: self.load_module("users")) # Nuevo módulo de usuarios

    def load_module(self, module_name):
        # Destruye el módulo actual si existe
        if self.current_module_frame:
            self.current_module_frame.destroy()
            self.current_module_frame = None

        if module_name == "products":
            self.current_module_frame = ProductManagerModule(self.main_frame)
        elif module_name == "sales":
            self.current_module_frame = SalesModule(self.main_frame)
        elif module_name == "reports":
            self.current_module_frame = ReportsModule(self.main_frame)
        elif module_name == "users":
            # Asegúrate de tener un UserManagementModule en modules/user_management.py
            # from modules.user_management import UserManagementModule
            # self.current_module_frame = UserManagementModule(self.main_frame)
            messagebox.showinfo(get_text("msg_info"), get_text("msg_module_under_construction"))
            return # Regresa si el módulo no está implementado
        else:
            messagebox.showerror(get_text("msg_error"), get_text("msg_module_not_found"))
            return

        self.current_module_frame.pack(fill=tk.BOTH, expand=True)
        # Actualiza el idioma si el módulo tiene el método update_language
        if hasattr(self.current_module_frame, 'update_language'):
            self.current_module_frame.update_language()

    def show_language_selection(self):
        # Implementa aquí la lógica para seleccionar el idioma
        # Esto podría ser un diálogo simple o una sección en el módulo de configuración
        response = messagebox.askyesno(
            get_text("language_change_title"),
            get_text("language_change_prompt")
        )
        if response:
            if current_language == "es":
                set_language("en")
            else:
                set_language("es")
            self.update_ui_language()

    def update_ui_language(self):
        self.title(get_text("app_title"))
        # Actualiza todos los elementos del menú
        self.nametowidget(self.winfo_menu()).entryconfig(0, label=get_text("menu_file"))
        self.nametowidget(self.winfo_menu()).entryconfig(1, label=get_text("menu_modules"))
        self.nametowidget(self.winfo_menu()).entryconfig(2, label=get_text("menu_settings"))

        # Actualiza los submenús
        file_menu = self.nametowidget(self.winfo_menu()).winfo_children()[0]
        file_menu.entryconfig(0, label=get_text("menu_exit"))

        modules_menu = self.nametowidget(self.winfo_menu()).winfo_children()[1]
        modules_menu.entryconfig(0, label=get_text("menu_products"))
        modules_menu.entryconfig(1, label=get_text("menu_sales"))
        modules_menu.entryconfig(2, label=get_text("menu_reports"))

        settings_menu = self.nametowidget(self.winfo_menu()).winfo_children()[2]
        settings_menu.entryconfig(0, label=get_text("menu_language"))
        settings_menu.entryconfig(1, label=get_text("menu_users"))

        # Si hay un módulo cargado, pídele que actualice su propio idioma
        if self.current_module_frame and hasattr(self.current_module_frame, 'update_language'):
            self.current_module_frame.update_language()

    def on_closing(self):
        """Called when the window is closed."""
        if messagebox.askokcancel(get_text("exit_confirm_title"), get_text("exit_confirm_message")):
            close_db_connection() # Close the database connection
            self.destroy()

if __name__ == "__main__":
    create_tables() # Initialize and create tables (and establish connection)
    app = SalesApp()
    app.mainloop()