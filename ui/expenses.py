# ui/expenses.py
import customtkinter as ctk
from database.db import (
    add_expense, get_recent_expenses, get_expense_by_id,
    update_expense, delete_expense, get_connection
)
from datetime import datetime
from ui.font_utils import get_font, get_font_bold, get_font_size

class ExpensesFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.editing_expense_id = None
        self.font_size = get_font_size()
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="💸 Expenses Management",
            font=get_font_bold(28)
        )
        title.pack(pady=(20, 10))
        
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Today's Summary
        self.summary_frame = ctk.CTkFrame(main_container, fg_color="#1a2a3a")
        self.summary_frame.pack(fill="x", pady=(0, 10))
        self.update_today_summary()
        
        # Expense Form
        form_frame = ctk.CTkFrame(main_container)
        form_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            form_frame,
            text="Post Expense",
            font=get_font_bold(16)
        ).pack(pady=5)
        
        input_frame = ctk.CTkFrame(form_frame)
        input_frame.pack(fill="x", pady=5)
        
        # Row 1: Name and Amount
        row1 = ctk.CTkFrame(input_frame)
        row1.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row1, text="Expense Name:", font=get_font(self.font_size), width=100).pack(side="left", padx=5)
        self.name_entry = ctk.CTkEntry(row1, placeholder_text="e.g., Electricity Bill", width=250)
        self.name_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Amount (UGX):", font=get_font(self.font_size), width=100).pack(side="left", padx=5)
        self.amount_entry = ctk.CTkEntry(row1, placeholder_text="e.g., 150000", width=150)
        self.amount_entry.pack(side="left", padx=5)
        
        # Row 2: Notes
        row2 = ctk.CTkFrame(input_frame)
        row2.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row2, text="Notes:", font=get_font(self.font_size), width=100).pack(side="left", padx=5)
        self.notes_entry = ctk.CTkEntry(row2, placeholder_text="Optional notes", width=400)
        self.notes_entry.pack(side="left", padx=5)
        
        # Row 3: Buttons
        row3 = ctk.CTkFrame(input_frame)
        row3.pack(fill="x", pady=10)
        
        self.add_btn = ctk.CTkButton(
            row3,
            text="💸 Post Expense",
            command=self.record_expense,
            width=150
        )
        self.add_btn.pack(side="left", padx=5)
        
        ctk.CTkButton(
            row3,
            text="🔄 Clear Form",
            command=self.clear_form,
            width=120
        ).pack(side="left", padx=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(row3, text="", font=get_font(self.font_size - 2))
        self.status_label.pack(side="left", padx=20)
        
        # Filter buttons
        filter_frame = ctk.CTkFrame(main_container)
        filter_frame.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            filter_frame,
            text="📅 Today",
            command=self.show_today_expenses,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame,
            text="📊 All Expenses",
            command=self.load_all_expenses,
            width=120
        ).pack(side="left", padx=5)
        
        # Expenses List
        list_frame = ctk.CTkFrame(main_container)
        list_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            list_frame,
            text="Expenses List",
            font=get_font_bold(16)
        ).pack(pady=5)
        
        self.expenses_list = ctk.CTkScrollableFrame(list_frame)
        self.expenses_list.pack(fill="both", expand=True, pady=5)
        
        # Load expenses - show today by default
        self.load_expenses(filter_date=datetime.now().strftime("%Y-%m-%d"))
    
    def update_today_summary(self):
        """Update today's expense summary"""
        try:
            for widget in self.summary_frame.winfo_children():
                widget.destroy()
        except:
            pass
        
        font_size = get_font_size()
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount), COUNT(*)
                FROM expenses
                WHERE DATE(expense_date) = ?
            """, (today,))
            total_today, count_today = cursor.fetchone() or (0, 0)
            conn.close()
        except Exception as e:
            print(f"Error getting today's expenses: {e}")
            total_today, count_today = 0, 0
        
        try:
            ctk.CTkLabel(
                self.summary_frame,
                text=f"📅 Today's Expenses: UGX {total_today:,.0f}",
                font=get_font_bold(font_size + 4),
                text_color="orange" if total_today > 0 else "gray"
            ).pack(side="left", padx=20, pady=10)
            
            ctk.CTkLabel(
                self.summary_frame,
                text=f"({count_today} entries)",
                font=get_font(font_size),
                text_color="gray"
            ).pack(side="left", padx=5, pady=10)
        except Exception as e:
            print(f"Error creating summary labels: {e}")
    
    def show_today_expenses(self):
        """Show only today's expenses"""
        self.load_expenses(filter_date=datetime.now().strftime("%Y-%m-%d"))
    
    def load_all_expenses(self):
        """Show all expenses"""
        self.load_expenses(filter_date=None)
    
    def load_expenses(self, filter_date=None):
        """Load expenses with optional date filter"""
        try:
            for widget in self.expenses_list.winfo_children():
                widget.destroy()
        except:
            pass
        
        font_size = get_font_size()
        expenses = []
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if filter_date:
                cursor.execute("""
                    SELECT id, name, amount, expense_date, notes
                    FROM expenses
                    WHERE DATE(expense_date) = ?
                    ORDER BY id DESC
                """, (filter_date,))
                title = f"📅 Expenses for {filter_date}"
            else:
                cursor.execute("""
                    SELECT id, name, amount, expense_date, notes
                    FROM expenses
                    ORDER BY id DESC
                """)
                title = "📊 All Expenses"
            
            expenses = cursor.fetchall()
            conn.close()
        except Exception as e:
            print(f"Error loading expenses: {e}")
            expenses = []
        
        # Update summary
        self.update_today_summary()
        
        # Show title - ALWAYS show this
        try:
            title_label = ctk.CTkLabel(
                self.expenses_list,
                text=title,
                font=get_font_bold(font_size + 2)
            )
            title_label.pack(pady=10)
        except Exception as e:
            print(f"Error creating title: {e}")
        
        if not expenses:
            try:
                ctk.CTkLabel(
                    self.expenses_list,
                    text="No expenses recorded for this period",
                    font=get_font(font_size + 2),
                    text_color="gray"
                ).pack(pady=20)
            except Exception as e:
                print(f"Error creating no expenses message: {e}")
            return
        
        # Header
        try:
            header = ctk.CTkFrame(self.expenses_list)
            header.pack(fill="x", pady=5)
            
            headers = ["#", "Name", "Amount", "Date", "Notes", "Actions"]
            widths = [40, 150, 120, 150, 200, 200]
            for h, w in zip(headers, widths):
                ctk.CTkLabel(
                    header,
                    text=h,
                    font=get_font_bold(font_size),
                    width=w
                ).pack(side="left", padx=5)
        except Exception as e:
            print(f"Error creating header: {e}")
        
        for idx, expense in enumerate(expenses, 1):
            try:
                exp_id, name, amount, date, notes = expense
                
                row = ctk.CTkFrame(self.expenses_list)
                row.pack(fill="x", pady=2)
                
                if idx % 2 == 0:
                    row.configure(fg_color="#1a2a3a")
                
                data = [
                    str(idx),
                    name,
                    f"UGX {amount:,.0f}",
                    date[:16] if date else "",
                    notes or ""
                ]
                
                for i, d in enumerate(data):
                    ctk.CTkLabel(
                        row,
                        text=d,
                        width=widths[i],
                        anchor="w",
                        font=get_font(font_size)
                    ).pack(side="left", padx=5)
                
                # Actions
                actions = ctk.CTkFrame(row, fg_color="transparent")
                actions.pack(side="left", padx=5)
                
                ctk.CTkButton(
                    actions,
                    text="✏️",
                    width=30,
                    command=lambda e=expense: self.edit_expense(e)
                ).pack(side="left", padx=2)
                
                ctk.CTkButton(
                    actions,
                    text="🗑️",
                    width=30,
                    fg_color="red",
                    hover_color="darkred",
                    command=lambda e=expense: self.delete_expense(e)
                ).pack(side="left", padx=2)
            except Exception as e:
                print(f"Error displaying expense {idx}: {e}")
    
    def record_expense(self):
        """Record or update an expense"""
        name = self.name_entry.get().strip()
        amount_str = self.amount_entry.get()
        notes = self.notes_entry.get().strip()
        
        if not name:
            self.show_message("Please enter an expense name", "red")
            return
        
        try:
            amount = float(amount_str)
        except ValueError:
            self.show_message("Please enter a valid amount", "red")
            return
        
        if amount <= 0:
            self.show_message("Amount must be greater than 0", "red")
            return
        
        # Show "processing" message
        self.add_btn.configure(text="⏳ Processing...", state="disabled")
        self.update_idletasks()  # Force UI update
        
        if self.editing_expense_id:
            success, msg = update_expense(self.editing_expense_id, name, amount, notes)
            if success:
                self.editing_expense_id = None
                self.clear_form()
                self.load_expenses(filter_date=datetime.now().strftime("%Y-%m-%d"))
                self.update_today_summary()
                self.refresh_dashboard()
                self.show_message(msg, "green")
            else:
                self.show_message(msg, "red")
        else:
            success, msg = add_expense(name, amount, notes)
            if success:
                self.clear_form()
                self.load_expenses(filter_date=datetime.now().strftime("%Y-%m-%d"))
                self.update_today_summary()
                self.refresh_dashboard()
                self.show_message(msg, "green")
            else:
                self.show_message(msg, "red")
        
        # Re-enable button
        self.add_btn.configure(text="💸 Post Expense", state="normal")
            
    def refresh_dashboard(self):
        """Refresh the dashboard"""
        try:
            root = self.winfo_toplevel()
            for child in root.winfo_children():
                if hasattr(child, 'content_frame'):
                    content = child.content_frame
                    for widget in content.winfo_children():
                        if hasattr(widget, 'refresh'):
                            widget.refresh()
                            print("Dashboard refreshed!")
                            return
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")

    def edit_expense(self, expense):
        """Load expense data into form for editing"""
        exp_id, name, amount, date, notes = expense
        
        self.editing_expense_id = exp_id
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, name)
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(amount))
        self.notes_entry.delete(0, "end")
        self.notes_entry.insert(0, notes or "")
        
        self.add_btn.configure(text="💾 Update Expense")
        self.status_label.configure(text=f"Editing: {name} (ID: {exp_id})", text_color="blue")
        self.show_message(f"Editing expense: {name}. Make changes and click Update.", "blue")
    
    def delete_expense(self, expense):
        """Delete an expense with confirmation"""
        exp_id, name, amount, date, notes = expense
        font_size = get_font_size()
        
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
            text=f"Delete Expense?",
            font=get_font_bold(16),
            text_color="red"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            dialog,
            text=f"Name: {name}\nAmount: UGX {amount:,.0f}",
            font=get_font(font_size)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            dialog,
            text="This action cannot be undone!",
            text_color="red",
            font=get_font(font_size - 2)
        ).pack()
        
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=15)
        
        def confirm():
            success, msg = delete_expense(exp_id)
            dialog.destroy()
            if success:
                self.load_expenses(filter_date=datetime.now().strftime("%Y-%m-%d"))
                self.update_today_summary()
                if self.editing_expense_id == exp_id:
                    self.clear_form()
                self.refresh_dashboard()
                self.show_message(msg, "green")
            else:
                self.show_message(msg, "red")
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete",
            fg_color="red",
            hover_color="darkred",
            command=confirm,
            width=100
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=100
        ).pack(side="left", padx=10)
    
    def clear_form(self):
        """Clear the form"""
        self.name_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.editing_expense_id = None
        self.add_btn.configure(text="💸 Post Expense")
        self.status_label.configure(text="")
    
    def show_message(self, msg, color="green"):
        """Show a message"""
        try:
            for widget in self.expenses_list.winfo_children():
                if hasattr(widget, "is_message"):
                    widget.destroy()
        except:
            pass
        
        font_size = get_font_size()
        
        try:
            label = ctk.CTkLabel(
                self.expenses_list,
                text=msg,
                text_color=color,
                font=get_font(font_size)
            )
            label.is_message = True
            label.pack(pady=5)
            
            self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)
        except Exception as e:
            print(f"Error showing message: {e}")