# ui/rooms.py
import customtkinter as ctk
from database.db import (
    get_all_rooms, get_available_rooms, get_current_bookings,
    add_room, delete_room, update_room_status,
    check_in, check_out, get_room_stats
)
from ui.font_utils import get_font, get_font_bold, get_font_size

# ui/rooms.py - At the top, update the imports
from database.db import (
    get_all_rooms, get_available_rooms, get_current_bookings,
    add_room, delete_room, update_room_status,
    check_in, check_out, get_room_stats, get_connection
)

class RoomsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.font_size = get_font_size()
        
        # Title
        title = ctk.CTkLabel(
            self,
            text="🛏️ Rooms Management",
            font=get_font_bold(28)
        )
        title.pack(pady=(20, 10))
        
        # Stats
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.pack(fill="x", padx=20, pady=10)
        self.update_stats()
        
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Check In/Out
        left_panel = ctk.CTkFrame(main_container, width=350)
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        ctk.CTkLabel(
            left_panel,
            text="Check In / Check Out",
            font=get_font_bold(16)
        ).pack(pady=10)
        
        # Check In
        checkin_frame = ctk.CTkFrame(left_panel)
        checkin_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(checkin_frame, text="Check In", font=get_font_bold(self.font_size + 2)).pack(pady=5)
        
        ctk.CTkLabel(checkin_frame, text="Room:", font=get_font(self.font_size)).pack(anchor="w")
        self.room_dropdown = ctk.CTkComboBox(
            checkin_frame,
            values=self.get_available_rooms(),
            width=200
        )
        self.room_dropdown.pack(fill="x", pady=2)
        
        ctk.CTkLabel(checkin_frame, text="Customer Name:", font=get_font(self.font_size)).pack(anchor="w")
        self.customer_name = ctk.CTkEntry(checkin_frame, placeholder_text="Guest name")
        self.customer_name.pack(fill="x", pady=2)
        
        ctk.CTkLabel(checkin_frame, text="Phone:", font=get_font(self.font_size)).pack(anchor="w")
        self.customer_phone = ctk.CTkEntry(checkin_frame, placeholder_text="Phone number")
        self.customer_phone.pack(fill="x", pady=2)
        
        ctk.CTkButton(
            checkin_frame,
            text="✅ Check In",
            command=self.do_check_in
        ).pack(pady=10)
        
        # Check Out
        checkout_frame = ctk.CTkFrame(left_panel)
        checkout_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(checkout_frame, text="Check Out", font=get_font_bold(self.font_size + 2)).pack(pady=5)
        
        ctk.CTkLabel(checkout_frame, text="Room:", font=get_font(self.font_size)).pack(anchor="w")
        self.checkout_dropdown = ctk.CTkComboBox(
            checkout_frame,
            values=self.get_occupied_rooms(),
            width=200
        )
        self.checkout_dropdown.pack(fill="x", pady=2)
        
        ctk.CTkButton(
            checkout_frame,
            text="🚪 Check Out",
            fg_color="orange",
            command=self.do_check_out
        ).pack(pady=10)
        
        # Right panel - Room list
        right_panel = ctk.CTkFrame(main_container)
        right_panel.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(
            right_panel,
            text="All Rooms",
            font=get_font_bold(16)
        ).pack(pady=5)
        
        self.rooms_list = ctk.CTkScrollableFrame(right_panel)
        self.rooms_list.pack(fill="both", expand=True, pady=5)
        
        # Load rooms
        self.load_rooms()
    
    def update_stats(self):
        """Update room statistics"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        font_size = get_font_size()
        occupied, total = get_room_stats()
        vacant = total - occupied
        
        stats = [
            (f"🏠 Total: {total}", ""),
            (f"🟢 Vacant: {vacant}", "green"),
            (f"🔴 Occupied: {occupied}", "red")
        ]
        
        for text, color in stats:
            ctk.CTkLabel(
                self.stats_frame,
                text=text,
                text_color=color if color else "white",
                font=get_font_bold(font_size + 2) if not color else get_font(font_size + 2)
            ).pack(side="left", padx=20)
    
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
        dialog.geometry("400x280")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()
        dialog.lift()
        
        dialog.update_idletasks()
        width = 400
        height = 280
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        font_size = get_font_size()
        
        ctk.CTkLabel(
            dialog,
            text=f"Checkout Room {room}?",
            font=get_font_bold(18)
        ).pack(pady=10)
        
        ctk.CTkLabel(
            dialog,
            text=f"Customer: {customer}",
            font=get_font(font_size)
        ).pack(pady=2)
        
        ctk.CTkLabel(
            dialog,
            text=f"Check-in: {check_in}",
            font=get_font(font_size)
        ).pack(pady=2)
        
        ctk.CTkLabel(
            dialog,
            text=f"Room Price: UGX {price:,.0f}",
            font=get_font_bold(font_size + 2),
            text_color="green"
        ).pack(pady=5)
        
        ctk.CTkLabel(
            dialog,
            text="This will be added to today's revenue",
            font=get_font(font_size - 2),
            text_color="orange"
        ).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(dialog)
        btn_frame.pack(pady=15)
        
        def confirm_checkout():
            # Disable buttons and show processing
            for widget in btn_frame.winfo_children():
                widget.configure(state="disabled")
            
            # Show processing message
            status_label = ctk.CTkLabel(
                dialog,
                text="⏳ Processing checkout...",
                font=get_font_bold(font_size),
                text_color="blue"
            )
            status_label.pack(pady=5)
            dialog.update_idletasks()
            
            # Perform checkout
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
            width=120
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=120
        ).pack(side="left", padx=10)

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
            ).pack(pady=20)
            return
        
        # Header
        header = ctk.CTkFrame(self.rooms_list)
        header.pack(fill="x", pady=5)
        
        headers = ["Room", "Type", "Price", "Status"]
        for h in headers:
            ctk.CTkLabel(
                header,
                text=h,
                font=get_font_bold(font_size),
                width=100
            ).pack(side="left", padx=5)
        
        for room in rooms:
            room_num, room_type, price, status = room
            
            row = ctk.CTkFrame(self.rooms_list)
            
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
                    width=100,
                    anchor="w",
                    font=get_font(font_size)
                ).pack(side="left", padx=5)
    
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
            font=get_font(font_size)
        )
        label.is_message = True
        label.pack(pady=5)
        
        self.after(3000, lambda: label.destroy() if label.winfo_exists() else None)