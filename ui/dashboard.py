# ui/dashboard.py
import customtkinter as ctk
from database.db import (
    get_room_stats, get_total_sales, get_total_expenses,
    get_low_stock_items, get_connection, get_business_date,
    get_weekly_start_date, get_weekly_expenses,
    get_cash_at_hand, get_cash_at_hand_week,
    get_merchant_balance, get_merchant_balance_week
)
from datetime import datetime, timedelta
from ui.font_utils import get_font, get_font_bold, get_font_size

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.font_size = get_font_size()
        
        # Configure grid to fill the entire frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=3)  # Stats rows (larger)
        self.grid_rowconfigure(2, weight=3)  # Cash rows (larger)
        self.grid_rowconfigure(3, weight=0)  # Quick actions
        self.grid_rowconfigure(4, weight=0)  # Low stock
        
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(25, 15), sticky="ew")
        
        title = ctk.CTkLabel(
            title_frame,
            text="📊 Dashboard",
            font=get_font_bold(36),
            text_color="#1f538d"
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Valley View Motel - Performance Overview",
            font=get_font(self.font_size),
            text_color="gray"
        )
        subtitle.pack()
        
        # Stats Grid - Row 1: Overview (5 cards)
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        
        # Configure 5 columns for the 5 cards
        for i in range(5):
            self.stats_frame.grid_columnconfigure(i, weight=1, uniform="stats")
        self.stats_frame.grid_rowconfigure(0, weight=1)
        
        self.load_stats()
        
        # Stats Grid - Row 2: Cash & Merchant (5 cards)
        self.cash_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cash_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        
        # Configure 5 columns for the 5 cards
        for i in range(5):
            self.cash_frame.grid_columnconfigure(i, weight=1, uniform="cash")
        self.cash_frame.grid_rowconfigure(0, weight=1)
        
        self.load_cash_stats()
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=3, column=0, padx=20, pady=15, sticky="ew")
        
        ctk.CTkLabel(
            actions_frame,
            text="⚡ Quick Actions",
            font=get_font_bold(18)
        ).pack(pady=5)
        
        actions_buttons = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_buttons.pack(pady=5)
        
        quick_actions = [
            ("🛏️ Check In", self.show_rooms, "#1f538d"),
            ("💰 Record Sale", self.show_sales, "#2d8f47"),
            ("💸 Add Expense", self.show_expenses, "#c0392b"),
            ("📦 Add Item", self.show_inventory, "#8e44ad")
        ]
        
        for text, command, color in quick_actions:
            btn = ctk.CTkButton(
                actions_buttons,
                text=text,
                command=command,
                width=160,
                height=50,
                fg_color=color,
                hover_color=color,
                corner_radius=10,
                font=get_font_bold(self.font_size + 2)
            )
            btn.pack(side="left", padx=12)
        
        # Low Stock Alert
        self.low_stock_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.low_stock_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.load_low_stock()
    
    def create_stat_card(self, parent, title, value, subtitle, icon="", is_balance=False, row=0, col=0):
        """Create a styled stat card in a grid cell"""
        card = ctk.CTkFrame(
            parent,
            fg_color="#1a2a3a",
            corner_radius=15,
            border_width=2,
            border_color="#2a3a4a"
        )
        card.grid(row=row, column=col, padx=8, pady=5, sticky="nsew")
        
        # Configure card grid for internal layout
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)  # Icon/Title
        card.grid_rowconfigure(1, weight=4)  # Value (larger)
        card.grid_rowconfigure(2, weight=1)  # Subtitle
        
        # Icon and title (Row 0)
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(12, 2))
        header_frame.grid_columnconfigure(1, weight=1)
        
        if icon:
            ctk.CTkLabel(
                header_frame,
                text=icon,
                font=get_font(self.font_size + 10)
            ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=get_font_bold(self.font_size + 2),
            text_color="gray"
        ).grid(row=0, column=1, sticky="w", padx=8)
        
        # Value (Row 1 - center)
        value_color = "white"
        if is_balance:
            if "UGX" in value:
                try:
                    num_str = value.replace("UGX", "").replace(",", "").strip()
                    num = float(num_str) if num_str else 0
                    if num > 0:
                        value_color = "#2ecc71"  # Green
                    elif num < 0:
                        value_color = "#e74c3c"  # Red
                    else:
                        value_color = "white"
                except:
                    pass
        
        ctk.CTkLabel(
            card,
            text=value,
            font=get_font_bold(self.font_size + 10),
            text_color=value_color
        ).grid(row=1, column=0, padx=20, pady=(8, 4))
        
        # Subtitle (Row 2)
        ctk.CTkLabel(
            card,
            text=subtitle,
            font=get_font(self.font_size),
            text_color="gray"
        ).grid(row=2, column=0, padx=20, pady=(4, 15))
        
        return card
    
    def load_stats(self):
        """Load statistics - cumulative from start of week"""
        # Clear existing widgets
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        business_date = get_business_date()
        
        # Get the start of the week (Sunday)
        week_start = get_weekly_start_date(business_date)
        week_end = business_date
        
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
        
        # Get WEEKLY expenses (cumulative from Sunday to today)
        week_expenses, week_expenses_count = get_weekly_expenses(week_start, week_end)
        
        # Calculate net profit
        net_profit = week_profit - week_expenses
        
        occupied, total = get_room_stats()
        
        # Row 1: Stats
        stats = [
            ("🛏️ Rooms", f"{occupied}/{total}", f"{occupied/total*100:.1f}% Occupied" if total > 0 else "0%", "", False),
            ("💰 Revenue", f"UGX {week_revenue:,.0f}", f"{week_sales_count} sales", "📈", False),
            ("📈 Profit", f"UGX {week_profit:,.0f}", "Gross profit", "📊", False),
            ("💸 Expenses", f"UGX {week_expenses:,.0f}", f"{week_expenses_count} entries", "📉", False),
            ("📊 Net Profit", f"UGX {net_profit:,.0f}", "Revenue - Expenses", "🏆", True)
        ]
        
        for col, (title, value, subtitle, icon, is_balance) in enumerate(stats):
            self.create_stat_card(
                self.stats_frame, 
                title, 
                value, 
                subtitle, 
                icon=icon,
                is_balance=is_balance,
                row=0,
                col=col
            )
    
    def load_cash_stats(self):
        """Load cash and merchant statistics"""
        # Clear existing widgets
        for widget in self.cash_frame.winfo_children():
            widget.destroy()
        
        business_date = get_business_date()
        
        # Get the start of the week (Sunday)
        week_start = get_weekly_start_date(business_date)
        week_end = business_date
        
        # Get cash at hand for today
        today_cash = get_cash_at_hand(business_date)
        
        # Get cash at hand for the week
        week_cash = get_cash_at_hand_week(week_start, week_end)
        
        # Get merchant balance for today
        today_merchant = get_merchant_balance(business_date)
        
        # Get merchant balance for the week
        week_merchant = get_merchant_balance_week(week_start, week_end)
        
        # Calculate combined totals
        combined_today = today_cash['cash_balance'] + today_merchant['merchant_balance']
        combined_week = week_cash['cash_balance'] + week_merchant['merchant_balance']
        
        # Row 2: Cash & Merchant Stats
        stats = [
            ("💰 Cash Sales", f"UGX {today_cash['cash_revenue']:,.0f}", f"{today_cash['cash_count']} today", "💵", False),
            ("💸 Cash Expenses", f"UGX {today_cash['cash_expenses']:,.0f}", f"{today_cash['exp_count']} today", "💳", False),
            ("💵 Cash at Hand", f"UGX {today_cash['cash_balance']:,.0f}", f"Week: UGX {week_cash['cash_balance']:,.0f}", "💰", True),
            ("💳 Merchant", f"UGX {today_merchant['merchant_balance']:,.0f}", f"Week: UGX {week_merchant['merchant_balance']:,.0f}", "🏦", True),
            ("📊 Total Balance", f"UGX {combined_today:,.0f}", f"Week: UGX {combined_week:,.0f}", "📊", True)
        ]
        
        for col, (title, value, subtitle, icon, is_balance) in enumerate(stats):
            self.create_stat_card(
                self.cash_frame, 
                title, 
                value, 
                subtitle, 
                icon=icon,
                is_balance=is_balance,
                row=0,
                col=col
            )
    
    def load_low_stock(self):
        """Load low stock alerts"""
        for widget in self.low_stock_frame.winfo_children():
            widget.destroy()
        
        low_stock = get_low_stock_items()
        
        if low_stock:
            alert_frame = ctk.CTkFrame(
                self.low_stock_frame,
                fg_color="#3a1a1a",
                corner_radius=12,
                border_width=1,
                border_color="#5a2a2a"
            )
            alert_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                alert_frame,
                text="⚠️ Low Stock Alert",
                font=get_font_bold(self.font_size + 4),
                text_color="orange"
            ).pack(pady=8)
            
            items_frame = ctk.CTkFrame(alert_frame, fg_color="transparent")
            items_frame.pack(pady=5)
            
            for name, qty in low_stock:
                ctk.CTkLabel(
                    items_frame,
                    text=f"• {name}: {qty} units remaining",
                    font=get_font(self.font_size + 2),
                    text_color="orange"
                ).pack(anchor="w", padx=20, pady=3)
        else:
            alert_frame = ctk.CTkFrame(
                self.low_stock_frame,
                fg_color="#1a3a1a",
                corner_radius=12,
                border_width=1,
                border_color="#2a5a2a"
            )
            alert_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                alert_frame,
                text="✅ All items have sufficient stock",
                font=get_font_bold(self.font_size + 4),
                text_color="green"
            ).pack(pady=18)
    
    def refresh(self):
        """Manually refresh the dashboard"""
        self.load_stats()
        self.load_cash_stats()
        self.load_low_stock()
    
    def show_rooms(self):
        self.master.master.show_rooms()
    
    def show_sales(self):
        self.master.master.show_sales()
    
    def show_expenses(self):
        self.master.master.show_expenses()
    
    def show_inventory(self):
        self.master.master.show_inventory()