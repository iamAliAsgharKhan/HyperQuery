import sqlite3
from datetime import datetime, timedelta
from random import randint, choice

def adapt_datetime(dt):
    """Convert datetime to ISO 8601 string"""
    return dt.isoformat()

# Register adapter for datetime objects
sqlite3.register_adapter(datetime, adapt_datetime)

def init_database():
    # Connect with type detection
    conn = sqlite3.connect(
        'ecommerce.db',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    c = conn.cursor()

    # Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY,
                  first_name TEXT,
                  last_name TEXT,
                  email TEXT UNIQUE,
                  phone TEXT,
                  created_at TIMESTAMP,
                  last_login TIMESTAMP,
                  address TEXT,
                  city TEXT,
                  country TEXT,
                  postal_code TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY,
                  name TEXT UNIQUE,
                  parent_id INTEGER,
                  FOREIGN KEY(parent_id) REFERENCES categories(id))''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY,
                  name TEXT,
                  description TEXT,
                  sku TEXT UNIQUE,
                  price REAL,
                  category_id INTEGER,
                  supplier_id INTEGER,
                  stock_quantity INTEGER,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP,
                  FOREIGN KEY(category_id) REFERENCES categories(id),
                  FOREIGN KEY(supplier_id) REFERENCES suppliers(id))''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS suppliers
                 (id INTEGER PRIMARY KEY,
                  company_name TEXT,
                  contact_name TEXT,
                  email TEXT,
                  phone TEXT,
                  address TEXT)''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY,
                  customer_id INTEGER,
                  order_date TIMESTAMP,
                  total_amount REAL,
                  status TEXT CHECK(status IN ('pending', 'processing', 'shipped', 'delivered', 'canceled')),
                  payment_status TEXT CHECK(payment_status IN ('paid', 'unpaid', 'refunded')),
                  FOREIGN KEY(customer_id) REFERENCES customers(id))''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS order_details
                 (id INTEGER PRIMARY KEY,
                  order_id INTEGER,
                  product_id INTEGER,
                  quantity INTEGER,
                  unit_price REAL,
                  discount REAL DEFAULT 0,
                  FOREIGN KEY(order_id) REFERENCES orders(id),
                  FOREIGN KEY(product_id) REFERENCES products(id))''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS payments
                 (id INTEGER PRIMARY KEY,
                  order_id INTEGER,
                  amount REAL,
                  payment_method TEXT,
                  transaction_id TEXT,
                  payment_date TIMESTAMP,
                  FOREIGN KEY(order_id) REFERENCES orders(id))''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (id INTEGER PRIMARY KEY,
                  product_id INTEGER,
                  customer_id INTEGER,
                  rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                  comment TEXT,
                  created_at TIMESTAMP,
                  FOREIGN KEY(product_id) REFERENCES products(id),
                  FOREIGN KEY(customer_id) REFERENCES customers(id))''')
                 
    c.execute('''CREATE TABLE IF NOT EXISTS inventory
                 (id INTEGER PRIMARY KEY,
                  product_id INTEGER,
                  quantity INTEGER,
                  location TEXT,
                  last_restocked TIMESTAMP,
                  FOREIGN KEY(product_id) REFERENCES products(id))''')
    
    # Insert Sample Data
    insert_sample_data(conn)
    
    conn.commit()
    conn.close()

def insert_sample_data(conn):
    c = conn.cursor()
    
    # Insert Categories
    categories = [
        ('Electronics', None),
        ('Computers', 1),
        ('Smartphones', 1),
        ('Furniture', None),
        ('Chairs', 4),
        ('Tables', 4),
        ('Clothing', None)
    ]
    c.executemany('INSERT INTO categories (name, parent_id) VALUES (?,?)', categories)
    
    # Insert Suppliers
    suppliers = [
        ('Tech Corp', 'John Techman', 'john@techcorp.com', '555-1234', '123 Tech Street'),
        ('Furniture World', 'Sarah Furnish', 'sarah@furnworld.com', '555-5678', '456 Comfort Ave'),
        ('Fashion Ltd', 'Emma Styles', 'emma@fashionltd.com', '555-9012', '789 Trend Blvd')
    ]
    c.executemany('INSERT INTO suppliers (company_name, contact_name, email, phone, address) VALUES (?,?,?,?,?)', suppliers)
    
    # Insert Products
    products = [
        ('Premium Laptop', 'High-end business laptop', 'LT-1001', 1499.99, 2, 1, 50, datetime.now()-timedelta(days=30)),
        ('Gaming Smartphone', 'Flagship gaming phone', 'PH-2001', 899.99, 3, 1, 100, datetime.now()-timedelta(days=20)),
        ('Ergonomic Chair', 'Office ergonomic chair', 'CH-3001', 299.99, 5, 2, 200, datetime.now()-timedelta(days=10)),
        ('Designer T-Shirt', 'Cotton premium t-shirt', 'TS-4001', 49.99, 7, 3, 500, datetime.now()-timedelta(days=5))
    ]
    c.executemany('''INSERT INTO products 
                  (name, description, sku, price, category_id, supplier_id, stock_quantity, created_at) 
                  VALUES (?,?,?,?,?,?,?,?)''', products)
    
    # Insert Customers
    customers = [
        ('John', 'Doe', 'john@example.com', '555-1111', datetime.now()-timedelta(days=100), 
         datetime.now()-timedelta(hours=2), '123 Main St', 'New York', 'USA', '10001'),
        ('Jane', 'Smith', 'jane@example.com', '555-2222', datetime.now()-timedelta(days=80), 
         datetime.now()-timedelta(hours=5), '456 Oak Ave', 'London', 'UK', 'SW1A 1AA'),
        ('Bob', 'Wilson', 'bob@example.com', '555-3333', datetime.now()-timedelta(days=60), 
         datetime.now()-timedelta(days=1), '789 Pine Rd', 'Sydney', 'Australia', '2000')
    ]
    c.executemany('''INSERT INTO customers 
                  (first_name, last_name, email, phone, created_at, last_login, address, city, country, postal_code) 
                  VALUES (?,?,?,?,?,?,?,?,?,?)''', customers)
    
    # Insert Orders and related data
    for i in range(1, 6):
        order_date = datetime.now() - timedelta(days=randint(1,10))
        c.execute('''INSERT INTO orders 
                  (customer_id, order_date, total_amount, status, payment_status) 
                  VALUES (?,?,?,?,?)''',
                  (randint(1,3), order_date, 0, choice(['pending', 'processing', 'shipped']), choice(['paid', 'unpaid'])))
        
        # Insert Order Details
        for _ in range(randint(1,3)):
            product_id = randint(1,4)
            quantity = randint(1,5)
            c.execute('SELECT price FROM products WHERE id=?', (product_id,))
            price = c.fetchone()[0]
            c.execute('''INSERT INTO order_details 
                      (order_id, product_id, quantity, unit_price) 
                      VALUES (?,?,?,?)''',
                      (i, product_id, quantity, price))
            
        # Update order total
        c.execute('''UPDATE orders SET total_amount = 
                  (SELECT SUM(quantity * unit_price) FROM order_details WHERE order_id=?)
                  WHERE id=?''', (i, i))
    
    # Insert Inventory
    inventory = [
        (1, 50, 'Warehouse A', datetime.now()-timedelta(days=7)),
        (2, 100, 'Warehouse B', datetime.now()-timedelta(days=14)),
        (3, 200, 'Warehouse C', datetime.now()-timedelta(days=21)),
        (4, 500, 'Warehouse A', datetime.now()-timedelta(days=3))
    ]
    c.executemany('INSERT INTO inventory (product_id, quantity, location, last_restocked) VALUES (?,?,?,?)', inventory)
    
    # Insert Reviews
    reviews = [
        (1, 1, 5, 'Excellent performance!', datetime.now()-timedelta(days=5)),
        (2, 2, 4, 'Great for gaming', datetime.now()-timedelta(days=3)),
        (3, 3, 5, 'Very comfortable', datetime.now()-timedelta(days=2)),
        (4, 1, 4, 'Good quality fabric', datetime.now()-timedelta(days=1))
    ]
    c.executemany('INSERT INTO reviews (product_id, customer_id, rating, comment, created_at) VALUES (?,?,?,?,?)', reviews)

if __name__ == "__main__":
    init_database()