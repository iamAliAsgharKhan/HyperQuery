import sqlite3
from datetime import datetime, timedelta
from random import randint, choice, sample

def adapt_datetime(dt):
    return dt.isoformat()

sqlite3.register_adapter(datetime, adapt_datetime)

def init_database():
    conn = sqlite3.connect(
        'ecommerce.db',
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    c = conn.cursor()

    # Create Tables with Enhanced Schema
    c.execute('''CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY,
        street TEXT,
        city TEXT,
        state TEXT,
        country TEXT,
        postal_code TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        created_at TIMESTAMP,
        last_login TIMESTAMP,
        address_id INTEGER,
        FOREIGN KEY(address_id) REFERENCES addresses(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY,
        company_name TEXT,
        contact_name TEXT,
        email TEXT,
        phone TEXT,
        address_id INTEGER,
        FOREIGN KEY(address_id) REFERENCES addresses(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        parent_id INTEGER,
        FOREIGN KEY(parent_id) REFERENCES categories(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        price REAL,
        category_id INTEGER,
        supplier_id INTEGER,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        FOREIGN KEY(category_id) REFERENCES categories(id),
        FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS product_variants (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        sku TEXT UNIQUE,
        size TEXT,
        color TEXT,
        price_adjustment REAL,
        stock_quantity INTEGER,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY,
        product_variant_id INTEGER,
        quantity INTEGER,
        location TEXT,
        last_restocked TIMESTAMP,
        FOREIGN KEY(product_variant_id) REFERENCES product_variants(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        order_date TIMESTAMP,
        total_amount REAL,
        status TEXT CHECK(status IN ('pending', 'processing', 'shipped', 'delivered', 'canceled')),
        payment_status TEXT CHECK(payment_status IN ('paid', 'unpaid', 'refunded')),
        shipping_address_id INTEGER,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(shipping_address_id) REFERENCES addresses(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS order_details (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_variant_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        discount REAL DEFAULT 0,
        FOREIGN KEY(order_id) REFERENCES orders(id),
        FOREIGN KEY(product_variant_id) REFERENCES product_variants(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        amount REAL,
        payment_method TEXT,
        transaction_id TEXT,
        payment_date TIMESTAMP,
        FOREIGN KEY(order_id) REFERENCES orders(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        customer_id INTEGER,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5),
        comment TEXT,
        created_at TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES products(id),
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS product_tags (
        product_id INTEGER,
        tag_id INTEGER,
        PRIMARY KEY (product_id, tag_id),
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS wishlists (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        added_at TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')

    # Insert Comprehensive Sample Data
    insert_sample_data(conn)
    
    conn.commit()
    conn.close()

def insert_sample_data(conn):
    c = conn.cursor()
    
    # Insert Addresses
    addresses = [
        ('123 Tech Street', 'San Francisco', 'CA', 'USA', '94016'),
        ('456 Comfort Ave', 'Chicago', 'IL', 'USA', '60007'),
        ('789 Trend Blvd', 'Los Angeles', 'CA', 'USA', '90001'),
        ('321 Gadget Lane', 'Austin', 'TX', 'USA', '73301'),
        ('654 Home Road', 'Miami', 'FL', 'USA', '33101'),
        ('987 Fabric Street', 'New York', 'NY', 'USA', '10001'),
        ('555 Smart Blvd', 'Seattle', 'WA', 'USA', '98101'),
        ('222 Cozy Corner', 'Boston', 'MA', 'USA', '02101'),
        ('888 Chic Avenue', 'Paris', None, 'France', '75000'),
        ('777 Maple Drive', 'Toronto', 'ON', 'Canada', 'M5V 3L9'),
    ]
    c.executemany('''INSERT INTO addresses 
        (street, city, state, country, postal_code) 
        VALUES (?,?,?,?,?)''', addresses)

    # Insert Customers
    customers = [
        ('John', 'Doe', 'john@example.com', '555-1111', 
         datetime.now()-timedelta(days=100), datetime.now()-timedelta(hours=2), 1),
        ('Jane', 'Smith', 'jane@example.com', '555-2222', 
         datetime.now()-timedelta(days=80), datetime.now()-timedelta(hours=5), 2),
        ('Bob', 'Wilson', 'bob@example.com', '555-3333', 
         datetime.now()-timedelta(days=60), datetime.now()-timedelta(days=1), 3),
        ('Alice', 'Brown', 'alice@example.com', '555-4444', 
         datetime.now()-timedelta(days=40), datetime.now()-timedelta(hours=12), 4),
        ('Charlie', 'Davis', 'charlie@example.com', '555-5555', 
         datetime.now()-timedelta(days=20), datetime.now()-timedelta(hours=8), 5)
    ]
    c.executemany('''INSERT INTO customers 
        (first_name, last_name, email, phone, created_at, last_login, address_id) 
        VALUES (?,?,?,?,?,?,?)''', customers)

    # Insert Suppliers
    suppliers = [
        ('Tech Corp', 'John Techman', 'john@techcorp.com', '555-1234', 1),
        ('Furniture World', 'Sarah Furnish', 'sarah@furnworld.com', '555-5678', 2),
        ('Fashion Ltd', 'Emma Styles', 'emma@fashionltd.com', '555-9012', 3),
        ('Gadget Inc', 'Mike Gadget', 'mike@gadget.com', '555-3456', 4),
        ('Home Essentials', 'Lucy Homely', 'lucy@home.com', '555-7890', 5)
    ]
    c.executemany('''INSERT INTO suppliers 
        (company_name, contact_name, email, phone, address_id) 
        VALUES (?,?,?,?,?)''', suppliers)

    # Insert Categories with deeper hierarchy
    categories = [
        ('Electronics', None),
        ('Computers', 1), ('Laptops', 2), ('Desktops', 2),
        ('Smartphones', 1), ('Android', 4), ('iOS', 4),
        ('Furniture', None), ('Chairs', 7), ('Tables', 7), ('Sofas', 7),
        ('Clothing', None), ('Men''s', 11), ('Women''s', 11),
        ('Shirts', 12), ('Pants', 12), ('Dresses', 13), ('Skirts', 13)
    ]
    c.executemany('INSERT INTO categories (name, parent_id) VALUES (?,?)', categories)

    # Insert Products
    products = [
        ('UltraBook Pro', 'Slim business laptop', 1299.99, 3, 1, datetime.now()-timedelta(days=30)),
        ('Gaming Beast', 'High-performance gaming laptop', 1999.99, 3, 1, datetime.now()-timedelta(days=25)),
        ('Workstation Tower', 'Professional desktop', 2999.99, 4, 1, datetime.now()-timedelta(days=20)),
        ('Phoenix X5', 'Android flagship phone', 799.99, 6, 4, datetime.now()-timedelta(days=15)),
        ('FruitPhone 15', 'Latest iOS device', 999.99, 7, 4, datetime.now()-timedelta(days=10)),
        ('ErgoChair Plus', 'Ergonomic office chair', 399.99, 9, 2, datetime.now()-timedelta(days=5)),
        ('Comfort Sofa', '3-seater fabric sofa', 899.99, 10, 2, datetime.now()-timedelta(days=3)),
        ('Premium Dress Shirt', 'Formal cotton shirt', 89.99, 14, 3, datetime.now()-timedelta(days=2)),
        ('Summer Dress', 'Floral print dress', 59.99, 16, 3, datetime.now()-timedelta(days=1))
    ]
    c.executemany('''INSERT INTO products 
        (name, description, price, category_id, supplier_id, created_at) 
        VALUES (?,?,?,?,?,?)''', products)

    # Insert Product Variants
    variants = [
        # UltraBook Pro (id=1)
        (1, 'UTB-SILVER', '15"', 'Silver', 0, 50),
        (1, 'UTB-GRAY', '15"', 'Space Gray', 50, 30),
        # Gaming Beast (id=2)
        (2, 'GB-16GB', '17"', 'Black', 0, 20),
        (2, 'GB-32GB', '17"', 'Black', 200, 15),
        # Phoenix X5 (id=4)
        (4, 'PHX5-BLACK', '6.7"', 'Black', 0, 100),
        (4, 'PHX5-BLUE', '6.7"', 'Blue', 0, 80),
        # ErgoChair Plus (id=6)
        (6, 'ECP-BLACK', None, 'Black', 0, 50),
        (6, 'ECP-GRAY', None, 'Gray', 50, 30),
        # Premium Dress Shirt (id=8)
        (8, 'SHIRT-WHITE', 'M', 'White', 0, 100),
        (8, 'SHIRT-BLUE', 'L', 'Navy', 10, 75),
        # Summer Dress (id=9)
        (9, 'DRESS-S', 'S', 'Floral', 0, 50),
        (9, 'DRESS-M', 'M', 'Floral', 0, 60)
    ]
    c.executemany('''INSERT INTO product_variants 
        (product_id, sku, size, color, price_adjustment, stock_quantity) 
        VALUES (?,?,?,?,?,?)''', variants)

    # Insert Inventory
    for variant_id in range(1, len(variants)+1):
        locations = ['Warehouse A', 'Warehouse B', 'Store Front']
        for loc in sample(locations, randint(1,2)):
            c.execute('''INSERT INTO inventory 
                (product_variant_id, quantity, location, last_restocked) 
                VALUES (?,?,?,?)''',
                (variant_id, randint(10,100), loc, datetime.now()-timedelta(days=randint(1,30)))
            )

    # Insert Tags
    tags = ['gaming', 'ergonomic', 'premium', 'portable', 'fashion', 'business', 'budget', 'luxury']
    for tag in tags:
        c.execute('INSERT INTO tags (name) VALUES (?)', (tag,))

    # Link Products to Tags
    product_tags = [
        (1, 2), (1, 4), (1, 6),  # UltraBook Pro: ergonomic, portable, business
        (2, 1), (2, 6),          # Gaming Beast: gaming, business
        (6, 2), (6, 3),          # ErgoChair Plus: ergonomic, premium
        (8, 3), (8, 5),          # Dress Shirt: premium, fashion
        (9, 5), (9, 8)           # Summer Dress: fashion, luxury
    ]
    c.executemany('INSERT INTO product_tags (product_id, tag_id) VALUES (?,?)', product_tags)

    # Insert Orders
    for _ in range(20):
        customer_id = randint(1, 5)
        shipping_address = randint(1, 10)
        order_date = datetime.now() - timedelta(days=randint(1, 30))
        c.execute('''INSERT INTO orders 
            (customer_id, order_date, total_amount, status, payment_status, shipping_address_id) 
            VALUES (?,?,?,?,?,?)''',
            (customer_id, order_date, 0, choice(['pending', 'processing', 'shipped']), 
             choice(['paid', 'unpaid']), shipping_address))
        order_id = c.lastrowid

        # Add Order Details
        total = 0
        for _ in range(randint(1, 4)):
            variant = choice(variants)
            variant_id = variants.index(variant) + 1
            product_id = variant[0]
            c.execute('''SELECT price + price_adjustment 
                FROM products p 
                JOIN product_variants v ON p.id = v.product_id 
                WHERE v.id = ?''', (variant_id,))
            unit_price = c.fetchone()[0]
            quantity = randint(1, 3)
            discount = choice([0, 0.1, 0.15])
            
            c.execute('''INSERT INTO order_details 
                (order_id, product_variant_id, quantity, unit_price, discount) 
                VALUES (?,?,?,?,?)''',
                (order_id, variant_id, quantity, unit_price, discount))
            
            total += unit_price * quantity * (1 - discount)

        # Update Order Total
        c.execute('UPDATE orders SET total_amount = ? WHERE id = ?', (round(total, 2), order_id))

        # Insert Payment if paid
        if choice([True, False]):
            c.execute('''INSERT INTO payments 
                (order_id, amount, payment_method, transaction_id, payment_date) 
                VALUES (?,?,?,?,?)''',
                (order_id, round(total, 2), choice(['credit_card', 'paypal']), 
                 f'TXN{order_id:04}', order_date + timedelta(minutes=randint(1, 120))))

    # Insert Reviews
    reviews = [
        (1, 1, 5, 'Excellent business laptop!', datetime.now()-timedelta(days=5)),
        (2, 2, 4, 'Great for gaming but heavy', datetime.now()-timedelta(days=3)),
        (6, 3, 5, 'Most comfortable chair ever', datetime.now()-timedelta(days=2)),
        (8, 4, 4, 'Perfect fit for formal occasions', datetime.now()-timedelta(days=1)),
        (9, 5, 5, 'Beautiful summer dress', datetime.now()-timedelta(hours=5))
    ]
    c.executemany('''INSERT INTO reviews 
        (product_id, customer_id, rating, comment, created_at) 
        VALUES (?,?,?,?,?)''', reviews)

    # Insert Wishlists
    for customer_id in range(1, 6):
        for product_id in sample(range(1, len(products)+1), 3):
            c.execute('''INSERT INTO wishlists 
                (customer_id, product_id, added_at) 
                VALUES (?,?,?)''',
                (customer_id, product_id, datetime.now()-timedelta(days=randint(1, 30)))
            )

if __name__ == "__main__":
    init_database()