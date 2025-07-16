# config/translations.py

# Default language setting. This can be changed dynamically by the application.
current_language = "es" # Can be "es" or "en"

# Dictionary to hold all translated strings
# Structure: {language_code: {key: value}}
TRANSLATIONS = {
    "es": {
        # General UI Elements and Actions
        "app_title": "Sistema de Gestión de Ventas",
        "btn_save": "Guardar",
        "btn_add": "Añadir",
        "btn_edit": "Editar",
        "btn_delete": "Eliminar",
        "btn_cancel": "Cancelar",
        "btn_close": "Cerrar",
        "btn_select_image": "Seleccionar Imagen",
        "lbl_name": "Nombre:",
        "lbl_description": "Descripción:",
        "lbl_price": "Precio:",
        "lbl_quantity": "Cantidad:",
        "lbl_language": "Idioma:",
        "all_files": "Todos los Archivos",
        "image_files": "Archivos de Imagen",
        "no_image_preview": "Sin vista previa de imagen",
        "error_loading_image": "Error al cargar la imagen.",

        # Confirmation Dialogs
        "confirm_delete_title": "Confirmar Eliminación",
        "confirm_delete_message": "¿Estás seguro de que quieres eliminar este elemento?",

        # Main Menu / Navigation
        "modules_menu_label": "Módulos",
        "menu_products": "Gestión de Productos",
        "menu_sales": "Módulo de Ventas",
        "menu_reports": "Módulo de Reportes",
        "menu_settings": "Configuración",
        "menu_language": "Idioma",
        "menu_language_es": "Español",
        "menu_language_en": "Inglés",
        "menu_logout": "Cerrar Sesión", # Added logout

        # Product Management Module
        "product_manager_title": "Gestión de Productos",
        "lbl_category": "Categoría:",
        "lbl_product_name": "Nombre del Producto:",
        "lbl_product_description": "Descripción del Producto:",
        "lbl_base_price": "Precio Base:",
        "lbl_image_path": "Ruta de Imagen:",
        "lbl_variants": "Variantes:",
        "lbl_modifiers": "Modificadores:",
        "lbl_is_available": "¿Está Disponible?", # Added availability checkbox

        # Product Management Buttons
        "btn_add_category": "Añadir Categoría",
        "btn_add_category_compact": "Añadir Cat.", # For smaller buttons/UI
        "btn_add_product": "Añadir Producto",
        "btn_add_variant": "Añadir Variante",
        "btn_add_modifier": "Añadir Modificador",
        "btn_clear_form": "Limpiar Formulario", # Added clear form button

        # Dialog Titles for Product Management
        "dialog_add_category_title": "Añadir Nueva Categoría",
        "dialog_edit_category_title": "Editar Categoría",
        "dialog_add_product_title": "Añadir Nuevo Producto",
        "dialog_edit_product_title": "Editar Producto",
        "dialog_add_variant_title": "Añadir Nueva Variante",
        "dialog_edit_variant_title": "Editar Variante",
        "dialog_add_modifier_title": "Añadir Nuevo Modificador",
        "dialog_edit_modifier_title": "Editar Modificador",

        # Variant Specific Labels
        "lbl_variant_name": "Nombre de Variante:",
        "lbl_price_adjustment": "Ajuste de Precio:",

        # Modifier Specific Labels and Options
        "lbl_modifier_name": "Nombre de Modificador:",
        "lbl_modifier_price": "Precio de Modificador:",
        "lbl_modifier_applies_to": "Aplica a:",
        "option_global_modifier": "Global",
        "option_product_modifier": "Producto Específico",
        "option_variant_modifier": "Variante Específica",
        "lbl_product_selection": "Seleccionar Producto:", # For modifier application
        "lbl_variant_selection": "Seleccionar Variante:", # For modifier application
        "tree_global_modifiers": "Modificadores Globales", # For treeview header/label

        # Treeview Column Headers (Product Management)
        "tree_col_id": "ID",
        "tree_col_name_es": "Nombre (ES)", # Added for clarity
        "tree_col_name_en": "Nombre (EN)", # Added for clarity
        "tree_col_category": "Categoría",
        "tree_col_product": "Producto",
        "tree_col_variant": "Variante",
        "tree_col_modifier": "Modificador",
        "tree_col_price": "Precio",
        "tree_col_base_price": "Precio Base", # Added for clarity
        "tree_col_adjustment": "Ajuste", # Added for clarity
        "tree_col_actions": "Acciones",
        "tree_col_available": "Disponible", # Added for availability

        # Product Management Context Menu Options
        "context_edit": "Editar",
        "context_delete": "Eliminar",
        "context_add_product": "Añadir Producto",
        "context_add_variant": "Añadir Variante",
        "context_add_modifier": "Añadir Modificador",

        # General Messages (Success, Error, Warning)
        "msg_success": "Operación exitosa.",
        "msg_error": "Error: ",
        "msg_warning": "Advertencia: ",
        "msg_no_selection": "Por favor, selecciona un elemento para esta acción.",
        "msg_item_not_found": "Elemento no encontrado.",
        "msg_delete_failed": "No se pudo eliminar el elemento.",
        "msg_fields_required": "Todos los campos de nombre son obligatorios.", # Refined
        "msg_save_failed": "No se pudo guardar el elemento.",
        "msg_price_positive": "El precio debe ser un número positivo.",
        "msg_invalid_price": "Precio inválido. Por favor, introduce un número válido.",
        "msg_quantity_positive": "La cantidad debe ser un número positivo.",
        "msg_invalid_quantity": "Cantidad inválida. Introduce un número entero válido.",
        "msg_image_copy_failed": "Fallo al copiar la imagen.",
        "msg_not_implemented": "Módulo aún no implementado.",
        "msg_select_category": "Por favor, selecciona una categoría.", # General select category
        "msg_select_product": "Por favor, selecciona un producto.", # General select product
        "msg_select_variant": "Por favor, selecciona una variante.", # General select variant


        # Product Management Specific Messages
        "msg_category_has_products": "No se puede eliminar la categoría porque tiene productos asociados.",
        "msg_product_has_variants": "No se puede eliminar el producto porque tiene variantes asociadas.",
        "msg_variant_has_modifiers": "No se puede eliminar la variante porque tiene modificadores asociados.",
        "msg_modifier_associated_with_sales": "No se puede eliminar el modificador porque está asociado a ventas.",
        "msg_modifier_product_variant_required": "Debes seleccionar un producto o variante si el modificador no es global.",
        "msg_global_modifier_no_association": "Un modificador global no debe tener producto o variante asociado.",

        # Dynamic CRUD Operation Messages (more specific)
        "msg_category_added": "Categoría añadida con éxito.",
        "msg_error_adding_category": "Error al añadir la categoría.",
        "msg_category_updated": "Categoría actualizada con éxito.",
        "msg_error_updating_category": "Error al actualizar la categoría.",
        "msg_product_added": "Producto añadido con éxito.",
        "msg_error_adding_product": "Error al añadir el producto.",
        "msg_product_updated": "Producto actualizado con éxito.",
        "msg_error_updating_product": "Error al actualizar el producto.",
        "msg_variant_added": "Variante añadida con éxito.",
        "msg_error_adding_variant": "Error al añadir la variante.",
        "msg_variant_updated": "Variante actualizada con éxito.",
        "msg_error_updating_variant": "Error al actualizar la variante.",
        "msg_modifier_added": "Modificador añadido con éxito.",
        "msg_error_adding_modifier": "Error al añadir el modificador.",
        "msg_modifier_updated": "Modificador actualizado con éxito.",
        "msg_error_updating_modifier": "Error al actualizar el modificador.",
        "msg_item_deleted_successfully": "Elemento eliminado con éxito.",
        "msg_error_deleting_item": "Error al eliminar el elemento.",


        # Sales Module
        "sales_title": "Módulo de Ventas",
        "lbl_order_summary": "Resumen del Pedido",
        "btn_checkout": "Cerrar Venta",
        "btn_clear_order": "Limpiar Pedido",
        "lbl_total": "Total:",
        "tree_col_item": "Artículo",
        "tree_col_item_quantity": "Cant.",
        "tree_col_item_price": "Precio Unit.",
        "tree_col_item_total": "Total",
        "btn_add_to_order": "Añadir al Pedido",
        "btn_remove_from_order": "Quitar del Pedido",
        "lbl_selected_product": "Producto Seleccionado:",
        "lbl_selected_variant": "Variante Seleccionada:",
        "lbl_selected_modifiers": "Modificadores Seleccionados:",
        "dialog_add_to_order_title": "Añadir al Pedido",
        "lbl_item_quantity": "Cantidad de Ítem:",
        "lbl_modifier_quantity": "Cantidad de Modificador:",
        "msg_sale_successful": "Venta realizada con éxito.",
        "msg_no_items_in_order": "No hay ítems en el pedido.",
        "msg_item_added_to_order": "Elemento añadido al pedido.", # Added confirmation
        "msg_item_removed_from_order": "Elemento quitado del pedido.", # Added confirmation
        "msg_product_selection_required": "Por favor, selecciona un producto para añadir al pedido.", # Sales specific

        # Reports Module
        "reports_title": "Módulo de Reportes",
        "lbl_report_type": "Tipo de Reporte:",
        "option_daily": "Diario",
        "option_weekly": "Semanal",
        "option_monthly": "Mensual",
        "option_date_range": "Rango de Fechas",
        "lbl_start_date": "Fecha Inicio:",
        "lbl_end_date": "Fecha Fin:",
        "btn_generate_report": "Generar Reporte",
        "lbl_total_sales": "Ventas Totales:",
        "lbl_total_items_sold": "Total Ítems Vendidos:",
        "report_col_date": "Fecha",
        "report_col_sale_id": "ID Venta",
        "report_col_total": "Total",
        "report_col_product_name": "Producto",
        "report_col_product_qty": "Cantidad",
        "report_col_product_price": "Precio",
        "report_col_item_name": "Artículo",
        "report_col_modifier_name": "Modificador",
        "msg_invalid_date_range": "La fecha de inicio no puede ser posterior a la fecha de fin.",
        "msg_no_sales_found": "No se encontraron ventas para el rango de fechas seleccionado.", # Added for reports

        # Settings Module
        "settings_title": "Configuración",
        "lbl_currency": "Moneda:", # Added for settings
        "lbl_tax_rate": "Tasa de Impuestos (%):", # Added for settings
        "btn_save_settings": "Guardar Configuración", # Added for settings
        "msg_settings_saved": "Configuración guardada con éxito.", # Added for settings
        "msg_error_saving_settings": "Error al guardar la configuración.", # Added for settings
        "msg_invalid_tax_rate": "Por favor, introduce una tasa de impuestos válida (número).", # Added for settings
        "lbl_about": "Acerca de",
        "about_text": "Sistema de Gestión de Ventas v1.0\nDesarrollado por [Tu Nombre/Empresa]", # Added developer info
        "btn_about": "Acerca de...",
    },
    "en": {
        # General UI Elements and Actions
        "app_title": "Sales Management System",
        "btn_save": "Save",
        "btn_add": "Add",
        "btn_edit": "Edit",
        "btn_delete": "Delete",
        "btn_cancel": "Cancel",
        "btn_close": "Close",
        "btn_select_image": "Select Image",
        "lbl_name": "Name:",
        "lbl_description": "Description:",
        "lbl_price": "Price:",
        "lbl_quantity": "Quantity:",
        "lbl_language": "Language:",
        "all_files": "All Files",
        "image_files": "Image Files",
        "no_image_preview": "No image preview",
        "error_loading_image": "Error loading image.",

        # Confirmation Dialogs
        "confirm_delete_title": "Confirm Deletion",
        "confirm_delete_message": "Are you sure you want to delete this item?",

        # Main Menu / Navigation
        "modules_menu_label": "Modules",
        "menu_products": "Product Management",
        "menu_sales": "Sales Module",
        "menu_reports": "Reports Module",
        "menu_settings": "Settings",
        "menu_language": "Language",
        "menu_language_es": "Spanish",
        "menu_language_en": "English",
        "menu_logout": "Logout",

        # Product Management Module
        "product_manager_title": "Product Management",
        "lbl_category": "Category:",
        "lbl_product_name": "Product Name:",
        "lbl_product_description": "Product Description:",
        "lbl_base_price": "Base Price:",
        "lbl_image_path": "Image Path:",
        "lbl_variants": "Variants:",
        "lbl_modifiers": "Modifiers:",
        "lbl_is_available": "Is Available?",

        # Product Management Buttons
        "btn_add_category": "Add Category",
        "btn_add_category_compact": "Add Cat.",
        "btn_add_product": "Add Product",
        "btn_add_variant": "Add Variant",
        "btn_add_modifier": "Add Modifier",
        "btn_clear_form": "Clear Form",

        # Dialog Titles for Product Management
        "dialog_add_category_title": "Add New Category",
        "dialog_edit_category_title": "Edit Category",
        "dialog_add_product_title": "Add New Product",
        "dialog_edit_product_title": "Edit Product",
        "dialog_add_variant_title": "Add New Variant",
        "dialog_edit_variant_title": "Edit Variant",
        "dialog_add_modifier_title": "Add New Modifier",
        "dialog_edit_modifier_title": "Edit Modifier",

        # Variant Specific Labels
        "lbl_variant_name": "Variant Name:",
        "lbl_price_adjustment": "Price Adjustment:",

        # Modifier Specific Labels and Options
        "lbl_modifier_name": "Modifier Name:",
        "lbl_modifier_price": "Modifier Price:",
        "lbl_modifier_applies_to": "Applies to:",
        "option_global_modifier": "Global",
        "option_product_modifier": "Specific Product",
        "option_variant_modifier": "Specific Variant",
        "lbl_product_selection": "Select Product:",
        "lbl_variant_selection": "Select Variant:",
        "tree_global_modifiers": "Global Modifiers",

        # Treeview Column Headers (Product Management)
        "tree_col_id": "ID",
        "tree_col_name_es": "Name (ES)",
        "tree_col_name_en": "Name (EN)",
        "tree_col_category": "Category",
        "tree_col_product": "Product",
        "tree_col_variant": "Variant",
        "tree_col_modifier": "Modifier",
        "tree_col_price": "Price",
        "tree_col_base_price": "Base Price",
        "tree_col_adjustment": "Adjustment",
        "tree_col_actions": "Actions",
        "tree_col_available": "Available",

        # Product Management Context Menu Options
        "context_edit": "Edit",
        "context_delete": "Delete",
        "context_add_product": "Add Product",
        "context_add_variant": "Add Variant",
        "context_add_modifier": "Add Modifier",

        # General Messages (Success, Error, Warning)
        "msg_success": "Operation successful.",
        "msg_error": "Error: ",
        "msg_warning": "Warning: ",
        "msg_no_selection": "Please select an item for this action.",
        "msg_item_not_found": "Item not found.",
        "msg_delete_failed": "Could not delete item.",
        "msg_fields_required": "All name fields are required.",
        "msg_save_failed": "Could not save item.",
        "msg_price_positive": "Price must be a positive number.",
        "msg_invalid_price": "Invalid price. Please enter a valid number.",
        "msg_quantity_positive": "Quantity must be a positive number.",
        "msg_invalid_quantity": "Invalid quantity. Please enter a valid integer.",
        "msg_image_copy_failed": "Failed to copy image.",
        "msg_not_implemented": "Module not yet implemented.",
        "msg_select_category": "Please select a category.",
        "msg_select_product": "Please select a product.",
        "msg_select_variant": "Please select a variant.",

        # Product Management Specific Messages
        "msg_category_has_products": "Cannot delete category because it has associated products.",
        "msg_product_has_variants": "Cannot delete product because it has associated variants.",
        "msg_variant_has_modifiers": "Cannot delete variant because it has associated modifiers.",
        "msg_modifier_associated_with_sales": "Cannot delete modifier because it is associated with sales.",
        "msg_modifier_product_variant_required": "You must select a product or variant if the modifier is not global.",
        "msg_global_modifier_no_association": "A global modifier should not have product or variant association.",

        # Dynamic CRUD Operation Messages (more specific)
        "msg_category_added": "Category added successfully.",
        "msg_error_adding_category": "Error adding category.",
        "msg_category_updated": "Category updated successfully.",
        "msg_error_updating_category": "Error updating category.",
        "msg_product_added": "Product added successfully.",
        "msg_error_adding_product": "Error adding product.",
        "msg_product_updated": "Product updated successfully.",
        "msg_error_updating_product": "Error updating product.",
        "msg_variant_added": "Variant added successfully.",
        "msg_error_adding_variant": "Error adding variant.",
        "msg_variant_updated": "Variant updated successfully.",
        "msg_error_updating_variant": "Error updating variant.",
        "msg_modifier_added": "Modifier added successfully.",
        "msg_error_adding_modifier": "Error adding modifier.",
        "msg_modifier_updated": "Modifier updated successfully.",
        "msg_error_updating_modifier": "Error updating modifier.",
        "msg_item_deleted_successfully": "Item deleted successfully.",
        "msg_error_deleting_item": "Error deleting item.",


        # Sales Module
        "sales_title": "Sales Module",
        "lbl_order_summary": "Order Summary",
        "btn_checkout": "Checkout",
        "btn_clear_order": "Clear Order",
        "lbl_total": "Total:",
        "tree_col_item": "Item",
        "tree_col_item_quantity": "Qty.",
        "tree_col_item_price": "Unit Price",
        "tree_col_item_total": "Total",
        "btn_add_to_order": "Add to Order",
        "btn_remove_from_order": "Remove from Order",
        "lbl_selected_product": "Selected Product:",
        "lbl_selected_variant": "Selected Variant:",
        "lbl_selected_modifiers": "Selected Modifiers:",
        "dialog_add_to_order_title": "Add to Order",
        "lbl_item_quantity": "Item Quantity:",
        "lbl_modifier_quantity": "Modifier Quantity:",
        "msg_sale_successful": "Sale successful.",
        "msg_no_items_in_order": "No items in order.",
        "msg_item_added_to_order": "Item added to order.",
        "msg_item_removed_from_order": "Item removed from order.",
        "msg_product_selection_required": "Please select a product to add to the order.",

        # Reports Module
        "reports_title": "Reports Module",
        "lbl_report_type": "Report Type:",
        "option_daily": "Daily",
        "option_weekly": "Weekly",
        "option_monthly": "Monthly",
        "option_date_range": "Date Range",
        "lbl_start_date": "Start Date:",
        "lbl_end_date": "End Date:",
        "btn_generate_report": "Generate Report",
        "lbl_total_sales": "Total Sales:",
        "lbl_total_items_sold": "Total Items Sold:",
        "report_col_date": "Date",
        "report_col_sale_id": "Sale ID",
        "report_col_total": "Total",
        "report_col_product_name": "Product",
        "report_col_product_qty": "Quantity",
        "report_col_product_price": "Price",
        "report_col_item_name": "Item",
        "report_col_modifier_name": "Modifier",
        "msg_invalid_date_range": "Start date cannot be after end date.",
        "msg_no_sales_found": "No sales found for the selected date range.",

        # Settings Module
        "settings_title": "Settings",
        "lbl_currency": "Currency:",
        "lbl_tax_rate": "Tax Rate (%):",
        "btn_save_settings": "Save Settings",
        "msg_settings_saved": "Settings saved successfully.",
        "msg_error_saving_settings": "Error saving settings.",
        "msg_invalid_tax_rate": "Please enter a valid tax rate (number).",
        "lbl_about": "About",
        "about_text": "Sales Management System v1.0\nDeveloped by [Your Name/Company]",
        "btn_about": "About...",
    }
}

def set_language(lang_code):
    """Sets the current language for the application."""
    global current_language
    if lang_code in TRANSLATIONS:
        current_language = lang_code
    else:
        print(f"Warning: Language '{lang_code}' not supported. Using '{current_language}'.")
        # Optionally, raise an error or fallback more gracefully
        # raise ValueError(f"Unsupported language code: {lang_code}")

def get_text(key, default=None):
    """
    Retrieves the translated text for a given key in the current language.
    If the key is not found, it falls back to English, then to a default value,
    and finally to a placeholder string.
    """
    # Try to get the text in the current language
    text = TRANSLATIONS.get(current_language, {}).get(key)
    if text is not None:
        return text

    # Fallback to English if not found in current language
    text = TRANSLATIONS["en"].get(key)
    if text is not None:
        return text

    # Fallback to provided default if still not found
    if default is not None:
        return default

    # Last resort: return a placeholder
    return f"MISSING_TEXT_{key}"