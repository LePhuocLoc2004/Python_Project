import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import time

class BillingApp:
    def __init__(self, master):
        self.master = master
        master.title("Billing System")
        master.geometry("1000x700")

        # --- Database Setup ---
        self.conn = sqlite3.connect('billing_system.db')
        self.cursor = self.conn.cursor()
        self.create_tables() 

        # --- Current Bill State ---
        # Stores items using the internal Primary Key (id) for reliable lookups
        self.current_bill_items = {} 

        # --- Set up the Main Frames ---
        self.setup_main_frames()
        self.setup_product_management_frame() 
        self.setup_billing_frame()
        self.setup_bill_display_frame()

        # Load initial product data
        self.view_products()

    # =================================================================
    #                           DATABASE METHODS
    # =================================================================

    def create_tables(self):
        try:
            # Products Table: 'id' is internal PK, 'sku' is the user-defined identifier
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Products (
                    id INTEGER PRIMARY KEY,     -- Internal, hidden, auto-incremented key
                    sku TEXT NOT NULL UNIQUE,   -- User-defined Product ID/SKU
                    name TEXT NOT NULL UNIQUE,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL
                )
            """)
            # Bills Table remains the same
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Bills (
                    bill_id INTEGER PRIMARY KEY,
                    date TEXT,
                    total_amount REAL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not create tables: {e}")

    def add_product(self):
        """Adds a new product using the user-defined SKU."""
        sku = self.product_sku_entry.get().strip() # Retrieve the user-defined SKU
        name = self.product_name_entry.get().strip()
        price_str = self.product_price_entry.get().strip()
        stock_str = self.product_stock_entry.get().strip()

        if not sku or not name or not price_str or not stock_str:
            messagebox.showerror("Input Error", "All product fields (including Product ID) are required.")
            return

        try:
            price = float(price_str)
            stock = int(stock_str)
            if price <= 0 or stock < 0:
                 messagebox.showerror("Input Error", "Price must be positive and Stock must be non-negative.")
                 return
        except ValueError:
            messagebox.showerror("Input Error", "Price must be a number and Stock must be an integer.")
            return

        try:
            # SQL inserts SKU, name, price, stock, letting 'id' be auto-generated
            self.cursor.execute("INSERT INTO Products (sku, name, price, stock) VALUES (?, ?, ?, ?)", (sku, name, price, stock))
            self.conn.commit()
            messagebox.showinfo("Success", f"Product '{name}' (SKU: {sku}) added successfully.")
            self.view_products()
            
            # Clear entries
            self.product_sku_entry.delete(0, tk.END)
            self.product_name_entry.delete(0, tk.END)
            self.product_price_entry.delete(0, tk.END)
            self.product_stock_entry.delete(0, tk.END)
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: Products.sku' in str(e):
                messagebox.showerror("Database Error", f"Product ID '{sku}' already exists. Please choose a different identifier.")
            elif 'UNIQUE constraint failed: Products.name' in str(e):
                messagebox.showerror("Database Error", f"A product named '{name}' already exists.")
            else:
                 messagebox.showerror("Database Error", f"An Integrity Error occurred: {e}")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")

    def view_products(self):
        """Fetches all products and displays them in the list (displaying SKU, hiding internal ID)."""
        for row in self.product_list.get_children():
            self.product_list.delete(row)

        # Select both the internal ID and the SKU
        self.cursor.execute("SELECT id, sku, name, price, stock FROM Products ORDER BY id")
        products = self.cursor.fetchall() 

        for product in products:
            internal_id = product[0]
            display_values = product[1:] # SKU, Name, Price, Stock
            # Display SKU, Name, Price, Stock
            self.product_list.insert('', tk.END, iid=internal_id, values=display_values)

    # =================================================================
    #                           GUI SETUP METHODS
    # =================================================================

    def setup_main_frames(self):
        """Sets up the top and bottom main containers."""
        self.top_frame = tk.Frame(self.master, padx=10, pady=10, bg='#f0f0f0')
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.bottom_frame = tk.Frame(self.master, padx=10, pady=10, bg='#e0e0e0')
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def setup_product_management_frame(self):
        """
        Sets up the frame for adding and viewing products.
        Uses 'SKU/Product ID' for user input and display.
        """
        prod_frame = tk.LabelFrame(self.top_frame, text="📦 Product Management", padx=10, pady=10, font=('Arial', 10, 'bold'))
        prod_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        # SKU/Product ID Field
        tk.Label(prod_frame, text="Product ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.product_sku_entry = tk.Entry(prod_frame, width=20) 
        self.product_sku_entry.grid(row=0, column=1, padx=5, pady=2)
        
        # Other Input Fields
        tk.Label(prod_frame, text="Name:").grid(row=1, column=0, sticky='w', pady=2)
        self.product_name_entry = tk.Entry(prod_frame, width=20)
        self.product_name_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(prod_frame, text="Price:").grid(row=2, column=0, sticky='w', pady=2)
        self.product_price_entry = tk.Entry(prod_frame, width=20)
        self.product_price_entry.grid(row=2, column=1, padx=5, pady=2)

        tk.Label(prod_frame, text="Stock:").grid(row=3, column=0, sticky='w', pady=2)
        self.product_stock_entry = tk.Entry(prod_frame, width=20)
        self.product_stock_entry.grid(row=3, column=1, padx=5, pady=2)

        tk.Button(prod_frame, text="➕ Add Product", command=self.add_product, bg='#4CAF50', fg='white').grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')

        # Product List Treeview with Scrollbar (showing SKU/ID)
        tk.Label(prod_frame, text="--- Product List ---", font=('Arial', 10, 'bold')).grid(row=5, column=0, columnspan=2, pady=5)
        
        list_container = tk.Frame(prod_frame)
        list_container.grid(row=6, column=0, columnspan=2, pady=5, sticky='nsew')
        
        columns = ("PRODUCT ID", "Name", "Price", "Stock") # Only visible columns
        self.product_list = ttk.Treeview(list_container, columns=columns, show='headings', height=8)

        vsb = ttk.Scrollbar(list_container, orient="vertical", command=self.product_list.yview)
        self.product_list.configure(yscrollcommand=vsb.set)

        vsb.pack(side='right', fill='y')
        self.product_list.pack(side='left', fill='both', expand=True)

        for col in columns:
            self.product_list.heading(col, text=col)
            self.product_list.column(col, width=60 if col in ("Price", "Stock") else 100, anchor='center')
        self.product_list.column("PRODUCT ID", width=70, anchor='center')
        self.product_list.column("Name", width=130, anchor='center')


    def setup_billing_frame(self):
        """Sets up the frame for adding items to the current bill."""
        bill_input_frame = tk.LabelFrame(self.top_frame, text="🛒 Add Item to Bill", padx=10, pady=10, font=('Arial', 10, 'bold'))
        bill_input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5)

        tk.Label(bill_input_frame, text="Product ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.bill_product_id_entry = tk.Entry(bill_input_frame, width=15)
        self.bill_product_id_entry.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(bill_input_frame, text="Quantity:").grid(row=1, column=0, sticky='w', pady=2)
        self.bill_quantity_entry = tk.Entry(bill_input_frame, width=15)
        self.bill_quantity_entry.insert(0, '1')
        self.bill_quantity_entry.grid(row=1, column=1, padx=5, pady=2)

        tk.Button(bill_input_frame, text="➕ Add to Bill", command=self.add_to_bill, bg='#2196F3', fg='white').grid(row=2, column=0, columnspan=2, pady=10, sticky='ew')
        tk.Button(bill_input_frame, text="🗑️ Clear Bill", command=self.clear_bill, bg='#F44336', fg='white').grid(row=3, column=0, columnspan=2, pady=5, sticky='ew')
        tk.Button(bill_input_frame, text="💰 Generate Invoice", command=self.generate_bill_final, bg='#FF9800', fg='white').grid(row=4, column=0, columnspan=2, pady=5, sticky='ew')
        
    def setup_bill_display_frame(self):
        """Sets up the frame to display the current bill and total with a scrollbar."""
        bill_display_frame = tk.LabelFrame(self.bottom_frame, text="🧾 Current Bill", padx=10, pady=10, font=('Arial', 12, 'bold'))
        bill_display_frame.pack(fill=tk.BOTH, expand=True)

        bill_container = tk.Frame(bill_display_frame)
        bill_container.pack(fill='both', expand=True)

        columns = ("PRODUCT ID", "Name", "Price", "Qty", "Subtotal") # Columns now use SKU/ID
        self.bill_display = ttk.Treeview(bill_container, columns=columns, show='headings')
        
        vsb_bill = ttk.Scrollbar(bill_container, orient="vertical", command=self.bill_display.yview)
        self.bill_display.configure(yscrollcommand=vsb_bill.set)

        vsb_bill.pack(side='right', fill='y')
        self.bill_display.pack(side='left', fill='both', expand=True)

        for col in columns:
            self.bill_display.heading(col, text=col)
            self.bill_display.column(col, width=100 if col in ("SKU/ID", "Price", "Qty", "Subtotal") else 300, anchor='center')
        
        self.total_var = tk.StringVar(value="Total: $0.00")
        tk.Label(bill_display_frame, textvariable=self.total_var, font=('Arial', 16, 'bold'), anchor='e', fg='darkgreen').pack(fill=tk.X, pady=10)

    # =================================================================
    #                         BILLING LOGIC METHODS
    # =================================================================

    def add_to_bill(self):
        """Fetches product details (by SKU/ID) and adds it to the current bill state."""
        sku_str = self.bill_product_id_entry.get().strip() # Use SKU for lookup
        quantity_str = self.bill_quantity_entry.get().strip()

        if not sku_str or not quantity_str:
            messagebox.showerror("Input Error", "Product SKU/ID and Quantity are required.")
            return

        try:
            qty = int(quantity_str)
            if qty <= 0:
                messagebox.showerror("Input Error", "Quantity must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be an integer.")
            return

        # 1. Fetch Product Data using SKU/ID
        self.cursor.execute("SELECT id, sku, name, price, stock FROM Products WHERE sku=?", (sku_str,))
        product = self.cursor.fetchone()

        if not product:
            messagebox.showerror("Error", f"Product with SKU/ID '{sku_str}' not found.")
            return

        # Extract data: Internal ID (p_id) is product[0], SKU is product[1]
        p_id, sku, name, price, stock = product[0], product[1], product[2], product[3], product[4]

        # 2. Check Stock
        if stock < qty:
            messagebox.showwarning("Stock Alert", f"Only {stock} units of {name} in stock. Adjusting quantity.")
            qty = stock
            if qty == 0:
                messagebox.showerror("Stock Error", f"{name} is out of stock.")
                return

        # 3. Update Bill State (using the internal 'p_id' as the dictionary key)
        subtotal = round(price * qty, 2)
        
        if p_id in self.current_bill_items:
            # Item already in bill, update quantity
            self.current_bill_items[p_id]['qty'] += qty
            self.current_bill_items[p_id]['subtotal'] = round(self.current_bill_items[p_id]['qty'] * price, 2)
        else:
            # New item
            self.current_bill_items[p_id] = {
                'sku': sku,
                'name': name,
                'price': price,
                'qty': qty,
                'subtotal': subtotal
            }
        
        # 4. Refresh Display
        self.refresh_bill_display()
        self.bill_product_id_entry.delete(0, tk.END)

    def refresh_bill_display(self):
        """Clears and re-populates the bill Treeview and updates the total."""
        for row in self.bill_display.get_children():
            self.bill_display.delete(row)

        grand_total = 0.0

        for p_id, item in self.current_bill_items.items():
            self.bill_display.insert('', tk.END, values=(
                item['sku'],       # Use SKU/ID for display
                item['name'], 
                f"{item['price']:.2f}", 
                item['qty'], 
                f"{item['subtotal']:.2f}"
            ))
            grand_total += item['subtotal']

        self.total_var.set(f"Total: ${grand_total:.2f}")

    def clear_bill(self):
        """Clears the current bill state and display."""
        if not self.current_bill_items:
             messagebox.showinfo("Info", "Bill is already empty.")
             return

        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the current bill?"):
            self.current_bill_items = {}
            self.refresh_bill_display()
            messagebox.showinfo("Cleared", "Current bill has been cleared.")

    def generate_bill_final(self):
        """Finalizes the bill, saves it to the database, and updates stock."""
        if not self.current_bill_items:
            messagebox.showerror("Error", "Cannot generate an empty bill.")
            return

        if not messagebox.askyesno("Confirm Bill", "Finalize and generate invoice?"):
            return

        try:
            grand_total = sum(item['subtotal'] for item in self.current_bill_items.values())

            # 1. Insert Bill Header
            current_date = time.strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute("INSERT INTO Bills (date, total_amount) VALUES (?, ?)", (current_date, grand_total))
            bill_id = self.cursor.lastrowid

            # 2. Update Stock for each item (p_id is the internal key)
            for p_id, item in self.current_bill_items.items():
                current_stock = self.cursor.execute("SELECT stock FROM Products WHERE id=?", (p_id,)).fetchone()[0]
                new_stock = current_stock - item['qty']
                    
                self.cursor.execute("UPDATE Products SET stock=? WHERE id=?", (new_stock, p_id))

            self.conn.commit()

            # 3. Display Success and Reset
            messagebox.showinfo("Success", f"Invoice #{bill_id} generated successfully!\nTotal Amount: ${grand_total:.2f}")
            self.current_bill_items = {}
            self.refresh_bill_display()
            self.view_products()

        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to generate bill: {e}")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Application Error", f"An unexpected error occurred during billing: {e}")

# =================================================================
#                       APPLICATION RUNNER
# =================================================================

if __name__ == '__main__':
    root = tk.Tk()
    app = BillingApp(root)
    root.mainloop()
    
    if app.conn:
        app.conn.close()
