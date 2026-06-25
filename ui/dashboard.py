# ui/dashboard.py
import customtkinter as ctk
from database.db import (
    get_room_stats, get_total_sales, get_total_expenses,
    get_low_stock_items, get_connection, get_business_date
)
from datetime import datetime
from ui.font_utils import get_font, get_font_bold, get_font_size

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.font_size = get_font_size()
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="📊 Dashboard",
            font=get_font_bold(28)
        )
        title.pack(pady=(20, 10))
        
        # Stats Grid - This is where stats will be displayed
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Refresh",
            command=self.refresh,
            width=100
        )
        refresh_btn.pack(pady=5)
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(self)
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=get_font_bold(16)
        ).pack(pady=5)
        
        actions_buttons = ctk.CTkFrame(actions_frame)
        actions_buttons.pack(pady=5)
        
        quick_actions = [
            ("🛏️ Check In", self.show_rooms),
            ("💰 Record Sale", self.show_sales),
            ("💸 Add Expense", self.show_expenses),
            ("📦 Add Item", self.show_inventory)
        ]
        
        for text, command in quick_actions:
            ctk.CTkButton(
                actions_buttons,
                text=text,
                command=command,
                width=120
            ).pack(side="left", padx=5)
        
        # Low Stock Alert
        self.low_stock_frame = ctk.CTkFrame(self)
        self.low_stock_frame.pack(fill="x", padx=20, pady=10)
        
        # Load data
        self.load_data()
    
    def load_data(self):
        """Load all dashboard data"""
        self.load_stats()
        self.load_low_stock()
    
    def load_stats(self):
        """Load statistics"""
        # Clear existing widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        business_date = get_business_date()
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get room stats
        occupied, total = get_room_stats()
        
        # Get today's sales
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(total_revenue), SUM(total_profit), COUNT(*)
                FROM sales
                WHERE DATE(sale_date) = ?
            """, (today,))
            sales_data = cursor.fetchone()
            conn.close()
        except Exception as e:
            print(f"Error getting sales: {e}")
            sales_data = (0, 0, 0)
        
        today_revenue = sales_data[0] or 0
        today_profit = sales_data[1] or 0
        today_count = sales_data[2] or 0
        
        # Get today's expenses
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount), COUNT(*)
                FROM expenses
                WHERE DATE(expense_date) = ?
            """, (today,))
            expenses_data = cursor.fetchone()
            conn.close()
        except Exception as e:
            print(f"Error getting expenses: {e}")
            expenses_data = (0, 0)
        
        expenses_total = expenses_data[0] or 0
        expenses_count = expenses_data[1] or 0
        
        # Calculate net profit
        net_profit = today_profit - expenses_total
        
        # Create stats cards
        stats = [
            ("🛏️ Rooms", f"{occupied}/{total}", f"{occupied/total*100:.1f}% Occupied" if total > 0 else "0%"),
            ("💰 Today's Revenue", f"UGX {today_revenue:,.0f}", f"{today_count} transactions"),
            ("📈 Today's Profit", f"UGX {today_profit:,.0f}", "Profit from sales today"),
            ("💸 Today's Expenses", f"UGX {expenses_total:,.0f}", f"{expenses_count} entries"),
            ("📊 Net Profit", f"UGX {net_profit:,.0f}", "Today's Profit - Today's Expenses")
        ]
        
        for title, value, sub in stats:
            card = ctk.CTkFrame(self.stats_frame, fg_color="#1a2a3a")
            card.pack(side="left", padx=5, fill="both", expand=True)
            
            ctk.CTkLabel(card, text=title, font=get_font(font_size)).pack(pady=2)
            ctk.CTkLabel(card, text=value, font=get_font_bold(font_size + 2)).pack(pady=2)
            ctk.CTkLabel(card, text=sub, font=get_font(font_size - 2), text_color="gray").pack(pady=2)
    
    def load_low_stock(self):
        """Load low stock alerts"""
        for widget in self.low_stock_frame.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        low_stock = get_low_stock_items()
        
        if low_stock:
            ctk.CTkLabel(
                self.low_stock_frame,
                text="⚠️ Low Stock Alert",
                font=get_font_bold(font_size + 2),
                text_color="orange"
            ).pack(pady=5)
            
            for name, qty in low_stock:
                ctk.CTkLabel(
                    self.low_stock_frame,
                    text=f"• {name}: {qty} units remaining",
                    font=get_font(font_size),
                    text_color="orange"
                ).pack(anchor="w", padx=20)
        else:
            ctk.CTkLabel(
                self.low_stock_frame,
                text="✅ All items have sufficient stock",
                font=get_font(font_size + 2),
                text_color="green"
            ).pack(pady=5)
    
    def refresh(self):
        """Manually refresh the dashboard"""
        self.load_data()
    
    def show_rooms(self):
        self.master.master.show_rooms()
    
    def show_sales(self):
        self.master.master.show_sales()
    
    def show_expenses(self):
        self.master.master.show_expenses()
    
    def show_inventory(self):
        self.master.master.show_inventory()