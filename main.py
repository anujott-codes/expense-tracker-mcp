import os
import sqlite3
from fastmcp import FastMCP

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP(name="ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
    ''')

init_db()

@mcp.tool
def add_expense(date: str, amount: float, category: str, subcategory: str = '', note: str = ''):
    """Add a new expense to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        
        curr = conn.execute('''
            INSERT INTO expenses (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, amount, category, subcategory, note))
        
    return {"status": "ok", "id": curr.lastrowid}

@mcp.tool
def list_expenses(start_date: str, end_date: str):
    """List all expenses in the database within the start date and end date."""
    with sqlite3.connect(DB_PATH) as conn:
        curr = conn.execute("""SELECT id, date, amount, category, subcategory, note FROM expenses
        WHERE date BETWEEN ? AND ? 
        ORDER BY id ASC""",
        (start_date, end_date))
        cols = [d[0] for d in curr.description]
        return [dict(zip(cols, row)) for row in curr.fetchall()]

@mcp.tool
def summarize_expenses(start_date: str, end_date: str, category: str = None):
    """Summarize expenses by category within the start date and end date."""
    with sqlite3.connect(DB_PATH) as conn:
        query = ("""SELECT category, SUM(amount) as total_amount FROM expenses
        WHERE date BETWEEN ? AND ?
        """)
        params = [start_date, end_date]
        if category:
            query += " AND category = ?"
            params.append(category)

        query += " GROUP BY category ORDER BY category ASC"
        curr = conn.execute(query, params)
        cols = [d[0] for d in curr.description]
        return [dict(zip(cols, row)) for row in curr.fetchall()]

@mcp.resource("expense://categories")
def categories():
    """Return a list of unique categories in the database."""
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

    
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)