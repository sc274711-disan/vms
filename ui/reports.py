# ui/reports.py
# ui/reports.py - Add at top
from ui.font_utils import get_font, get_font_bold, get_font_size

# Then replace all font declarations with get_font() and get_font_bold()
import customtkinter as ctk
from database.db import (
    get_daily_report, get_weekly_report, get_weekly_report_data,
    get_daily_balance, get_sales_by_payment_type
)
from datetime import datetime, timedelta
import csv

class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="📈 Reports",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=(20, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="📊 Daily Report",
            command=self.show_daily_report,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📈 Weekly Report",
            command=self.show_weekly_report,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📊 Balance Report",
            command=self.show_balance_report,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📥 Export CSV",
            command=self.export_report,
            width=150
        ).pack(side="left", padx=5)
        
        # Report display
        self.report_frame = ctk.CTkScrollableFrame(self)
        self.report_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Show daily report by default
        self.show_daily_report()
    
    def clear_report(self):
        """Clear the report frame"""
        for widget in self.report_frame.winfo_children():
            widget.destroy()
    
    def show_daily_report(self):
        """Show daily report with profit and payment breakdown"""
        self.clear_report()
        
        date = datetime.now().strftime("%Y-%m-%d")
        report = get_daily_report(date)
        
        ctk.CTkLabel(
            self.report_frame,
            text=f"📊 Daily Report - {date}",
            font=("Arial", 20, "bold")
        ).pack(pady=10)
        
        # Check if it's Saturday (Collection Day)
        if report.get('is_saturday', False):
            collection_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a3a1a")
            collection_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                collection_frame,
                text="💰 SATURDAY - CASH COLLECTION DAY 💰",
                font=("Arial", 16, "bold"),
                text_color="gold"
            ).pack(pady=5)
            
            ctk.CTkLabel(
                collection_frame,
                text=f"Cash Collected: UGX {report.get('cash_collected', 0):,.0f}",
                font=("Arial", 12)
            ).pack(pady=2)
            
            ctk.CTkLabel(
                collection_frame,
                text=f"Merchant Collected: UGX {report.get('merchant_collected', 0):,.0f}",
                font=("Arial", 12)
            ).pack(pady=2)
            
            ctk.CTkLabel(
                collection_frame,
                text=f"Total Collected: UGX {report.get('cash_collected', 0) + report.get('merchant_collected', 0):,.0f}",
                font=("Arial", 14, "bold"),
                text_color="green"
            ).pack(pady=2)
        
        # Balance Summary
        balance_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a2a3a")
        balance_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(balance_frame, text="BALANCE SUMMARY", font=("Arial", 14, "bold")).pack(pady=5)
        
        balance_stats = [
            ("Opening Balance", f"UGX {report.get('opening_balance', 0):,.0f}"),
            ("Closing Balance", f"UGX {report.get('closing_balance', 0):,.0f}")
        ]
        
        for label, value in balance_stats:
            row = ctk.CTkFrame(balance_frame)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=("Arial", 12)).pack(side="left", padx=20)
            ctk.CTkLabel(row, text=value, font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        # Payment Type Breakdown
        payment_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a2a3a")
        payment_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(payment_frame, text="PAYMENT BREAKDOWN", font=("Arial", 14, "bold")).pack(pady=5)
        
        payment_stats = [
            ("Cash Sales", f"UGX {report.get('cash_sales', 0):,.0f}"),
            ("Merchant Sales", f"UGX {report.get('merchant_sales', 0):,.0f}")
        ]
        
        for label, value in payment_stats:
            row = ctk.CTkFrame(payment_frame)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=("Arial", 12)).pack(side="left", padx=20)
            ctk.CTkLabel(row, text=value, font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        # Sales Summary
        sales_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a2a3a")
        sales_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(sales_frame, text="SALES SUMMARY", font=("Arial", 14, "bold")).pack(pady=5)
        
        sales_stats = [
            ("Total Revenue", f"UGX {report['sales_revenue']:,.0f}"),
            ("Cost of Goods", f"UGX {report['sales_cost']:,.0f}"),
            ("Gross Profit", f"UGX {report['sales_profit']:,.0f}"),
            ("Transactions", str(report['sales_count']))
        ]
        
        for label, value in sales_stats:
            row = ctk.CTkFrame(sales_frame)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=("Arial", 12)).pack(side="left", padx=20)
            ctk.CTkLabel(row, text=value, font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        # Expenses
        expenses_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a2a3a")
        expenses_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(expenses_frame, text="EXPENSES", font=("Arial", 14, "bold")).pack(pady=5)
        
        exp_row = ctk.CTkFrame(expenses_frame)
        exp_row.pack(fill="x", pady=2)
        ctk.CTkLabel(exp_row, text="Total Expenses", font=("Arial", 12)).pack(side="left", padx=20)
        ctk.CTkLabel(exp_row, text=f"UGX {report['expenses']:,.0f}", font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        exp_row2 = ctk.CTkFrame(expenses_frame)
        exp_row2.pack(fill="x", pady=2)
        ctk.CTkLabel(exp_row2, text="Expense Count", font=("Arial", 12)).pack(side="left", padx=20)
        ctk.CTkLabel(exp_row2, text=str(report['expenses_count']), font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        # Net Profit
        profit_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a3a1a" if report['net_profit'] >= 0 else "#3a1a1a")
        profit_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(profit_frame, text="NET PROFIT", font=("Arial", 14, "bold")).pack(pady=5)
        
        profit_row = ctk.CTkFrame(profit_frame)
        profit_row.pack(fill="x", pady=2)
        ctk.CTkLabel(profit_row, text="Net Profit", font=("Arial", 12)).pack(side="left", padx=20)
        ctk.CTkLabel(
            profit_row, 
            text=f"UGX {report['net_profit']:,.0f}", 
            font=("Arial", 16, "bold"),
            text_color="green" if report['net_profit'] >= 0 else "red"
        ).pack(side="right", padx=20)
        
        # Rooms
        rooms_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a2a3a")
        rooms_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(rooms_frame, text="ROOMS", font=("Arial", 14, "bold")).pack(pady=5)
        
        room_row = ctk.CTkFrame(rooms_frame)
        room_row.pack(fill="x", pady=2)
        ctk.CTkLabel(room_row, text="Occupied Rooms", font=("Arial", 12)).pack(side="left", padx=20)
        ctk.CTkLabel(room_row, text=f"{report['occupied']}/{report['total_rooms']}", font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        occupancy = (report['occupied'] / report['total_rooms'] * 100) if report['total_rooms'] > 0 else 0
        room_row2 = ctk.CTkFrame(rooms_frame)
        room_row2.pack(fill="x", pady=2)
        ctk.CTkLabel(room_row2, text="Occupancy Rate", font=("Arial", 12)).pack(side="left", padx=20)
        ctk.CTkLabel(room_row2, text=f"{occupancy:.1f}%", font=("Arial", 12, "bold")).pack(side="right", padx=20)
        
        # Store for export
        self.current_report = report
        self.report_type = "daily"
    
    def show_weekly_report(self):
        """Show weekly report with profit"""
        self.clear_report()
        
        sales_data, expenses_data = get_weekly_report()
        
        ctk.CTkLabel(
            self.report_frame,
            text="📈 Weekly Performance",
            font=("Arial", 20, "bold")
        ).pack(pady=10)
        
        # Combine data
        weekly_data = {}
        for date, revenue, cost, profit in sales_data:
            weekly_data[date] = {
                "revenue": revenue or 0,
                "cost": cost or 0,
                "profit": profit or 0,
                "expenses": 0
            }
        for date, expenses in expenses_data:
            if date in weekly_data:
                weekly_data[date]["expenses"] = expenses or 0
            else:
                weekly_data[date] = {
                    "revenue": 0,
                    "cost": 0,
                    "profit": 0,
                    "expenses": expenses or 0
                }
        
        if not weekly_data:
            ctk.CTkLabel(
                self.report_frame,
                text="No data for the past week",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Header
        header = ctk.CTkFrame(self.report_frame)
        header.pack(fill="x", pady=5)
        
        headers = ["Date", "Revenue", "Cost", "Gross Profit", "Expenses", "Net Profit"]
        for h in headers:
            ctk.CTkLabel(
                header,
                text=h,
                font=("Arial", 12, "bold"),
                width=120
            ).pack(side="left", padx=5)
        
        total_revenue = 0
        total_cost = 0
        total_gross_profit = 0
        total_expenses = 0
        
        for date in sorted(weekly_data.keys()):
            data = weekly_data[date]
            revenue = data["revenue"]
            cost = data["cost"]
            gross_profit = data["profit"]
            expenses = data["expenses"]
            net_profit = gross_profit - expenses
            
            total_revenue += revenue
            total_cost += cost
            total_gross_profit += gross_profit
            total_expenses += expenses
            
            row = ctk.CTkFrame(self.report_frame)
            row.pack(fill="x", pady=2)
            
            row_data = [
                date,
                f"UGX {revenue:,.0f}",
                f"UGX {cost:,.0f}",
                f"UGX {gross_profit:,.0f}",
                f"UGX {expenses:,.0f}",
                f"UGX {net_profit:,.0f}"
            ]
            
            for i, d in enumerate(row_data):
                if i == 5:  # Net Profit column
                    color = "green" if net_profit >= 0 else "red"
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=120,
                        text_color=color,
                        font=("Arial", 12, "bold")
                    ).pack(side="left", padx=5)
                else:
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=120
                    ).pack(side="left", padx=5)
        
        # Totals
        total_net_profit = total_gross_profit - total_expenses
        total_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a2a3a")
        total_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Revenue: UGX {total_revenue:,.0f}",
            font=("Arial", 14)
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Cost: UGX {total_cost:,.0f}",
            font=("Arial", 14)
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Gross Profit: UGX {total_gross_profit:,.0f}",
            font=("Arial", 14)
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Expenses: UGX {total_expenses:,.0f}",
            font=("Arial", 14)
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Net Profit: UGX {total_net_profit:,.0f}",
            font=("Arial", 14, "bold"),
            text_color="green" if total_net_profit >= 0 else "red"
        ).pack(side="left", padx=20)
        
        # Store for export
        self.current_report = {
            "date": "Weekly",
            "revenue": total_revenue,
            "cost": total_cost,
            "gross_profit": total_gross_profit,
            "expenses": total_expenses,
            "net_profit": total_net_profit,
            "weekly_data": weekly_data
        }
        self.report_type = "weekly"
    
    def show_balance_report(self):
        """Show weekly balance report with opening/closing balances"""
        self.clear_report()
        
        today = datetime.now().strftime("%Y-%m-%d")
        weekly_data = get_weekly_report_data(today)
        
        ctk.CTkLabel(
            self.report_frame,
            text="📊 Weekly Balance Report",
            font=("Arial", 20, "bold")
        ).pack(pady=10)
        
        if not weekly_data:
            ctk.CTkLabel(
                self.report_frame,
                text="No data for this week",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Header
        header = ctk.CTkFrame(self.report_frame)
        header.pack(fill="x", pady=5)
        
        headers = ["Date", "Opening", "Revenue", "Expenses", "Closing", "Cash Collected", "Merchant", "Day"]
        widths = [100, 100, 100, 100, 100, 120, 120, 80]
        
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                header,
                text=h,
                font=("Arial", 12, "bold"),
                width=w
            ).pack(side="left", padx=5)
        
        total_revenue = 0
        total_expenses = 0
        total_cash = 0
        total_merchant = 0
        opening_balance = 0
        
        for data in weekly_data:
            row = ctk.CTkFrame(self.report_frame)
            row.pack(fill="x", pady=2)
            
            # Highlight Saturday
            if data["is_saturday"]:
                row.configure(fg_color="#1a3a1a")  # Green for collection day
            
            # Format day name
            date_obj = datetime.strptime(data["date"], "%Y-%m-%d")
            day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date_obj.weekday()]
            
            row_data = [
                data["date"],
                f"UGX {data['opening_balance']:,.0f}",
                f"UGX {data['daily_revenue']:,.0f}",
                f"UGX {data['daily_expenses']:,.0f}",
                f"UGX {data['closing_balance']:,.0f}",
                f"UGX {data['cash_collected']:,.0f}",
                f"UGX {data['merchant_collected']:,.0f}",
                day_name
            ]
            
            if data["is_saturday"]:
                row_data[7] = "📅 SAT (Collection)"
            
            total_revenue += data["daily_revenue"]
            total_expenses += data["daily_expenses"]
            total_cash += data["cash_collected"]
            total_merchant += data["merchant_collected"]
            
            for i, d in enumerate(row_data):
                # Highlight balance columns
                if i == 4:  # Closing balance
                    color = "green" if data["closing_balance"] >= 0 else "red"
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        text_color=color,
                        font=("Arial", 12, "bold")
                    ).pack(side="left", padx=5)
                elif i == 7:  # Day
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        font=("Arial", 12, "bold") if data["is_saturday"] else ("Arial", 12)
                    ).pack(side="left", padx=5)
                else:
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        anchor="w" if i > 0 else "center"
                    ).pack(side="left", padx=5)
        
        # Totals
        total_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a2a3a")
        total_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Revenue: UGX {total_revenue:,.0f}",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Expenses: UGX {total_expenses:,.0f}",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Cash Collected: UGX {total_cash:,.0f}",
            font=("Arial", 14, "bold"),
            text_color="green"
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            total_frame,
            text=f"Total Merchant: UGX {total_merchant:,.0f}",
            font=("Arial", 14, "bold"),
            text_color="blue"
        ).pack(side="left", padx=20)
        
        # Net Balance
        net_balance = total_revenue - total_expenses
        net_frame = ctk.CTkFrame(self.report_frame, fg_color="#1a3a1a" if net_balance >= 0 else "#3a1a1a")
        net_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            net_frame,
            text="NET BALANCE FOR WEEK",
            font=("Arial", 14, "bold")
        ).pack(side="left", padx=20)
        
        ctk.CTkLabel(
            net_frame,
            text=f"UGX {net_balance:,.0f}",
            font=("Arial", 16, "bold"),
            text_color="green" if net_balance >= 0 else "red"
        ).pack(side="right", padx=20)
        
        # Store for export
        self.current_report = {
            "date": "Balance Report",
            "weekly_data": weekly_data,
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "total_cash": total_cash,
            "total_merchant": total_merchant,
            "net_balance": net_balance
        }
        self.report_type = "balance"
    
    def export_report(self):
        """Export the current report to CSV"""
        if not hasattr(self, 'current_report'):
            self.show_message("Please generate a report first", "red")
            return
        
        report = self.current_report
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(["Valley View Motel Report"])
                writer.writerow([f"Report Type: {report.get('date', 'Unknown')}"])
                writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([])
                
                # Balance Report
                if 'weekly_data' in report and report.get('date') == "Balance Report":
                    writer.writerow(["WEEKLY BALANCE REPORT"])
                    writer.writerow([])
                    writer.writerow(["Date", "Opening Balance", "Revenue", "Expenses", "Closing Balance", "Cash Collected", "Merchant Collected", "Day"])
                    
                    for data in report['weekly_data']:
                        date_obj = datetime.strptime(data["date"], "%Y-%m-%d")
                        day_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date_obj.weekday()]
                        if data["is_saturday"]:
                            day_name = "SAT (Collection)"
                        
                        writer.writerow([
                            data["date"],
                            data["opening_balance"],
                            data["daily_revenue"],
                            data["daily_expenses"],
                            data["closing_balance"],
                            data["cash_collected"],
                            data["merchant_collected"],
                            day_name
                        ])
                    
                    writer.writerow([])
                    writer.writerow(["TOTALS"])
                    writer.writerow(["Total Revenue", report.get("total_revenue", 0)])
                    writer.writerow(["Total Expenses", report.get("total_expenses", 0)])
                    writer.writerow(["Total Cash Collected", report.get("total_cash", 0)])
                    writer.writerow(["Total Merchant Collected", report.get("total_merchant", 0)])
                    writer.writerow(["Net Balance", report.get("net_balance", 0)])
                
                # Daily or Weekly Report
                else:
                    if 'weekly_data' in report:
                        writer.writerow(["WEEKLY PERFORMANCE"])
                        writer.writerow([])
                        writer.writerow(["Metric", "Value"])
                        writer.writerow(["Total Revenue", report.get('revenue', 0)])
                        writer.writerow(["Cost of Goods", report.get('cost', 0)])
                        writer.writerow(["Gross Profit", report.get('gross_profit', 0)])
                        writer.writerow(["Total Expenses", report.get('expenses', 0)])
                        writer.writerow(["Net Profit", report.get('net_profit', 0)])
                        
                        writer.writerow([])
                        writer.writerow(["Daily Breakdown"])
                        writer.writerow(["Date", "Revenue", "Cost", "Gross Profit", "Expenses", "Net Profit"])
                        for date, data in sorted(report['weekly_data'].items()):
                            writer.writerow([
                                date,
                                data.get('revenue', 0),
                                data.get('cost', 0),
                                data.get('profit', 0),
                                data.get('expenses', 0),
                                data.get('profit', 0) - data.get('expenses', 0)
                            ])
                    else:
                        # Daily Report
                        writer.writerow(["DAILY REPORT"])
                        writer.writerow([])
                        writer.writerow(["Metric", "Value"])
                        writer.writerow(["Date", report.get('date', 'Unknown')])
                        writer.writerow(["Opening Balance", report.get('opening_balance', 0)])
                        writer.writerow(["Closing Balance", report.get('closing_balance', 0)])
                        writer.writerow(["Cash Sales", report.get('cash_sales', 0)])
                        writer.writerow(["Merchant Sales", report.get('merchant_sales', 0)])
                        writer.writerow(["Total Revenue", report.get('sales_revenue', 0)])
                        writer.writerow(["Cost of Goods", report.get('sales_cost', 0)])
                        writer.writerow(["Gross Profit", report.get('sales_profit', 0)])
                        writer.writerow(["Total Expenses", report.get('expenses', 0)])
                        writer.writerow(["Net Profit", report.get('net_profit', 0)])
                        writer.writerow(["Occupied Rooms", report.get('occupied', 0)])
                        writer.writerow(["Total Rooms", report.get('total_rooms', 0)])
                        writer.writerow(["Occupancy Rate", f"{report.get('occupied', 0)/report.get('total_rooms', 1)*100:.1f}%"])
                        
                        if report.get('is_saturday', False):
                            writer.writerow([])
                            writer.writerow(["SATURDAY COLLECTION"])
                            writer.writerow(["Cash Collected", report.get('cash_collected', 0)])
                            writer.writerow(["Merchant Collected", report.get('merchant_collected', 0)])
                            writer.writerow(["Total Collected", report.get('cash_collected', 0) + report.get('merchant_collected', 0)])
            
            self.show_message(f"✅ Report exported to: {filename}", "green")
        except Exception as e:
            self.show_message(f"Error exporting report: {str(e)}", "red")
    
    def show_message(self, msg, color="green"):
        """Show a message"""
        self.clear_report()
        ctk.CTkLabel(
            self.report_frame,
            text=msg,
            text_color=color,
            font=("Arial", 14)
        ).pack(pady=20)