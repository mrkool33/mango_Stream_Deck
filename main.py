import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import customtkinter as ctk
import json
import os
import subprocess
import shutil
from pathlib import Path


class StreamDeckApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mango Stream Deck")
        self.root.geometry("900x700")
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")  # "dark" or "light"
        ctk.set_default_color_theme("blue")
        
        # Configure window background
        self.root.configure(bg="#1a1a1a")  # Dark background
        
        # Configure grid weight for responsive layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Grid configuration (default 4 columns x 3 rows)
        self.grid_cols = 4
        self.grid_rows = 3
        
        # Button appearance settings
        self.corner_radius = 15  # Default corner radius
        self.current_theme = "dark"  # Track current theme
        
        # Button configurations storage
        self.button_configs = {}
        self.button_images = {}  # Store PhotoImage references
        self.loaded_image_paths = {}  # Track which images are loaded
        self.config_file = "button_config.json"
        
        # Icons folder for storing selected images
        self.icons_folder = "icons"
        if not os.path.exists(self.icons_folder):
            os.makedirs(self.icons_folder)
        
        # Load saved configurations
        self.load_config()
        
        # Create main container
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title and controls frame
        header_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        header_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Configure grid columns to center buttons
        header_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        header_frame.grid_columnconfigure(1, weight=0)  # Settings button
        header_frame.grid_columnconfigure(2, weight=0)  # Theme button
        header_frame.grid_columnconfigure(3, weight=0)  # Help button
        header_frame.grid_columnconfigure(4, weight=1)  # Right spacer
        
        # Title label
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Mango Stream Deck Control ", 
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=5, pady=15)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            header_frame,
            text="⚙️ Settings",
            width=120,
            text_color="#000000",
            command=self.open_settings,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        settings_btn.grid(row=1, column=1, pady=(0, 15))
        
        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            header_frame,
            text="🌙 Dark Mode" if self.current_theme == "dark" else "☀️ Light Mode",
            width=120,
            text_color="#000000",
            command=self.toggle_theme,
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        self.theme_btn.grid(row=1, column=2, pady=(0, 15), padx=10)
        
        # Help button
        help_btn = ctk.CTkButton(
            header_frame,
            text="❓ Help",
            text_color="#000000",
            width=120,
            command=self.show_instructions,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        help_btn.grid(row=1, column=3, pady=(0, 15))
        
        # Button grid frame
        self.button_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        self.button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame, 
            text="Ready", 
            anchor="w",
            height=30
        )
        self.status_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Create button grid
        self.create_button_grid()
    
    def create_button_grid(self):
        """Create the grid of buttons based on current grid size"""
        # Clear existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        self.buttons = []
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                btn_num = row * self.grid_cols + col + 1
                
                # Get saved config or use defaults
                config = self.button_configs.get(btn_num, {
                    "text": f"Button {btn_num}",
                    "image_path": None,
                    "app_path": None
                })
                
                btn = ctk.CTkButton(
                    self.button_frame,
                    text=config["text"],
                    width=150,
                    height=100,
                    command=lambda num=btn_num: self.button_clicked(num),
                    fg_color="#2196F3",
                    hover_color="#1976D2",
                    text_color="white",
                    font=("Arial", 12, "bold"),
                    corner_radius=self.corner_radius,
                    compound="top"  # Allow text over image
                )
                
                # Right-click to customize - bind to button and all child widgets
                def bind_right_click(widget, num):
                    widget.bind("<Button-3>", lambda e, n=num: self.customize_button(n))
                    for child in widget.winfo_children():
                        bind_right_click(child, num)
                
                bind_right_click(btn, btn_num)
                
                btn.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
                self.buttons.append(btn)
                
                # Apply saved configuration if exists
                if btn_num in self.button_configs:
                    self.update_button_display(btn_num)
                
                # Load image if configured
                if config.get("image_path") and os.path.exists(config["image_path"]):
                    self.set_button_image(btn_num, config["image_path"])
                
                # Make buttons expand with window
                self.button_frame.grid_rowconfigure(row, weight=1)
                self.button_frame.grid_columnconfigure(col, weight=1)
    
    def open_settings(self):
        """Open settings dialog for grid, theme, and appearance"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configure dialog to use CTk appearance
        if self.current_theme == "dark":
            dialog.configure(bg="#2b2b2b")
        else:
            dialog.configure(bg="#ebebeb")
        
        # Settings frame
        settings_frame = ctk.CTkFrame(dialog)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            settings_frame,
            text="Application Settings",
            font=("Arial", 18, "bold")
        ).pack(pady=(10, 20))
        
        # Grid Settings Section
        grid_section = ctk.CTkFrame(settings_frame)
        grid_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            grid_section,
            text="Grid Layout",
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 10))
        
        # Columns
        cols_frame = ctk.CTkFrame(grid_section, fg_color="transparent")
        cols_frame.pack(pady=5)
        ctk.CTkLabel(cols_frame, text="Columns:", width=100).pack(side=tk.LEFT, padx=5)
        cols_var = tk.StringVar(value=str(self.grid_cols))
        cols_entry = ctk.CTkEntry(cols_frame, width=100, textvariable=cols_var)
        cols_entry.pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(cols_frame, text="(1-8)").pack(side=tk.LEFT, padx=5)
        
        # Rows
        rows_frame = ctk.CTkFrame(grid_section, fg_color="transparent")
        rows_frame.pack(pady=5)
        ctk.CTkLabel(rows_frame, text="Rows:", width=100).pack(side=tk.LEFT, padx=5)
        rows_var = tk.StringVar(value=str(self.grid_rows))
        rows_entry = ctk.CTkEntry(rows_frame, width=100, textvariable=rows_var)
        rows_entry.pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(rows_frame, text="(1-8)").pack(side=tk.LEFT, padx=5)
        
        # Appearance Settings Section
        appearance_section = ctk.CTkFrame(settings_frame)
        appearance_section.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            appearance_section,
            text="Appearance",
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 10))
        
        # Corner Radius
        radius_frame = ctk.CTkFrame(appearance_section, fg_color="transparent")
        radius_frame.pack(pady=5)
        ctk.CTkLabel(radius_frame, text="Corner Radius:", width=120).pack(side=tk.LEFT, padx=5)
        radius_var = tk.StringVar(value=str(self.corner_radius))
        radius_entry = ctk.CTkEntry(radius_frame, width=100, textvariable=radius_var)
        radius_entry.pack(side=tk.LEFT, padx=5)
        ctk.CTkLabel(radius_frame, text="(0-50)").pack(side=tk.LEFT, padx=5)
        
        # Theme selector
        theme_frame = ctk.CTkFrame(appearance_section, fg_color="transparent")
        theme_frame.pack(pady=10, padx=10)
        ctk.CTkLabel(theme_frame, text="Theme:", width=120).pack(side=tk.LEFT, padx=5)
        
        theme_var = tk.StringVar(value=self.current_theme)
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light"],
            variable=theme_var,
            width=150
        )
        theme_menu.pack(side=tk.LEFT, padx=5)
        
        def apply_settings():
            try:
                new_cols = int(cols_var.get())
                new_rows = int(rows_var.get())
                new_radius = int(radius_var.get())
                new_theme = theme_var.get()
                
                if new_cols < 1 or new_cols > 8 or new_rows < 1 or new_rows > 8:
                    messagebox.showerror("Invalid Grid Size", "Grid size must be between 1 and 8")
                    return
                
                if new_radius < 0 or new_radius > 50:
                    messagebox.showerror("Invalid Radius", "Corner radius must be between 0 and 50")
                    return
                
                # Apply theme if changed
                if new_theme != self.current_theme:
                    self.current_theme = new_theme
                    ctk.set_appearance_mode(new_theme)
                    self.root.configure(bg="#1a1a1a" if new_theme == "dark" else "#ebebeb")
                    self.theme_btn.configure(
                        text="🌙 Dark Mode" if new_theme == "dark" else "☀️ Light Mode"
                    )
                
                # Apply grid and radius
                self.grid_cols = new_cols
                self.grid_rows = new_rows
                self.corner_radius = new_radius
                
                # Recreate button grid
                self.create_button_grid()
                
                # Save settings
                self.save_config()
                
                self.status_label.configure(
                    text=f"Settings applied: {new_cols}x{new_rows} grid, radius: {new_radius}, theme: {new_theme}"
                )
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid numbers")
        
        def reset_to_defaults():
            # Confirm reset
            if messagebox.askyesno("Reset to Defaults", 
                                  "Are you sure you want to reset all settings and button configurations to default?\n\nThis will:\n• Reset grid to 4x3\n• Reset corner radius to 15\n• Reset theme to dark\n• Clear all button customizations\n• Delete all icons in the icons folder\n\nThis action cannot be undone!"):
                # Clear icons folder
                try:
                    if os.path.exists(self.icons_folder):
                        for file in os.listdir(self.icons_folder):
                            file_path = os.path.join(self.icons_folder, file)
                            try:
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                            except Exception as e:
                                print(f"Error deleting {file_path}: {e}")
                except Exception as e:
                    print(f"Error clearing icons folder: {e}")
                
                # Reset to defaults
                self.grid_cols = 4
                self.grid_rows = 3
                self.corner_radius = 15
                self.current_theme = "dark"
                self.button_configs = {}
                self.button_images = {}
                self.loaded_image_paths = {}
                
                # Apply theme
                ctk.set_appearance_mode("dark")
                self.root.configure(bg="#1a1a1a")
                self.theme_btn.configure(text="🌙 Dark Mode")
                
                # Recreate button grid
                self.create_button_grid()
                
                # Save config
                self.save_config()
                
                self.status_label.configure(text="Settings reset to defaults")
                dialog.destroy()
        
        # Buttons
        btn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="Apply",
            command=apply_settings,
            width=120,
            text_color="#000000",
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side=tk.LEFT, padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Reset to Defaults",
            command=reset_to_defaults,
            width=140,
            text_color="#000000",
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side=tk.LEFT, padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            text_color="#000000",
            fg_color="#f44336",
            hover_color="#da190b"
        ).pack(side=tk.LEFT, padx=10)
    
    def apply_grid(self):
        """Deprecated - now using settings dialog"""
        self.open_settings()
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        if self.current_theme == "dark":
            ctk.set_appearance_mode("light")
            self.current_theme = "light"
            self.root.configure(bg="#ebebeb")  # Light background
            self.theme_btn.configure(text="☀️ Light Mode")
            self.status_label.configure(text="Switched to Light Mode")
        else:
            ctk.set_appearance_mode("dark")
            self.current_theme = "dark"
            self.root.configure(bg="#1a1a1a")  # Dark background
            self.theme_btn.configure(text="🌙 Dark Mode")
            self.status_label.configure(text="Switched to Dark Mode")
    
    def show_instructions(self):
        """Show instructions and help dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("How to Use Stream Deck")
        dialog.geometry("700x800")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Configure dialog theme
        if self.current_theme == "dark":
            dialog.configure(bg="#2b2b2b")
        else:
            dialog.configure(bg="#ebebeb")
        
        # Scrollable content
        scrollable_frame = ctk.CTkScrollableFrame(dialog, width=660, height=750)
        scrollable_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        ctk.CTkLabel(
            scrollable_frame,
            text="📚 Stream Deck - User Guide",
            font=("Arial", 24, "bold")
        ).pack(pady=(10, 20))
        
        # Instructions sections
        sections = [
            {
                "title": "🎯 Getting Started",
                "content": [
                    "• This is a customizable button grid controller",
                    "• Each button can perform different actions",
                    "• Right-click any button to customize it",
                    "• Left-click to execute the button's action"
                ]
            },
            {
                "title": "🎨 Customizing Buttons",
                "content": [
                    "1. Right-click on any button",
                    "2. A customization dialog will open",
                    "3. Configure these sections:",
                    "   • PREVIEW - See your button design",
                    "   • TITLE - Change the button text",
                    "   • TEXT APPEARANCE - Size and color",
                    "   • COLOR - Background color and opacity",
                    "   • ICON - Add an image (PNG, JPG)",
                    "   • ACTION - What happens when clicked",
                    "4. Click 'Save' or 'OK' to apply changes"
                ]
            },
            {
                "title": "⚡ Action Types",
                "content": [
                    "Open - Launch applications (.exe files)",
                    "  → Browse for any program on your computer",
                    "",
                    "Website - Open URLs in browser",
                    "  → Enter any web address (https://...)",
                    "",
                    "Hotkey - Send keyboard shortcuts",
                    "  → Click 'Record' and press your keys",
                    "  → Examples: Ctrl+C, Alt+Tab, Win+D",
                    "  → Requires: pip install pyautogui",
                    "",
                    "Text - Type text automatically",
                    "  → Enter any text to type when clicked",
                    "  → Requires: pip install pyautogui",
                    "",
                    "Multi Action - Coming soon!",
                    "  → Execute multiple actions in sequence"
                ]
            },
            {
                "title": "🎨 Customization Options",
                "content": [
                    "Text Size: 6-72 pixels",
                    "Text Color: Hex codes (#FFFFFF) or names (white)",
                    "Button Color: Choose from presets or custom hex",
                    "Color Opacity: 0-100% transparency",
                    "Icon: Any image file (auto-cropped to fit)",
                    "Icon Opacity: 0-100% transparency"
                ]
            },
            {
                "title": "⚙️ Settings",
                "content": [
                    "Click the '⚙️ Settings' button to:",
                    "• Change grid size (1-8 rows/columns)",
                    "• Adjust button corner radius (0-50)",
                    "• Switch between dark/light themes",
                    "",
                    "All settings are saved automatically!"
                ]
            },
            {
                "title": "💡 Tips & Tricks",
                "content": [
                    "• Double-check action type before saving",
                    "• Use transparent icons for better design",
                    "• Test hotkeys before closing dialog",
                    "• Adjust opacity for layered effects",
                    "• Save frequently to prevent data loss",
                    "• Use descriptive button titles"
                ]
            },
            {
                "title": "🔧 Optional Dependencies",
                "content": [
                    "For Hotkey and Text actions, install:",
                    "  pip install pyautogui",
                    "",
                    "Open PowerShell/Terminal and run the command above"
                ]
            },
            {
                "title": "💾 Data Storage",
                "content": [
                    "All configurations are saved to:",
                    "  button_config.json",
                    "",
                    "This file contains:",
                    "• Grid layout settings",
                    "• Theme preferences",
                    "• All button configurations",
                    "• Actions and customizations"
                ]
            }
        ]
        
        for section in sections:
            # Section frame
            section_frame = ctk.CTkFrame(scrollable_frame, fg_color="#2b2b2b" if self.current_theme == "dark" else "#d0d0d0")
            section_frame.pack(fill="x", pady=(0, 15), padx=10)
            
            # Section title
            ctk.CTkLabel(
                section_frame,
                text=section["title"],
                font=("Arial", 16, "bold"),
                anchor="w"
            ).pack(anchor="w", padx=15, pady=(12, 8))
            
            # Section content
            for line in section["content"]:
                ctk.CTkLabel(
                    section_frame,
                    text=line,
                    font=("Arial", 11),
                    anchor="w",
                    justify="left"
                ).pack(anchor="w", padx=20, pady=2)
            
            # Bottom padding
            ctk.CTkLabel(section_frame, text="", height=5).pack()
        
        # Close button
        ctk.CTkButton(
            scrollable_frame,
            text="Got it!",
            command=dialog.destroy,
            width=200,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049",
            font=("Arial", 14, "bold")
        ).pack(pady=20)
    
    def on_button_resize(self, button_number):
        """Handle button resize event to adjust image"""
        config = self.button_configs.get(button_number, {})
        if config.get("image_path") and os.path.exists(config["image_path"]):
            # Delay to ensure button has finished resizing
            self.root.after(100, lambda: self.set_button_image(button_number, config["image_path"]))
        
    def button_clicked(self, button_number):
        """Handle button click events"""
        config = self.button_configs.get(button_number, {})
        button_name = config.get("text", f"Button {button_number}")
        action_type = config.get("action_type", "Open")
        
        try:
            if action_type == "Open":
                # Launch application
                app_path = config.get("app_path")
                if app_path and os.path.exists(app_path):
                    subprocess.Popen([app_path], shell=True)
                    self.status_label.configure(text=f"Launched: {button_name}")
                    print(f"Launched application: {app_path}")
                else:
                    self.status_label.configure(text=f"{button_name} clicked!")
                    
            elif action_type == "Website":
                # Open URL in browser
                url = config.get("url", "")
                if url and url != "https://":
                    import webbrowser
                    webbrowser.open(url)
                    self.status_label.configure(text=f"Opened: {url}")
                    print(f"Opened URL: {url}")
                else:
                    self.status_label.configure(text="No URL configured")
                    
            elif action_type == "Hotkey":
                # Send hotkey combination
                hotkey = config.get("hotkey", "")
                if hotkey:
                    try:
                        import pyautogui
                        # Parse hotkey (simple implementation)
                        keys = [k.strip().lower() for k in hotkey.split("+")]
                        if len(keys) > 1:
                            # Press modifier keys
                            modifiers = keys[:-1]
                            main_key = keys[-1]
                            pyautogui.hotkey(*keys)
                        else:
                            pyautogui.press(hotkey)
                        self.status_label.configure(text=f"Pressed: {hotkey}")
                        print(f"Pressed hotkey: {hotkey}")
                    except ImportError:
                        messagebox.showwarning("Module Required", "PyAutoGUI module required for hotkey functionality.\nInstall with: pip install pyautogui")
                        self.status_label.configure(text="PyAutoGUI not installed")
                    except Exception as e:
                        self.status_label.configure(text=f"Hotkey error: {e}")
                else:
                    self.status_label.configure(text="No hotkey configured")
                    
            elif action_type == "Text":
                # Type text
                text = config.get("type_text", "")
                if text:
                    try:
                        import pyautogui
                        import time
                        time.sleep(0.1)  # Small delay
                        pyautogui.write(text, interval=0.05)
                        self.status_label.configure(text=f"Typed: {text[:30]}...")
                        print(f"Typed text: {text}")
                    except ImportError:
                        messagebox.showwarning("Module Required", "PyAutoGUI module required for text typing.\nInstall with: pip install pyautogui")
                        self.status_label.configure(text="PyAutoGUI not installed")
                    except Exception as e:
                        self.status_label.configure(text=f"Type error: {e}")
                else:
                    self.status_label.configure(text="No text configured")
                    
            elif action_type == "Multi Action":
                self.status_label.configure(text="Multi Action - Coming soon!")
                
        except Exception as e:
            messagebox.showerror("Action Error", f"Could not execute action: {e}")
            self.status_label.configure(text=f"Error: {e}")
        
        print(f"Button {button_number} ({button_name}) - Action: {action_type}")
    
    def customize_button(self, button_number):
        """Open customization dialog for a button - Stream Deck style"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Configure Key {button_number}")
        dialog.geometry("600x700")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Configure dark theme for dialog
        if self.current_theme == "dark":
            dialog.configure(bg="#2b2b2b")
        else:
            dialog.configure(bg="#f0f0f0")
        
        # Get current config - make a copy to work with
        config = self.button_configs.get(button_number, {
            "text": f"Button {button_number}",
            "image_path": None,
            "app_path": None,
            "color": "#2196F3",  # Default blue color
            "text_size": 12,  # Default text size
            "text_color": "white",  # Default text color
            "color_opacity": 100,  # Default color opacity (0-100)
            "image_opacity": 100  # Default image opacity (0-100)
        }).copy()
        
        # Ensure all keys exist
        if "color" not in config:
            config["color"] = "#2196F3"
        if "text_size" not in config:
            config["text_size"] = 12
        if "text_color" not in config:
            config["text_color"] = "white"
        if "color_opacity" not in config:
            config["color_opacity"] = 100
        if "image_opacity" not in config:
            config["image_opacity"] = 100
        
        # If button doesn't exist in configs, add default
        if button_number not in self.button_configs:
            self.button_configs[button_number] = config.copy()
        
        # Create scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(dialog, width=560, height=650)
        scrollable_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Main container inside scrollable frame
        main_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text=f"Key {button_number}",
            font=("Arial", 20, "bold")
        ).pack(anchor="w")
        
        # Preview Section
        preview_frame = ctk.CTkFrame(main_container)
        preview_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            preview_frame,
            text="PREVIEW",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Button preview
        preview_btn_frame = ctk.CTkFrame(preview_frame, fg_color="transparent")
        preview_btn_frame.pack(pady=(0, 15), padx=15)
        
        preview_btn = ctk.CTkButton(
            preview_btn_frame,
            text=config["text"],
            width=120,
            height=80,
            corner_radius=self.corner_radius,
            fg_color=config["color"],
            text_color=config["text_color"],
            font=("Arial", config["text_size"], "bold"),
            state="disabled"
        )
        preview_btn.pack()
        
        # Title Section
        title_frame = ctk.CTkFrame(main_container)
        title_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            title_frame,
            text="TITLE",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        name_var = tk.StringVar(value=config["text"])
        name_entry = ctk.CTkEntry(
            title_frame,
            textvariable=name_var,
            placeholder_text="Enter button title...",
            height=35,
            font=("Arial", 12)
        )
        name_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        def update_preview(*args):
            preview_btn.configure(text=name_var.get())
        
        name_var.trace('w', update_preview)
        
        # Text Appearance Section
        text_appearance_frame = ctk.CTkFrame(main_container)
        text_appearance_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            text_appearance_frame,
            text="TEXT APPEARANCE",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        text_app_content = ctk.CTkFrame(text_appearance_frame, fg_color="transparent")
        text_app_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # Text size
        ctk.CTkLabel(text_app_content, text="Size:", width=50).pack(side="left", padx=(0, 5))
        text_size_var = tk.StringVar(value=str(config["text_size"]))
        text_size_entry = ctk.CTkEntry(
            text_app_content,
            textvariable=text_size_var,
            width=50
        )
        text_size_entry.pack(side="left", padx=(0, 15))
        
        def update_text_size(*args):
            try:
                size = int(text_size_var.get())
                if 6 <= size <= 72:
                    config["text_size"] = size
                    preview_btn.configure(font=("Arial", size, "bold"))
            except:
                pass
        
        text_size_var.trace('w', update_text_size)
        
        # Text color
        ctk.CTkLabel(text_app_content, text="Color:", width=50).pack(side="left", padx=(0, 5))
        
        # Text color preview
        text_color_preview = ctk.CTkButton(
            text_app_content,
            text="",
            width=30,
            height=25,
            fg_color=config["text_color"],
            hover_color=config["text_color"],
            state="disabled"
        )
        text_color_preview.pack(side="left", padx=(0, 5))
        
        text_color_var = tk.StringVar(value=config["text_color"])
        text_color_entry = ctk.CTkEntry(
            text_app_content,
            textvariable=text_color_var,
            width=80
        )
        text_color_entry.pack(side="left", padx=(0, 10))
        
        def update_text_color(*args):
            try:
                color = text_color_var.get()
                if color.startswith("#") and len(color) == 7:
                    text_color_preview.configure(fg_color=color, hover_color=color)
                    preview_btn.configure(text_color=color)
                    config["text_color"] = color
                elif color.lower() in ["white", "black", "gray"]:
                    text_color_preview.configure(fg_color=color, hover_color=color)
                    preview_btn.configure(text_color=color)
                    config["text_color"] = color
            except:
                pass
        
        text_color_var.trace('w', update_text_color)
        
        # Preset text colors
        preset_text_colors = ["white", "black", "#FFEB3B", "#00BCD4", "#FF5722"]
        for color in preset_text_colors:
            ctk.CTkButton(
                text_app_content,
                text="",
                width=22,
                height=22,
                fg_color=color,
                hover_color=color,
                command=lambda c=color: text_color_var.set(c)
            ).pack(side="left", padx=1)
        
        # Color Section
        color_frame = ctk.CTkFrame(main_container)
        color_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            color_frame,
            text="COLOR",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        color_content = ctk.CTkFrame(color_frame, fg_color="transparent")
        color_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # Color preview box
        color_preview = ctk.CTkButton(
            color_content,
            text="",
            width=40,
            height=30,
            fg_color=config["color"],
            hover_color=config["color"],
            state="disabled"
        )
        color_preview.pack(side="left", padx=(0, 10))
        
        color_var = tk.StringVar(value=config["color"])
        color_entry = ctk.CTkEntry(
            color_content,
            textvariable=color_var,
            placeholder_text="#2196F3",
            width=100
        )
        color_entry.pack(side="left", padx=(0, 10))
        
        def update_color(*args):
            try:
                new_color = color_var.get()
                if new_color.startswith("#") and len(new_color) == 7:
                    color_preview.configure(fg_color=new_color, hover_color=new_color)
                    preview_btn.configure(fg_color=new_color)
                    config["color"] = new_color
            except:
                pass
        
        color_var.trace('w', update_color)
        
        # Preset colors
        preset_colors = ["#2196F3", "#4CAF50", "#F44336", "#FF9800", "#9C27B0", "#607D8B"]
        for color in preset_colors:
            ctk.CTkButton(
                color_content,
                text="",
                width=25,
                height=25,
                fg_color=color,
                hover_color=color,
                command=lambda c=color: color_var.set(c)
            ).pack(side="left", padx=2)
        
        # Color opacity
        opacity_row = ctk.CTkFrame(color_frame, fg_color="transparent")
        opacity_row.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(opacity_row, text="Opacity:", width=60).pack(side="left")
        
        color_opacity_var = tk.IntVar(value=config["color_opacity"])
        color_opacity_slider = ctk.CTkSlider(
            opacity_row,
            from_=0,
            to=100,
            variable=color_opacity_var,
            width=200,
            number_of_steps=100
        )
        color_opacity_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        color_opacity_label = ctk.CTkLabel(opacity_row, text="100%", width=40)
        color_opacity_label.pack(side="left")
        
        def update_color_opacity(*args):
            opacity = color_opacity_var.get()
            color_opacity_label.configure(text=f"{opacity}%")
            config["color_opacity"] = opacity
            
            # Update preview with opacity effect
            try:
                base_color = config["color"]
                opacity_val = opacity / 100.0
                
                if opacity_val < 1.0 and base_color.startswith("#"):
                    # Convert hex to RGB
                    hex_color = base_color.lstrip('#')
                    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    # Blend with dialog background
                    if dialog.cget('bg') == "#2b2b2b":
                        bg_r, bg_g, bg_b = 43, 43, 43
                    else:
                        bg_r, bg_g, bg_b = 240, 240, 240
                    
                    # Apply opacity by blending
                    final_r = int(r * opacity_val + bg_r * (1 - opacity_val))
                    final_g = int(g * opacity_val + bg_g * (1 - opacity_val))
                    final_b = int(b * opacity_val + bg_b * (1 - opacity_val))
                    
                    # Convert back to hex
                    blended_color = f"#{final_r:02x}{final_g:02x}{final_b:02x}"
                    preview_btn.configure(fg_color=blended_color)
                else:
                    preview_btn.configure(fg_color=base_color)
            except:
                pass
        
        color_opacity_var.trace('w', update_color_opacity)
        
        # Icon Section
        icon_frame = ctk.CTkFrame(main_container)
        icon_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            icon_frame,
            text="ICON",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Icon display and buttons
        icon_content = ctk.CTkFrame(icon_frame, fg_color="transparent")
        icon_content.pack(fill="x", padx=15, pady=(0, 15))
        
        # Icon preview box (same size as color preview)
        icon_preview = ctk.CTkLabel(
            icon_content,
            text="",
            width=40,
            height=30,
            fg_color="gray30",
            corner_radius=5
        )
        icon_preview.pack(side="left", padx=(0, 10))
        
        icon_info = ctk.CTkLabel(
            icon_content,
            text=config["image_path"].split("/")[-1] if config["image_path"] else "No icon selected",
            font=("Arial", 10),
            wraplength=250,
            anchor="w"
        )
        icon_info.pack(side="left", fill="x", expand=True)
        
        icon_btn_frame = ctk.CTkFrame(icon_content, fg_color="transparent")
        icon_btn_frame.pack(side="right")
        
        def select_image():
            filename = filedialog.askopenfilename(
                title="Select Icon",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                # Copy image to icons folder
                try:
                    # Get original filename
                    original_name = os.path.basename(filename)
                    # Create unique filename to avoid conflicts
                    base_name, ext = os.path.splitext(original_name)
                    counter = 1
                    new_filename = original_name
                    dest_path = os.path.join(self.icons_folder, new_filename)
                    
                    # Check if file already exists and create unique name if needed
                    while os.path.exists(dest_path) and os.path.abspath(filename) != os.path.abspath(dest_path):
                        new_filename = f"{base_name}_{counter}{ext}"
                        dest_path = os.path.join(self.icons_folder, new_filename)
                        counter += 1
                    
                    # Copy file if it's not already in the icons folder
                    if os.path.abspath(filename) != os.path.abspath(dest_path):
                        shutil.copy2(filename, dest_path)
                    
                    # Update config with new path (old icon deletion happens on Save)
                    config["image_path"] = dest_path
                    icon_info.configure(text=new_filename)
                    
                    # Update icon preview box
                    img = Image.open(dest_path)
                    img.thumbnail((36, 26), Image.Resampling.LANCZOS)
                    icon_thumb = ctk.CTkImage(light_image=img, dark_image=img, size=(36, 26))
                    icon_preview.configure(image=icon_thumb, text="")
                    
                    # Update main preview with icon
                    img = Image.open(dest_path)
                    img = img.resize((100, 66), Image.Resampling.LANCZOS)
                    preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 66))
                    preview_btn.configure(image=preview_img, fg_color="transparent")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy icon: {e}")
                    return
        
        def remove_image():
            # Just clear the config, don't delete the file yet (deletion happens on Save)
            config["image_path"] = None
            icon_info.configure(text="No icon selected")
            icon_preview.configure(image=None, text="", fg_color="gray30")
            preview_btn.configure(image=None, fg_color=config["color"])
        
        ctk.CTkButton(
            icon_btn_frame,
            text="Browse...",
            command=select_image,
            width=80,
            height=28,
            fg_color="#555555",
            hover_color="#666666"
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            icon_btn_frame,
            text="Clear",
            command=remove_image,
            width=60,
            height=28,
            fg_color="#555555",
            hover_color="#666666"
        ).pack(side="left", padx=2)
        
        # Image opacity
        image_opacity_row = ctk.CTkFrame(icon_frame, fg_color="transparent")
        image_opacity_row.pack(fill="x", padx=15, pady=(5, 15))
        
        ctk.CTkLabel(image_opacity_row, text="Opacity:", width=60).pack(side="left")
        
        image_opacity_var = tk.IntVar(value=config["image_opacity"])
        image_opacity_slider = ctk.CTkSlider(
            image_opacity_row,
            from_=0,
            to=100,
            variable=image_opacity_var,
            width=200,
            number_of_steps=100
        )
        image_opacity_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        image_opacity_label = ctk.CTkLabel(image_opacity_row, text="100%", width=40)
        image_opacity_label.pack(side="left")
        
        def update_image_opacity(*args):
            opacity = image_opacity_var.get()
            image_opacity_label.configure(text=f"{opacity}%")
            config["image_opacity"] = opacity
            # Force reload image in preview if one is selected
            if config.get("image_path") and os.path.exists(config["image_path"]):
                try:
                    img = Image.open(config["image_path"])
                    img = img.resize((100, 66), Image.Resampling.LANCZOS)
                    # Apply opacity
                    if opacity < 100:
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        alpha = img.split()[3]
                        alpha = alpha.point(lambda p: int(p * opacity / 100))
                        img.putalpha(alpha)
                    preview_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 66))
                    preview_btn.configure(image=preview_img, fg_color="transparent")
                except:
                    pass
        
        image_opacity_var.trace('w', update_image_opacity)
        
        # Load existing icon preview if available
        if config["image_path"] and os.path.exists(config["image_path"]):
            try:
                img = Image.open(config["image_path"])
                img.thumbnail((36, 26), Image.Resampling.LANCZOS)
                icon_thumb = ctk.CTkImage(light_image=img, dark_image=img, size=(36, 26))
                icon_preview.configure(image=icon_thumb, text="")
            except:
                pass
        
        # Action Section - Elgato Stream Deck Style
        action_frame = ctk.CTkFrame(main_container)
        action_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            action_frame,
            text="ACTION",
            font=("Arial", 11, "bold"),
            text_color="gray"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Action type selector
        action_type_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        action_type_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        # Get current action type from config
        action_type = config.get("action_type", "Open")
        
        # Action type dropdown
        action_type_var = tk.StringVar(value=action_type)
        action_types = ["Open", "Website", "Hotkey", "Text", "Multi Action"]
        
        action_dropdown = ctk.CTkOptionMenu(
            action_type_frame,
            values=action_types,
            variable=action_type_var,
            width=200,
            height=32,
            fg_color="#3a3a3a",
            button_color="#4a4a4a",
            button_hover_color="#5a5a5a"
        )
        action_dropdown.pack(anchor="w")
        
        # Container for action-specific settings
        action_settings_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        action_settings_container.pack(fill="x", padx=15, pady=(0, 15))
        
        # Variables to hold widgets that need updating
        action_widgets = {}
        
        def update_action_settings(*args):
            # Clear current settings
            for widget in action_settings_container.winfo_children():
                widget.destroy()
            action_widgets.clear()
            
            selected_type = action_type_var.get()
            config["action_type"] = selected_type
            
            if selected_type == "Open":
                # Open Application settings
                app_label_frame = ctk.CTkFrame(action_settings_container, fg_color="#2b2b2b", corner_radius=8)
                app_label_frame.pack(fill="x", pady=(0, 10))
                
                ctk.CTkLabel(
                    app_label_frame,
                    text="Application",
                    font=("Arial", 10),
                    text_color="gray"
                ).pack(anchor="w", padx=10, pady=(8, 2))
                
                app_path_display = ctk.CTkLabel(
                    app_label_frame,
                    text=config.get("app_path", "").split("\\")[-1] if config.get("app_path") else "No application selected",
                    font=("Arial", 11),
                    anchor="w"
                )
                app_path_display.pack(anchor="w", padx=10, pady=(0, 8))
                action_widgets["app_display"] = app_path_display
                
                # Browse and clear buttons
                btn_row = ctk.CTkFrame(action_settings_container, fg_color="transparent")
                btn_row.pack(fill="x")
                
                def select_app():
                    filename = filedialog.askopenfilename(
                        title="Select Application",
                        filetypes=[
                            ("Executable files", "*.exe"),
                            ("All files", "*.*")
                        ]
                    )
                    if filename:
                        config["app_path"] = filename
                        action_widgets["app_display"].configure(text=filename.split("\\")[-1])
                
                def clear_app():
                    config["app_path"] = None
                    action_widgets["app_display"].configure(text="No application selected")
                
                ctk.CTkButton(
                    btn_row,
                    text="Browse...",
                    command=select_app,
                    width=100,
                    height=32,
                    fg_color="#3a3a3a",
                    hover_color="#4a4a4a"
                ).pack(side="left", padx=(0, 5))
                
                ctk.CTkButton(
                    btn_row,
                    text="Clear",
                    command=clear_app,
                    width=80,
                    height=32,
                    fg_color="#3a3a3a",
                    hover_color="#4a4a4a"
                ).pack(side="left")
                
            elif selected_type == "Website":
                # Website URL settings
                url_label_frame = ctk.CTkFrame(action_settings_container, fg_color="#2b2b2b", corner_radius=8)
                url_label_frame.pack(fill="x", pady=(0, 10))
                
                ctk.CTkLabel(
                    url_label_frame,
                    text="URL",
                    font=("Arial", 10),
                    text_color="gray"
                ).pack(anchor="w", padx=10, pady=(8, 2))
                
                url_var = tk.StringVar(value=config.get("url", "https://"))
                url_entry = ctk.CTkEntry(
                    url_label_frame,
                    textvariable=url_var,
                    placeholder_text="https://example.com",
                    height=32
                )
                url_entry.pack(fill="x", padx=10, pady=(0, 8))
                
                def update_url(*args):
                    config["url"] = url_var.get()
                
                url_var.trace('w', update_url)
                
            elif selected_type == "Hotkey":
                # Hotkey settings
                hotkey_label_frame = ctk.CTkFrame(action_settings_container, fg_color="#2b2b2b", corner_radius=8)
                hotkey_label_frame.pack(fill="x", pady=(0, 10))
                
                ctk.CTkLabel(
                    hotkey_label_frame,
                    text="Hotkey Combination",
                    font=("Arial", 10),
                    text_color="gray"
                ).pack(anchor="w", padx=10, pady=(8, 2))
                
                # Entry and Record button container
                hotkey_input_frame = ctk.CTkFrame(hotkey_label_frame, fg_color="transparent")
                hotkey_input_frame.pack(fill="x", padx=10, pady=(0, 8))
                
                hotkey_var = tk.StringVar(value=config.get("hotkey", ""))
                hotkey_entry = ctk.CTkEntry(
                    hotkey_input_frame,
                    textvariable=hotkey_var,
                    placeholder_text="Press 'Record' to capture keys",
                    height=32
                )
                hotkey_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
                
                # Recording state
                is_recording = {"value": False, "keys": set()}
                
                record_btn = ctk.CTkButton(
                    hotkey_input_frame,
                    text="🎙️ Record",
                    width=100,
                    height=32,
                    fg_color="#3a3a3a",
                    hover_color="#4a4a4a"
                )
                record_btn.pack(side="left")
                
                def on_key_press(event):
                    if not is_recording["value"]:
                        return
                    
                    # Map key names
                    key = event.keysym
                    
                    # Normalize modifier keys
                    if key in ["Control_L", "Control_R"]:
                        key = "Ctrl"
                    elif key in ["Alt_L", "Alt_R"]:
                        key = "Alt"
                    elif key in ["Shift_L", "Shift_R"]:
                        key = "Shift"
                    elif key in ["Win_L", "Win_R", "Super_L", "Super_R"]:
                        key = "Win"
                    
                    # Add key to set
                    is_recording["keys"].add(key)
                    
                    # Update display
                    keys_list = sorted(is_recording["keys"], key=lambda x: (
                        0 if x == "Ctrl" else 
                        1 if x == "Alt" else 
                        2 if x == "Shift" else 
                        3 if x == "Win" else 4
                    ))
                    hotkey_str = "+".join(keys_list)
                    hotkey_var.set(hotkey_str)
                
                def on_key_release(event):
                    if not is_recording["value"]:
                        return
                    
                    # Stop recording after all keys released
                    # Small delay to ensure we captured the combo
                    dialog.after(100, stop_recording)
                
                def start_recording():
                    is_recording["value"] = True
                    is_recording["keys"].clear()
                    record_btn.configure(text="⏺️ Recording...", fg_color="#E53935")
                    hotkey_entry.configure(placeholder_text="Press key combination now...")
                    hotkey_var.set("")
                    
                    # Bind keyboard events to dialog
                    dialog.bind("<KeyPress>", on_key_press)
                    dialog.bind("<KeyRelease>", on_key_release)
                    dialog.focus_set()
                
                def stop_recording():
                    if not is_recording["value"]:
                        return
                    is_recording["value"] = False
                    record_btn.configure(text="🎙️ Record", fg_color="#3a3a3a")
                    hotkey_entry.configure(placeholder_text="Press 'Record' to capture keys")
                    
                    # Unbind events
                    dialog.unbind("<KeyPress>")
                    dialog.unbind("<KeyRelease>")
                    
                    # Update config
                    config["hotkey"] = hotkey_var.get()
                
                record_btn.configure(command=start_recording)
                
                def update_hotkey(*args):
                    if not is_recording["value"]:
                        config["hotkey"] = hotkey_var.get()
                
                hotkey_var.trace('w', update_hotkey)
                
                ctk.CTkLabel(
                    action_settings_container,
                    text="💡 Click Record and press your key combination",
                    font=("Arial", 9),
                    text_color="gray"
                ).pack(anchor="w", pady=(0, 5))
                
            elif selected_type == "Text":
                # Text typing settings
                text_label_frame = ctk.CTkFrame(action_settings_container, fg_color="#2b2b2b", corner_radius=8)
                text_label_frame.pack(fill="x", pady=(0, 10))
                
                ctk.CTkLabel(
                    text_label_frame,
                    text="Text to Type",
                    font=("Arial", 10),
                    text_color="gray"
                ).pack(anchor="w", padx=10, pady=(8, 2))
                
                text_var = tk.StringVar(value=config.get("type_text", ""))
                text_entry = ctk.CTkEntry(
                    text_label_frame,
                    textvariable=text_var,
                    placeholder_text="Enter text to type...",
                    height=32
                )
                text_entry.pack(fill="x", padx=10, pady=(0, 8))
                
                def update_text(*args):
                    config["type_text"] = text_var.get()
                
                text_var.trace('w', update_text)
                
            elif selected_type == "Multi Action":
                # Multi action placeholder
                multi_label_frame = ctk.CTkFrame(action_settings_container, fg_color="#2b2b2b", corner_radius=8)
                multi_label_frame.pack(fill="x", pady=(0, 10))
                
                ctk.CTkLabel(
                    multi_label_frame,
                    text="⚡ Multi Action",
                    font=("Arial", 11, "bold")
                ).pack(anchor="w", padx=10, pady=(8, 2))
                
                ctk.CTkLabel(
                    multi_label_frame,
                    text="Execute multiple actions in sequence",
                    font=("Arial", 9),
                    text_color="gray"
                ).pack(anchor="w", padx=10, pady=(0, 8))
                
                ctk.CTkLabel(
                    action_settings_container,
                    text="Coming soon: Add multiple actions to execute",
                    font=("Arial", 9),
                    text_color="gray"
                ).pack(anchor="w", pady=(0, 5))
        
        # Initialize with current action type
        action_type_var.trace('w', update_action_settings)
        update_action_settings()
        
        # Bottom buttons
        bottom_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        def save_changes():
            # Check if image was removed and delete old icon if needed
            old_config = self.button_configs.get(button_number, {})
            old_path = old_config.get("image_path")
            new_path = config.get("image_path")
            
            # If icon was removed or changed, delete the old one
            if old_path and old_path != new_path and os.path.exists(old_path):
                if os.path.dirname(os.path.abspath(old_path)) == os.path.abspath(self.icons_folder):
                    # Check if any other button uses this icon
                    is_used = any(
                        btn_config.get("image_path") == old_path 
                        for btn_num, btn_config in self.button_configs.items() 
                        if btn_num != button_number
                    )
                    if not is_used:
                        try:
                            os.remove(old_path)
                        except Exception as e:
                            print(f"Error deleting old icon: {e}")
            
            # Update config with all current values
            config["text"] = name_var.get()
            # config already has image_path and app_path updated from their respective functions
            
            # Save to button_configs
            self.button_configs[button_number] = config.copy()
            
            # Update button display
            self.update_button_display(button_number)
            
            # Save to file
            self.save_config()
            
            # Show confirmation
            self.status_label.configure(text=f"Button {button_number} saved!")
        
        def save_and_close():
            save_changes()
            dialog.destroy()
        
        button_container = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        button_container.pack(side="right")
        
        ctk.CTkButton(
            button_container,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            height=35,
            fg_color="#555555",
            hover_color="#666666"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_container,
            text="Save",
            command=save_changes,
            width=100,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_container,
            text="OK",
            command=save_and_close,
            width=100,
            height=35,
            fg_color="#0066FF",
            hover_color="#0052CC"
        ).pack(side="left", padx=5)
    
    def update_button_display(self, button_number):
        """Update button appearance with new config"""
        btn = self.buttons[button_number - 1]
        config = self.button_configs[button_number]
        
        # Update text
        btn.configure(text=config["text"])
        
        # Update text appearance
        if "text_size" in config:
            btn.configure(font=("Arial", config["text_size"], "bold"))
        if "text_color" in config:
            text_color = config["text_color"]
            btn.configure(text_color=text_color)
        
        # Update color with opacity
        if "color" in config:
            base_color = config["color"]
            opacity = config.get("color_opacity", 100) / 100.0
            
            # Convert hex color to RGB with opacity
            if opacity < 1.0 and base_color.startswith("#"):
                try:
                    # Convert hex to RGB
                    hex_color = base_color.lstrip('#')
                    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    # Blend with background (assuming dark background #2b2b2b)
                    bg_r, bg_g, bg_b = 43, 43, 43 if self.current_theme == "dark" else 235, 235, 235
                    
                    # Apply opacity by blending
                    final_r = int(r * opacity + bg_r * (1 - opacity))
                    final_g = int(g * opacity + bg_g * (1 - opacity))
                    final_b = int(b * opacity + bg_b * (1 - opacity))
                    
                    # Convert back to hex
                    blended_color = f"#{final_r:02x}{final_g:02x}{final_b:02x}"
                    btn.configure(fg_color=blended_color)
                except:
                    btn.configure(fg_color=base_color)
            else:
                btn.configure(fg_color=base_color)
        
        # Update image
        if config["image_path"] and os.path.exists(config["image_path"]):
            self.set_button_image(button_number, config["image_path"])
        else:
            # Remove image and use color - restore fixed size
            btn.configure(
                image=None,
                width=150,
                height=100
            )
            if "color" in config:
                btn.configure(fg_color=config["color"], hover_color=config["color"])
            else:
                btn.configure(fg_color="#2196F3", hover_color="#1976D2")
            if button_number in self.button_images:
                del self.button_images[button_number]
            if button_number in self.loaded_image_paths:
                del self.loaded_image_paths[button_number]
        
        self.status_label.configure(text=f"Button {button_number} updated!")
    
    def set_button_image(self, button_number, image_path):
        """Set background image for a button"""
        try:
            # Check if button still exists
            if button_number > len(self.buttons):
                return
            
            btn = self.buttons[button_number - 1]
            config = self.button_configs[button_number]
            
            # Check if this image is already loaded with same opacity
            current_opacity = config.get("image_opacity", 100)
            cache_key = f"{image_path}_{current_opacity}"
            if button_number in self.loaded_image_paths:
                if self.loaded_image_paths[button_number] == cache_key:
                    return  # Already loaded with same opacity, skip to prevent flickering
            
            # Force consistent button size
            btn_width = 150
            btn_height = 100
            
            # Open and resize image to fit button exactly
            img = Image.open(image_path)
            
            # Calculate aspect ratio and resize to fill button completely
            img_ratio = img.width / img.height
            btn_ratio = btn_width / btn_height
            
            if img_ratio > btn_ratio:
                # Image is wider, fit to height and crop width
                new_height = btn_height
                new_width = int(new_height * img_ratio)
            else:
                # Image is taller, fit to width and crop height
                new_width = btn_width
                new_height = int(new_width / img_ratio)
            
            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop to exact button size (center crop)
            left = (new_width - btn_width) // 2
            top = (new_height - btn_height) // 2
            right = left + btn_width
            bottom = top + btn_height
            img = img.crop((left, top, right, bottom))
            
            # Apply opacity to image
            opacity = config.get("image_opacity", 100) / 100.0
            if opacity < 1.0:
                # Convert to RGBA if needed and apply transparency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                alpha = img.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                img.putalpha(alpha)
            
            # Convert to CTkImage with fixed size
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(btn_width, btn_height))
            
            # Store reference to prevent garbage collection
            self.button_images[button_number] = ctk_img
            self.loaded_image_paths[button_number] = cache_key
            
            # Update button with image - keep fixed size
            btn.configure(
                image=ctk_img,
                width=btn_width,
                height=btn_height,
                fg_color="transparent",
                hover_color="gray25",
                text_color="white"
            )
            
            # Rebind right-click to all child widgets (including image)
            def bind_right_click(widget, num):
                widget.bind("<Button-3>", lambda e, n=num: self.customize_button(n))
                for child in widget.winfo_children():
                    bind_right_click(child, num)
            
            # Wait a moment for image to be created, then bind
            btn.after(10, lambda: bind_right_click(btn, button_number))
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def save_config(self):
        """Save button configurations to file"""
        try:
            config_data = {
                "grid_cols": self.grid_cols,
                "grid_rows": self.grid_rows,
                "corner_radius": self.corner_radius,
                "theme": self.current_theme,
                "buttons": self.button_configs
            }
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def load_config(self):
        """Load button configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    
                    # Check if it's the new format with grid size
                    if isinstance(loaded, dict) and "buttons" in loaded:
                        self.grid_cols = loaded.get("grid_cols", 4)
                        self.grid_rows = loaded.get("grid_rows", 3)
                        self.corner_radius = loaded.get("corner_radius", 15)
                        self.current_theme = loaded.get("theme", "dark")
                        # Apply loaded theme
                        ctk.set_appearance_mode(self.current_theme)
                        self.root.configure(bg="#1a1a1a" if self.current_theme == "dark" else "#ebebeb")
                        self.button_configs = {int(k): v for k, v in loaded["buttons"].items()}
                    else:
                        # Old format - just button configs
                        self.button_configs = {int(k): v for k, v in loaded.items()}
        except Exception as e:
            print(f"Error loading config: {e}")


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = StreamDeckApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
