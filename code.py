import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# Tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL,
    quantity INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    gst TEXT,
    address TEXT,
    contact TEXT,
    email TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    customer_id INTEGER,
    date TEXT,
    total REAL,
    gst REAL,
    final_total REAL
)
''')

conn.commit()

cart = []

# Add product
def add_product():
    cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                   (p_name.get(), float(p_price.get()), int(p_qty.get())))
    conn.commit()
    messagebox.showinfo("Success", "Product Added")

# Add customer
def add_customer():
    cursor.execute("INSERT INTO customers (name, gst, address, contact, email) VALUES (?, ?, ?, ?, ?)",
                   (c_name.get(), c_gst.get(), c_address.get(), c_contact.get(), c_email.get()))
    conn.commit()
    messagebox.showinfo("Success", "Customer Added")

# Add to cart
def add_to_cart():
    name = item_name.get()
    qty = int(item_qty.get())

    cursor.execute("SELECT price FROM products WHERE name=?", (name,))
    result = cursor.fetchone()

    if result:
        price = result[0]
        cart.append((name, price, qty))
        listbox.insert(tk.END, f"{name} x{qty} = ₹{price*qty}")
    else:
        messagebox.showerror("Error", "Product not found")

# Generate invoice
def generate_invoice():
    customer = customer_id.get()

    total = sum(p*q for _, p, q in cart)
    gst = total * 0.18
    final = total + gst

    invoice_no = f"INV{int(datetime.now().timestamp())}"

    cursor.execute("INSERT INTO invoices (invoice_no, customer_id, date, total, gst, final_total) VALUES (?, ?, ?, ?, ?, ?)",
                   (invoice_no, customer, str(datetime.now()), total, gst, final))
    conn.commit()

    bill = f"Invoice No: {invoice_no}\nDate: {datetime.now()}\n\n"

    for item in cart:
        bill += f"{item[0]} x{item[2]} = ₹{item[1]*item[2]}\n"

    bill += f"\nTotal: ₹{total}\nGST: ₹{gst}\nFinal: ₹{final}"

    text_bill.delete("1.0", tk.END)
    text_bill.insert(tk.END, bill)

    messagebox.showinfo("Success", "Invoice Generated")

# UI
root = tk.Tk()
root.title("GST Billing Software")

# Product Section
tk.Label(root, text="Product Name").grid(row=0, column=0)
tk.Label(root, text="Price").grid(row=1, column=0)
tk.Label(root, text="Qty").grid(row=2, column=0)

p_name = tk.Entry(root)
p_price = tk.Entry(root)
p_qty = tk.Entry(root)

p_name.grid(row=0, column=1)
p_price.grid(row=1, column=1)
p_qty.grid(row=2, column=1)

tk.Button(root, text="Add Product", command=add_product).grid(row=3, column=0, columnspan=2)

# Customer Section
tk.Label(root, text="Customer ID").grid(row=4, column=0)
customer_id = tk.Entry(root)
customer_id.grid(row=4, column=1)

tk.Label(root, text="Name").grid(row=5, column=0)
tk.Label(root, text="GST").grid(row=6, column=0)
tk.Label(root, text="Address").grid(row=7, column=0)
tk.Label(root, text="Contact").grid(row=8, column=0)
tk.Label(root, text="Email").grid(row=9, column=0)

c_name = tk.Entry(root)
c_gst = tk.Entry(root)
c_address = tk.Entry(root)
c_contact = tk.Entry(root)
c_email = tk.Entry(root)

c_name.grid(row=5, column=1)
c_gst.grid(row=6, column=1)
c_address.grid(row=7, column=1)
c_contact.grid(row=8, column=1)
c_email.grid(row=9, column=1)

tk.Button(root, text="Add Customer", command=add_customer).grid(row=10, column=0, columnspan=2)

# Cart Section
tk.Label(root, text="Item Name").grid(row=11, column=0)
tk.Label(root, text="Qty").grid(row=12, column=0)

item_name = tk.Entry(root)
item_qty = tk.Entry(root)

item_name.grid(row=11, column=1)
item_qty.grid(row=12, column=1)

tk.Button(root, text="Add to Cart", command=add_to_cart).grid(row=13, column=0, columnspan=2)

listbox = tk.Listbox(root, width=40)
listbox.grid(row=14, column=0, columnspan=2)

tk.Button(root, text="Generate Invoice", command=generate_invoice).grid(row=15, column=0, columnspan=2)

text_bill = tk.Text(root, height=10, width=40)
text_bill.grid(row=16, column=0, columnspan=2)

root.mainloop()