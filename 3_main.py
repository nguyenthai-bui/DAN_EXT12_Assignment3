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