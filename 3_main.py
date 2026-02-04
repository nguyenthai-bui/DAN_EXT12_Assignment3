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
    
    def build_native_menu(self):
        """Build native menu bar with File and Edit menus."""
        # Menu styling
        menu_theme = {
            "bg": "#2b2b2b", 
            "fg": "white", 
            "activebackground": "#555", 
            "activeforeground": "white", 
            "tearoff": 0, 
            "bd": 0
        }
        
        # Create menu bar
        menubar = tk.Menu(self) 
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, **menu_theme)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label=" Open", image=self.menu_icons["open"], compound="left", command=self.open_image)
        file_menu.add_command(label=" Save", image=self.menu_icons["save"], compound="left", command=self.save)
        file_menu.add_command(label=" Save As", image=self.menu_icons["save_as"], compound="left", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label=" Exit", image=self.menu_icons["close"], compound="left", command=self.confirm_exit)

        # Edit menu
        edit_menu = tk.Menu(menubar, **menu_theme)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label=" Undo", image=self.menu_icons["undo"], compound="left", command=self.undo)
        edit_menu.add_command(label=" Redo", image=self.menu_icons["redo"], compound="left", command=self.redo)

    def build_status_bar(self):
        """Build status bar at bottom of window."""
        # Create status frame
        self.status_frame = ctk.CTkFrame(self, height=25, corner_radius=0, fg_color="#222222")
        self.status_frame.pack(side="bottom", fill="x")
        
        # Create status label
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready", 
            text_color="gray", 
            font=("Arial", 11), 
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=2)

    def build_controls(self):
        """Build control panel with effects, adjustments, and transformations."""
        # Main control frame
        control_frame = ctk.CTkFrame(
            self, 
            fg_color=("#E0E0E0", "#2B2B2B"), 
            height=160, 
            corner_radius=15
        )
        control_frame.pack(side="bottom", fill="x", padx=20, pady=10) 

        # Left column - Effects
        col1 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col1.pack(side="left", fill="y", padx=20, pady=20)
        
        # Effects section
        ctk.CTkLabel(col1, text="EFFECTS", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        ctk.CTkButton(col1, text="Grayscale", width=100, command=self.grayscale).pack(pady=5)
        ctk.CTkButton(col1, text="Edge Detect", width=100, command=self.edge).pack(pady=5)

        # Middle column - Adjustments
        col2 = ctk.CTkFrame(control_frame, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=20, pady=10)
        
        # Adjustments section label
        ctk.CTkLabel(col2, text="ADJUSTMENTS", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))

        # Helper function to create slider with label and reset button
        def make_slider(parent, name, f, t, default_val, cmd_drag, cmd_rel, show_reset=True):
            """Create slider widget with label and optional reset button."""
            # Create container frame
            sub = ctk.CTkFrame(parent, fg_color="transparent")
            sub.pack(fill="x", pady=2)
            
            # Create label with current value
            lbl_text = f"{name}: {default_val}"
            lbl = ctk.CTkLabel(sub, text=lbl_text, width=110, anchor="w", font=("Arial", 11))
            lbl.pack(side="left")
            self.slider_labels[name] = lbl

            # Update label text on drag
            def on_drag_wrapper(val):
                # Format value for display
                if name == "Blur" or name == "Brightness": 
                    display_val = int(val)
                else: 
                    display_val = f"{val:.2f}"
                
                # Update label
                self.slider_labels[name].configure(text=f"{name}: {display_val}")
                
                # Call drag callback
                cmd_drag(val)

            # Reset button action
            def reset_action():
                # Reset slider to default
                slider.set(default_val)
                
                # Update label
                on_drag_wrapper(default_val) 
                
                # Call release callback
                cmd_rel(None)

            # Create reset button if needed
            if show_reset:
                btn_reset = ctk.CTkButton(
                    sub, 
                    text="⟲", 
                    width=25, 
                    height=20, 
                    fg_color="transparent", 
                    border_width=1, 
                    border_color="gray",
                    text_color=("black", "white"), 
                    font=("Arial", 10, "bold"),
                    command=reset_action
                )
                btn_reset.pack(side="left", padx=(0, 5))
            else:
                # Placeholder for alignment
                ctk.CTkFrame(sub, width=25, height=20, fg_color="transparent").pack(side="left", padx=(0, 5))

            # Create and configure slider
            slider = ctk.CTkSlider(sub, from_=f, to=t, height=18)
            slider.set(default_val)
            slider.pack(side="left", fill="x", expand=True, padx=5)
            
            # Bind slider events
            slider.configure(command=on_drag_wrapper)
            slider.bind("<ButtonRelease-1>", cmd_rel)
            
            return slider