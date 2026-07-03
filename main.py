# main.py
import customtkinter as ctk
from PIL import Image, ImageDraw
import os
from database.db import initialize_database, initialize_system, sync_business_date
from ui.dashboard import DashboardFrame
from ui.expenses import ExpensesFrame
from ui.inventory import InventoryFrame
from ui.sales import SalesFrame
from ui.rooms import RoomsFrame
from ui.reports import ReportsFrame
from ui.settings import SettingsFrame
from ui.font_utils import get_font, get_font_bold, get_font_size

# App Settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Initialize Database and System
initialize_database()  # Creates all tables including daily_balance
initialize_system()    # Now daily_balance exists, so this works!
sync_business_date()    

def create_circular_image(image_path, size=(150, 150)):
    """Create a circular image from a file"""
    try:
        # Open the image
        img = Image.open(image_path)
        # Resize the image
        img = img.resize(size, Image.Resampling.LANCZOS)
        
        # Create a mask for circular crop
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        
        # Apply the mask to create circular image
        circular_img = Image.new('RGBA', size, (0, 0, 0, 0))
        circular_img.paste(img, (0, 0), mask)
        
        return circular_img
    except Exception as e:
        print(f"Error creating circular image: {e}")
        return None

class MotelManagementSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Valley View Motel Management System")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Create sidebar (left panel)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Logo/Title Section
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(20, 10))
        
        # Load and display circular logo - try both .png and .jpg
        font_size = get_font_size()
        logo_path_png = os.path.join(os.path.dirname(__file__), "logo.png")
        logo_path_jpg = os.path.join(os.path.dirname(__file__), "logo.jpg")
        
        self.logo_ctk = None  # Store reference to prevent garbage collection
        
        logo_found = False
        if os.path.exists(logo_path_png):
            logo_path = logo_path_png
            logo_found = True
        elif os.path.exists(logo_path_jpg):
            logo_path = logo_path_jpg
            logo_found = True
        
        if logo_found:
            try:
                # Create circular image
                circular_img = create_circular_image(logo_path, size=(150, 150))
                
                if circular_img:
                    # Convert PIL image to CTkImage
                    self.logo_ctk = ctk.CTkImage(
                        light_image=circular_img,
                        dark_image=circular_img,
                        size=(150, 150)
                    )
                    
                    logo_label = ctk.CTkLabel(
                        logo_frame,
                        image=self.logo_ctk,
                        text=""
                    )
                    logo_label.pack(pady=5)
                else:
                    self.show_text_logo(logo_frame)
            except Exception as e:
                print(f"Error loading logo: {e}")
                self.show_text_logo(logo_frame)
        else:
            print("Logo file not found, using text fallback")
            self.show_text_logo(logo_frame)
        
        # Motel Name
        ctk.CTkLabel(
            logo_frame,
            text="Valley View Motel",
            font=get_font_bold(font_size + 2)
        ).pack(pady=(5, 0))
        
        ctk.CTkLabel(
            logo_frame,
            text="Management System",
            font=get_font(font_size - 2),
            text_color="gray"
        ).pack()
        
        # Navigation buttons
        nav_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("💸 Expenses", self.show_expenses),
            ("📦 Inventory", self.show_inventory),
            ("💰 Sales", self.show_sales),
            ("🛏️ Rooms", self.show_rooms),
            ("📈 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings)
        ]
        
        self.nav_buttons = {}
        
        for text, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                fg_color="transparent",
                hover_color=("#2c3e50", "#1a2a3a"),
                anchor="w",
                height=40
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[text] = btn
        
        # Version info
        ctk.CTkLabel(
            self.sidebar,
            text="Version 1.0",
            font=get_font(font_size - 2),
            text_color="gray"
        ).pack(side="bottom", pady=10)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def show_text_logo(self, parent):
        """Fallback text logo if image fails to load"""
        font_size = get_font_size()
        ctk.CTkLabel(
            parent,
            text="🏨 VMS",
            font=get_font_bold(font_size + 24)
        ).pack(pady=5)
    
    def clear_content(self):
        """Clear the content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def highlight_button(self, active_text):
        """Highlight the active navigation button"""
        for text, btn in self.nav_buttons.items():
            if text == active_text:
                btn.configure(fg_color=("#1f538d", "#14375e"))
            else:
                btn.configure(fg_color="transparent")
    
    def refresh_all_ui(self):
        """Refresh all UI components to apply font changes"""
        # Find which page is currently showing
        current_page = None
        for text, btn in self.nav_buttons.items():
            if btn.cget("fg_color") == ("#1f538d", "#14375e"):
                current_page = text
                break
        
        # Refresh the current page
        if current_page == "📊 Dashboard":
            self.show_dashboard()
        elif current_page == "💸 Expenses":
            self.show_expenses()
        elif current_page == "📦 Inventory":
            self.show_inventory()
        elif current_page == "💰 Sales":
            self.show_sales()
        elif current_page == "🛏️ Rooms":
            self.show_rooms()
        elif current_page == "📈 Reports":
            self.show_reports()
        elif current_page == "⚙️ Settings":
            self.show_settings()
        else:
            self.show_dashboard()
    
    def show_dashboard(self):
        self.clear_content()
        self.highlight_button("📊 Dashboard")
        DashboardFrame(self.content_frame).pack(fill="both", expand=True)
    
    def show_expenses(self):
        self.clear_content()
        self.highlight_button("💸 Expenses")
        ExpensesFrame(self.content_frame).pack(fill="both", expand=True)
    
    def show_inventory(self):
        self.clear_content()
        self.highlight_button("📦 Inventory")
        InventoryFrame(self.content_frame).pack(fill="both", expand=True)
    
    def show_sales(self):
        self.clear_content()
        self.highlight_button("💰 Sales")
        SalesFrame(self.content_frame).pack(fill="both", expand=True)
    
    def show_rooms(self):
        self.clear_content()
        self.highlight_button("🛏️ Rooms")
        RoomsFrame(self.content_frame).pack(fill="both", expand=True)
    
    def show_reports(self):
        self.clear_content()
        self.highlight_button("📈 Reports")
        ReportsFrame(self.content_frame).pack(fill="both", expand=True)
    
    def show_settings(self):
        self.clear_content()
        self.highlight_button("⚙️ Settings")
        SettingsFrame(self.content_frame).pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MotelManagementSystem()
    app.mainloop()