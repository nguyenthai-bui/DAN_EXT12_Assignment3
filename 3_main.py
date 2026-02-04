"""
Main application class for image editor GUI.

Provides a complete graphical interface for image processing with controls
for effects, adjustments, transformations, and file operations.
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk, ImageDraw
import importlib

# Import modules dynamically (updated names)
image_processing_module = importlib.import_module("1_image_processing")
image_display_module = importlib.import_module("2_image_display")

ImageModel = image_processing_module.ImageModel
ScrollableImageCanvas = image_display_module.ScrollableImageCanvas


# Set application theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    """
    Main application window for image editor.
    
    Manages UI layout, user interactions, file operations, and coordinates
    between the model and view components.
    """
    
    def __init__(self):
        """Initialize main application window."""
        super().__init__()

        # Set window properties
        self.title("Assignment 3")
        self.geometry("1100x750")
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        # Initialize model
        self.model = ImageModel()
        
        # UI state
        self.menu_icons = {}
        self.load_menu_icons()
        self.slider_labels = {} 

        # Build UI components
        self.build_native_menu()
        self.build_status_bar()
        self.build_controls()
        
        # Add image display area
        self.image_area = ScrollableImageCanvas(self, fg_color="#1a1a1a", corner_radius=0)
        self.image_area.pack(side="top", fill="both", expand=True)

        # Bind resize event
        self.bind("<Configure>", self.on_resize)

    def load_menu_icons(self):
        """Load or create menu icons from files."""
        # Icon names to load
        icon_names = ["open", "save", "save_as", "undo", "redo", "close"]
        
        # Get icons directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_dir, "icons") 

        # Load or create each icon
        for name in icon_names:
            path = os.path.join(icon_path, f"{name}.png")
            
            # Load from file if exists, otherwise create placeholder
            if os.path.exists(path):
                img = Image.open(path)
            else:
                # Create blank white rectangle as placeholder
                img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                d.rectangle([2,2,18,18], fill="white")
            
            # Resize icon to 18x18 pixels
            img = img.resize((18, 18), Image.Resampling.LANCZOS)
            
            # Ensure RGBA format
            if img.mode != 'RGBA': 
                img = img.convert('RGBA')
            
            # Extract alpha channel
            r, g, b, a = img.split()
            
            # Create white background
            white_bg = Image.new('RGB', img.size, (255, 255, 255))
            
            # Combine with alpha for proper display
            img = Image.merge('RGBA', (*white_bg.split(), a))
            
            # Convert to PhotoImage
            self.menu_icons[name] = ImageTk.PhotoImage(img)