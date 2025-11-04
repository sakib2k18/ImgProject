import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import time
import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk, ImageEnhance
from queue import Queue
from threading import Lock
import matplotlib.pyplot as plt

class PhotoEditorGUI:
    def __init__(self, root, processor):
        self.root = root
        self.processor = processor
        self.setup_style()
        self.create_widgets()
        
    def setup_style(self):
        """Setup modern professional theme with minimal borders and professional colors"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Font settings
        default_font = ('Arial', 10)
        heading_font = ('Arial', 11, 'bold')
        
        # Color palette
        bg_color = '#1e1e2e'  # Dark blue-gray
        tab_bg = '#2a2a3a'    # Slightly lighter than background
        tab_active_bg = '#3a3a4a'  # Active tab color
        text_color = '#e0e0e0'     # Light gray text
        accent_color = '#4a90e2'   # Soft blue
        button_bg = '#3a3a4a'      # Button background
        button_active = '#5a5a6a'   # Button active state
        
        # Configure main styles
        style.configure('.', background=bg_color, foreground=text_color)
        
        # Notebook style
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=tab_bg,
                       foreground=text_color,
                       padding=[15, 5],
                       borderwidth=0,
                       focuscolor=bg_color)
        style.map('TNotebook.Tab',
                 background=[('selected', tab_active_bg)],
                 lightcolor=[('selected', tab_active_bg)],
                 bordercolor=[('selected', tab_active_bg)])
        
        # Frame and label styles
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', 
                      background=bg_color, 
                      foreground=text_color,
                      font=default_font)
        style.configure('TLabelframe.Label', 
                      background=bg_color,
                      foreground=accent_color,
                      font=heading_font)
        style.configure('TButton',
                       background=button_bg,
                       foreground=text_color,
                       borderwidth=0,
                       focuscolor=bg_color)
        style.map('TButton',
                 background=[('active', button_active), ('pressed', button_active)],
                 relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
        
        # Scale style
        style.configure('Horizontal.TScale',
                      background=bg_color,
                      troughcolor='#3a3a4a',
                      darkcolor=accent_color,
                      lightcolor=accent_color,
                      bordercolor=bg_color,
                      arrowcolor=text_color)
        
        # LabelFrame style
        style.configure('TLabelframe', 
                      background=bg_color, 
                      borderwidth=0,
                      relief='flat')
        
        # Entry style
        style.configure('TEntry',
                      fieldbackground='#2a2a3a',
                      foreground=text_color,
                      insertcolor=text_color,
                      borderwidth=1,
                      relief='solid',
                      padding=3,
                      font=default_font)
                      
        # Button style
        style.configure('TButton',
                      background=button_bg,
                      foreground=text_color,
                      borderwidth=0,
                      font=default_font,
                      padding=5)
        style.map('TButton',
                 background=[('active', button_active), ('pressed', button_active)],
                 relief=[('pressed', 'sunken'), ('!pressed', 'flat')])
                 
        # Accent button style
        style.configure('Accent.TButton',
                      background=accent_color,
                      foreground='white',
                      font=default_font,
                      padding=5)
        style.map('Accent.TButton',
                 background=[('active', '#3a7bc8'), ('pressed', '#2a6cb9')])
        
        # Configure the root window background
        self.root.configure(background=bg_color)
        
    def create_widgets(self):
        """Create main GUI layout"""
        # Configure the root window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create main container with grid layout
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky='nsew')
        
        # Configure main container grid
        main_container.grid_rowconfigure(1, weight=1)  # For content area
        main_container.grid_columnconfigure(0, weight=1)
        
        # Create toolbar with grid layout
        toolbar_frame = ttk.Frame(main_container)
        toolbar_frame.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 0))
        self.create_toolbar(toolbar_frame)
        
        # Create content area with grid layout
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure content frame grid - adjust weights to make control panel even narrower
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=7)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Create image panel with grid layout
        img_frame = ttk.Frame(content_frame)
        img_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Create control panel with grid layout
        control_frame = ttk.Frame(content_frame)
        control_frame.grid(row=0, column=1, sticky='nsew')
        
        # Configure the panels
        self.create_image_panel(img_frame)
        self.create_control_panel(control_frame)
        
        # Set minimum window size
        self.root.minsize(1200, 800)
        
    def create_toolbar(self, parent):
        """Create top toolbar with file operations"""
        # Configure parent grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Create toolbar frame
        toolbar = ttk.Frame(parent)
        toolbar.grid(row=0, column=0, sticky='ew')
        
        # Configure grid for toolbar
        for i in range(10):  # Enough columns for all elements
            toolbar.columnconfigure(i, weight=0)
        toolbar.columnconfigure(10, weight=1)  # Let the last column expand
        
        # File operations
        col = 0
        ttk.Button(toolbar, text="Open Image", command=self.open_image).grid(
            row=0, column=col, padx=(0, 5), pady=5, sticky='w')
        col += 1
        
        ttk.Button(toolbar, text="Save Image", command=self.save_image).grid(
            row=0, column=col, padx=(0, 5), pady=5, sticky='w')
        col += 1
        
        ttk.Button(toolbar, text="Reset", command=self.reset_image).grid(
            row=0, column=col, padx=(0, 5), pady=5, sticky='w')
        col += 1
        
        # Undo/Redo buttons
        ttk.Button(toolbar, text="Undo", command=self.undo_action).grid(
            row=0, column=col, padx=(0, 2), pady=5, sticky='w')
        col += 1
        
        ttk.Button(toolbar, text="Redo", command=self.redo_action).grid(
            row=0, column=col, padx=(2, 5), pady=5, sticky='w')
        col += 1
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).grid(
            row=0, column=col, padx=10, pady=5, sticky='ns')
        col += 1
        
        # Image info (aligned to the right)
        self.info_label = ttk.Label(toolbar, text="No image loaded")
        self.info_label.grid(
            row=0, column=col, padx=(10, 0), pady=5, sticky='e')
        
        # Add some padding around the toolbar
        toolbar.grid_configure(padx=10, pady=(10, 0))
        
    def create_image_panel(self, parent):
        """Create image display panel with matplotlib showing original and edited images"""
        # Configure parent frame
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Create a frame for the image display
        self.image_frame = ttk.Frame(parent)
        self.image_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure the image frame
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        
        # Create a canvas with scrollbars
        self.canvas = tk.Canvas(self.image_frame, bg='#2b2b2b', highlightthickness=0)
        scroll_y = ttk.Scrollbar(self.image_frame, orient="vertical", command=self.canvas.yview)
        scroll_x = ttk.Scrollbar(self.image_frame, orient="horizontal", command=self.canvas.xview)
        
        # Configure the canvas
        self.canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Create a frame inside the canvas
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        # Create a window in the canvas to hold the scrollable frame
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Grid the canvas and scrollbars
        self.canvas.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        
        # Create frames for original and edited images
        self.original_frame = ttk.LabelFrame(self.scrollable_frame, text="Original Image")
        self.original_frame.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.edited_frame = ttk.LabelFrame(self.scrollable_frame, text="Edited Image")
        self.edited_frame.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
        
        # Configure grid for the scrollable frame
        self.scrollable_frame.grid_rowconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        
        # Create matplotlib figures and axes for original image
        self.orig_fig = Figure(figsize=(5, 5), dpi=100, facecolor='#2b2b2b')
        self.orig_ax = self.orig_fig.add_subplot(111)
        self.orig_ax.set_facecolor('#2b2b2b')
        self.orig_ax.tick_params(axis='both', colors='white')
        self.orig_canvas = FigureCanvasTkAgg(self.orig_fig, master=self.original_frame)
        self.orig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create matplotlib figures and axes for edited image
        self.edit_fig = Figure(figsize=(5, 5), dpi=100, facecolor='#2b2b2b')
        self.edit_ax = self.edit_fig.add_subplot(111)
        self.edit_ax.set_facecolor('#2b2b2b')
        self.edit_ax.tick_params(axis='both', colors='white')
        self.edit_canvas = FigureCanvasTkAgg(self.edit_fig, master=self.edited_frame)
        self.edit_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Show empty placeholders
        self.show_empty_images()

    def show_empty_images(self):
        """Show empty placeholder images"""
        # Clear and set up original image panel
        self.orig_ax.clear()
        self.orig_ax.set_facecolor('#2b2b2b')
        self.orig_ax.text(0.5, 0.5, 'No Image Loaded', 
                        ha='center', va='center', fontsize=12, color='white',
                        transform=self.orig_ax.transAxes)
        self.orig_ax.axis('off')
        self.orig_canvas.draw()
        
        # Clear and set up edited image panel
        self.edit_ax.clear()
        self.edit_ax.set_facecolor('#2b2b2b')
        self.edit_ax.text(0.5, 0.5, 'Edited Image', 
                        ha='center', va='center', fontsize=12, color='white',
                        transform=self.edit_ax.transAxes)
        self.edit_ax.set_xlim(0, 1)
        self.edit_ax.set_ylim(0, 1)
        self.edit_canvas.draw()

    def update_image_display(self):
        """Update the image display for both original and edited images"""
        try:
            # Store the current time to prevent rapid updates
            current_time = time.time()
            if hasattr(self, '_last_update_time') and (current_time - self._last_update_time) < 0.05:  # 50ms debounce
                if not hasattr(self, '_pending_update'):
                    self._pending_update = True
                    self.root.after(100, self._process_pending_update)
                return
                
            self._last_update_time = current_time
            
            # Update original image display if available
            if hasattr(self.processor, 'original_image') and self.processor.original_image is not None:
                try:
                    # Make sure we have a valid image
                    orig_img = self.processor.original_image
                    if orig_img is None or orig_img.size == 0:
                        raise ValueError("Original image is empty")
                        
                    # Convert BGR to RGB for display if it's a color image
                    if len(orig_img.shape) == 3 and orig_img.shape[2] == 3:  # Color image
                        orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
                    
                    # Clear and update the original image display
                    self.orig_ax.clear()
                    if len(orig_img.shape) == 2:  # Grayscale image
                        self.orig_ax.imshow(orig_img, cmap='gray', aspect='equal')
                    else:  # Color image
                        self.orig_ax.imshow(orig_img, aspect='equal')
                        
                    self.orig_ax.axis('off')
                    self.orig_ax.set_facecolor('#2b2b2b')
                    
                    # Draw the original canvas
                    if hasattr(self, 'orig_canvas'):
                        self.orig_canvas.draw()
                        
                except Exception as e:
                    print(f"Error displaying original image: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Show error in the original image panel
                    self.orig_ax.clear()
                    self.orig_ax.text(0.5, 0.5, 'Error loading image', 
                                    ha='center', va='center', fontsize=12, 
                                    color='red', transform=self.orig_ax.transAxes)
                    self.orig_ax.axis('off')
                    if hasattr(self, 'orig_canvas'):
                        self.orig_canvas.draw()
            else:
                # No original image, show placeholder
                self.orig_ax.clear()
                self.orig_ax.set_facecolor('#2b2b2b')
                self.orig_ax.text(0.5, 0.5, 'No Image Loaded', 
                                ha='center', va='center', fontsize=12, 
                                color='white', transform=self.orig_ax.transAxes)
                self.orig_ax.axis('off')
                if hasattr(self, 'orig_canvas'):
                    self.orig_canvas.draw()
            
            # Update edited image display
            if hasattr(self.processor, 'current_image') and self.processor.current_image is not None:
                try:
                    # Get the current image for display
                    edit_img = self.processor.current_image
                    if edit_img is None or edit_img.size == 0:
                        raise ValueError("Edited image is empty")
                    
                    # Clear and update the edited image display
                    self.edit_ax.clear()
                    
                    # Handle both grayscale and color images
                    if len(edit_img.shape) == 2:  # Grayscale image
                        self.edit_ax.imshow(edit_img, cmap='gray', aspect='equal')
                    else:  # Color image
                        if edit_img.shape[2] == 3:  # Ensure it's a 3-channel image
                            edit_img = cv2.cvtColor(edit_img, cv2.COLOR_BGR2RGB)
                        self.edit_ax.imshow(edit_img, aspect='equal')
                    
                    self.edit_ax.axis('off')
                    self.edit_ax.set_facecolor('#2b2b2b')
                    
                    # Draw the edit canvas
                    if hasattr(self, 'edit_canvas'):
                        self.edit_canvas.draw()
                    
                    # Update info label with current image dimensions if it exists
                    if hasattr(self, 'info_label'):
                        try:
                            height, width = edit_img.shape[:2]
                            self.info_label.config(text=f"Image: {width}x{height}")
                        except Exception as e:
                            print(f"Error updating info label: {str(e)}")
                    
                except Exception as e:
                    print(f"Error displaying edited image: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Show error in the edited image panel
                    self.edit_ax.clear()
                    self.edit_ax.text(0.5, 0.5, 'Error displaying image', 
                                    ha='center', va='center', fontsize=12, 
                                    color='red', transform=self.edit_ax.transAxes)
                    self.edit_ax.axis('off')
                    if hasattr(self, 'edit_canvas'):
                        self.edit_canvas.draw()
            else:
                # No current image, show placeholder
                self.edit_ax.clear()
                self.edit_ax.set_facecolor('#2b2b2b')
                self.edit_ax.text(0.5, 0.5, 'No Edits Yet', 
                                ha='center', va='center', fontsize=12, 
                                color='white', transform=self.edit_ax.transAxes)
                self.edit_ax.axis('off')
                if hasattr(self, 'edit_canvas'):
                    self.edit_canvas.draw()
                
        except Exception as e:
            print(f"Error in update_image_display: {str(e)}")
            import traceback
            traceback.print_exc()
            # Ensure we clear any partial updates on error
            self.show_empty_images()
    
    def _process_pending_update(self):
        """Process any pending display updates"""
        if hasattr(self, '_pending_update'):
            delattr(self, '_pending_update')
            self.update_image_display()
            
    def schedule_update(self):
        """Schedule an image display update"""
        if not hasattr(self, '_update_scheduled'):
            self._update_scheduled = True
            self.after(50, self._process_scheduled_update)
    
    def _process_scheduled_update(self):
        """Process the scheduled update"""
        if hasattr(self, '_update_scheduled'):
            delattr(self, '_update_scheduled')
            self.update_image_display()

    def open_image(self):
        """Open image file and initialize both original and working copies"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return  # User cancelled
                
            # Show loading state
            self.root.config(cursor="watch")
            self.root.update()
            
            try:
                # Clear any previous images
                if hasattr(self, '_current_image_id'):
                    self.after_cancel(self._current_image_id)
                
                # Clear the current display
                self.show_empty_images()
                
                # Load the image using the processor
                if not hasattr(self.processor, 'load_image'):
                    raise RuntimeError("Image processor is not properly initialized")
                
                # Load the image in a separate thread to keep the UI responsive
                def load_and_display():
                    try:
                        # Load the image
                        if not self.processor.load_image(file_path):
                            raise RuntimeError("Failed to load image")
                        
                        # Make sure we have a valid image
                        if not hasattr(self.processor, 'current_image') or self.processor.current_image is None:
                            raise RuntimeError("No image data was loaded")
                        
                        # Store the original image
                        self.processor.original_image = self.processor.current_image.copy()
                        
                        # Update the display in the main thread
                        self.root.after(0, self._finalize_image_load)
                        
                    except Exception as e:
                        error_msg = f"Failed to load image: {str(e)}"
                        print(error_msg)
                        import traceback
                        traceback.print_exc()
                        self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                    finally:
                        self.root.after(0, lambda: self.root.config(cursor=""))
                
                # Start the loading in a separate thread
                import threading
                threading.Thread(target=load_and_display, daemon=True).start()
                
            except Exception as e:
                self.root.config(cursor="")
                error_msg = f"Failed to load image: {str(e)}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", error_msg)
                
        except Exception as e:
            self.root.config(cursor="")
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", error_msg)
    
    def _finalize_image_load(self):
        """Finalize the image loading process in the main thread"""
        try:
            # Make sure we have valid images
            if not hasattr(self.processor, 'original_image') or self.processor.original_image is None:
                raise RuntimeError("No original image available")
                
            if not hasattr(self.processor, 'current_image') or self.processor.current_image is None:
                self.processor.current_image = self.processor.original_image.copy()
            
            # Update the display
            self.update_image_display()
            
            # Force update both canvases
            self.orig_canvas.draw()
            self.edit_canvas.draw()
            
            # Show success message
            messagebox.showinfo("Success", "Image loaded successfully!")
            
        except Exception as e:
            error_msg = f"Failed to display image: {str(e)}"
            print(error_msg)
            import traceback
            self.processor.current_image = self.processor.original_image.copy()
            messagebox.showwarning("Warning", "No original image to reset to!")

    def on_scale_change(self, value, var, value_label=None, min_val=None, max_val=None):
        """Handle scale value change - ensures only integer values"""
        try:
            # Convert to integer and ensure it's within bounds
            if value == '':
                return
                
            try:
                int_val = int(round(float(value)))
            except (ValueError, TypeError):
                return
                
            if min_val is not None and int_val < min_val:
                int_val = min_val
            if max_val is not None and int_val > max_val:
                int_val = max_val
                
            # Update the variable
            if var.get() != int_val:
                var.set(int_val)
            
            # Update the value label if provided
            if value_label:
                value_label.config(text=str(int_val))
                
        except (ValueError, tk.TclError) as e:
            print(f"Error in on_scale_change: {e}")

    def create_labeled_scale(self, parent, label_text, from_, to, variable, resolution=1, show_apply=False, apply_command=None, show_value=True):
        """Helper to create a labeled scale with an optional apply button"""
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=2)
        
        # Label and value display
        label_frame = ttk.Frame(container)
        label_frame.pack(fill=tk.X)
        
        ttk.Label(label_frame, text=label_text).pack(side=tk.LEFT)
        
        # Scale and entry in a frame
        scale_frame = ttk.Frame(container)
        scale_frame.pack(fill=tk.X, pady=2)
        
        # Entry for direct value input (this will be the only place showing the value)
        entry = ttk.Entry(scale_frame, width=5, justify=tk.RIGHT)
        entry.insert(0, str(int(round(float(variable.get())))))
        entry.pack(side=tk.RIGHT, padx=5)
        
        # Remove the separate value label since we're showing it in the entry field
        value_label = None
        
        # Update variable when entry changes
        def on_entry_change(event):
            try:
                val = int(entry.get())
                if from_ <= val <= to:
                    variable.set(val)
            except ValueError:
                # Revert to previous value if invalid
                entry.delete(0, tk.END)
                entry.insert(0, str(variable.get()))
        
        entry.bind('<Return>', on_entry_change)
        entry.bind('<FocusOut>', on_entry_change)
        
        # Scale
        scale = ttk.Scale(
            scale_frame,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            variable=variable,
            command=lambda v: [
                entry.delete(0, tk.END),
                entry.insert(0, str(round(float(v)))),
                self.on_scale_change(v, variable, None, from_, to)
            ]
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Update entry when variable changes
        def update_display(*args):
            val = variable.get()
            entry.delete(0, tk.END)
            entry.insert(0, str(int(round(float(val)))))
        
        variable.trace_add('write', lambda *args: update_display())
        
        # Apply button if needed
        if show_apply and apply_command:
            ttk.Button(container, 
                      text="Apply", 
                      command=apply_command,
                      style='Accent.TButton').pack(fill=tk.X, pady=(0, 5))
            
        return container
        
    def create_control_panel(self, parent):
        """Create control panel with tabs"""
        # Configure styles with larger fonts
        style = ttk.Style()
        
        # Set default font for all widgets
        default_font = ('Arial', 11)
        self.root.option_add('*Font', default_font)
        
        # Configure notebook style
        style.configure('TNotebook', background='#2b2b2b')
        style.configure('TNotebook.Tab', 
                       background='#3b3b3b', 
                       foreground='white',
                       padding=[20, 10],
                       font=('Arial', 12, 'bold'))
        
        # Configure section headers
        style.configure('Section.TLabelframe.Label', 
                       font=('Arial', 12, 'bold'),
                       foreground='white')
        
        # Configure buttons
        style.configure('TButton', 
                      background='#4a4a4a', 
                      foreground='white',
                      font=('Arial', 11))
        
        # Configure labels
        style.configure('TLabel', font=('Arial', 11))
        
        # Configure entries
        style.configure('TEntry', font=('Arial', 11))
        
        # Configure option menus
        style.configure('TMenubutton', font=('Arial', 11))
        
        # Create main container with grid configuration
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Create a frame to hold canvas and scrollbar
        canvas_frame = ttk.Frame(container)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(canvas_frame, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        # Configure canvas scrolling
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        def on_canvas_configure(event):
            canvas.itemconfig(1, width=event.width)  # Update the canvas window width
            
        self.scrollable_frame.bind("<Configure>", on_frame_configure)
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Create window in canvas to hold the frame
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind mousewheel for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create tabs
        self.tab_control = ttk.Notebook(self.scrollable_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Make the rows and columns of the scrollable frame expand
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.rowconfigure(0, weight=1)
        
        # Create tabs
        self.filters_tab = ttk.Frame(self.tab_control)
        self.color_tab = ttk.Frame(self.tab_control)
        self.edge_tab = ttk.Frame(self.tab_control)
        self.geometric_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.filters_tab, text='Filters')
        self.tab_control.add(self.color_tab, text='Color')
        self.tab_control.add(self.edge_tab, text='Edges')
        self.tab_control.add(self.geometric_tab, text='Geometric')
        
        self.create_filters_tab()
        self.create_color_tab()
        self.create_edge_tab()
        self.create_geometric_tab()

    def create_filters_tab(self):
        """Create filters tab with available operations"""
        frame = self.filters_tab
        
        # Denoising
        denoise_frame = ttk.LabelFrame(frame, text="Denoising & Smoothing")
        denoise_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Gaussian Blur
        self.gauss_kernel = tk.IntVar(value=5)
        self.gauss_sigma = tk.IntVar(value=1)  # Changed to IntVar
        
        # Kernel size slider
        self.create_labeled_scale(
            denoise_frame,
            "Kernel Size (odd numbers only):",
            1, 21,
            self.gauss_kernel,
            resolution=2,
            show_apply=False,
            show_value=True
        )
        
        # Sigma slider
        self.create_labeled_scale(
            denoise_frame,
            "Sigma (1-10):",
            1, 10,  # Changed range to use integers
            self.gauss_sigma,
            resolution=1,
            show_apply=False,
            show_value=True
        )
        
        # Single apply button for denoising
        ttk.Button(denoise_frame, 
                  text="Apply Denoising", 
                  command=self.apply_gaussian_denoise,
                  style='Accent.TButton').pack(fill=tk.X, pady=(5, 0))
        
        # Sharpening
        sharpen_frame = ttk.LabelFrame(frame, text="Sharpening")
        sharpen_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.sharpen_strength = tk.IntVar(value=1)
        self.create_labeled_scale(
            sharpen_frame,
            "Sharpening Strength (1-30):",
            1, 30,
            self.sharpen_strength,
            resolution=1,
            show_apply=True,
            apply_command=self.apply_sharpen
        )
        
        # Thresholding
        thresh_frame = ttk.LabelFrame(frame, text="Global Thresholding")
        thresh_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.global_thresh = tk.IntVar(value=127)
        self.create_labeled_scale(
            thresh_frame,
            "Threshold:",
            0, 255,
            self.global_thresh,
            resolution=1,
            show_apply=True,
            apply_command=self.apply_global_threshold
        )
        
        # Histogram Equalization
        hist_frame = ttk.LabelFrame(frame, text="Histogram Operations")
        hist_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(hist_frame, 
                  text="Apply Histogram Equalization", 
                  command=self.apply_histogram_equalization).pack(fill=tk.X, pady=5)
        
        # Frequency Domain Filtering
        freq_frame = ttk.LabelFrame(frame, text="Frequency Domain Filtering")
        freq_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.freq_cutoff = tk.IntVar(value=10)
        self.create_labeled_scale(
            freq_frame,
            "Low-pass Cutoff (1-100):",
            1, 100,
            self.freq_cutoff,
            resolution=1,
            show_apply=True,
            apply_command=self.apply_frequency_lowpass
        )
        
        # Manual Convolution
        conv_frame = ttk.LabelFrame(frame, text="Manual Convolution")
        conv_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Kernel input frame
        kernel_frame = ttk.Frame(conv_frame)
        kernel_frame.pack(fill=tk.X, pady=5)
        
        # Kernel size selection
        ttk.Label(kernel_frame, text="Kernel Size:").pack(side=tk.LEFT, padx=5)
        self.kernel_size = tk.IntVar(value=3)
        size_menu = ttk.OptionMenu(kernel_frame, self.kernel_size, 3, 3, 5, 7, command=self.update_kernel_entries)
        size_menu.pack(side=tk.LEFT, padx=5)
        
        # Kernel entries frame
        self.kernel_entries_frame = ttk.Frame(conv_frame)
        self.kernel_entries_frame.pack(fill=tk.X, pady=5)
        
        # Default kernel (3x3 identity)
        self.kernel_entries = []
        self.update_kernel_entries()
        
        # Apply button
        ttk.Button(
            conv_frame,
            text="Apply Convolution",
            command=self.apply_manual_convolution,
            style='Accent.TButton'
        ).pack(fill=tk.X, pady=(5, 0))
        
    def create_geometric_tab(self):
        """Create geometric operations tab"""
        frame = self.geometric_tab
        
        # Rotation
        rotation_frame = ttk.LabelFrame(frame, text="Rotation")
        rotation_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.rotation_angle = tk.IntVar(value=0)
        self.create_labeled_scale(
            rotation_frame,
            "Rotation Angle (degrees):",
            -180, 180,
            self.rotation_angle,
            resolution=1,
            show_apply=True,
            apply_command=self.apply_rotation,
            show_value=True
        )
        
        # Flipping
        flip_frame = ttk.LabelFrame(frame, text="Flipping")
        flip_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(flip_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, 
                  text="Flip Horizontal", 
                  command=lambda: self.apply_flip('horizontal')).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        ttk.Button(btn_frame, 
                  text="Flip Vertical", 
                  command=lambda: self.apply_flip('vertical')).pack(side=tk.RIGHT, padx=2, expand=True, fill=tk.X)
    
    def create_edge_tab(self):
        """Create edge detection tab with available operations"""
        frame = self.edge_tab
        
        # Canny Edge Detection
        canny_frame = ttk.LabelFrame(frame, text="Canny Edge Detection")
        canny_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Threshold 1
        self.canny_thresh1 = tk.IntVar(value=50)
        self.create_labeled_scale(
            canny_frame,
            "Threshold 1:",
            0, 255,
            self.canny_thresh1,
            resolution=1,
            show_value=True
        )
        
        # Threshold 2
        self.canny_thresh2 = tk.IntVar(value=150)
        self.create_labeled_scale(
            canny_frame,
            "Threshold 2:",
            0, 255,
            self.canny_thresh2,
            resolution=1,
            show_value=True
        )
        
        # Apply button
        ttk.Button(canny_frame, 
                  text="Apply Canny Edge Detection", 
                  command=self.apply_canny).pack(fill=tk.X, pady=5)
        
        # Sobel Edge Detection
        sobel_frame = ttk.LabelFrame(frame, text="Sobel Edge Detection")
        sobel_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(sobel_frame, 
                  text="Apply Sobel Edge Detection", 
                  command=self.apply_sobel).pack(fill=tk.X, pady=5)
        
        # Laplacian Edge Detection
        laplacian_frame = ttk.LabelFrame(frame, text="Laplacian Edge Detection")
        laplacian_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(laplacian_frame, 
                  text="Apply Laplacian Edge Detection", 
                  command=self.apply_laplacian).pack(fill=tk.X, pady=5)
        
        # Zero-Crossing Edge Detection
        zero_cross_frame = ttk.LabelFrame(frame, text="Zero-Crossing Edge Detection")
        zero_cross_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.zero_cross_sigma = tk.IntVar(value=10)  # 1.0 * 10 for integer scaling
        self.create_labeled_scale(
            zero_cross_frame,
            "Sigma (1-50):",
            1, 50,  # 0.1 to 5.0 scaled by 10
            self.zero_cross_sigma,
            resolution=1,
            show_apply=True,
            apply_command=self.apply_zero_crossing,
            show_value=True
        )
    
    def create_color_tab(self):
        """Create color manipulation tab"""
        frame = self.color_tab
        
        # Color Channel View
        channel_frame = ttk.LabelFrame(frame, text="Color Channel View")
        channel_frame.pack(fill=tk.X, pady=(0, 10))
        
        btn_frame = ttk.Frame(channel_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Red Channel", 
                  command=lambda: self.apply_view_channel('R')).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="Green Channel", 
                  command=lambda: self.apply_view_channel('G')).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(btn_frame, text="Blue Channel", 
                  command=lambda: self.apply_view_channel('B')).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # HSV Channel View
        hsv_frame = ttk.LabelFrame(frame, text="HSV Channel View")
        hsv_frame.pack(fill=tk.X, pady=(0, 10))
        
        hsv_btn_frame = ttk.Frame(hsv_frame)
        hsv_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(hsv_btn_frame, text="Hue", 
                  command=lambda: self.apply_view_hsv_channel('H')).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(hsv_btn_frame, text="Saturation", 
                  command=lambda: self.apply_view_hsv_channel('S')).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        ttk.Button(hsv_btn_frame, text="Value", 
                  command=lambda: self.apply_view_hsv_channel('V')).pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
        
        # Color Conversion
        conv_frame = ttk.LabelFrame(frame, text="Color Conversion")
        conv_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(conv_frame, 
                  text="Convert to Grayscale", 
                  command=self.apply_grayscale).pack(fill=tk.X, pady=5)
                  
        # Binary thresholding
        binary_frame = ttk.LabelFrame(conv_frame, text="Binary Conversion")
        binary_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.binary_thresh = tk.IntVar(value=127)
        self.create_labeled_scale(
            binary_frame,
            "Threshold:",
            0, 255,
            self.binary_thresh,
            resolution=1,
            show_apply=True,
            apply_command=self.apply_binary_threshold
        )
        
    def apply_canny(self):
        """Apply Canny edge detection"""
        self.processor.push_state()
        self.processor.canny_edge_detection(
            threshold1=self.canny_thresh1.get(),
            threshold2=self.canny_thresh2.get()
        )
        self.update_image_display()
    
    def apply_sobel(self):
        """Apply Sobel edge detection"""
        self.processor.push_state()
        self.processor.sobel_edge_detection()
        self.update_image_display()
    
    def apply_laplacian(self):
        """Apply Laplacian edge detection"""
        self.processor.push_state()
        self.processor.laplacian_edge_detection()
        self.update_image_display()

    # ==================== FILTERS TAB METHODS ====================
    
    def apply_gaussian_denoise(self):
        """Apply Gaussian denoising"""
        self.processor.push_state()
        kernel_size = self.gauss_kernel.get()
        # Ensure kernel size is odd
        kernel_size = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
        self.processor.gaussian_denoise(
            kernel_size=kernel_size,
            sigma=self.gauss_sigma.get()
        )
        self.update_image_display()
    
    def apply_sharpen(self):
        """Apply sharpening filter"""
        self.processor.push_state()
        # Scale the integer value to a float between 0.1 and 3.0
        strength = self.sharpen_strength.get() / 10.0
        self.processor.sharpen(strength=strength)
        self.update_image_display()
    
    def apply_global_threshold(self):
        """Apply global thresholding"""
        self.processor.push_state()
        self.processor.global_threshold(
            threshold_value=self.global_thresh.get(),
            threshold_type=cv2.THRESH_BINARY
        )
        self.update_image_display()
    
    def apply_histogram_equalization(self):
        """Apply histogram equalization"""
        self.processor.push_state()
        self.processor.histogram_equalization()
        self.update_image_display()
    
    def update_kernel_entries(self, *args):
        """Update the kernel entry widgets based on selected size"""
        # Clear existing entries
        for widget in self.kernel_entries_frame.winfo_children():
            widget.destroy()
        self.kernel_entries = []
        
        size = self.kernel_size.get()
        
        # Create entry grid
        for i in range(size):
            row_entries = []
            row_frame = ttk.Frame(self.kernel_entries_frame)
            row_frame.pack(fill=tk.X, pady=1)
            
            for j in range(size):
                entry = ttk.Entry(row_frame, width=5, justify=tk.CENTER)
                # Set default values (identity kernel)
                default_val = 1 if (i == j and i == size//2) else 0
                entry.insert(0, str(default_val))
                entry.pack(side=tk.LEFT, padx=1)
                row_entries.append(entry)
            
            self.kernel_entries.append(row_entries)
    
    def apply_manual_convolution(self):
        """Apply manual convolution with the user-defined kernel"""
        try:
            # Get kernel size
            size = self.kernel_size.get()
            
            # Create kernel from entries
            kernel = np.zeros((size, size), dtype=np.float32)
            for i in range(size):
                for j in range(size):
                    try:
                        val = float(self.kernel_entries[i][j].get())
                        kernel[i, j] = val
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid value at position ({i+1}, {j+1})")
                        return
            
            # Apply convolution
            self.processor.push_state()
            if not self.processor.manual_convolution(kernel):
                raise Exception("Failed to apply convolution")
                
            self.update_image_display()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply convolution: {str(e)}")
    
    def apply_frequency_lowpass(self):
        """Apply frequency domain low-pass filter"""
        self.processor.push_state()
        # Scale the integer value (1-100) to a float (0.01-1.0)
        cutoff = self.freq_cutoff.get() / 100.0
        self.processor.frequency_low_pass(cutoff=cutoff)
        self.update_image_display()
    
    # ==================== COLOR TAB METHODS ====================
    
    def apply_view_channel(self, channel):
        """View specific RGB channel"""
        self.processor.push_state()
        self.processor.view_rgb_channel(channel=channel)
        self.update_image_display()
    
    def apply_view_hsv_channel(self, channel):
        """View specific HSV channel"""
        self.processor.push_state()
        self.processor.view_hsv_channel(channel=channel)
        self.update_image_display()
    
    def apply_grayscale(self):
        """Convert image to grayscale"""
        self.processor.push_state()
        self.processor.convert_to_grayscale()
        self.update_image_display()
    
    def apply_binary_threshold(self):
        """Apply binary thresholding"""
        self.processor.push_state()
        self.processor.convert_to_binary(threshold=self.binary_thresh.get())
        self.update_image_display()
    
    # ==================== GEOMETRIC OPERATIONS ====================
    
    def apply_rotation(self):
        """Apply rotation to the image"""
        self.processor.push_state()
        self.processor.rotate_image(angle=self.rotation_angle.get())
        self.update_image_display()
    
    def apply_flip(self, direction):
        """Flip the image horizontally or vertically"""
        self.processor.push_state()
        self.processor.flip_image(direction=direction)
        self.update_image_display()
    
    
    # ==================== EDGE DETECTION METHODS ====================
    
    def apply_canny(self):
        """Apply Canny edge detection"""
        self.processor.push_state()
        self.processor.canny_edge_detection(
            threshold1=self.canny_thresh1.get(),
            threshold2=self.canny_thresh2.get()
        )
        self.update_image_display()
    
    def apply_sobel(self):
        """Apply Sobel edge detection"""
        self.processor.push_state()
        self.processor.sobel_edge_detection()
        self.update_image_display()
    
    def apply_laplacian(self):
        """Apply Laplacian edge detection"""
        self.processor.push_state()
        self.processor.laplacian_edge_detection()
        self.update_image_display()
        
    def apply_zero_crossing(self):
        """Apply zero-crossing edge detection"""
        if not hasattr(self.processor, 'zero_crossing_edge_detection'):
            messagebox.showerror("Error", "Zero-crossing edge detection is not available")
            return
            
        self.processor.push_state()
        # Convert from integer (1-50) to float (0.1-5.0)
        sigma = self.zero_cross_sigma.get() / 10.0
        self.processor.zero_crossing_edge_detection(sigma=sigma)
        self.update_image_display()
    
    # ==================== FILE OPERATIONS ====================
    
    def save_image(self):
        """Save the current edited image to a file"""
        if not hasattr(self.processor, 'current_image') or self.processor.current_image is None:
            messagebox.showerror("Error", "No image to save")
            return
            
        filetypes = [
            ('PNG files', '*.png'),
            ('JPEG files', '*.jpg;*.jpeg'),
            ('All files', '*.*')
        ]
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=filetypes,
            title="Save Image As"
        )
        
        if filename:
            try:
                # Convert BGR to RGB for saving
                if len(self.processor.current_image.shape) == 3:
                    image_to_save = cv2.cvtColor(self.processor.current_image, cv2.COLOR_BGR2RGB)
                else:
                    image_to_save = self.processor.current_image
                
                # Save the image
                cv2.imwrite(filename, image_to_save)
                messagebox.showinfo("Success", f"Image saved successfully to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def reset_image(self):
        """Reset the image to its original state"""
        if hasattr(self.processor, 'reset_image'):
            self.processor.reset_image()
            self.update_image_display()
        else:
            messagebox.showwarning("Warning", "Cannot reset: No original image available")
    
    def undo_action(self):
        """Undo the last action if possible"""
        if hasattr(self.processor, 'undo') and callable(self.processor.undo):
            try:
                if self.processor.undo():
                    self.update_image_display()
                else:
                    messagebox.showinfo("Info", "No more actions to undo")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to undo action: {str(e)}")
        else:
            messagebox.showinfo("Info", "Undo not available")
            
    def redo_action(self):
        """Redo the last undone action if possible"""
        if hasattr(self.processor, 'redo') and callable(self.processor.redo):
            try:
                if self.processor.redo():
                    self.update_image_display()
                else:
                    messagebox.showinfo("Info", "No more actions to redo")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to redo action: {str(e)}")
        else:
            messagebox.showinfo("Info", "Redo not available")

