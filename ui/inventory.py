# ui/inventory.py
import customtkinter as ctk
from database.db import (
    get_all_categories, add_category, delete_category,
    get_all_items, add_item, delete_item, update_item, search_items,
    get_item_by_name
)
from ui.font_utils import get_font, get_font_bold, get_font_size

class InventoryFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.editing_item_id = None
        self.editing_category_id = None
        self.font_size = get_font_size()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=1)  # Main content
        
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(25, 15), sticky="ew")
        
        ctk.CTkLabel(
            title_frame,
            text="📦 Inventory Management",
            font=get_font_bold(36),
            text_color="#1f538d"
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Manage your stock and product categories",
            font=get_font(self.font_size),
            text_color="gray"
        ).pack()
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, padx=25, pady=5, sticky="nsew")
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # ============ LEFT PANEL - CATEGORIES ============
        left_panel = ctk.CTkFrame(
            main_container,
            width=280,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_panel.grid_propagate(False)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Category header
        ctk.CTkLabel(
            left_panel,
            text="📂 Categories",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        # Add category
        cat_input_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        cat_input_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            cat_input_frame,
            text="Category Name:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w")
        
        self.category_entry = ctk.CTkEntry(
            cat_input_frame,
            placeholder_text="Enter category name",
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.category_entry.pack(fill="x", pady=(5, 10))
        
        ctk.CTkButton(
            cat_input_frame,
            text="➕ Add Category",
            command=self.add_category,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size),
            fg_color="#2d8f47",
            hover_color="#1f6a33"
        ).pack(fill="x", pady=2)
        
        # Category list
        ctk.CTkLabel(
            left_panel,
            text="Existing Categories:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        self.category_list = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent"
        )
        self.category_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ============ RIGHT PANEL - ITEMS ============
        right_panel = ctk.CTkFrame(
            main_container,
            fg_color="transparent"
        )
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=0)  # Search
        right_panel.grid_rowconfigure(1, weight=0)  # Form
        right_panel.grid_rowconfigure(2, weight=1)  # List
        
        # Search bar - Modern card
        search_frame = ctk.CTkFrame(
            right_panel,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        search_frame.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=get_font(self.font_size + 6)
        ).grid(row=0, column=0, padx=(15, 5), pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search items by name or category...",
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        
        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_items,
            width=100,
            height=38,
            corner_radius=8,
            font=get_font_bold(self.font_size),
            fg_color="#1f538d",
            hover_color="#14375e"
        ).grid(row=0, column=2, padx=5, pady=10)
        
        ctk.CTkButton(
            search_frame,
            text="Clear",
            command=self.load_items,
            width=80,
            height=38,
            corner_radius=8,
            font=get_font_bold(self.font_size),
            fg_color="#555555",
            hover_color="#444444"
        ).grid(row=0, column=3, padx=(0, 15), pady=10)
        
        # Add/Edit Item Form - Modern card
        form_frame = ctk.CTkFrame(
            right_panel,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        form_frame.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            form_frame,
            text="✏️ Add / Edit Item",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        
        # Row 1: Item Name and Category
        row1 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        row1.grid_columnconfigure(1, weight=1)
        row1.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(
            row1,
            text="Item Name:",
            font=get_font_bold(self.font_size),
            width=100
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        self.item_name = ctk.CTkEntry(
            row1,
            placeholder_text="e.g., Beer",
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.item_name.grid(row=0, column=1, sticky="ew", padx=5)
        
        ctk.CTkLabel(
            row1,
            text="Category:",
            font=get_font_bold(self.font_size),
            width=80
        ).grid(row=0, column=2, sticky="w", padx=5)
        
        self.item_category = ctk.CTkComboBox(
            row1,
            values=[cat[1] for cat in get_all_categories()],
            width=180,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.item_category.grid(row=0, column=3, sticky="w", padx=5)
        
        # Row 2: Quantity, Cost, Price
        row2 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row2,
            text="Quantity:",
            font=get_font_bold(self.font_size),
            width=100
        ).pack(side="left", padx=5)
        
        self.item_quantity = ctk.CTkEntry(
            row2,
            placeholder_text="e.g., 50",
            width=120,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.item_quantity.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row2,
            text="Cost Price:",
            font=get_font_bold(self.font_size),
            width=100
        ).pack(side="left", padx=5)
        
        self.item_cost = ctk.CTkEntry(
            row2,
            placeholder_text="e.g., 4000",
            width=140,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.item_cost.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row2,
            text="Selling Price:",
            font=get_font_bold(self.font_size),
            width=110
        ).pack(side="left", padx=5)
        
        self.item_price = ctk.CTkEntry(
            row2,
            placeholder_text="e.g., 5000",
            width=140,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.item_price.pack(side="left", padx=5)
        
        # Row 3: Buttons
        row3 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row3.pack(fill="x", pady=15)
        
        self.add_btn = ctk.CTkButton(
            row3,
            text="➕ Add Item",
            command=self.add_item,
            width=140,
            height=45,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#2d8f47",
            hover_color="#1f6a33"
        )
        self.add_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            row3,
            text="🔄 Clear Form",
            command=self.clear_item_form,
            width=130,
            height=45,
            corner_radius=10,
            font=get_font_bold(self.font_size),
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row3,
            text="💡 Tip: To restock, enter quantity to add (e.g., +50)",
            font=get_font(self.font_size - 2),
            text_color="gray"
        ).pack(side="left", padx=20)
        
        # Item list - Modern card
        list_frame = ctk.CTkFrame(
            right_panel,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        list_frame.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            list_frame,
            text="📋 Inventory Items",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        self.item_list = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent"
        )
        self.item_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load data
        self.load_categories()
        self.load_items()
    
    def load_categories(self):
        """Load categories into the list"""
        for widget in self.category_list.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        categories = get_all_categories()
        
        if not categories:
            ctk.CTkLabel(
                self.category_list,
                text="No categories yet",
                font=get_font(font_size),
                text_color="gray"
            ).pack(pady=20)
            return
        
        for cat_id, name in categories:
            frame = ctk.CTkFrame(
                self.category_list,
                fg_color="#1a2a3a",
                corner_radius=8
            )
            frame.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                frame,
                text=name,
                font=get_font(font_size + 2),
                text_color="#ccddee"
            ).pack(side="left", padx=15, pady=8)
            
            ctk.CTkButton(
                frame,
                text="✕",
                width=28,
                height=28,
                corner_radius=8,
                fg_color="#6a2a2a",
                hover_color="#5a1a1a",
                command=lambda cid=cat_id: self.delete_category(cid)
            ).pack(side="right", padx=10)
        
        # Update dropdown
        self.item_category.configure(values=[cat[1] for cat in get_all_categories()])
    
    def add_category(self):
        """Add a new category"""
        name = self.category_entry.get().strip()
        if not name:
            self.show_message("Please enter a category name", "red")
            return
        
        success, msg = add_category(name)
        if success:
            self.category_entry.delete(0, "end")
            self.load_categories()
            self.show_message(msg, "green")
        else:
            self.show_message(msg, "red")
    
    def delete_category(self, category_id):
        """Delete a category"""
        success, msg = delete_category(category_id)
        if success:
            self.load_categories()
            self.load_items()
            self.show_message(msg, "green")
        else:
            self.show_message(msg, "red")
    
    def load_items(self):
        """Load all items into the list"""
        for widget in self.item_list.winfo_children():
            widget.destroy()
        
        items = get_all_items()
        self.display_items(items)
    
    def display_items(self, items):
        """Display items in the list"""
        font_size = get_font_size()
        
        if not items:
            ctk.CTkLabel(
                self.item_list,
                text="No items found. Add your first item above!",
                font=get_font(font_size + 2),
                text_color="gray"
            ).pack(pady=30)
            return
        
        # Header
        header = ctk.CTkFrame(
            self.item_list,
            fg_color="#0a1a2a",
            corner_radius=8
        )
        header.pack(fill="x", pady=5)
        
        headers = ["Category", "Item", "Qty", "Cost", "Selling", "Actions"]
        widths = [100, 120, 60, 100, 100, 160]
        
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                header,
                text=h,
                font=get_font_bold(font_size),
                width=w,
                text_color="#8899aa"
            ).pack(side="left", padx=8, pady=8)
        
        for item in items:
            self.display_item(item, font_size)
    
    def display_item(self, item, font_size=None):
        """Display a single item"""
        if font_size is None:
            font_size = get_font_size()
            
        item_id, category, name, qty, cost, price = item
        
        row = ctk.CTkFrame(
            self.item_list,
            corner_radius=6
        )
        row.pack(fill="x", pady=2)
        
        # Color code based on quantity
        if qty <= 0:
            color = "#3a1a1a"  # Red - out of stock
        elif qty <= 5:
            color = "#3a2a1a"  # Orange - low stock
        else:
            color = "#1a2a1a"  # Green - good stock
        
        row.configure(fg_color=color)
        
        data = [category, name, str(qty), f"UGX {cost:,.0f}", f"UGX {price:,.0f}"]
        widths = [100, 120, 60, 100, 100]
        
        for i, d in enumerate(data):
            ctk.CTkLabel(
                row,
                text=d,
                width=widths[i],
                anchor="w",
                font=get_font(font_size),
                text_color="#ccddee"
            ).pack(side="left", padx=8, pady=6)
        
        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions,
            text="✏️",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#2a4a6a",
            hover_color="#1a3a5a",
            command=lambda i=item: self.edit_item(i)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            actions,
            text="➕",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#2d8f47",
            hover_color="#1f6a33",
            command=lambda i=item: self.add_stock(i)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            actions,
            text="🗑️",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#6a2a2a",
            hover_color="#5a1a1a",
            command=lambda i=item: self.delete_item(i)
        ).pack(side="left", padx=2)
    
    def add_item(self):
        """Add a new item or update existing"""
        name = self.item_name.get().strip()
        category = self.item_category.get()
        qty_str = self.item_quantity.get()
        cost_str = self.item_cost.get()
        price_str = self.item_price.get()
        
        if not name:
            self.show_message("Please enter item name", "red")
            return
        
        if not category:
            self.show_message("Please select a category", "red")
            return
        
        try:
            qty = float(qty_str) if qty_str else 0
            cost = float(cost_str) if cost_str else 0
            price = float(price_str) if price_str else 0
        except ValueError:
            self.show_message("Please enter valid numbers for quantity and prices", "red")
            return
        
        if qty < 0:
            self.show_message("Quantity cannot be negative", "red")
            return
        
        if self.editing_item_id:
            # Update existing item - ADD to stock
            success, msg = update_item(self.editing_item_id, name, qty, cost, price, add_to_stock=True)
            if success:
                self.editing_item_id = None
                self.clear_item_form()
                self.load_items()
                self.show_message(msg, "green")
            else:
                self.show_message(msg, "red")
        else:
            # Add new item (case insensitive)
            success, msg = add_item(category, name, qty, cost, price)
            if success:
                self.clear_item_form()
                self.load_items()
                self.show_message(msg, "green")
            else:
                self.show_message(msg, "red")
    
    def edit_item(self, item):
        """Edit an existing item - load into form"""
        item_id, category, name, qty, cost, price = item
        
        self.editing_item_id = item_id
        self.item_name.delete(0, "end")
        self.item_name.insert(0, name)
        self.item_category.set(category)
        self.item_quantity.delete(0, "end")
        self.item_quantity.insert(0, "0")
        self.item_quantity.configure(placeholder_text="Enter quantity to add")
        self.item_cost.delete(0, "end")
        self.item_cost.insert(0, str(cost))
        self.item_price.delete(0, "end")
        self.item_price.insert(0, str(price))
        
        self.add_btn.configure(text="🔄 Update (Add Stock)", fg_color="#f39c12", hover_color="#d68910")
        self.show_message(f"✏️ Editing: {name}. Enter quantity to ADD to current stock ({qty} units)", "blue")
    
    def add_stock(self, item):
        """Quick stock addition"""
        item_id, category, name, qty, cost, price = item
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Stock")
        dialog.geometry("420x230")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        dialog.update_idletasks()
        width = 420
        height = 230
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        ctk.CTkLabel(
            dialog,
            text=f"📦 Add Stock: {name}",
            font=get_font_bold(20),
            text_color="#1f538d"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text=f"Current Stock: {qty} units",
            font=get_font(self.font_size + 2)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            dialog,
            text="Quantity to Add:",
            font=get_font_bold(self.font_size)
        ).pack(pady=5)
        
        qty_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="Enter quantity",
            width=180,
            height=40,
            corner_radius=8,
            font=get_font(self.font_size + 2)
        )
        qty_entry.pack(pady=5)
        qty_entry.focus()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        def confirm():
            try:
                add_qty = float(qty_entry.get())
                if add_qty <= 0:
                    self.show_message("Quantity must be greater than 0", "red")
                    return
                
                success, msg = update_item(item_id, name, add_qty, cost, price, add_to_stock=True)
                dialog.destroy()
                if success:
                    self.load_items()
                    self.show_message(f"✅ Stock updated! New quantity: {qty + add_qty}", "green")
                else:
                    self.show_message(msg, "red")
            except ValueError:
                self.show_message("Please enter a valid number", "red")
        
        ctk.CTkButton(
            btn_frame,
            text="✅ Add Stock",
            command=confirm,
            width=130,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#2d8f47",
            hover_color="#1f6a33"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=130,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=10)
    
    def delete_item(self, item):
        """Delete an item"""
        item_id, _, name, _, _, _ = item
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("350x180")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        dialog.update_idletasks()
        width = 350
        height = 180
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        ctk.CTkLabel(
            dialog,
            text=f"🗑️ Delete '{name}'?",
            font=get_font_bold(18),
            text_color="red"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text="This action cannot be undone!",
            text_color="red",
            font=get_font(self.font_size - 2)
        ).pack()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def confirm():
            success, msg = delete_item(item_id)
            dialog.destroy()
            if success:
                self.load_items()
                self.show_message(msg, "green")
            else:
                self.show_message(msg, "red")
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            fg_color="red",
            hover_color="darkred",
            command=confirm,
            width=120,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size),
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=10)
    
    def search_items(self):
        """Search items"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.load_items()
            return
        
        items = search_items(keyword)
        
        for widget in self.item_list.winfo_children():
            widget.destroy()
        
        self.display_items(items)
    
    def clear_item_form(self):
        """Clear item form"""
        self.item_name.delete(0, "end")
        self.item_quantity.delete(0, "end")
        self.item_quantity.configure(placeholder_text="e.g., 50")
        self.item_cost.delete(0, "end")
        self.item_price.delete(0, "end")
        self.editing_item_id = None
        self.add_btn.configure(text="➕ Add Item", fg_color="#2d8f47", hover_color="#1f6a33")
    
    def show_message(self, msg, color="green"):
        """Show a message in the item list"""
        for widget in self.item_list.winfo_children():
            if hasattr(widget, "is_message"):
                widget.destroy()
        
        label = ctk.CTkLabel(
            self.item_list,
            text=msg,
            text_color=color,
            font=get_font_bold(self.font_size),
            fg_color="#1a2a3a" if color == "green" or color == "blue" else "#3a1a1a",
            corner_radius=8,
            padx=20,
            pady=10
        )
        label.is_message = True
        label.pack(pady=10, fill="x")
        
        self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)