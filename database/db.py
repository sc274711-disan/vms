# database/db.py
import sqlite3
import os
import time
import json
from datetime import datetime, timedelta

DB_PATH = "motel.db"
MAX_RETRIES = 3
RETRY_DELAY = 0.5  # seconds

def get_connection():
    """Get database connection with timeout and WAL mode"""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            for i in range(2):
                time.sleep(0.2)
                try:
                    conn = sqlite3.connect(DB_PATH, timeout=5)
                    conn.execute("PRAGMA journal_mode=WAL")
                    conn.execute("PRAGMA synchronous=NORMAL")
                    return conn
                except:
                    continue
            raise
        raise

def initialize_database():
    """Create all tables if they don't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    
    # Inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            quantity REAL DEFAULT 0,
            cost_price REAL DEFAULT 0,
            selling_price REAL DEFAULT 0,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    """)
    
    # Rooms
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            room_type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'Vacant'
        )
    """)
    
    # Room Bookings
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT,
            customer_name TEXT,
            phone TEXT,
            check_in TEXT,
            check_out TEXT,
            status TEXT,
            FOREIGN KEY(room_number) REFERENCES rooms(room_number)
        )
    """)
    
    # Sales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            quantity REAL DEFAULT 1,
            cost_price REAL DEFAULT 0,
            unit_price REAL DEFAULT 0,
            total_revenue REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            total_profit REAL DEFAULT 0,
            sale_date TEXT,
            notes TEXT,
            payment_type TEXT DEFAULT 'Cash'
        )
    """)
    
    # Expenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount REAL,
            expense_date TEXT,
            notes TEXT
        )
    """)
    
    # Non-Inventory Items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS non_inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_date TEXT
        )
    """)
    
    # Daily Balance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            opening_balance REAL DEFAULT 0,
            daily_revenue REAL DEFAULT 0,
            daily_expenses REAL DEFAULT 0,
            closing_balance REAL DEFAULT 0,
            cash_collected REAL DEFAULT 0,
            merchant_collected REAL DEFAULT 0,
            is_saturday INTEGER DEFAULT 0
        )
    """)
    
    # Default categories
    default_categories = ["Food", "Alcohol", "Beverages", "Cleaning Supplies", "Room Supplies", "Stationery"]
    for cat in default_categories:
        cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (cat,))
    
    # Default non-inventory items
    default_non_inventory = [
        "French Fries", "Burger", "Pizza", "Sandwich", "Salad",
        "Smoothie", "Juice", "Coffee", "Tea", "Room Service",
        "Chicken", "Fish", "Rice", "Pasta", "Soup"
    ]
    for item in default_non_inventory:
        cursor.execute("INSERT OR IGNORE INTO non_inventory_items (name) VALUES (?)", (item,))
    
    # ================ INITIALIZE ROOMS ================
    # Room data: (room_number, room_type, price)
    default_rooms = [
        ("Gorilla", "Standard", 40000),
        ("Antelope", "Standard", 40000),
        ("Lion", "Deluxe", 50000),
        ("Elephant", "Deluxe", 50000),
        ("Peacock", "Budget", 30000),
        ("Zebra", "Budget", 30000),
        ("Rhino", "Budget", 30000)
    ]
    
    for room_number, room_type, price in default_rooms:
        cursor.execute("""
            INSERT OR IGNORE INTO rooms (room_number, room_type, price, status)
            VALUES (?, ?, ?, 'Vacant')
        """, (room_number, room_type, price))
    
    conn.commit()
    conn.close()

# ================ SYSTEM INITIALIZATION ================

STATE_FILE = "system_state.json"

def initialize_system():
    """Initialize system - create daily balance for today"""
    today = datetime.now().strftime("%Y-%m-%d")
    initialize_daily_balance(today)
    
    # Check if business date exists
    if not os.path.exists(STATE_FILE):
        set_business_date(today)

def get_business_date():
    """Get current business date"""
    if not os.path.exists(STATE_FILE):
        default = {"business_date": datetime.now().strftime("%Y-%m-%d")}
        with open(STATE_FILE, "w") as f:
            json.dump(default, f)
        return default["business_date"]
    with open(STATE_FILE, "r") as f:
        return json.load(f).get("business_date", datetime.now().strftime("%Y-%m-%d"))

def set_business_date(date):
    """Set business date"""
    with open(STATE_FILE, "w") as f:
        json.dump({"business_date": date}, f)

# ================ INVENTORY FUNCTIONS ================

def get_all_categories():
    """Get all categories"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()
    conn.close()
    return categories

def add_category(name):
    """Add a new category"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return True, "Category added successfully"
    except:
        conn.close()
        return False, "Category already exists"

def delete_category(category_id):
    """Delete a category"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE category_id = ?", (category_id,))
        count = cursor.fetchone()[0]
        if count > 0:
            conn.close()
            return False, "Cannot delete category with existing items"
        
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        conn.close()
        return True, "Category deleted successfully"
    except:
        conn.close()
        return False, "Error deleting category"

def get_all_items():
    """Get all inventory items with category names"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, c.name, i.name, i.quantity, i.cost_price, i.selling_price
        FROM inventory i
        JOIN categories c ON i.category_id = c.id
        ORDER BY c.name, i.name
    """)
    items = cursor.fetchall()
    conn.close()
    return items

def add_item(category_name, name, quantity, cost_price, selling_price):
    """Add a new inventory item - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return False, "Category not found"
        
        category_id = result[0]
        
        cursor.execute("""
            SELECT id, quantity FROM inventory 
            WHERE category_id = ? AND LOWER(name) = LOWER(?)
        """, (category_id, name))
        existing = cursor.fetchone()
        
        if existing:
            new_qty = existing[1] + quantity
            cursor.execute("""
                UPDATE inventory 
                SET quantity = ?, cost_price = ?, selling_price = ?
                WHERE id = ?
            """, (new_qty, cost_price, selling_price, existing[0]))
            conn.commit()
            conn.close()
            return True, f"Stock updated. New quantity: {new_qty}"
        else:
            cursor.execute("""
                INSERT INTO inventory (category_id, name, quantity, cost_price, selling_price)
                VALUES (?, ?, ?, ?, ?)
            """, (category_id, name.title(), quantity, cost_price, selling_price))
            conn.commit()
            conn.close()
            return True, "Item added successfully"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_item(item_id):
    """Delete an inventory item"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return True, "Item deleted successfully"
    except:
        conn.close()
        return False, "Error deleting item"

def update_item(item_id, name, quantity, cost_price, selling_price, add_to_stock=True):
    """Update an inventory item - with option to add or replace stock"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if add_to_stock:
            cursor.execute("SELECT quantity FROM inventory WHERE id = ?", (item_id,))
            current_qty = cursor.fetchone()[0]
            new_qty = current_qty + quantity
        else:
            new_qty = quantity
            
        cursor.execute("""
            UPDATE inventory 
            SET name = ?, quantity = ?, cost_price = ?, selling_price = ?
            WHERE id = ?
        """, (name.title(), new_qty, cost_price, selling_price, item_id))
        conn.commit()
        conn.close()
        return True, f"Item updated. New quantity: {new_qty}"
    except:
        conn.close()
        return False, "Error updating item"

def get_item_by_name(item_name):
    """Get item by name (case insensitive)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, quantity, cost_price, selling_price
        FROM inventory 
        WHERE LOWER(name) = LOWER(?)
    """, (item_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "id": result[0],
            "name": result[1],
            "quantity": result[2],
            "cost_price": result[3],
            "selling_price": result[4]
        }
    return None

def search_items(keyword):
    """Search inventory items - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, c.name, i.name, i.quantity, i.cost_price, i.selling_price
        FROM inventory i
        JOIN categories c ON i.category_id = c.id
        WHERE LOWER(i.name) LIKE LOWER(?) OR LOWER(c.name) LIKE LOWER(?)
        ORDER BY c.name, i.name
    """, (f"%{keyword}%", f"%{keyword}%"))
    items = cursor.fetchall()
    conn.close()
    return items

def get_low_stock_items(threshold=5):
    """Get items with low stock"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.name, i.quantity
        FROM inventory i
        WHERE i.quantity <= ?
        ORDER BY i.quantity ASC
    """, (threshold,))
    items = cursor.fetchall()
    conn.close()
    return items

def get_item_details(item_name):
    """Get full item details including cost and selling price - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, quantity, cost_price, selling_price
        FROM inventory 
        WHERE LOWER(name) = LOWER(?)
    """, (item_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "id": result[0],
            "name": result[1],
            "quantity": result[2],
            "cost_price": result[3],
            "selling_price": result[4]
        }
    return None

# ================ NON-INVENTORY ITEMS FUNCTIONS ================

def get_non_inventory_items():
    """Get list of non-inventory items from database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM non_inventory_items ORDER BY name")
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

def add_non_inventory_item(name):
    """Add a new non-inventory item - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM non_inventory_items WHERE LOWER(name) = LOWER(?)", (name,))
        if cursor.fetchone():
            conn.close()
            return False, "Item already exists"
            
        cursor.execute(
            "INSERT INTO non_inventory_items (name, created_date) VALUES (?, datetime('now'))",
            (name.title(),)
        )
        conn.commit()
        conn.close()
        return True, "Item added successfully"
    except:
        conn.close()
        return False, "Error adding item"

def delete_non_inventory_item(name):
    """Delete a non-inventory item - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM non_inventory_items WHERE LOWER(name) = LOWER(?)", (name,))
        conn.commit()
        conn.close()
        return True, "Item deleted successfully"
    except:
        conn.close()
        return False, "Error deleting item"

def get_all_sale_items():
    """Get all items available for sale (inventory + non-inventory)"""
    inventory_items = get_sale_items()
    non_inventory_items = get_non_inventory_items()
    all_items = [item for item in inventory_items if item != "No items available"]
    all_items.extend(non_inventory_items)
    return sorted(set(all_items))

def get_item_type(item_name):
    """Determine if an item is inventory or non-inventory - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM inventory WHERE LOWER(name) = LOWER(?)", (item_name,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return "inventory"
    return "non_inventory"

# ================ SALES FUNCTIONS ================

def get_sale_items():
    """Get items available for sale (with stock > 0)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM inventory 
        WHERE quantity > 0 
        ORDER BY name
    """)
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

def get_item_price(item_name):
    """Get item price, cost, and stock by name - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT selling_price, cost_price, quantity 
        FROM inventory 
        WHERE LOWER(name) = LOWER(?)
    """, (item_name,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "price": result[0],
            "cost": result[1],
            "quantity": result[2],
            "profit_per_unit": result[0] - result[1],
            "type": "inventory"
        }
    else:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM non_inventory_items WHERE LOWER(name) = LOWER(?)", (item_name,))
        non_inv_result = cursor.fetchone()
        conn.close()
        
        if non_inv_result:
            return {
                "price": 0,
                "cost": 0,
                "quantity": 999999,
                "profit_per_unit": 0,
                "type": "non_inventory"
            }
        return None

def update_item_stock(item_name, quantity_sold):
    """Update stock after a sale (only for inventory items) - case insensitive"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM inventory WHERE LOWER(name) = LOWER(?)", (item_name,))
    result = cursor.fetchone()
    
    if result:
        try:
            cursor.execute("""
                UPDATE inventory 
                SET quantity = quantity - ? 
                WHERE LOWER(name) = LOWER(?)
            """, (quantity_sold, item_name))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False
    else:
        conn.close()
        return True

def add_sale_item(item_name, quantity, unit_price, total_revenue, notes="", cost_price=0, payment_type="Cash"):
    """Record a sale with payment type and update daily balance"""
    conn = None
    cursor = None
    
    total_cost = quantity * cost_price
    total_profit = total_revenue - total_cost
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sales (
                item_name, quantity, cost_price, unit_price, 
                total_revenue, total_cost, total_profit, 
                sale_date, notes, payment_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), ?, ?)
        """, (item_name.title(), quantity, cost_price, unit_price, 
              total_revenue, total_cost, total_profit, notes, payment_type))
        
        conn.commit()
        conn.close()
        
        # Update daily balance in a separate connection
        try:
            update_daily_balance(today, total_revenue, 0)
        except Exception as e:
            print(f"Warning: Could not update daily balance: {e}")
        
        return True, f"Sale recorded: {quantity} x {item_name} = UGX {total_revenue:,.0f} | Profit: UGX {total_profit:,.0f}"
        
    except Exception as e:
        if conn:
            conn.close()
        return False, f"Error: {str(e)}"
    
def get_recent_sales(limit=50):
    """Get recent sales with all details including profit and payment type"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT item_name, quantity, unit_price, total_revenue, total_cost, total_profit, sale_date, notes, payment_type
        FROM sales
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    sales = cursor.fetchall()
    conn.close()
    return sales

def get_total_sales(date=None):
    """Get total sales and profit for a date"""
    conn = get_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("""
            SELECT SUM(total_revenue), SUM(total_cost), SUM(total_profit), COUNT(*)
            FROM sales
            WHERE DATE(sale_date) = ?
        """, (date,))
    else:
        cursor.execute("""
            SELECT SUM(total_revenue), SUM(total_cost), SUM(total_profit), COUNT(*)
            FROM sales
        """)
    result = cursor.fetchone()
    conn.close()
    return {
        "revenue": result[0] or 0,
        "cost": result[1] or 0,
        "profit": result[2] or 0,
        "count": result[3] or 0
    }

def get_sales_by_payment_type(date=None):
    """Get sales broken down by payment type"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if date:
        cursor.execute("""
            SELECT 
                payment_type,
                SUM(total_revenue) as total,
                COUNT(*) as count
            FROM sales
            WHERE DATE(sale_date) = ?
            GROUP BY payment_type
        """, (date,))
    else:
        cursor.execute("""
            SELECT 
                payment_type,
                SUM(total_revenue) as total,
                COUNT(*) as count
            FROM sales
            GROUP BY payment_type
        """)
    
    results = cursor.fetchall()
    conn.close()
    
    sales_by_type = {"Cash": 0, "Merchant": 0}
    for payment_type, total, count in results:
        sales_by_type[payment_type] = total
    
    return sales_by_type

# ================ EXPENSES FUNCTIONS ================

def add_expense(name, amount, notes=""):
    """Record an expense and update daily balance"""
    conn = None
    cursor = None
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO expenses (name, amount, expense_date, notes)
            VALUES (?, ?, datetime('now'), ?)
        """, (name, amount, notes))
        
        # Update daily balance in a separate connection to avoid lock
        conn.commit()
        conn.close()
        
        # Update daily balance in a separate connection
        try:
            update_daily_balance(today, 0, amount)
        except Exception as e:
            print(f"Warning: Could not update daily balance: {e}")
        
        return True, "Expense recorded successfully"
        
    except Exception as e:
        if conn:
            conn.close()
        return False, f"Error: {str(e)}"
    
def get_all_expenses(limit=None):
    """Get all expenses with optional limit"""
    conn = get_connection()
    cursor = conn.cursor()
    if limit:
        cursor.execute("""
            SELECT id, name, amount, expense_date, notes
            FROM expenses
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
    else:
        cursor.execute("""
            SELECT id, name, amount, expense_date, notes
            FROM expenses
            ORDER BY id DESC
        """)
    expenses = cursor.fetchall()
    conn.close()
    return expenses

def get_recent_expenses(limit=50):
    """Get recent expenses"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, amount, expense_date, notes
        FROM expenses
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    expenses = cursor.fetchall()
    conn.close()
    return expenses

def get_expense_by_id(expense_id):
    """Get a single expense by ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, amount, expense_date, notes
        FROM expenses
        WHERE id = ?
    """, (expense_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "id": result[0],
            "name": result[1],
            "amount": result[2],
            "date": result[3],
            "notes": result[4]
        }
    return None

def update_expense(expense_id, name, amount, notes=""):
    """Update an existing expense"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE expenses 
            SET name = ?, amount = ?, notes = ?
            WHERE id = ?
        """, (name, amount, notes, expense_id))
        conn.commit()
        conn.close()
        return True, "Expense updated successfully"
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_expense(expense_id):
    """Delete an expense"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
        return True, "Expense deleted successfully"
    except Exception as e:
        conn.close()
        return False, str(e)
    
def get_weekly_expenses(start_date, end_date=None):
    """Get total expenses for a week period"""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(amount), COUNT(*)
        FROM expenses
        WHERE DATE(expense_date) >= ? AND DATE(expense_date) <= ?
    """, (start_date, end_date))
    result = cursor.fetchone()
    conn.close()
    return result[0] or 0, result[1] or 0

def get_total_expenses(date=None):
    """Get total expenses for a date"""
    conn = get_connection()
    cursor = conn.cursor()
    if date:
        cursor.execute("""
            SELECT SUM(amount), COUNT(*)
            FROM expenses
            WHERE DATE(expense_date) = ?
        """, (date,))
    else:
        cursor.execute("SELECT SUM(amount), COUNT(*) FROM expenses")
    result = cursor.fetchone()
    conn.close()
    return result[0] or 0, result[1] or 0

# ================ DAILY BALANCE FUNCTIONS ================

def get_day_of_week(date_str):
    """Get day of week (0=Monday, 6=Sunday)"""
    return datetime.strptime(date_str, "%Y-%m-%d").weekday()

def get_weekly_start_date(date_str):
    """Get the Sunday that starts the week"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    days_to_sunday = (dt.weekday() + 1) % 7
    sunday = dt - timedelta(days=days_to_sunday)
    return sunday.strftime("%Y-%m-%d")

def initialize_daily_balance(date_str):
    """Initialize daily balance for a date"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM daily_balance WHERE date = ?", (date_str,))
    if cursor.fetchone():
        conn.close()
        return
    
    prev_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute("SELECT closing_balance FROM daily_balance WHERE date = ?", (prev_date,))
    prev_balance = cursor.fetchone()
    opening_balance = prev_balance[0] if prev_balance else 0
    
    is_saturday = get_day_of_week(date_str) == 5
    
    if is_saturday:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN payment_type = 'Cash' THEN total_revenue ELSE 0 END),
                SUM(CASE WHEN payment_type = 'Merchant' THEN total_revenue ELSE 0 END)
            FROM sales 
            WHERE DATE(sale_date) = ?
        """, (date_str,))
        cash_collected, merchant_collected = cursor.fetchone() or (0, 0)
        opening_balance = 0
        
        cursor.execute("""
            INSERT INTO daily_balance (date, opening_balance, daily_revenue, daily_expenses, closing_balance, cash_collected, merchant_collected, is_saturday)
            VALUES (?, ?, 0, 0, ?, ?, ?, ?)
        """, (date_str, opening_balance, opening_balance, cash_collected or 0, merchant_collected or 0, 1))
    else:
        cursor.execute("""
            INSERT INTO daily_balance (date, opening_balance, daily_revenue, daily_expenses, closing_balance, cash_collected, merchant_collected, is_saturday)
            VALUES (?, ?, 0, 0, ?, 0, 0, 0)
        """, (date_str, opening_balance, opening_balance))
    
    conn.commit()
    conn.close()

def update_daily_balance(date_str, revenue_amount=0, expense_amount=0):
    """Update daily balance with revenue and expenses"""
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if daily_balance exists for this date
        cursor.execute("SELECT id FROM daily_balance WHERE date = ?", (date_str,))
        exists = cursor.fetchone()
        
        if not exists:
            conn.close()
            initialize_daily_balance(date_str)
            conn = get_connection()
            cursor = conn.cursor()
        
        # Get current balance
        cursor.execute("""
            SELECT opening_balance, daily_revenue, daily_expenses, closing_balance
            FROM daily_balance 
            WHERE date = ?
        """, (date_str,))
        result = cursor.fetchone()
        
        if result:
            opening_balance, daily_revenue, daily_expenses, closing_balance = result
            new_daily_revenue = daily_revenue + revenue_amount
            new_daily_expenses = daily_expenses + expense_amount
            new_closing_balance = opening_balance + new_daily_revenue - new_daily_expenses
            
            cursor.execute("""
                UPDATE daily_balance 
                SET daily_revenue = ?, daily_expenses = ?, closing_balance = ?
                WHERE date = ?
            """, (new_daily_revenue, new_daily_expenses, new_closing_balance, date_str))
            conn.commit()
            conn.close()
            return new_closing_balance
        
        conn.close()
        return 0
        
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error updating daily balance: {e}")
        return 0
    
def get_daily_balance(date_str):
    """Get daily balance for a date"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, opening_balance, daily_revenue, daily_expenses, closing_balance, 
               cash_collected, merchant_collected, is_saturday
        FROM daily_balance 
        WHERE date = ?
    """, (date_str,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "date": result[0],
            "opening_balance": result[1],
            "daily_revenue": result[2],
            "daily_expenses": result[3],
            "closing_balance": result[4],
            "cash_collected": result[5],
            "merchant_collected": result[6],
            "is_saturday": bool(result[7])
        }
    return None

def get_weekly_report(date_str):
    """Get weekly report starting from Sunday"""
    start_date = get_weekly_start_date(date_str)
    end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT date, opening_balance, daily_revenue, daily_expenses, closing_balance,
               cash_collected, merchant_collected, is_saturday
        FROM daily_balance 
        WHERE date >= ? AND date <= ?
        ORDER BY date
    """, (start_date, end_date))
    
    results = cursor.fetchall()
    conn.close()
    
    weekly_data = []
    for row in results:
        weekly_data.append({
            "date": row[0],
            "opening_balance": row[1],
            "daily_revenue": row[2],
            "daily_expenses": row[3],
            "closing_balance": row[4],
            "cash_collected": row[5],
            "merchant_collected": row[6],
            "is_saturday": bool(row[7])
        })
    
    return weekly_data

# ================ NIGHT AUDIT FUNCTIONS ================

def perform_night_audit():
    """Perform night audit - reset expenses, carry forward balance"""
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT opening_balance, daily_revenue, daily_expenses, closing_balance,
                   cash_collected, merchant_collected, is_saturday
            FROM daily_balance 
            WHERE date = ?
        """, (today,))
        today_balance = cursor.fetchone()
        
        if not today_balance:
            conn.close()
            initialize_daily_balance(today)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT opening_balance, daily_revenue, daily_expenses, closing_balance,
                       cash_collected, merchant_collected, is_saturday
                FROM daily_balance 
                WHERE date = ?
            """, (today,))
            today_balance = cursor.fetchone()
        
        if today_balance:
            opening_balance, daily_revenue, daily_expenses, closing_balance, cash_collected, merchant_collected, is_saturday = today_balance
            
            is_saturday = get_day_of_week(today) == 5
            new_opening = 0 if is_saturday else closing_balance
            
            cursor.execute("""
                UPDATE daily_balance 
                SET daily_revenue = 0, daily_expenses = 0, closing_balance = ?
                WHERE date = ?
            """, (closing_balance, today))
            
            cursor.execute("SELECT id FROM daily_balance WHERE date = ?", (tomorrow,))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE daily_balance 
                    SET opening_balance = ?, closing_balance = ?, 
                        daily_revenue = 0, daily_expenses = 0,
                        cash_collected = 0, merchant_collected = 0,
                        is_saturday = ?
                    WHERE date = ?
                """, (new_opening, new_opening, 1 if is_saturday else 0, tomorrow))
            else:
                cursor.execute("""
                    INSERT INTO daily_balance (date, opening_balance, daily_revenue, daily_expenses, closing_balance, cash_collected, merchant_collected, is_saturday)
                    VALUES (?, ?, 0, 0, ?, 0, 0, ?)
                """, (tomorrow, new_opening, new_opening, 1 if is_saturday else 0))
        
        conn.commit()
        conn.close()
        
        set_business_date(tomorrow)
        
        return True, f"Night audit completed. Balance carried forward to {tomorrow}"
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Night audit failed: {str(e)}"

# ================ ROOMS FUNCTIONS ================

def get_all_rooms():
    """Get all rooms"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_number, room_type, price, status FROM rooms ORDER BY room_number")
    rooms = cursor.fetchall()
    conn.close()
    return rooms

def get_available_rooms():
    """Get available (vacant) rooms"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_number FROM rooms WHERE status = 'Vacant' ORDER BY room_number")
    rooms = [row[0] for row in cursor.fetchall()]
    conn.close()
    return rooms

def add_room(room_number, room_type, price):
    """Add a new room"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO rooms (room_number, room_type, price, status)
            VALUES (?, ?, ?, 'Vacant')
        """, (room_number, room_type, price))
        conn.commit()
        conn.close()
        return True, "Room added successfully"
    except:
        conn.close()
        return False, "Room number already exists"

def delete_room(room_number):
    """Delete a room"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_number,))
        conn.commit()
        conn.close()
        return True, "Room deleted successfully"
    except:
        conn.close()
        return False, "Error deleting room"

def update_room_status(room_number, status):
    """Update room status"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rooms SET status = ? WHERE room_number = ?", (status, room_number))
        conn.commit()
        conn.close()
        return True, "Room status updated"
    except:
        conn.close()
        return False, "Error updating room"

def check_in(room_number, customer_name, phone):
    """Check in a guest"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE room_number = ?", (room_number,))
        
        cursor.execute("""
            INSERT INTO bookings (room_number, customer_name, phone, check_in, check_out, status)
            VALUES (?, ?, ?, datetime('now'), '', 'Checked In')
        """, (room_number, customer_name, phone))
        
        conn.commit()
        conn.close()
        return True, f"Guest checked into room {room_number}"
    except Exception as e:
        conn.close()
        return False, str(e)

# ========== UPDATED check_out FUNCTION - Records Room Revenue ==========
def check_out(room_number):
    """Check out a guest and record room revenue"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get room price and booking details in one query
        cursor.execute("""
            SELECT r.price, b.customer_name, b.check_in
            FROM rooms r
            JOIN bookings b ON b.room_number = r.room_number
            WHERE r.room_number = ? AND b.status = 'Checked In'
        """, (room_number,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "No active booking found for this room"
        
        room_price, customer_name, check_in = result
        
        # Update room status and booking in one transaction
        check_out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Update room status
        cursor.execute("UPDATE rooms SET status = 'Vacant' WHERE room_number = ?", (room_number,))
        
        # Update booking
        cursor.execute("""
            UPDATE bookings 
            SET check_out = ?, status = 'Checked Out'
            WHERE room_number = ? AND status = 'Checked In'
        """, (check_out_time, room_number))
        
        # Record room revenue as a sale
        item_name = f"Room: {room_number} - {customer_name}"
        
        cursor.execute("""
            INSERT INTO sales (
                item_name, quantity, cost_price, unit_price, 
                total_revenue, total_cost, total_profit, 
                sale_date, notes, payment_type
            )
            VALUES (?, 1, 0, ?, ?, 0, ?, datetime('now'), ?, 'Cash')
        """, (item_name, room_price, room_price, room_price, 
              f"Room checkout: {customer_name}, Check-in: {check_in}"))
        
        # Update daily balance
        cursor.execute("""
            UPDATE daily_balance 
            SET daily_revenue = daily_revenue + ?, 
                closing_balance = closing_balance + ?
            WHERE date = ?
        """, (room_price, room_price, today))
        
        conn.commit()
        conn.close()
        
        return True, f"Room {room_number} checked out. Revenue: UGX {room_price:,.0f} recorded."
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)
def get_current_bookings():
    """Get current bookings"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT room_number, customer_name, phone, check_in
        FROM bookings 
        WHERE status = 'Checked In'
    """)
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_room_stats():
    """Get room statistics"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status = 'Occupied'")
    occupied = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM rooms")
    total = cursor.fetchone()[0] or 0
    conn.close()
    return occupied, total

# ================ REPORTS FUNCTIONS ================

def get_daily_report(date):
    """Get daily report data with profit and balances"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT SUM(total_revenue), SUM(total_cost), SUM(total_profit), COUNT(*)
        FROM sales
        WHERE DATE(sale_date) = ?
    """, (date,))
    sales_data = cursor.fetchone()
    sales_revenue = sales_data[0] or 0
    sales_cost = sales_data[1] or 0
    sales_profit = sales_data[2] or 0
    sales_count = sales_data[3] or 0
    
    payment_types = get_sales_by_payment_type(date)
    
    cursor.execute("""
        SELECT SUM(amount), COUNT(*)
        FROM expenses
        WHERE DATE(expense_date) = ?
    """, (date,))
    expenses_data = cursor.fetchone()
    expenses_total = expenses_data[0] or 0
    expenses_count = expenses_data[1] or 0
    
    balance = get_daily_balance(date)
    occupied, total = get_room_stats()
    
    conn.close()
    
    return {
        'date': date,
        'sales_revenue': sales_revenue,
        'sales_cost': sales_cost,
        'sales_profit': sales_profit,
        'sales_count': sales_count,
        'cash_sales': payment_types.get('Cash', 0),
        'merchant_sales': payment_types.get('Merchant', 0),
        'expenses': expenses_total,
        'expenses_count': expenses_count,
        'net_profit': sales_profit - expenses_total,
        'opening_balance': balance['opening_balance'] if balance else 0,
        'closing_balance': balance['closing_balance'] if balance else 0,
        'occupied': occupied,
        'total_rooms': total,
        'is_saturday': balance['is_saturday'] if balance else False,
        'cash_collected': balance['cash_collected'] if balance else 0,
        'merchant_collected': balance['merchant_collected'] if balance else 0
    }

def get_weekly_report_data(date_str):
    """Get weekly report data with balances"""
    return get_weekly_report(date_str)


def sync_business_date():
    """Sync business date with current date"""
    from datetime import datetime, timedelta
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    business_date = get_business_date()
    
    print(f"Current date: {current_date}, Business date: {business_date}")
    
    if business_date < current_date:
        # Perform night audit for each day between business_date and current_date
        current = datetime.strptime(business_date, "%Y-%m-%d")
        end = datetime.strptime(current_date, "%Y-%m-%d")
        
        day_count = 0
        while current < end:
            current += timedelta(days=1)
            perform_night_audit()
            day_count += 1
            print(f"Night audit performed for day {day_count}")
        
        set_business_date(current_date)
        return True, f"Business date synced to {current_date}. {day_count} night audits performed."
    return False, "Business date is up to date"
# Run initialization when module is imported
# initialize_system()  # Called from main.py