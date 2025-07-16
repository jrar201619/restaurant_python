# utils/helpers.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from config.translations import get_text

# Global dictionary to keep references to images
# Tkinter's PhotoImage objects can be garbage-collected if not held by a Python variable,
# causing images to disappear.
_photo_image_refs = {}

def load_icon(icon_name, size=(24, 24)):
    """
    Loads an icon from the assets/icons directory.
    Caches the PhotoImage to prevent garbage collection.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__)) # Get current directory of this file
    project_root = os.path.abspath(os.path.join(base_dir, os.pardir)) # Go up one level to project root
    icon_path = os.path.join(project_root, "assets", "icons", icon_name)

    if not os.path.exists(icon_path):
        messagebox.showerror(get_text("msg_error"), get_text("icon_path_error") + f"\nPath: {icon_path}")
        return None

    try:
        image = Image.open(icon_path)
        image = image.resize(size, Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(image)

        # Store a reference to prevent garbage collection
        _photo_image_refs[icon_name + str(size)] = photo_image
        return photo_image
    except Exception as e:
        messagebox.showerror(get_text("msg_error"), f"Error loading icon '{icon_name}': {e}")
        return None

def load_image_for_preview(image_path, size=(200, 150)):
    """
    Loads an image for preview, resizing it to fit without distortion.
    Caches the PhotoImage.
    """
    if not image_path or not os.path.exists(image_path):
        return None

    try:
        image = Image.open(image_path)
        original_width, original_height = image.size
        target_width, target_height = size

        # Calculate new size to fit within target_size while maintaining aspect ratio
        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(image)

        # Store a reference
        _photo_image_refs[image_path + str(size)] = photo_image
        return photo_image
    except Exception as e:
        messagebox.showerror(get_text("msg_error"), get_text("error_loading_image") + f"\n{e}")
        return None

def copy_image_to_assets(source_path, destination_dir="assets/images"):
    """
    Copies an image from source_path to the specified destination_dir within assets.
    Returns the relative path to the copied image from the project root.
    """
    if not source_path or not os.path.exists(source_path):
        return None

    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, os.pardir))
        target_dir = os.path.join(project_root, destination_dir)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Generate a unique filename to prevent overwriting
        filename = os.path.basename(source_path)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{os.urandom(4).hex()}{ext}" # Add random hex for uniqueness
        destination_path = os.path.join(target_dir, unique_filename)

        with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
            dst.write(src.read())

        # Return relative path from project root
        relative_path = os.path.relpath(destination_path, project_root)
        return relative_path

    except Exception as e:
        messagebox.showerror(get_text("msg_error"), get_text("msg_image_copy_failed") + f"\n{e}")
        return None