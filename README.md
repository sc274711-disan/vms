# 🏨 Valley View Motel Management System

A complete desktop-based hotel/motel management system built with Python and CustomTkinter. Streamline your motel operations including room bookings, sales, inventory, expenses, and financial reporting.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.14+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📋 Table of Contents

- [Features](#-features)
- [Business Rules](#-business-rules)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Database Structure](#-database-structure)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🏠 Dashboard
- Real-time overview of weekly performance
- Quick action buttons for common tasks
- Low stock alerts
- Shows: Week Revenue, Week Profit, Week Expenses, Net Profit

### 🛏️ Rooms Management
- 7 themed rooms (Gorilla, Antelope, Lion, Elephant, Peacock, Zebra, Rhino)
- Check-in/Check-out system
- Room status tracking (Vacant/Occupied)
- **Automatically records room revenue** on checkout

### 💰 Sales Management
- Sell inventory items with stock tracking
- Sell non-inventory items (food/services with custom pricing)
- Quantity selection with auto-calculation
- Payment types: Cash and Merchant
- Profit tracking (Revenue - Cost)
- Auto stock deduction on sale

### 📦 Inventory Management
- Categories management (Food, Alcohol, Beverages, etc.)
- Add, edit, delete items
- Stock management (add to existing stock)
- Low stock alerts
- Search functionality

### 💸 Expenses Management
- Record daily expenses
- Edit and delete expenses
- Filter by Today or All Expenses
- Real-time dashboard updates

### 📊 Reports
- Daily reports with profit and balances
- Weekly performance reports
- Balance reports with Saturday collection
- CSV export

### ⚙️ Settings
- Business date management
- Appearance (Dark/Light mode, font size)
- Database backup and restore
- Calendar date picker
- Auto night audit

---

## 📅 Business Rules

| Day | Revenue | Expenses | Profit | Balance |
|-----|---------|----------|--------|---------|
| Monday - Friday | Cumulative | Cumulative | Cumulative | Carried forward |
| Saturday | Collected | Collected | Collected | Reset to 0 |
| Sunday | Reset to 0 | Reset to 0 | Reset to 0 | Starts fresh |

### Night Audit System
- **Automatic at midnight** - Background thread checks every hour
- Manual advance option available
- **Saturday collection**: All money (Cash + Merchant) is collected
- **Sunday reset**: Everything resets to 0 for the new week

---

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Rooms Management
![Rooms](screenshots/rooms.png)

### Sales
![Sales](screenshots/sales.png)

### Inventory
![Inventory](screenshots/inventory.png)

### Reports
![Reports](screenshots/reports.png)

---

## 🚀 Installation

### Prerequisites
- Python 3.14 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/valley-view-motel.git
cd valley-view-motel