# ui/sales.py
import customtkinter as ctk
from database.db import (
    get_sale_items, get_item_price, get_item_type, get_non_inventory_items,
    add_sale_item, get_recent_sales, update_item_stock,
    add_non_inventory_item, delete_non_inventory_item
)
from ui.font_utils import get_font, get_font_bold, get_font_size

class SalesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
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
            text="💰 Sales Management",
            font=get_font_bold(36),
            text_color="#1f538d"
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Record and track all your sales transactions",
            font=get_font(self.font_size),
            text_color="gray"
        ).pack()
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, padx=25, pady=5, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=0)  # Form
        main_container.grid_rowconfigure(1, weight=1)  # Records
        
        # ============ SALES FORM - Modern Card ============
        form_frame = ctk.CTkFrame(
            main_container,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        form_frame.grid(row=0, column=0, padx=5, pady=(0, 15), sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            form_frame,
            text="📝 Record Sale",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        
        # Row 1: Item Type Selection
        row0 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row0.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row0,
            text="Item Type:",
            font=get_font_bold(self.font_size),
            width=100
        ).pack(side="left", padx=5)
        
        self.item_type_var = ctk.StringVar(value="inventory")
        self.inventory_radio = ctk.CTkRadioButton(
            row0,
            text="📦 Inventory",
            variable=self.item_type_var,
            value="inventory",
            command=self.on_type_change,
            font=get_font(self.font_size)
        )
        self.inventory_radio.pack(side="left", padx=10)
        
        self.non_inventory_radio = ctk.CTkRadioButton(
            row0,
            text="🍽️ Non-Inventory (Food/Service)",
            variable=self.item_type_var,
            value="non_inventory",
            command=self.on_type_change,
            font=get_font(self.font_size)
        )
        self.non_inventory_radio.pack(side="left", padx=10)
        
        # Row 2: Item Selection
        row1 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row1,
            text="Item:",
            font=get_font_bold(self.font_size),
            width=100
        ).pack(side="left", padx=5)
        
        self.item_dropdown = ctk.CTkComboBox(
            row1,
            values=self.get_inventory_items(),
            width=280,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.item_dropdown.bind('<<ComboboxSelected>>', self.on_item_select)
        self.item_dropdown.pack(side="left", padx=5)
        
        self.manage_btn = ctk.CTkButton(
            row1,
            text="⚙️ Manage",
            width=90,
            height=38,
            corner_radius=8,
            font=get_font_bold(self.font_size - 1),
            fg_color="#555555",
            hover_color="#444444",
            command=self.manage_non_inventory
        )
        self.manage_btn.pack(side="left", padx=5)
        self.manage_btn.pack_forget()
        
        # Row 3: Quantity and Price
        row2 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        row2.grid_columnconfigure(1, weight=0)
        row2.grid_columnconfigure(3, weight=0)
        
        ctk.CTkLabel(
            row2,
            text="Quantity:",
            font=get_font_bold(self.font_size),
            width=100
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        self.qty_entry = ctk.CTkEntry(
            row2,
            placeholder_text="0",
            width=120,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.qty_entry.grid(row=0, column=1, sticky="w", padx=5)
        self.qty_entry.bind('<KeyRelease>', self.calculate_totals)
        
        self.price_frame = ctk.CTkFrame(row2, fg_color="transparent")
        self.price_frame.grid(row=0, column=2, columnspan=2, sticky="w", padx=5)
        
        ctk.CTkLabel(
            self.price_frame,
            text="Price per unit:",
            font=get_font(self.font_size)
        ).pack(side="left", padx=5)
        
        self.custom_price_entry = ctk.CTkEntry(
            self.price_frame,
            placeholder_text="UGX",
            width=140,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.custom_price_entry.pack(side="left", padx=5)
        self.custom_price_entry.bind('<KeyRelease>', self.calculate_totals)
        self.custom_price_entry.pack_forget()
        
        # Row 4: Price Display
        row3 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row3.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row3,
            text="Selling Price:",
            font=get_font(self.font_size),
            width=110
        ).pack(side="left", padx=5)
        
        self.unit_price_label = ctk.CTkLabel(
            row3,
            text="UGX 0",
            font=get_font_bold(self.font_size),
            width=130,
            text_color="#2ecc71"
        )
        self.unit_price_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row3,
            text="Cost Price:",
            font=get_font(self.font_size),
            width=90
        ).pack(side="left", padx=5)
        
        self.cost_price_label = ctk.CTkLabel(
            row3,
            text="UGX 0",
            font=get_font(self.font_size),
            width=130,
            text_color="#e67e22"
        )
        self.cost_price_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row3,
            text="Profit/Unit:",
            font=get_font_bold(self.font_size),
            width=90
        ).pack(side="left", padx=5)
        
        self.profit_per_unit_label = ctk.CTkLabel(
            row3,
            text="UGX 0",
            font=get_font_bold(self.font_size),
            width=130,
            text_color="#2ecc71"
        )
        self.profit_per_unit_label.pack(side="left", padx=5)
        
        # Row 5: Totals
        row4 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row4.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row4,
            text="Total Revenue:",
            font=get_font_bold(self.font_size),
            width=110
        ).pack(side="left", padx=5)
        
        self.total_revenue_label = ctk.CTkLabel(
            row4,
            text="UGX 0",
            font=get_font_bold(self.font_size + 4),
            width=140,
            text_color="#3498db"
        )
        self.total_revenue_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row4,
            text="Total Cost:",
            font=get_font_bold(self.font_size),
            width=90
        ).pack(side="left", padx=5)
        
        self.total_cost_label = ctk.CTkLabel(
            row4,
            text="UGX 0",
            font=get_font_bold(self.font_size + 4),
            width=140,
            text_color="#e67e22"
        )
        self.total_cost_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            row4,
            text="Total Profit:",
            font=get_font_bold(self.font_size),
            width=90
        ).pack(side="left", padx=5)
        
        self.total_profit_label = ctk.CTkLabel(
            row4,
            text="UGX 0",
            font=get_font_bold(self.font_size + 4),
            width=140,
            text_color="#2ecc71"
        )
        self.total_profit_label.pack(side="left", padx=5)
        
        # Row 6: Notes
        row5 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row5.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row5,
            text="Notes:",
            font=get_font_bold(self.font_size),
            width=100
        ).pack(side="left", padx=5)
        
        self.notes_entry = ctk.CTkEntry(
            row5,
            placeholder_text="Optional notes",
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.notes_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Row 7: Payment Type
        row_payment = ctk.CTkFrame(input_frame, fg_color="transparent")
        row_payment.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row_payment,
            text="Payment Type:",
            font=get_font_bold(self.font_size),
            width=100
        ).pack(side="left", padx=5)
        
        self.payment_type = ctk.StringVar(value="Cash")
        cash_radio = ctk.CTkRadioButton(
            row_payment,
            text="💰 Cash",
            variable=self.payment_type,
            value="Cash",
            font=get_font(self.font_size)
        )
        cash_radio.pack(side="left", padx=10)
        
        merchant_radio = ctk.CTkRadioButton(
            row_payment,
            text="💳 Merchant",
            variable=self.payment_type,
            value="Merchant",
            font=get_font(self.font_size)
        )
        merchant_radio.pack(side="left", padx=10)
        
        # Row 8: Buttons and Stock
        row6 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row6.pack(fill="x", pady=15)
        
        self.record_btn = ctk.CTkButton(
            row6,
            text="💵 Record Sale",
            command=self.record_sale,
            width=160,
            height=45,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#2d8f47",
            hover_color="#1f6a33"
        )
        self.record_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            row6,
            text="🔄 Clear",
            command=self.clear_form,
            width=120,
            height=45,
            corner_radius=10,
            font=get_font_bold(self.font_size),
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=5)
        
        self.stock_label = ctk.CTkLabel(
            row6,
            text="",
            font=get_font(self.font_size - 1),
            text_color="#8899aa"
        )
        self.stock_label.pack(side="left", padx=20)
        
        # ============ SALES RECORDS - Modern Card ============
        records_frame = ctk.CTkFrame(
            main_container,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        records_frame.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="nsew")
        records_frame.grid_columnconfigure(0, weight=1)
        records_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            records_frame,
            text="📋 Sales Records",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        self.records_list = ctk.CTkScrollableFrame(
            records_frame,
            fg_color="transparent"
        )
        self.records_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load data
        self.current_item_data = None
        self.current_item_type = "inventory"
        self.load_sales()
        self.on_type_change()
    
    def get_inventory_items(self):
        """Get inventory items only"""
        items = get_sale_items()
        return items if items else ["No items available"]
    
    def get_non_inventory_items_list(self):
        """Get non-inventory items only"""
        items = get_non_inventory_items()
        return items if items else ["No items available"]
    
    def on_type_change(self):
        """Handle item type change"""
        self.current_item_type = self.item_type_var.get()
        
        if self.current_item_type == "inventory":
            self.item_dropdown.configure(values=self.get_inventory_items())
            self.manage_btn.pack_forget()
            self.custom_price_entry.pack_forget()
            self.unit_price_label.pack(side="left", padx=5)
            self.cost_price_label.pack(side="left", padx=5)
            self.profit_per_unit_label.pack(side="left", padx=5)
            self.stock_label.configure(text="")
        else:
            self.item_dropdown.configure(values=self.get_non_inventory_items_list())
            self.manage_btn.pack(side="left", padx=5)
            self.custom_price_entry.pack(side="left", padx=5)
            self.unit_price_label.pack_forget()
            self.cost_price_label.pack_forget()
            self.profit_per_unit_label.pack_forget()
            self.stock_label.configure(text="Unlimited stock")
        
        self.clear_form()
    
    def on_item_select(self, event=None):
        """When an item is selected, show its details"""
        choice = self.item_dropdown.get()
        
        if choice == "No items available" or not choice:
            return
        
        if self.current_item_type == "inventory":
            item_data = get_item_price(choice)
            if item_data:
                self.current_item_data = item_data
                self.unit_price_label.configure(text=f"UGX {item_data['price']:,.0f}")
                self.cost_price_label.configure(text=f"UGX {item_data['cost']:,.0f}")
                self.profit_per_unit_label.configure(text=f"UGX {item_data['profit_per_unit']:,.0f}")
                self.stock_label.configure(text=f"📦 Stock: {item_data['quantity']} units")
            else:
                self.current_item_data = None
                self.unit_price_label.configure(text="UGX 0")
                self.cost_price_label.configure(text="UGX 0")
                self.profit_per_unit_label.configure(text="UGX 0")
                self.stock_label.configure(text="")
        else:
            self.current_item_data = None
            self.custom_price_entry.focus()
        
        self.calculate_totals()
    
    def calculate_totals(self, event=None):
        """Calculate all totals based on quantity and price"""
        try:
            qty = float(self.qty_entry.get()) if self.qty_entry.get() else 0
            
            if self.current_item_type == "inventory" and self.current_item_data:
                price = self.current_item_data['price']
                cost = self.current_item_data['cost']
                profit_per_unit = self.current_item_data['profit_per_unit']
                
                revenue = qty * price
                total_cost = qty * cost
                total_profit = qty * profit_per_unit
                
                self.unit_price_label.configure(text=f"UGX {price:,.0f}")
                self.cost_price_label.configure(text=f"UGX {cost:,.0f}")
                self.profit_per_unit_label.configure(text=f"UGX {profit_per_unit:,.0f}")
                
            elif self.current_item_type == "non_inventory":
                custom_price_str = self.custom_price_entry.get()
                if custom_price_str:
                    try:
                        price = float(custom_price_str)
                        revenue = qty * price
                        total_cost = 0
                        total_profit = revenue
                    except ValueError:
                        revenue = 0
                        total_cost = 0
                        total_profit = 0
                else:
                    revenue = 0
                    total_cost = 0
                    total_profit = 0
            else:
                revenue = 0
                total_cost = 0
                total_profit = 0
            
            self.total_revenue_label.configure(text=f"UGX {revenue:,.0f}")
            self.total_cost_label.configure(text=f"UGX {total_cost:,.0f}")
            self.total_profit_label.configure(text=f"UGX {total_profit:,.0f}")
            
            if total_profit > 0:
                self.total_profit_label.configure(text_color="#2ecc71")
            elif total_profit < 0:
                self.total_profit_label.configure(text_color="#e74c3c")
            else:
                self.total_profit_label.configure(text_color="gray")
                
        except ValueError:
            self.total_revenue_label.configure(text="UGX 0")
            self.total_cost_label.configure(text="UGX 0")
            self.total_profit_label.configure(text="UGX 0")
    
    def record_sale(self):
        """Record a sale with payment type"""
        item = self.item_dropdown.get()
        qty_str = self.qty_entry.get()
        notes = self.notes_entry.get().strip()
        payment_type = self.payment_type.get()
        
        if item == "No items available" or not item:
            self.show_message("Please select an item", "red")
            return
        
        if not qty_str:
            self.show_message("Please enter quantity", "red")
            return
        
        try:
            qty = float(qty_str)
        except ValueError:
            self.show_message("Please enter a valid quantity", "red")
            return
        
        if qty <= 0:
            self.show_message("Quantity must be greater than 0", "red")
            return
        
        self.record_btn.configure(text="⏳ Processing...", state="disabled")
        self.update_idletasks()
        
        if self.current_item_type == "inventory":
            if not self.current_item_data:
                self.show_message("Please select an inventory item first", "red")
                self.record_btn.configure(text="💵 Record Sale", state="normal")
                return
            
            if qty > self.current_item_data['quantity']:
                self.show_message(f"Insufficient stock! Only {self.current_item_data['quantity']} units available", "red")
                self.record_btn.configure(text="💵 Record Sale", state="normal")
                return
            
            unit_price = self.current_item_data['price']
            cost_price = self.current_item_data['cost']
            total_revenue = qty * unit_price
            total_cost = qty * cost_price
            total_profit = qty * self.current_item_data['profit_per_unit']
            
        else:
            custom_price_str = self.custom_price_entry.get()
            if not custom_price_str:
                self.show_message("Please enter a price for this item", "red")
                self.record_btn.configure(text="💵 Record Sale", state="normal")
                return
            
            try:
                unit_price = float(custom_price_str)
            except ValueError:
                self.show_message("Please enter a valid price", "red")
                self.record_btn.configure(text="💵 Record Sale", state="normal")
                return
            
            if unit_price <= 0:
                self.show_message("Price must be greater than 0", "red")
                self.record_btn.configure(text="💵 Record Sale", state="normal")
                return
            
            cost_price = 0
            total_revenue = qty * unit_price
            total_cost = 0
            total_profit = total_revenue
        
        success, msg = add_sale_item(
            item, 
            qty, 
            unit_price, 
            total_revenue, 
            notes, 
            cost_price,
            payment_type
        )
        
        if success:
            if self.current_item_type == "inventory":
                update_item_stock(item, qty)
            
            self.clear_form()
            self.load_sales()
            if self.current_item_type == "inventory":
                self.item_dropdown.configure(values=self.get_inventory_items())
            else:
                self.item_dropdown.configure(values=self.get_non_inventory_items_list())
            self.show_message(msg, "green")
        else:
            self.show_message(msg, "red")
        
        self.record_btn.configure(text="💵 Record Sale", state="normal")
    
    def manage_non_inventory(self):
        """Open management dialog for non-inventory items"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Manage Non-Inventory Items")
        dialog.geometry("520x420")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        dialog.update_idletasks()
        width = 520
        height = 420
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        font_size = get_font_size()
        
        ctk.CTkLabel(
            dialog,
            text="⚙️ Manage Non-Inventory Items",
            font=get_font_bold(20),
            text_color="#1f538d"
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            dialog,
            text="Food items, services, etc. that don't have inventory tracking",
            font=get_font(font_size - 2),
            text_color="gray"
        ).pack(pady=5)
        
        add_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            add_frame,
            text="Add New Item:",
            font=get_font_bold(font_size)
        ).pack(side="left", padx=5)
        
        self.dialog_name_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Item name",
            width=220,
            height=38,
            corner_radius=8,
            font=get_font(font_size)
        )
        self.dialog_name_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            add_frame,
            text="➕ Add",
            command=lambda: self.dialog_add_item(dialog),
            width=90,
            height=38,
            corner_radius=8,
            font=get_font_bold(font_size),
            fg_color="#2d8f47",
            hover_color="#1f6a33"
        ).pack(side="left", padx=5)
        
        list_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            list_frame,
            text="Current Non-Inventory Items:",
            font=get_font_bold(font_size)
        ).pack(anchor="w", pady=5)
        
        self.dialog_list = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="#1a2a3a",
            corner_radius=8
        )
        self.dialog_list.pack(fill="both", expand=True)
        
        self.dialog_load_items()
    
    def dialog_add_item(self, dialog):
        """Add item from dialog"""
        name = self.dialog_name_entry.get().strip()
        if not name:
            self.dialog_show_message(dialog, "Please enter an item name", "red")
            return
        
        success, msg = add_non_inventory_item(name)
        if success:
            self.dialog_name_entry.delete(0, "end")
            self.dialog_load_items()
            if self.current_item_type == "non_inventory":
                self.item_dropdown.configure(values=self.get_non_inventory_items_list())
            self.dialog_show_message(dialog, msg, "green")
        else:
            self.dialog_show_message(dialog, msg, "red")
    
    def dialog_delete_item(self, dialog, name):
        """Delete item from dialog"""
        confirm = ctk.CTkToplevel(dialog)
        confirm.title("Confirm Delete")
        confirm.geometry("350x160")
        confirm.transient(dialog)
        confirm.grab_set()
        confirm.focus_force()
        confirm.lift()
        
        confirm.update_idletasks()
        width = 350
        height = 160
        x = (confirm.winfo_screenwidth() // 2) - (width // 2)
        y = (confirm.winfo_screenheight() // 2) - (height // 2)
        confirm.geometry(f'{width}x{height}+{x}+{y}')
        
        ctk.CTkLabel(
            confirm,
            text=f"🗑️ Delete '{name}'?",
            font=get_font_bold(18),
            text_color="red"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            confirm,
            text="This action cannot be undone!",
            text_color="red",
            font=get_font(self.font_size - 2)
        ).pack()
        
        btn_frame = ctk.CTkFrame(confirm, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        def do_delete():
            success, msg = delete_non_inventory_item(name)
            confirm.destroy()
            if success:
                self.dialog_load_items()
                if self.current_item_type == "non_inventory":
                    self.item_dropdown.configure(values=self.get_non_inventory_items_list())
                self.dialog_show_message(dialog, msg, "green")
            else:
                self.dialog_show_message(dialog, msg, "red")
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            fg_color="red",
            hover_color="darkred",
            command=do_delete,
            width=120,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=confirm.destroy,
            width=120,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size),
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=10)
    
    def dialog_load_items(self):
        """Load items in dialog"""
        for widget in self.dialog_list.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        items = get_non_inventory_items()
        
        if not items:
            ctk.CTkLabel(
                self.dialog_list,
                text="No non-inventory items",
                font=get_font(font_size),
                text_color="gray"
            ).pack(pady=30)
            return
        
        for item in items:
            row = ctk.CTkFrame(
                self.dialog_list,
                fg_color="#1a2a3a",
                corner_radius=6
            )
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row,
                text=item,
                font=get_font(font_size + 2),
                text_color="#ccddee"
            ).pack(side="left", padx=15, pady=8)
            
            ctk.CTkButton(
                row,
                text="🗑️",
                width=30,
                height=30,
                corner_radius=8,
                fg_color="#6a2a2a",
                hover_color="#5a1a1a",
                command=lambda i=item: self.dialog_delete_item(self.dialog_list.winfo_toplevel(), i)
            ).pack(side="right", padx=10)
    
    def dialog_show_message(self, dialog, msg, color="green"):
        """Show message in dialog"""
        for widget in self.dialog_list.winfo_children():
            if hasattr(widget, "is_message"):
                widget.destroy()
        
        font_size = get_font_size()
        
        label = ctk.CTkLabel(
            self.dialog_list,
            text=msg,
            text_color=color,
            font=get_font_bold(font_size),
            fg_color="#1a2a3a" if color == "green" else "#3a1a1a",
            corner_radius=8,
            padx=20,
            pady=10
        )
        label.is_message = True
        label.pack(pady=10, fill="x")
        
        self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)
    
    def clear_form(self):
        """Clear the form"""
        self.qty_entry.delete(0, "end")
        self.custom_price_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.total_revenue_label.configure(text="UGX 0")
        self.total_cost_label.configure(text="UGX 0")
        self.total_profit_label.configure(text="UGX 0")
        self.unit_price_label.configure(text="UGX 0")
        self.cost_price_label.configure(text="UGX 0")
        self.profit_per_unit_label.configure(text="UGX 0")
        self.current_item_data = None
        
        if self.current_item_type == "inventory":
            self.unit_price_label.pack(side="left", padx=5)
            self.cost_price_label.pack(side="left", padx=5)
            self.profit_per_unit_label.pack(side="left", padx=5)
            self.custom_price_entry.pack_forget()
            self.stock_label.configure(text="")
        else:
            self.custom_price_entry.pack(side="left", padx=5)
            self.unit_price_label.pack_forget()
            self.cost_price_label.pack_forget()
            self.profit_per_unit_label.pack_forget()
            self.stock_label.configure(text="Unlimited stock")
        
        if self.item_dropdown.get() != "No items available":
            self.on_item_select()
    
    def load_sales(self):
        """Load recent sales with profit data and payment type"""
        for widget in self.records_list.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        sales = get_recent_sales()
        
        if not sales:
            ctk.CTkLabel(
                self.records_list,
                text="No sales recorded yet",
                font=get_font(font_size + 2),
                text_color="gray"
            ).pack(pady=30)
            return
        
        # Header
        header = ctk.CTkFrame(
            self.records_list,
            fg_color="#0a1a2a",
            corner_radius=8
        )
        header.pack(fill="x", pady=5)
        
        headers = ["Item", "Qty", "Unit Price", "Revenue", "Cost", "Profit", "Payment", "Date", "Notes"]
        widths = [80, 40, 80, 100, 100, 100, 80, 100, 100]
        
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                header,
                text=h,
                font=get_font_bold(font_size),
                width=w,
                text_color="#8899aa"
            ).pack(side="left", padx=8, pady=8)
        
        for sale in sales:
            item, qty, unit_price, revenue, cost, profit, date, notes, payment_type = sale
            
            row = ctk.CTkFrame(
                self.records_list,
                corner_radius=6
            )
            row.pack(fill="x", pady=2)
            
            item_type = get_item_type(item)
            if item_type == "non_inventory":
                row.configure(fg_color="#1a2a3a")
            
            if payment_type == "Merchant":
                row.configure(fg_color="#1a2a5a")
            
            data = [
                item,
                str(qty),
                f"UGX {unit_price:,.0f}",
                f"UGX {revenue:,.0f}",
                f"UGX {cost:,.0f}",
                f"UGX {profit:,.0f}",
                f"{payment_type}",
                date[:16] if date else "",
                notes or ""
            ]
            
            for i, d in enumerate(data):
                if i == 5:  # Profit column
                    color = "#2ecc71" if profit > 0 else "#e74c3c" if profit < 0 else "gray"
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        text_color=color,
                        font=get_font_bold(font_size)
                    ).pack(side="left", padx=8, pady=6)
                elif i == 6:  # Payment type
                    color = "#2ecc71" if payment_type == "Cash" else "#3498db"
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        text_color=color,
                        font=get_font_bold(font_size)
                    ).pack(side="left", padx=8, pady=6)
                else:
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        anchor="w" if i > 0 else "center",
                        font=get_font(font_size),
                        text_color="#ccddee"
                    ).pack(side="left", padx=8, pady=6)
    
    def show_message(self, msg, color="green"):
        """Show a message"""
        for widget in self.records_list.winfo_children():
            if hasattr(widget, "is_message"):
                widget.destroy()
        
        font_size = get_font_size()
        
        label = ctk.CTkLabel(
            self.records_list,
            text=msg,
            text_color=color,
            font=get_font_bold(font_size),
            fg_color="#1a2a3a" if color == "green" or color == "blue" else "#3a1a1a",
            corner_radius=8,
            padx=20,
            pady=10
        )
        label.is_message = True
        label.pack(pady=10, fill="x")
        
        self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)