# mi_sistema_ventas/ui/main_window.py

import tkinter as tk
from tkinter import ttk, messagebox

# Importa tus traducciones y la clase ProductManagerUI
from config.translations import get_text, set_language, current_language
from ui.product_manager_ui import ProductManagerUI # Importa la clase de gestión de productos

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(get_text("app_title")) # Título inicial de la ventana
        self.geometry("1024x768") # Tamaño inicial de la ventana
        self.minsize(800, 600) # Tamaño mínimo para la ventana

        self.current_module_frame = None # Para mantener una referencia al módulo actualmente mostrado

        self.create_menu()
        self.create_main_content_area()
        self.update_texts() # Asegura que todos los textos se carguen correctamente al inicio

        # Cargar el módulo de gestión de productos por defecto al iniciar
        self.show_product_manager_module()

    def create_menu(self):
        """Crea la barra de menú de la aplicación."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Menú Idioma
        language_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=get_text("menu_settings"), menu=language_menu) # Usamos "Settings" como base
        
        # Submenú para seleccionar idioma
        sub_language_menu = tk.Menu(language_menu, tearoff=0)
        language_menu.add_cascade(label=get_text("menu_language"), menu=sub_language_menu)
        
        sub_language_menu.add_command(label=get_text("menu_language_es"), command=lambda: self.change_language("es"))
        sub_language_menu.add_command(label=get_text("menu_language_en"), command=lambda: self.change_language("en"))

        # Menú Módulos (Navegación)
        module_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Módulos", menu=module_menu) # Este texto no está traducido en translations, considerarlo
        module_menu.add_command(label=get_text("menu_products"), command=self.show_product_manager_module)
        module_menu.add_command(label=get_text("menu_sales"), command=self.show_sales_module)
        module_menu.add_command(label=get_text("menu_reports"), command=self.show_reports_module)

    def create_main_content_area(self):
        """Crea el área donde se cargarán los diferentes módulos."""
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both")

    def set_main_title(self, title_key):
        """
        Método para que los módulos puedan actualizar el título de la ventana principal.
        Recibe una clave de traducción y la usa para el título.
        """
        self.title(get_text(title_key))


    def change_language(self, lang_code):
        """Cambia el idioma de la aplicación y actualiza la UI."""
        set_language(lang_code)
        self.update_texts()
        # Notifica a la instancia del módulo actual para que actualice sus propios textos
        if self.current_module_frame and hasattr(self.current_module_frame, 'update_texts'):
            self.current_module_frame.update_texts()

    def update_texts(self):
        """Actualiza todos los textos de la ventana principal y sus menús."""
        self.title(get_text("app_title"))

        # Actualiza los textos de los menús
        # Para el menú Settings (Configuración)
        self.winfo_children()[0].entryconfig(0, label=get_text("menu_settings")) # Accede al primer menú
        
        # Para el submenú de Idioma
        settings_menu = self.winfo_children()[0].entrycget(0, "menu") # Obtiene la referencia al menú de Configuración
        settings_menu.entryconfig(0, label=get_text("menu_language")) # Accede al submenú de Idioma
        
        lang_menu = settings_menu.entrycget(0, "menu") # Obtiene la referencia al submenú de Idioma
        lang_menu.entryconfig(0, label=get_text("menu_language_es"))
        lang_menu.entryconfig(1, label=get_text("menu_language_en"))

        # Para el menú Módulos
        self.winfo_children()[0].entryconfig(1, label=get_text("modules_menu_label", default="Módulos")) # Asegúrate de añadir "modules_menu_label" a translations
        module_menu = self.winfo_children()[0].entrycget(1, "menu")
        module_menu.entryconfig(0, label=get_text("menu_products"))
        module_menu.entryconfig(1, label=get_text("menu_sales"))
        module_menu.entryconfig(2, label=get_text("menu_reports"))


    def _clear_main_frame(self):
        """Elimina todos los widgets del área de contenido principal."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_module_frame = None

    def show_product_manager_module(self):
        """Muestra el módulo de gestión de productos."""
        self._clear_main_frame()
        self.current_module_frame = ProductManagerUI(self.main_frame, self)
        self.current_module_frame.pack(expand=True, fill="both")
        self.set_main_title("product_manager_title") # Actualiza el título de la ventana

    def show_sales_module(self):
        """Muestra el módulo de ventas (aún no implementado)."""
        self._clear_main_frame()
        # Aquí iría la inicialización de tu SalesUI
        # self.current_module_frame = SalesUI(self.main_frame, self)
        # self.current_module_frame.pack(expand=True, fill="both")
        # self.set_main_title("sales_title")
        messagebox.showinfo(get_text("app_title"), get_text("msg_not_implemented", default="Módulo de Ventas aún no implementado."))
        self.set_main_title("app_title") # Vuelve al título principal

    def show_reports_module(self):
        """Muestra el módulo de reportes (aún no implementado)."""
        self._clear_main_frame()
        # Aquí iría la inicialización de tu ReportsUI
        # self.current_module_frame = ReportsUI(self.main_frame, self)
        # self.current_module_frame.pack(expand=True, fill="both")
        # self.set_main_title("reports_title")
        messagebox.showinfo(get_text("app_title"), get_text("msg_not_implemented", default="Módulo de Reportes aún no implementado."))
        self.set_main_title("app_title") # Vuelve al título principal