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
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="📦 Inventory Management",
            font=get_font_bold(28)
        )
        title.pack(pady=(20, 10))
        
        # Create main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left Panel - Categories
        left_panel = ctk.CTkFrame(main_container, width=250)
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        ctk.CTkLabel(
            left_panel,
            text="Categories",
            font=get_font_bold(16)
        ).pack(pady=10)
        
        # Add category
        cat_input_frame = ctk.CTkFrame(left_panel)
        cat_input_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(cat_input_frame, text="Category Name:", font=get_font(self.font_size)).pack(anchor="w")
        self.category_entry = ctk.CTkEntry(
            cat_input_frame,
            placeholder_text="Enter category name"
        )
        self.category_entry.pack(fill="x", pady=(2, 5))
        
        ctk.CTkButton(
            cat_input_frame,
            text="➕ Add Category",
            command=self.add_category
        ).pack(fill="x", pady=2)
        
        # Category list
        ctk.CTkLabel(
            left_panel,
            text="Existing Categories:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.category_list = ctk.CTkScrollableFrame(left_panel)
        self.category_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Right Panel - Items
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Search
        search_frame = ctk.CTkFrame(right_panel)
        search_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(search_frame, text="Search:", font=get_font(self.font_size)).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search items by name or category...",
            width=300
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_items,
            width=100
        ).pack(side="right", padx=2)
        
        ctk.CTkButton(
            search_frame,
            text="Clear",
            command=self.load_items,
            width=100
        ).pack(side="right", padx=2)
        
        # Add item form
        form_frame = ctk.CTkFrame(right_panel)
        form_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            form_frame,
            text="Add / Edit Item",
            font=get_font_bold(14)
        ).pack(pady=5)
        
        input_frame = ctk.CTkFrame(form_frame)
        input_frame.pack(fill="x", pady=5)
        
        # Row 1: Item Name and Category
        row1 = ctk.CTkFrame(input_frame)
        row1.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row1, text="Item Name:", font=get_font(self.font_size), width=80).pack(side="left", padx=5)
        self.item_name = ctk.CTkEntry(row1, placeholder_text="e.g., Beer", width=180)
        self.item_name.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Category:", font=get_font(self.font_size), width=70).pack(side="left", padx=5)
        self.item_category = ctk.CTkComboBox(
            row1,
            values=[cat[1] for cat in get_all_categories()],
            width=150
        )
        self.item_category.pack(side="left", padx=5)
        
        # Row 2: Quantity, Cost, Price
        row2 = ctk.CTkFrame(input_frame)
        row2.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row2, text="Quantity:", font=get_font(self.font_size), width=80).pack(side="left", padx=5)
        self.item_quantity = ctk.CTkEntry(row2, placeholder_text="e.g., 50", width=100)
        self.item_quantity.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Cost Price:", font=get_font(self.font_size), width=80).pack(side="left", padx=5)
        self.item_cost = ctk.CTkEntry(row2, placeholder_text="e.g., 4000", width=120)
        self.item_cost.pack(side="left", padx=5)
        
        ctk.CTkLabel(row2, text="Selling Price:", font=get_font(self.font_size), width=90).pack(side="left", padx=5)
        self.item_price = ctk.CTkEntry(row2, placeholder_text="e.g., 5000", width=120)
        self.item_price.pack(side="left", padx=5)
        
        # Row 3: Buttons
        row3 = ctk.CTkFrame(input_frame)
        row3.pack(fill="x", pady=5)
        
        self.add_btn = ctk.CTkButton(
            row3,
            text="➕ Add Item",
            command=self.add_item,
            width=120
        )
        self.add_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            row3,
            text="🔄 Clear Form",
            command=self.clear_item_form,
            width=120
        ).pack(side="left", padx=5)
        
        # Hint text
        ctk.CTkLabel(
            row3,
            text="💡 Tip: To restock, enter quantity to add (e.g., +50)",
            font=get_font(self.font_size - 2),
            text_color="gray"
        ).pack(side="left", padx=20)
        
        # Item list
        ctk.CTkLabel(
            right_panel,
            text="Inventory Items:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w", pady=(10, 5))
        
        self.item_list = ctk.CTkScrollableFrame(right_panel)
        self.item_list.pack(fill="both", expand=True)
        
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
            ).pack(pady=10)
            return
        
        for cat_id, name in categories:
            frame = ctk.CTkFrame(self.category_list)
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                frame,
                text=name,
                font=get_font(font_size)
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                frame,
                text="✕",
                width=25,
                fg_color="red",
                hover_color="darkred",
                command=lambda cid=cat_id: self.delete_category(cid)
            ).pack(side="right", padx=5)
        
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
            ).pack(pady=20)
            return
        
        # Header
        header = ctk.CTkFrame(self.item_list)
        header.pack(fill="x", pady=5)
        
        headers = ["Category", "Item", "Qty", "Cost", "Selling", "Actions"]
        for h in headers:
            ctk.CTkLabel(
                header,
                text=h,
                font=get_font_bold(font_size),
                width=100 if h != "Actions" else 150
            ).pack(side="left", padx=5)
        
        for item in items:
            self.display_item(item)
    
    def display_item(self, item):
        """Display a single item"""
        item_id, category, name, qty, cost, price = item
        font_size = get_font_size()
        
        row = ctk.CTkFrame(self.item_list)
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
        for i, d in enumerate(data):
            ctk.CTkLabel(
                row,
                text=d,
                width=100,
                anchor="w",
                font=get_font(font_size)
            ).pack(side="left", padx=5)
        
        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions,
            text="✏️ Edit",
            width=60,
            command=lambda i=item: self.edit_item(i)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            actions,
            text="➕ Stock",
            width=70,
            command=lambda i=item: self.add_stock(i)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            actions,
            text="🗑️",
            width=30,
            fg_color="red",
            hover_color="darkred",
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
        font_size = get_font_size()
        
        self.editing_item_id = item_id
        self.item_name.delete(0, "end")
        self.item_name.insert(0, name)
        self.item_category.set(category)
        self.item_quantity.delete(0, "end")
        self.item_quantity.insert(0, "0")  # Default to 0 for adding stock
        self.item_quantity.configure(placeholder_text="Enter quantity to add")
        self.item_cost.delete(0, "end")
        self.item_cost.insert(0, str(cost))
        self.item_price.delete(0, "end")
        self.item_price.insert(0, str(price))
        
        self.add_btn.configure(text="🔄 Update (Add Stock)")
        self.show_message(f"Editing: {name}. Enter quantity to ADD to current stock ({qty} units)", "blue")
    
    def add_stock(self, item):
        """Quick stock addition"""
        item_id, category, name, qty, cost, price = item
        font_size = get_font_size()
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Stock")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        # Center the dialog
        dialog.update_idletasks()
        width = 400
        height = 200
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        ctk.CTkLabel(
            dialog,
            text=f"Add Stock: {name}",
            font=get_font_bold(16)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            dialog,
            text=f"Current Stock: {qty} units",
            font=get_font(font_size)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            dialog,
            text="Quantity to Add:",
            font=get_font(font_size)
        ).pack(pady=5)
        
        qty_entry = ctk.CTkEntry(dialog, placeholder_text="Enter quantity", width=150)
        qty_entry.pack(pady=5)
        qty_entry.focus()
        
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)
        
        def confirm():
            try:
                add_qty = float(qty_entry.get())
                if add_qty <= 0:
                    self.show_message("Quantity must be greater than 0", "red")
                    return
                
                # Update stock by adding quantity
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
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120
        ).pack(side="left", padx=5)
    
    def delete_item(self, item):
        """Delete an item"""
        item_id, _, name, _, _, _ = item
        font_size = get_font_size()
        
        # Confirm deletion
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        ctk.CTkLabel(
            dialog,
            text=f"Delete '{name}'?",
            font=get_font_bold(14)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            dialog,
            text="This action cannot be undone!",
            text_color="red",
            font=get_font(font_size - 2)
        ).pack()
        
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=10)
        
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
            text="Delete",
            fg_color="red",
            command=confirm
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        ).pack(side="left", padx=5)
    
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
        self.add_btn.configure(text="➕ Add Item")
    
    def show_message(self, msg, color="green"):
        """Show a message in the item list"""
        # Remove old messages
        for widget in self.item_list.winfo_children():
            if hasattr(widget, "is_message"):
                widget.destroy()
        
        font_size = get_font_size()
        
        label = ctk.CTkLabel(
            self.item_list,
            text=msg,
            text_color=color,
            font=get_font(font_size)
        )
        label.is_message = True
        label.pack(pady=5)
        
        self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)