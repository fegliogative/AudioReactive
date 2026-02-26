"""
Custom Modal Dialogs for SoundReactive GUI
Replaces default system modals with styled custom dialogs
"""

import tkinter as tk
from tkinter import ttk


class CustomModal:
    """Base class for custom modal dialogs"""
    
    def __init__(self, parent, title, message, modal_type="info"):
        """
        Create a custom modal dialog
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Dialog message
            modal_type: Type of modal ("info", "warning", "error", "success")
        """
        self.parent = parent
        self.result = None
        
        # Create modal window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (200 // 2)
        self.window.geometry(f"400x200+{x}+{y}")
        
        # Configure style based on type
        self.configure_style(modal_type)
        
        # Create content
        self.create_content(title, message, modal_type)
    
    def configure_style(self, modal_type):
        """Configure colors based on modal type"""
        colors = {
            "info": {"bg": "#E3F2FD", "fg": "#1976D2", "accent": "#2196F3"},
            "success": {"bg": "#E8F5E9", "fg": "#388E3C", "accent": "#4CAF50"},
            "warning": {"bg": "#FFF3E0", "fg": "#F57C00", "accent": "#FF9800"},
            "error": {"bg": "#FFEBEE", "fg": "#C62828", "accent": "#F44336"}
        }
        
        self.colors = colors.get(modal_type, colors["info"])
        self.window.configure(bg=self.colors["bg"])
    
    def create_content(self, title, message, modal_type):
        """Create dialog content"""
        # Title frame with icon
        title_frame = tk.Frame(self.window, bg=self.colors["bg"])
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Icon (simple text icon)
        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✕"
        }
        icon_text = icons.get(modal_type, "ℹ")
        
        icon_label = tk.Label(
            title_frame,
            text=icon_text,
            font=("Helvetica", 24, "bold"),
            fg=self.colors["accent"],
            bg=self.colors["bg"]
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        title_label = tk.Label(
            title_frame,
            text=title,
            font=("Helvetica", 16, "bold"),
            fg=self.colors["fg"],
            bg=self.colors["bg"]
        )
        title_label.pack(side=tk.LEFT)
        
        # Message
        message_frame = tk.Frame(self.window, bg=self.colors["bg"])
        message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        message_label = tk.Label(
            message_frame,
            text=message,
            font=("Helvetica", 11),
            fg="#333333",
            bg=self.colors["bg"],
            wraplength=350,
            justify=tk.LEFT
        )
        message_label.pack(anchor=tk.W)
        
        # Button frame
        button_frame = tk.Frame(self.window, bg=self.colors["bg"])
        button_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        self.create_buttons(button_frame)
    
    def create_buttons(self, parent):
        """Create dialog buttons (override in subclasses)"""
        button = tk.Button(
            parent,
            text="OK",
            command=self.on_ok,
            bg=self.colors["accent"],
            fg="white",
            font=("Helvetica", 11, "bold"),
            padx=30,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        button.pack(side=tk.RIGHT)
        
        # Hover effect
        def on_enter(e):
            button.config(bg=self.colors["fg"])
        
        def on_leave(e):
            button.config(bg=self.colors["accent"])
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def on_ok(self):
        """Handle OK button click"""
        self.result = "ok"
        self.window.destroy()
    
    def show(self):
        """Show modal and wait for result"""
        self.window.wait_window()
        return self.result


class CustomMessageBox(CustomModal):
    """Simple message box (info, success, warning, error)"""
    
    @staticmethod
    def showinfo(parent, title, message):
        """Show info message"""
        dialog = CustomModal(parent, title, message, "info")
        return dialog.show()
    
    @staticmethod
    def showsuccess(parent, title, message):
        """Show success message"""
        dialog = CustomModal(parent, title, message, "success")
        return dialog.show()
    
    @staticmethod
    def showwarning(parent, title, message):
        """Show warning message"""
        dialog = CustomModal(parent, title, message, "warning")
        return dialog.show()
    
    @staticmethod
    def showerror(parent, title, message):
        """Show error message"""
        dialog = CustomModal(parent, title, message, "error")
        return dialog.show()


class CustomQuestion(CustomModal):
    """Question dialog with Yes/No buttons"""
    
    def __init__(self, parent, title, message):
        super().__init__(parent, title, message, "info")
    
    def create_buttons(self, parent):
        """Create Yes/No buttons"""
        button_frame = tk.Frame(parent, bg=self.colors["bg"])
        button_frame.pack(side=tk.RIGHT)
        
        no_button = tk.Button(
            button_frame,
            text="No",
            command=self.on_no,
            bg="#757575",
            fg="white",
            font=("Helvetica", 11, "bold"),
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        no_button.pack(side=tk.LEFT, padx=(0, 10))
        
        yes_button = tk.Button(
            button_frame,
            text="Yes",
            command=self.on_yes,
            bg=self.colors["accent"],
            fg="white",
            font=("Helvetica", 11, "bold"),
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        yes_button.pack(side=tk.LEFT)
        
        # Hover effects
        def on_enter_no(e):
            no_button.config(bg="#616161")
        
        def on_leave_no(e):
            no_button.config(bg="#757575")
        
        def on_enter_yes(e):
            yes_button.config(bg=self.colors["fg"])
        
        def on_leave_yes(e):
            yes_button.config(bg=self.colors["accent"])
        
        no_button.bind("<Enter>", on_enter_no)
        no_button.bind("<Leave>", on_leave_no)
        yes_button.bind("<Enter>", on_enter_yes)
        yes_button.bind("<Leave>", on_leave_yes)
    
    def on_yes(self):
        """Handle Yes button click"""
        self.result = "yes"
        self.window.destroy()
    
    def on_no(self):
        """Handle No button click"""
        self.result = "no"
        self.window.destroy()
    
    @staticmethod
    def askyesno(parent, title, message):
        """Ask yes/no question"""
        dialog = CustomQuestion(parent, title, message)
        result = dialog.show()
        return result == "yes"

