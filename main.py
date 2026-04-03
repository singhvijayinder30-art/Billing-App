import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import os
import sys

# --- MAC-SPECIFIC DATABASE PATH FIX ---
# This ensures the database file stays with the App bundle on macOS
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")

db_path = os.path.join(base_path, "shop.db")

# Database setup
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tables setup
cursor.execute('''CREATE TABLE IF NOT EXISTS products 
               (id INTEGER PRIMARY KEY, name TEXT UNIQUE, price REAL, quantity INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS customers 
               (id INTEGER PRIMARY KEY, name TEXT, gst TEXT, address TEXT, contact TEXT, email TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS invoices 
               (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_no TEXT, customer_id TEXT, 
                date TEXT, total REAL, gst REAL, final_total REAL)''')
conn.commit()

cart = []

# --- FUNCTIONS ---

def add_product():
    try:
        cursor.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                       (p_name.get(), float(p_price.get()), int(p_qty.get())))
        conn.commit()
        messagebox.showinfo("Success", "Product Added to Inventory")
    except Exception as e:
        messagebox.showerror("Error", f"Could not add product: {e}")

def add_customer():
    try:
        cursor.execute("INSERT INTO customers (name, gst, address, contact, email) VALUES (?, ?, ?, ?, ?)",
                       (c_name.get(), c_gst.get(), c_address.get(), c_contact.get(), c_email.get()))
        conn.commit()
        messagebox.showinfo("Success", "Customer Registered")
    except Exception as e:
        messagebox.showerror("Error", f"Could not add customer: {e}")

def add_to_cart():
    name = item_name.get()
    try:
        qty = int(item_qty.get())
        cursor.execute("SELECT price FROM products WHERE name=?", (name,))
        result = cursor.fetchone()

        if result:
            price = result[0]
            cart.append((name, price, qty))
            listbox.insert(tk.END, f"{name} x{qty} = ₹{price*qty:.2f}")
        else:
            messagebox.showerror("Error", "Product not found")
    except ValueError:
        messagebox.showerror("Error", "Enter a valid quantity")

def generate_invoice():
    if not cart:
        return messagebox.showwarning("Empty", "Cart is empty!")
    
    customer = customer_id.get()
    total = sum(p*q for _, p, q in cart)
    gst = total * 0.18
    final = total + gst
    invoice_no = f"INV{int(datetime.now().timestamp())}"

    # Save to Database
    cursor.execute("INSERT INTO invoices (invoice_no, customer_id, date, total, gst, final_total) VALUES (?, ?, ?, ?, ?, ?)",
                   (invoice_no, customer, str(datetime.now().strftime("%Y-%m-%d %H:%M")), total, gst, final))
    conn.commit()

    # Create the text for the bill
    bill = f"INVOICE: {invoice_no}\nDate: {datetime.now().strftime('%Y-%m-%d')}\nCust: {customer}\n"
    bill += "-"*30 + "\n"
    for item in cart:
        bill += f"{item[0]} x{item[2]} = ₹{item[1]*item[2]:.2f}\n"
    bill += "-"*30 + "\n"
    bill += f"Total: ₹{total:.2f}\nGST (18%): ₹{gst:.2f}\nFinal: ₹{final:.2f}"

    # --- NEW: SAVE TO FILE FOR PRINTING ---
    file_name = f"Invoice_{invoice_no}.txt"
    # This saves it in the same folder as your App
    with open(os.path.join(base_path, file_name), "w") as f:
        f.write(bill)

    text_bill.delete("1.0", tk.END)
    text_bill.insert(tk.END, bill)
    
    messagebox.showinfo("Success", f"Invoice Saved as {file_name}\nYou can now open and print it!")

# --- UI SETUP ---
root = tk.Tk()
root.title("GST Billing Software Pro")
root.geometry("700x750")

# Use Notebook (Tabs) for a cleaner Mac look
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Inventory & Customers')
tab_control.add(tab2, text='Billing Console')
tab_control.pack(expand=1, fill="both")

# TAB 1: Inventory & Customer Management
lbl_frame1 = ttk.LabelFrame(tab1, text=" Add New Product ")
lbl_frame1.pack(padx=10, pady=10, fill="x")

ttk.Label(lbl_frame1, text="Product Name").grid(row=0, column=0, padx=5, pady=5)
p_name = ttk.Entry(lbl_frame1); p_name.grid(row=0, column=1)
ttk.Label(lbl_frame1, text="Price").grid(row=1, column=0); p_price = ttk.Entry(lbl_frame1); p_price.grid(row=1, column=1)
ttk.Label(lbl_frame1, text="Qty").grid(row=2, column=0); p_qty = ttk.Entry(lbl_frame1); p_qty.grid(row=2, column=1)
ttk.Button(lbl_frame1, text="Add Product", command=add_product).grid(row=3, columnspan=2, pady=10)

lbl_frame2 = ttk.LabelFrame(tab1, text=" Register Customer ")
lbl_frame2.pack(padx=10, pady=10, fill="x")

ttk.Label(lbl_frame2, text="Name").grid(row=0, column=0); c_name = ttk.Entry(lbl_frame2); c_name.grid(row=0, column=1)
ttk.Label(lbl_frame2, text="GST").grid(row=1, column=0); c_gst = ttk.Entry(lbl_frame2); c_gst.grid(row=1, column=1)
ttk.Label(lbl_frame2, text="Address").grid(row=2, column=0); c_address = ttk.Entry(lbl_frame2); c_address.grid(row=2, column=1)
ttk.Label(lbl_frame2, text="Contact").grid(row=3, column=0); c_contact = ttk.Entry(lbl_frame2); c_contact.grid(row=3, column=1)
ttk.Label(lbl_frame2, text="Email").grid(row=4, column=0); c_email = ttk.Entry(lbl_frame2); c_email.grid(row=4, column=1)
ttk.Button(lbl_frame2, text="Add Customer", command=add_customer).grid(row=5, columnspan=2, pady=10)

# TAB 2: Billing Console
lbl_frame3 = ttk.LabelFrame(tab2, text=" Create Bill ")
lbl_frame3.pack(padx=10, pady=10, fill="both", expand=True)

ttk.Label(lbl_frame3, text="Customer ID/Name:").grid(row=0, column=0); customer_id = ttk.Entry(lbl_frame3); customer_id.grid(row=0, column=1)
ttk.Label(lbl_frame3, text="Item Name:").grid(row=1, column=0); item_name = ttk.Entry(lbl_frame3); item_name.grid(row=1, column=1)
ttk.Label(lbl_frame3, text="Quantity:").grid(row=2, column=0); item_qty = ttk.Entry(lbl_frame3); item_qty.grid(row=2, column=1)

ttk.Button(lbl_frame3, text="Add to Cart", command=add_to_cart).grid(row=3, columnspan=2, pady=5)
listbox = tk.Listbox(lbl_frame3, height=8); listbox.grid(row=4, columnspan=2, sticky="nsew", padx=5)

ttk.Button(lbl_frame3, text="Generate & Save Invoice", command=generate_invoice).grid(row=5, columnspan=2, pady=10)
text_bill = tk.Text(lbl_frame3, height=10); text_bill.grid(row=6, columnspan=2, sticky="nsew", padx=5)

def clear_cart():
    global cart
    cart = []
    listbox.delete(0, tk.END)
    text_bill.delete("1.0", tk.END)

def update_dropdown():
    cursor.execute("SELECT name FROM products")
    names = [row[0] for row in cursor.fetchall()]
    item_name['values'] = names




root.mainloop()