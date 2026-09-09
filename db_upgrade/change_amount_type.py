#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('..//bankapp.db')
cursor = conn.cursor()

# 1. Create a new table with the correct 'TEXT' (string) column type
cursor.execute("""
    CREATE TABLE customers_tmp (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        balance TEXT DEFAULT '0' -- Changed from INTEGER to TEXT
    );
""")
print("Created temporary table with TEXT balance column.")
# 2. Copy the data over while casting the column to TEXT
cursor.execute("""
    INSERT INTO customers_tmp (id, username, password, balance)
    SELECT id, username, password, CAST(balance AS TEXT) FROM customers;
""")
print("Copied data to temporary table.")
# 3. Drop the old table
cursor.execute("DROP TABLE customers;")
print("Dropped old customers table.")
# 4. Rename the new table to the original name
cursor.execute("ALTER TABLE customers_tmp RENAME TO customers;")
print("Renamed temporary table to customers.")


# 1. Create a temporary table with the correct 'TEXT' (string) column type
cursor.execute("""
    CREATE TABLE transactions_tmp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER,
        amount TEXT, -- Changed from INTEGER to TEXT
        type_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES customers (id),
        FOREIGN KEY (receiver_id) REFERENCES customers (id),
        FOREIGN KEY (type_id) REFERENCES transactions_types (id)
    );
""")
print("Created temporary transactions table with TEXT amount column.")
# 2. Copy the data over while casting the column to TEXT
cursor.execute("""
    INSERT INTO transactions_tmp (id, sender_id, receiver_id, amount, type_id, created_at)
    SELECT id, sender_id, receiver_id, CAST(amount AS TEXT), type_id, created_at FROM transactions;
""")
print("Copied data to temporary table.")
# 3. Drop the old table
cursor.execute("DROP TABLE transactions;")
print("Dropped old transactions table.")
# 4. Rename the new table to the original name
cursor.execute("ALTER TABLE transactions_tmp RENAME TO transactions;")
print("Renamed temporary table to transactions.")

conn.commit()
conn.close()