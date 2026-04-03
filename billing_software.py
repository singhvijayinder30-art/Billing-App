import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

class BillingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro-GST Billing Management System")
        self.root.geometry("900x650")
        
        self.cart = []
        self.db_init()
        self.create_widgets()

    def db_init(self):
        """Initialize database and tables."""
        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS products 
                           (id INTEGER PRIMARY KEY, name TEXT UNIQUE, price REAL, quantity INTEGER)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS customers 
                           (id INTEGER PRIMARY KEY, name TEXT, gst TEXT, address TEXT, contact TEXT, email TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS invoices 
                           (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_no TEXT, customer_id TEXT, 
                            date TEXT, total REAL, gst REAL, final_total REAL)''')
            conn.commit()

    def create_widgets(self):
        # --- Main Container ---
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # --- Product & Customer Input Section (Left Side) ---
        left_frame = tk.LabelFrame(main_frame, text="Management", padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5)

        # Product Entry
        tk.Label(left_frame, text="--- Add Product ---", font=("Arial", 10, "bold")).grid(row=0, columnspan=2, pady=5)
        tk.Label(left_frame, text="Name:").grid(row=1, column=0, sticky="w")
        self.p_name = tk.Entry(left_frame)
        self.p_name.grid(row=1, column=1, pady=2)

        tk.Label(left_frame, text="Price:").grid(row=2, column=0, sticky="w")
        self.p_price = tk.Entry(left_frame)
        self.p_price.grid(row=2, column=1, pady=2)

        tk.Label(left_frame, text="Stock Qty:").grid(row=3, column=0, sticky="w")
        self.p_qty = tk.Entry(left_frame)
        self.p_qty.grid(row=3, column=1, pady=2)

        tk.Button(left_frame, text="Add Product to DB", bg="#e1f5fe", command=self.add_product).grid(row=4, columnspan=2, pady=10)

        # Customer Entry
        tk.Label(left_frame, text="--- Add Customer ---", font=("Arial", 10, "bold")).grid(row=5, columnspan=2, pady=5)
        self.c_entries = {}
        fields = [("Name", "name"), ("GST No", "gst"), ("Address", "addr"), ("Contact", "phone"), ("Email", "email")]
        
        for i, (label, key) in enumerate(fields):
            tk.Label(left_frame, text=f"{label}:").grid(row=6+i, column=0, sticky="w")
            entry = tk.Entry(left_frame)
            entry.grid(row=6+i, column=1, pady=2)
            self.c_entries[key] = entry

        tk.Button(left_frame, text="Register Customer", bg="#e8f5e9", command=self.add_customer).grid(row=11, columnspan=2, pady=10)

        # --- Billing & Cart Section (Right Side) ---
        right_frame = tk.LabelFrame(main_frame, text="Billing Console", padx=10, pady=10)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5)

        tk.Label(right_frame, text="Customer ID/Name:").grid(row=0, column=0)
        self.bill_cust_id = tk.Entry(right_frame)
        self.bill_cust_id.grid(row=0, column=1)

        tk.Label(right_frame, text="Product Name:").grid(row=1, column=0)
        self.bill_p_name = tk.Entry(right_frame)
        self.bill_p_name.grid(row=1, column=1)

        tk.Label(right_frame, text="Qty:").grid(row=2, column=0)
        self.bill_p_qty = tk.Entry(right_frame)
        self.bill_p_qty.grid(row=2, column=1)

        tk.Button(right_frame, text="Add to Cart", command=self.add_to_cart, bg="#fffde7").grid(row=3, columnspan=2, pady=5)

        self.listbox = tk.Listbox(right_frame, width=50, height=10)
        self.listbox.grid(row=4, columnspan=2, pady=5)

        tk.Button(right_frame, text="Generate Final Invoice", command=self.generate_invoice, bg="#ffebee", font=("Arial", 10, "bold")).grid(row=5, columnspan=2, pady=5)

        self.text_bill = tk.Text(right_frame, height=12, width=50, bg="#f9f9f9")
        self.text_bill.grid(row=6, columnspan=2, pady=5)

    # --- Logic ---

    def add_product(self):
        try:
            with sqlite3.connect("shop.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                               (self.p_name.get(), float(self.p_price.get()), int(self.p_qty.get())))
                conn.commit()
            messagebox.showinfo("Success", "Product stored in inventory.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not add product: {e}")

    def add_customer(self):
        try:
            data = [self.c_entries[k].get() for k in ["name", "gst", "addr", "phone", "email"]]
            with sqlite3.connect("shop.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO customers (name, gst, address, contact, email) VALUES (?, ?, ?, ?, ?)", data)
                conn.commit()
            messagebox.showinfo("Success", "Customer profile created.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not add customer: {e}")

    def add_to_cart(self):
        name = self.bill_p_name.get()
        try:
            qty = int(self.bill_p_qty.get())
            with sqlite3.connect("shop.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT price, quantity FROM products WHERE name=?", (name,))
                result = cursor.fetchone()

            if result:
                price, stock = result
                if stock >= qty:
                    self.cart.append((name, price, qty))
                    self.listbox.insert(tk.END, f"{name} | Qty: {qty} | Price: ₹{price*qty:.2f}")
                else:
                    messagebox.showwarning("Out of Stock", f"Only {stock} units available.")
            else:
                messagebox.showerror("Error", "Product not found in database.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")

    def generate_invoice(self):
        if not self.cart:
            return messagebox.showwarning("Warning", "Cart is empty!")

        cust = self.bill_cust_id.get()
        total = sum(p * q for _, p, q in self.cart)
        gst = total * 0.18
        final = total + gst
        inv_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO invoices (invoice_no, customer_id, date, total, gst, final_total) VALUES (?, ?, ?, ?, ?, ?)",
                           (inv_no, cust, datetime.now().strftime("%Y-%m-%d %H:%M"), total, gst, final))
            conn.commit()

        # Display Bill
        bill_str = f"{'='*30}\n      TAX INVOICE\n{'='*30}\n"
        bill_str += f"Invoice: {inv_no}\nCustomer: {cust}\n"
        bill_str += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        bill_str += "-"*30 + "\n"
        for item in self.cart:
            bill_str += f"{item[0][:15]:<15} x{item[2]:<3} ₹{item[1]*item[2]:>8.2f}\n"
        bill_str += "-"*30 + "\n"
        bill_str += f"Subtotal:       ₹{total:>8.2f}\n"
        bill_str += f"GST (18%):      ₹{gst:>8.2f}\n"
        bill_str += f"Total Payable:  ₹{final:>8.2f}\n"
        bill_str += f"{'='*30}\n"

        self.text_bill.delete("1.0", tk.END)
        self.text_bill.insert(tk.END, bill_str)
        self.cart = [] # Clear cart after generation
        self.listbox.delete(0, tk.END)
        messagebox.showinfo("Success", "Invoice Generated and Saved.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BillingSystem(root)
    root.mainloop()