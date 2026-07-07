# ui/rooms.py
import customtkinter as ctk
from database.db import (
    get_all_rooms, get_available_rooms, get_current_bookings,
    add_room, delete_room, update_room_status,
    check_in, check_out, get_room_stats, get_connection
)
from ui.font_utils import get_font, get_font_bold, get_font_size

class RoomsFrame(ctk.CTkFrame):
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
            text="🛏️ Rooms Management",
            font=get_font_bold(36),
            text_color="#1f538d"
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="Manage room bookings, check-ins, and check-outs",
            font=get_font(self.font_size),
            text_color="gray"
        ).pack()
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, padx=25, pady=5, sticky="nsew")
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # ============ LEFT PANEL - Check In/Out ============
        left_panel = ctk.CTkFrame(
            main_container,
            width=380,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        left_panel.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        left_panel.grid_propagate(False)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Stats at top of left panel
        self.stats_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=15, pady=(15, 10))
        self.update_stats()
        
        ctk.CTkLabel(
            left_panel,
            text="📋 Check In / Check Out",
            font=get_font_bold(18)
        ).pack(pady=(5, 10))
        
        # Check In Section
        checkin_frame = ctk.CTkFrame(
            left_panel,
            fg_color="#15202a",
            corner_radius=10,
            border_width=1,
            border_color="#2a3a4a"
        )
        checkin_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            checkin_frame,
            text="✅ Check In",
            font=get_font_bold(16),
            text_color="#2ecc71"
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            checkin_frame,
            text="Room:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w", padx=15)
        
        self.room_dropdown = ctk.CTkComboBox(
            checkin_frame,
            values=self.get_available_rooms(),
            width=200,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.room_dropdown.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            checkin_frame,
            text="Customer Name:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w", padx=15)
        
        self.customer_name = ctk.CTkEntry(
            checkin_frame,
            placeholder_text="Guest name",
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.customer_name.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            checkin_frame,
            text="Phone:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w", padx=15)
        
        self.customer_phone = ctk.CTkEntry(
            checkin_frame,
            placeholder_text="Phone number",
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.customer_phone.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(
            checkin_frame,
            text="✅ Check In",
            command=self.do_check_in,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#2d8f47",
            hover_color="#1f6a33"
        ).pack(pady=(10, 15), padx=15, fill="x")
        
        # Check Out Section
        checkout_frame = ctk.CTkFrame(
            left_panel,
            fg_color="#15202a",
            corner_radius=10,
            border_width=1,
            border_color="#2a3a4a"
        )
        checkout_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            checkout_frame,
            text="🚪 Check Out",
            font=get_font_bold(16),
            text_color="#f39c12"
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            checkout_frame,
            text="Room:",
            font=get_font_bold(self.font_size)
        ).pack(anchor="w", padx=15)
        
        self.checkout_dropdown = ctk.CTkComboBox(
            checkout_frame,
            values=self.get_occupied_rooms(),
            width=200,
            height=38,
            corner_radius=8,
            font=get_font(self.font_size)
        )
        self.checkout_dropdown.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkButton(
            checkout_frame,
            text="🚪 Check Out",
            command=self.do_check_out,
            height=40,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#e67e22",
            hover_color="#d68910"
        ).pack(pady=(10, 15), padx=15, fill="x")
        
        # ============ RIGHT PANEL - Room List ============
        right_panel = ctk.CTkFrame(
            main_container,
            fg_color="#1a2a3a",
            corner_radius=12,
            border_width=1,
            border_color="#2a3a4a"
        )
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            right_panel,
            text="📋 All Rooms",
            font=get_font_bold(18)
        ).pack(pady=(15, 10))
        
        self.rooms_list = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="transparent"
        )
        self.rooms_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Load rooms
        self.load_rooms()
    
    def update_stats(self):
        """Update room statistics"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        occupied, total = get_room_stats()
        vacant = total - occupied
        
        stats_frame_inner = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        stats_frame_inner.pack(fill="x")
        
        ctk.CTkLabel(
            stats_frame_inner,
            text=f"🏠 Total: {total}",
            font=get_font_bold(font_size + 2)
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            stats_frame_inner,
            text=f"🟢 Vacant: {vacant}",
            font=get_font_bold(font_size + 2),
            text_color="#2ecc71"
        ).pack(side="left", padx=10)
        
        ctk.CTkLabel(
            stats_frame_inner,
            text=f"🔴 Occupied: {occupied}",
            font=get_font_bold(font_size + 2),
            text_color="#e74c3c"
        ).pack(side="left", padx=10)
    
    def get_available_rooms(self):
        """Get available rooms for dropdown"""
        rooms = get_available_rooms()
        return rooms if rooms else ["No rooms available"]
    
    def get_occupied_rooms(self):
        """Get occupied rooms for checkout"""
        all_rooms = get_all_rooms()
        occupied = [r[0] for r in all_rooms if r[3] == "Occupied"]
        return occupied if occupied else ["No occupied rooms"]
    
    def do_check_in(self):
        """Check in a guest"""
        room = self.room_dropdown.get()
        name = self.customer_name.get().strip()
        phone = self.customer_phone.get().strip()
        
        if room == "No rooms available":
            self.show_message("No available rooms", "red")
            return
        
        if not name:
            self.show_message("Please enter customer name", "red")
            return
        
        success, msg = check_in(room, name, phone)
        
        if success:
            self.customer_name.delete(0, "end")
            self.customer_phone.delete(0, "end")
            self.refresh_ui()
            self.show_message(msg, "green")
        else:
            self.show_message(msg, "red")
    
    def do_check_out(self):
        """Check out a guest and record revenue"""
        room = self.checkout_dropdown.get()
        
        if room == "No occupied rooms":
            self.show_message("No occupied rooms", "red")
            return
        
        # Get room details first
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.price, b.customer_name, b.check_in
            FROM rooms r
            JOIN bookings b ON b.room_number = r.room_number
            WHERE r.room_number = ? AND b.status = 'Checked In'
        """, (room,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            self.show_message("No active booking found", "red")
            return
        
        price, customer, check_in = result
        
        # Show confirmation dialog with details
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Checkout")
        dialog.geometry("450x320")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        dialog.update_idletasks()
        width = 450
        height = 320
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        font_size = get_font_size()
        
        ctk.CTkLabel(
            dialog,
            text="🚪 Confirm Checkout",
            font=get_font_bold(20),
            text_color="#f39c12"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text=f"Room: {room}",
            font=get_font_bold(font_size + 4),
            text_color="#1f538d"
        ).pack(pady=5)
        
        ctk.CTkLabel(
            dialog,
            text=f"Customer: {customer}",
            font=get_font(font_size + 2)
        ).pack(pady=2)
        
        ctk.CTkLabel(
            dialog,
            text=f"Check-in: {check_in}",
            font=get_font(font_size + 2)
        ).pack(pady=2)
        
        ctk.CTkFrame(dialog, height=2, fg_color="#2a3a4a").pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(
            dialog,
            text=f"Room Price: UGX {price:,.0f}",
            font=get_font_bold(font_size + 4),
            text_color="#2ecc71"
        ).pack(pady=5)
        
        ctk.CTkLabel(
            dialog,
            text="💡 This will be added to today's revenue",
            font=get_font(font_size - 2),
            text_color="#8899aa"
        ).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def confirm_checkout():
            for widget in btn_frame.winfo_children():
                widget.configure(state="disabled")
            
            status_label = ctk.CTkLabel(
                dialog,
                text="⏳ Processing checkout...",
                font=get_font_bold(font_size),
                text_color="#3498db"
            )
            status_label.pack(pady=5)
            dialog.update_idletasks()
            
            success, msg = check_out(room)
            dialog.destroy()
            
            if success:
                self.refresh_ui()
                self.refresh_dashboard()
                self.show_message(msg, "green")
            else:
                self.show_message(msg, "red")
        
        ctk.CTkButton(
            btn_frame,
            text="✅ Confirm Checkout",
            command=confirm_checkout,
            width=140,
            height=45,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#2d8f47",
            hover_color="#1f6a33"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=140,
            height=45,
            corner_radius=10,
            font=get_font_bold(self.font_size + 2),
            fg_color="#555555",
            hover_color="#444444"
        ).pack(side="left", padx=10)

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

    def load_rooms(self):
        """Load all rooms"""
        for widget in self.rooms_list.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        rooms = get_all_rooms()
        
        if not rooms:
            ctk.CTkLabel(
                self.rooms_list,
                text="No rooms configured",
                font=get_font(font_size + 2),
                text_color="gray"
            ).pack(pady=30)
            return
        
        # Header
        header = ctk.CTkFrame(
            self.rooms_list,
            fg_color="#0a1a2a",
            corner_radius=8
        )
        header.pack(fill="x", pady=5)
        
        headers = ["Room", "Type", "Price", "Status"]
        widths = [100, 120, 120, 100]
        
        for h, w in zip(headers, widths):
            ctk.CTkLabel(
                header,
                text=h,
                font=get_font_bold(font_size),
                width=w,
                text_color="#8899aa"
            ).pack(side="left", padx=8, pady=8)
        
        for room in rooms:
            room_num, room_type, price, status = room
            
            row = ctk.CTkFrame(
                self.rooms_list,
                corner_radius=6
            )
            
            # Color coding
            if status == "Vacant":
                row.configure(fg_color="#1a3a1a")  # Green
            elif status == "Occupied":
                row.configure(fg_color="#3a1a1a")  # Red
            else:
                row.configure(fg_color="#3a2a1a")  # Orange - Maintenance
            
            row.pack(fill="x", pady=2)
            
            data = [room_num, room_type, f"UGX {price:,.0f}", status]
            for i, d in enumerate(data):
                ctk.CTkLabel(
                    row,
                    text=d,
                    width=widths[i],
                    anchor="w",
                    font=get_font(font_size),
                    text_color="#ccddee"
                ).pack(side="left", padx=8, pady=6)
    
    def refresh_ui(self):
        """Refresh all UI components"""
        self.room_dropdown.configure(values=self.get_available_rooms())
        self.checkout_dropdown.configure(values=self.get_occupied_rooms())
        self.update_stats()
        self.load_rooms()
    
    def show_message(self, msg, color="green"):
        """Show a message"""
        for widget in self.rooms_list.winfo_children():
            if hasattr(widget, "is_message"):
                widget.destroy()
        
        font_size = get_font_size()
        
        label = ctk.CTkLabel(
            self.rooms_list,
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