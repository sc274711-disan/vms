# ui/dashboard.py
import customtkinter as ctk
from database.db import (
    get_room_stats, get_total_sales, get_total_expenses,
    get_low_stock_items, get_connection, get_business_date,
    get_weekly_start_date, get_weekly_expenses
)
from datetime import datetime, timedelta
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
        
        # Stats Grid
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        self.load_stats()
        
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
        self.load_low_stock()
    
    def load_stats(self):
        """Load statistics - cumulative from start of week"""
        # Clear existing widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        business_date = get_business_date()
        
        print(f"\n=== Dashboard Loading ===")
        print(f"Business Date: {business_date}")
        
        # Get the start of the week (Sunday)
        week_start = get_weekly_start_date(business_date)
        week_end = business_date  # Today
        print(f"Week Start: {week_start}, Week End: {week_end}")
        
        # Get TOTAL revenue for the week (cumulative from Sunday)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT SUM(total_revenue), SUM(total_profit), COUNT(*)
            FROM sales
            WHERE DATE(sale_date) >= ? AND DATE(sale_date) <= ?
        """, (week_start, week_end))
        sales_data = cursor.fetchone()
        conn.close()
        
        week_revenue = sales_data[0] or 0
        week_profit = sales_data[1] or 0
        week_sales_count = sales_data[2] or 0
        
        print(f"Week Revenue: {week_revenue}, Week Profit: {week_profit}")
        
        # Get WEEKLY expenses (cumulative from Sunday to today)
        week_expenses, week_expenses_count = get_weekly_expenses(week_start, week_end)
        
        print(f"Week Expenses: {week_expenses}, Count: {week_expenses_count}")
        
        # Calculate net profit
        net_profit = week_profit - week_expenses
        
        occupied, total = get_room_stats()
        
        # Format week range
        week_start_display = datetime.strptime(week_start, "%Y-%m-%d").strftime("%b %d")
        week_end_display = datetime.strptime(week_end, "%Y-%m-%d").strftime("%b %d")
        week_range = f"{week_start_display} - {week_end_display}"
        
        stats = [
            ("🛏️ Rooms", f"{occupied}/{total}", f"{occupied/total*100:.1f}% Occupied" if total > 0 else "0%"),
            ("💰 Week Revenue", f"UGX {week_revenue:,.0f}", f"Week of {week_range}"),
            ("📈 Week Profit", f"UGX {week_profit:,.0f}", f"{week_sales_count} sales this week"),
            ("💸 Week Expenses", f"UGX {week_expenses:,.0f}", f"{week_expenses_count} expenses this week"),
            ("📊 Net Profit", f"UGX {net_profit:,.0f}", "Week Profit - Week Expenses")
        ]
        
        for title, value, sub in stats:
            card = ctk.CTkFrame(self.stats_frame, fg_color="#1a2a3a")
            card.pack(side="left", padx=5, fill="both", expand=True)
            
            ctk.CTkLabel(card, text=title, font=get_font(font_size)).pack(pady=2)
            ctk.CTkLabel(card, text=value, font=get_font_bold(font_size + 2)).pack(pady=2)
            ctk.CTkLabel(card, text=sub, font=get_font(font_size - 2), text_color="gray").pack(pady=2)
        
        print("=== Dashboard Load Complete ===\n")
    
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
        self.load_stats()
        self.load_low_stock()
    
    def show_rooms(self):
        self.master.master.show_rooms()
    
    def show_sales(self):
        self.master.master.show_sales()
    
    def show_expenses(self):
        self.master.master.show_expenses()
    
    def show_inventory(self):
        self.master.master.show_inventory()