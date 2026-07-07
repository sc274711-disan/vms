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
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=1)  # Main content
        
        # Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=0, pady=(25, 15), sticky="ew")
        
        ctk.CTkLabel(
            title_frame,
            text="💸 Expenses Management",
            font=get_font_bold(36),
            text_color="#1f538d"
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Track and manage all your business expenses",
            font=get_font(self.font_size),
            text_color="gray"
        ).pack()
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, padx=25, pady=5, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(0, weight=0)  # Summary
        main_container.grid_rowconfigure(1, weight=0)  # Form
        main_container.grid_rowconfigure(2, weight=0)  # Filters
        main_container.grid_rowconfigure(3, weight=1)  # List
        
        # Today's Summary - Modern card
        self.summary_frame = ctk.CTkFrame(
            main_container,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        self.summary_frame.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="ew")
        self.summary_frame.grid_columnconfigure(0, weight=1)
        self.update_today_summary()
        
        # Expense Form - Modern card
        form_frame = ctk.CTkFrame(
            main_container,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        form_frame.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="ew")
        form_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            form_frame,
            text="📝 Post Expense",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=5)
        
        # Row 1: Name and Amount
        row1 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        row1.grid_columnconfigure(1, weight=1)
        row1.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(
            row1,
            text="Expense Name:",
            font=get_font_bold(self.font_size),
            width=120
        ).grid(row=0, column=0, sticky="w", padx=5)
        
        self.name_entry = ctk.CTkEntry(
            row1,
            placeholder_text="e.g., Electricity Bill",
            width=250,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        ctk.CTkLabel(
            row1,
            text="Amount (UGX):",
            font=get_font_bold(self.font_size),
            width=120
        ).grid(row=0, column=2, sticky="w", padx=5)
        
        self.amount_entry = ctk.CTkEntry(
            row1,
            placeholder_text="e.g., 150000",
            width=180,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.amount_entry.grid(row=0, column=3, sticky="w", padx=5)
        
        # Row 2: Notes
        row2 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            row2,
            text="Notes:",
            font=get_font_bold(self.font_size),
            width=120
        ).pack(side="left", padx=5)
        
        self.notes_entry = ctk.CTkEntry(
            row2,
            placeholder_text="Optional notes",
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.notes_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Row 3: Buttons
        row3 = ctk.CTkFrame(input_frame, fg_color="transparent")
        row3.pack(fill="x", pady=15)
        
        self.add_btn = ctk.CTkButton(
            row3,
            text="💸 Post Expense",
            command=self.record_expense,
            width=160,
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
            command=self.clear_form,
            width=130,
            height=45,
            corner_radius=10,
            font=get_font_bold(self.font_size),
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            row3,
            text="",
            font=get_font(self.font_size - 2),
            text_color="gray"
        )
        self.status_label.pack(side="left", padx=20)
        
        # Filter buttons - Modern style
        filter_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        filter_frame.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")
        
        ctk.CTkButton(
            filter_frame,
            text="📅 Today",
            command=self.show_today_expenses,
            width=100,
            height=35,
            corner_radius=8,
            font=get_font(self.font_size),
            fg_color="#1f538d",
            hover_color="#14375e"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame,
            text="📊 All Expenses",
            command=self.load_all_expenses,
            width=120,
            height=35,
            corner_radius=8,
            font=get_font(self.font_size),
            fg_color="#2a3a4a",
            hover_color="#1a2a3a"
        ).pack(side="left", padx=5)
        
        # Expenses List - Modern card
        list_frame = ctk.CTkFrame(
            main_container,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        list_frame.grid(row=3, column=0, padx=5, pady=(0, 5), sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            list_frame,
            text="📋 Expenses List",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        self.expenses_list = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent"
        )
        self.expenses_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
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
        
        # Summary row with modern styling
        summary_inner = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        summary_inner.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            summary_inner,
            text="📅 Today's Expenses",
            font=get_font_bold(font_size + 2)
        ).pack(side="left")
        
        ctk.CTkLabel(
            summary_inner,
            text=f"UGX {total_today:,.0f}",
            font=get_font_bold(font_size + 6),
            text_color="orange" if total_today > 0 else "gray"
        ).pack(side="right")
        
        ctk.CTkLabel(
            summary_inner,
            text=f"({count_today} entries)",
            font=get_font(font_size - 1),
            text_color="gray"
        ).pack(side="right", padx=10)
    
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
                title = f"📅 {filter_date}"
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
        
        # Show title
        title_label = ctk.CTkLabel(
            self.expenses_list,
            text=title,
            font=get_font_bold(font_size + 2),
            text_color="#1f538d"
        )
        title_label.pack(anchor="w", pady=(5, 10))
        
        if not expenses:
            ctk.CTkLabel(
                self.expenses_list,
                text="No expenses recorded for this period",
                font=get_font(font_size + 2),
                text_color="gray"
            ).pack(pady=30)
            return
        
        # Header with modern styling
        header = ctk.CTkFrame(
            self.expenses_list,
            fg_color="#0a1a2a",
            corner_radius=8
        )
        header.pack(fill="x", pady=5)
        
        headers = ["#", "Name", "Amount", "Date", "Notes", "Actions"]
        widths = [35, 150, 130, 150, 200, 160]
        
        for i, (h, w) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(
                header,
                text=h,
                font=get_font_bold(font_size),
                width=w,
                text_color="#8899aa"
            ).pack(side="left", padx=8, pady=8)
        
        for idx, expense in enumerate(expenses, 1):
            try:
                exp_id, name, amount, date, notes = expense
                
                row = ctk.CTkFrame(
                    self.expenses_list,
                    fg_color="#1a2a3a" if idx % 2 == 0 else "#15202a",
                    corner_radius=6
                )
                row.pack(fill="x", pady=2)
                
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
                    command=lambda e=expense: self.edit_expense(e)
                ).pack(side="left", padx=2)
                
                ctk.CTkButton(
                    actions,
                    text="🗑️",
                    width=32,
                    height=32,
                    corner_radius=8,
                    fg_color="#6a2a2a",
                    hover_color="#5a1a1a",
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
        self.update_idletasks()
        
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
        
        self.add_btn.configure(text="💾 Update Expense", fg_color="#f39c12", hover_color="#d68910")
        self.status_label.configure(text=f"✏️ Editing: {name}", text_color="blue")
        self.show_message(f"Editing expense: {name}. Make changes and click Update.", "blue")
    
    def delete_expense(self, expense):
        """Delete an expense with confirmation"""
        exp_id, name, amount, date, notes = expense
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("400x220")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        dialog.update_idletasks()
        width = 400
        height = 220
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        ctk.CTkLabel(
            dialog,
            text="🗑️ Delete Expense?",
            font=get_font_bold(20),
            text_color="red"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text=f"Name: {name}\nAmount: UGX {amount:,.0f}",
            font=get_font(self.font_size + 2)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            dialog,
            text="This action cannot be undone!",
            text_color="red",
            font=get_font(self.font_size - 2)
        ).pack()
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
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
    
    def clear_form(self):
        """Clear the form"""
        self.name_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.notes_entry.delete(0, "end")
        self.editing_expense_id = None
        self.add_btn.configure(text="💸 Post Expense", fg_color="#2d8f47", hover_color="#1f6a33")
        self.status_label.configure(text="")
    
    def show_message(self, msg, color="green"):
        """Show a message"""
        try:
            for widget in self.expenses_list.winfo_children():
                if hasattr(widget, "is_message"):
                    widget.destroy()
        except:
            pass
        
        label = ctk.CTkLabel(
            self.expenses_list,
            text=msg,
            text_color=color,
            font=get_font_bold(self.font_size),
            fg_color="#1a2a3a" if color == "green" else "#3a1a1a",
            corner_radius=8,
            padx=20,
            pady=10
        )
        label.is_message = True
        label.pack(pady=10, fill="x")
        
        self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)