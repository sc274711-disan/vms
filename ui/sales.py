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
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="💰 Sales Management",
            font=get_font_bold(28)
        )
        title.pack(pady=(20, 10))
        
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sales Form
        form_frame = ctk.CTkFrame(main_container)
        form_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            form_frame,
            text="Record Sale",
            font=get_font_bold(16)
        ).pack(pady=5)
        
        input_frame = ctk.CTkFrame(form_frame)
        input_frame.pack(fill="x", pady=5)
        
        # Row 1: Item Type Selection
        row0 = ctk.CTkFrame(input_frame)
        row0.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row0, text="Item Type:", font=get_font(self.font_size), width=80).pack(side="left", padx=5)
        
        self.item_type_var = ctk.StringVar(value="inventory")
        self.inventory_radio = ctk.CTkRadioButton(
            row0,
            text="📦 Inventory",
            variable=self.item_type_var,
            value="inventory",
            command=self.on_type_change
        )
        self.inventory_radio.pack(side="left", padx=10)
        
        self.non_inventory_radio = ctk.CTkRadioButton(
            row0,
            text="🍽️ Non-Inventory (Food/Service)",
            variable=self.item_type_var,
            value="non_inventory",
            command=self.on_type_change
        )
        self.non_inventory_radio.pack(side="left", padx=10)
        
        # Row 2: Item Selection
        row1 = ctk.CTkFrame(input_frame)
        row1.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row1, text="Item:", font=get_font(self.font_size), width=60).pack(side="left", padx=5)
        self.item_dropdown = ctk.CTkComboBox(
            row1,
            values=self.get_inventory_items(),
            width=250
        )
        self.item_dropdown.bind('<<ComboboxSelected>>', self.on_item_select)
        self.item_dropdown.pack(side="left", padx=5)
        
        # Manage Non-Inventory Items Button
        self.manage_btn = ctk.CTkButton(
            row1,
            text="⚙️ Manage",
            width=80,
            command=self.manage_non_inventory
        )
        self.manage_btn.pack(side="left", padx=5)
        self.manage_btn.pack_forget()  # Hidden by default
        
        # Row 3: Quantity and Price
        row2 = ctk.CTkFrame(input_frame)
        row2.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row2, text="Quantity:", font=get_font(self.font_size), width=60).pack(side="left", padx=5)
        self.qty_entry = ctk.CTkEntry(row2, placeholder_text="0", width=100)
        self.qty_entry.pack(side="left", padx=5)
        self.qty_entry.bind('<KeyRelease>', self.calculate_totals)
        
        # Price entry for non-inventory
        self.price_frame = ctk.CTkFrame(row2, fg_color="transparent")
        self.price_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.price_frame, text="Price per unit:", font=get_font(self.font_size)).pack(side="left", padx=5)
        self.custom_price_entry = ctk.CTkEntry(self.price_frame, placeholder_text="UGX", width=120)
        self.custom_price_entry.pack(side="left", padx=5)
        self.custom_price_entry.bind('<KeyRelease>', self.calculate_totals)
        self.custom_price_entry.pack_forget()  # Hidden by default
        
        # Row 4: Price Display
        row3 = ctk.CTkFrame(input_frame)
        row3.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row3, text="Selling Price:", font=get_font(self.font_size), width=100).pack(side="left", padx=5)
        self.unit_price_label = ctk.CTkLabel(row3, text="UGX 0", font=get_font(self.font_size), width=120)
        self.unit_price_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(row3, text="Cost Price:", font=get_font(self.font_size), width=80).pack(side="left", padx=5)
        self.cost_price_label = ctk.CTkLabel(row3, text="UGX 0", font=get_font(self.font_size), width=120)
        self.cost_price_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(row3, text="Profit/Unit:", font=get_font_bold(self.font_size), width=80).pack(side="left", padx=5)
        self.profit_per_unit_label = ctk.CTkLabel(row3, text="UGX 0", font=get_font_bold(self.font_size), text_color="green", width=120)
        self.profit_per_unit_label.pack(side="left", padx=5)
        
        # Row 5: Totals
        row4 = ctk.CTkFrame(input_frame)
        row4.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row4, text="Total Revenue:", font=get_font_bold(self.font_size), width=100).pack(side="left", padx=5)
        self.total_revenue_label = ctk.CTkLabel(row4, text="UGX 0", font=get_font_bold(self.font_size + 2), text_color="blue", width=120)
        self.total_revenue_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Total Cost:", font=get_font_bold(self.font_size), width=80).pack(side="left", padx=5)
        self.total_cost_label = ctk.CTkLabel(row4, text="UGX 0", font=get_font_bold(self.font_size + 2), text_color="orange", width=120)
        self.total_cost_label.pack(side="left", padx=5)
        
        ctk.CTkLabel(row4, text="Total Profit:", font=get_font_bold(self.font_size), width=80).pack(side="left", padx=5)
        self.total_profit_label = ctk.CTkLabel(row4, text="UGX 0", font=get_font_bold(self.font_size + 2), text_color="green", width=120)
        self.total_profit_label.pack(side="left", padx=5)
        
        # Row 6: Notes
        row5 = ctk.CTkFrame(input_frame)
        row5.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row5, text="Notes:", font=get_font(self.font_size), width=60).pack(side="left", padx=5)
        self.notes_entry = ctk.CTkEntry(row5, placeholder_text="Optional notes", width=300)
        self.notes_entry.pack(side="left", padx=5)
        
        # Row 7: Payment Type
        row_payment = ctk.CTkFrame(input_frame)
        row_payment.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row_payment, text="Payment Type:", font=get_font(self.font_size), width=100).pack(side="left", padx=5)
        
        self.payment_type = ctk.StringVar(value="Cash")
        cash_radio = ctk.CTkRadioButton(
            row_payment,
            text="💰 Cash",
            variable=self.payment_type,
            value="Cash"
        )
        cash_radio.pack(side="left", padx=10)
        
        merchant_radio = ctk.CTkRadioButton(
            row_payment,
            text="💳 Merchant",
            variable=self.payment_type,
            value="Merchant"
        )
        merchant_radio.pack(side="left", padx=10)
        
        # Row 8: Buttons and Stock
        row6 = ctk.CTkFrame(input_frame)
        row6.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            row6,
            text="💵 Record Sale",
            command=self.record_sale,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            row6,
            text="🔄 Clear",
            command=self.clear_form,
            width=100
        ).pack(side="left", padx=5)
        
        self.stock_label = ctk.CTkLabel(row6, text="", font=get_font(self.font_size - 2))
        self.stock_label.pack(side="left", padx=20)
        
        # Sales Records
        records_frame = ctk.CTkFrame(main_container)
        records_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            records_frame,
            text="Sales Records",
            font=get_font_bold(16)
        ).pack(pady=5)
        
        self.records_list = ctk.CTkScrollableFrame(records_frame)
        self.records_list.pack(fill="both", expand=True, pady=5)
        
        # Load data
        self.current_item_data = None
        self.current_item_type = "inventory"
        self.load_sales()
        self.on_type_change()  # Initialize UI state
    
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
            # Show inventory items
            self.item_dropdown.configure(values=self.get_inventory_items())
            self.manage_btn.pack_forget()
            self.custom_price_entry.pack_forget()
            self.unit_price_label.pack(side="left", padx=5)
            self.cost_price_label.pack(side="left", padx=5)
            self.profit_per_unit_label.pack(side="left", padx=5)
            self.stock_label.configure(text="")
        else:
            # Show non-inventory items
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
            # Inventory item
            item_data = get_item_price(choice)
            if item_data:
                self.current_item_data = item_data
                self.unit_price_label.configure(text=f"UGX {item_data['price']:,.0f}")
                self.cost_price_label.configure(text=f"UGX {item_data['cost']:,.0f}")
                self.profit_per_unit_label.configure(text=f"UGX {item_data['profit_per_unit']:,.0f}")
                self.stock_label.configure(text=f"Stock: {item_data['quantity']} units")
            else:
                self.current_item_data = None
                self.unit_price_label.configure(text="UGX 0")
                self.cost_price_label.configure(text="UGX 0")
                self.profit_per_unit_label.configure(text="UGX 0")
                self.stock_label.configure(text="")
        else:
            # Non-inventory item - user enters price
            self.current_item_data = None
            self.custom_price_entry.focus()
        
        self.calculate_totals()
    
    def calculate_totals(self, event=None):
        """Calculate all totals based on quantity and price"""
        try:
            qty = float(self.qty_entry.get()) if self.qty_entry.get() else 0
            
            if self.current_item_type == "inventory" and self.current_item_data:
                # Inventory item - use stored price
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
                # Non-inventory item - use custom price
                custom_price_str = self.custom_price_entry.get()
                if custom_price_str:
                    try:
                        price = float(custom_price_str)
                        revenue = qty * price
                        total_cost = 0  # No cost for non-inventory
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
            
            # Color code profit
            if total_profit > 0:
                self.total_profit_label.configure(text_color="green")
            elif total_profit < 0:
                self.total_profit_label.configure(text_color="red")
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
        
        if self.current_item_type == "inventory":
            # Inventory item
            if not self.current_item_data:
                self.show_message("Please select an inventory item first", "red")
                return
            
            # Check stock
            if qty > self.current_item_data['quantity']:
                self.show_message(f"Insufficient stock! Only {self.current_item_data['quantity']} units available", "red")
                return
            
            unit_price = self.current_item_data['price']
            cost_price = self.current_item_data['cost']
            total_revenue = qty * unit_price
            total_cost = qty * cost_price
            total_profit = qty * self.current_item_data['profit_per_unit']
            
        else:
            # Non-inventory item
            custom_price_str = self.custom_price_entry.get()
            if not custom_price_str:
                self.show_message("Please enter a price for this item", "red")
                return
            
            try:
                unit_price = float(custom_price_str)
            except ValueError:
                self.show_message("Please enter a valid price", "red")
                return
            
            if unit_price <= 0:
                self.show_message("Price must be greater than 0", "red")
                return
            
            cost_price = 0
            total_revenue = qty * unit_price
            total_cost = 0
            total_profit = total_revenue
        
        # Record sale with payment type
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
            # Update stock if inventory item
            if self.current_item_type == "inventory":
                update_item_stock(item, qty)
            
            self.clear_form()
            self.load_sales()
            # Refresh dropdowns
            if self.current_item_type == "inventory":
                self.item_dropdown.configure(values=self.get_inventory_items())
            else:
                self.item_dropdown.configure(values=self.get_non_inventory_items_list())
            self.show_message(msg, "green")
        else:
            self.show_message(msg, "red")
    
    def manage_non_inventory(self):
        """Open management dialog for non-inventory items"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Manage Non-Inventory Items")
        dialog.geometry("500x400")
        
        # Make dialog stay on top
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        # Center the dialog
        dialog.update_idletasks()
        width = 500
        height = 400
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        font_size = get_font_size()
        
        # Title
        ctk.CTkLabel(
            dialog,
            text="Manage Non-Inventory Items",
            font=get_font_bold(18)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            dialog,
            text="Food items, services, etc. that don't have inventory tracking",
            font=get_font(font_size - 2),
            text_color="gray"
        ).pack(pady=5)
        
        # Add new item
        add_frame = ctk.CTkFrame(dialog)
        add_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(add_frame, text="Add New Item:", font=get_font(font_size)).pack(side="left", padx=5)
        self.dialog_name_entry = ctk.CTkEntry(add_frame, placeholder_text="Item name", width=200)
        self.dialog_name_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            add_frame,
            text="➕ Add",
            command=lambda: self.dialog_add_item(dialog),
            width=80
        ).pack(side="left", padx=5)
        
        # Items list
        list_frame = ctk.CTkFrame(dialog)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            list_frame,
            text="Current Non-Inventory Items:",
            font=get_font_bold(font_size)
        ).pack(anchor="w", pady=5)
        
        self.dialog_list = ctk.CTkScrollableFrame(list_frame)
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
            # Refresh main dropdown
            if self.current_item_type == "non_inventory":
                self.item_dropdown.configure(values=self.get_non_inventory_items_list())
            self.dialog_show_message(dialog, msg, "green")
        else:
            self.dialog_show_message(dialog, msg, "red")
    
    def dialog_delete_item(self, dialog, name):
        """Delete item from dialog"""
        # Confirm
        confirm = ctk.CTkToplevel(dialog)
        confirm.title("Confirm Delete")
        confirm.geometry("300x150")
        confirm.transient(dialog)
        confirm.grab_set()
        confirm.focus_force()
        confirm.lift()
        
        font_size = get_font_size()
        
        ctk.CTkLabel(
            confirm,
            text=f"Delete '{name}'?",
            font=get_font(14)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            confirm,
            text="This action cannot be undone!",
            text_color="red"
        ).pack()
        
        btn_frame = ctk.CTkFrame(confirm)
        btn_frame.pack(pady=10)
        
        def do_delete():
            success, msg = delete_non_inventory_item(name)
            confirm.destroy()
            if success:
                self.dialog_load_items()
                # Refresh main dropdown
                if self.current_item_type == "non_inventory":
                    self.item_dropdown.configure(values=self.get_non_inventory_items_list())
                self.dialog_show_message(dialog, msg, "green")
            else:
                self.dialog_show_message(dialog, msg, "red")
        
        ctk.CTkButton(
            btn_frame,
            text="Delete",
            fg_color="red",
            command=do_delete
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=confirm.destroy
        ).pack(side="left", padx=5)
    
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
            ).pack(pady=20)
            return
        
        for item in items:
            row = ctk.CTkFrame(self.dialog_list)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row,
                text=item,
                font=get_font(font_size),
                anchor="w"
            ).pack(side="left", padx=10, fill="x", expand=True)
            
            ctk.CTkButton(
                row,
                text="🗑️",
                width=30,
                fg_color="red",
                hover_color="darkred",
                command=lambda i=item: self.dialog_delete_item(self.dialog_list.winfo_toplevel(), i)
            ).pack(side="right", padx=5)
    
    def dialog_show_message(self, dialog, msg, color="green"):
        """Show message in dialog"""
        # Remove old messages
        for widget in self.dialog_list.winfo_children():
            if hasattr(widget, "is_message"):
                widget.destroy()
        
        font_size = get_font_size()
        
        label = ctk.CTkLabel(
            self.dialog_list,
            text=msg,
            text_color=color,
            font=get_font(font_size)
        )
        label.is_message = True
        label.pack(pady=5)
        
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
        
        # Reset based on type
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
            ).pack(pady=20)
            return
        
        # Header
        header = ctk.CTkFrame(self.records_list)
        header.pack(fill="x", pady=5)
        
        headers = ["Item", "Qty", "Unit Price", "Revenue", "Cost", "Profit", "Payment", "Date", "Notes"]
        widths = [80, 40, 80, 100, 100, 100, 80, 100, 100]
        
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                header,
                text=h,
                font=get_font_bold(font_size),
                width=w
            ).pack(side="left", padx=5)
        
        for sale in sales:
            item, qty, unit_price, revenue, cost, profit, date, notes, payment_type = sale
            
            row = ctk.CTkFrame(self.records_list)
            row.pack(fill="x", pady=2)
            
            # Determine item type for coloring
            item_type = get_item_type(item)
            if item_type == "non_inventory":
                row.configure(fg_color="#1a2a3a")  # Different color for non-inventory
            
            # Color code payment type
            if payment_type == "Merchant":
                row.configure(fg_color="#1a2a5a")  # Blue tint for merchant
            
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
                # Highlight profit column
                if i == 5:
                    color = "green" if profit > 0 else "red" if profit < 0 else "gray"
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        text_color=color,
                        font=get_font_bold(font_size)
                    ).pack(side="left", padx=5)
                elif i == 6:  # Payment type
                    color = "green" if payment_type == "Cash" else "blue"
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        text_color=color,
                        font=get_font(font_size)
                    ).pack(side="left", padx=5)
                else:
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        anchor="w" if i > 0 else "center"
                    ).pack(side="left", padx=5)
    
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
            font=get_font(font_size)
        )
        label.is_message = True
        label.pack(pady=5)
        
        self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)