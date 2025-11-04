#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import os
from image_processor import ImageProcessor
from gui_components import PhotoEditorGUI

class PhotoEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simple Photo Editor")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize image processor
        self.processor = ImageProcessor()
        
        # Initialize GUI
        self.gui = PhotoEditorGUI(self.root, self.processor)
        
        # Current image variables
        self.original_image = None
        self.current_image = None
        self.image_path = None
        
    def run(self):
        """Start the photo editor application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PhotoEditor()
    app.run()