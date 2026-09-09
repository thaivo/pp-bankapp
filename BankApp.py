#!/usr/bin/env python3
import re
from dataclasses import dataclass
import sqlite3
import hashlib
from functools import singledispatch
from decimal import Decimal

def encrypt_password(plain_password):
    password_bytes = plain_password.encode("utf-8")
    return hashlib.sha256(password_bytes).hexdigest()

@dataclass
class Username:
    value: str

@dataclass
class Password:
    value: str

@singledispatch
def validate_input(arg, verbose=False) -> bool:
    if verbose:
        print(f"Unsupported type: {type(arg)}")
    # raise NotImplementedError("Unsupported type")
    print("Unsupported type.")
    return False

@validate_input.register(Username)
def _(arg: Username, verbose=False) -> bool:
    if verbose:
        print(f"Validating username input: {arg.value}")
    if not re.match(r"^[a-zA-Z0-9_]{3,20}$", arg.value):
        print("Invalid username: Must be 3-20 characters long and contain only letters, numbers, and underscores.")
        return False
    return True


@validate_input.register(Password)
def _(arg: Password, verbose=False) -> bool:
    if verbose:
        print(f"Validating password input: {arg.value}")
    # (?=.*[a-z]) — Contains lowercase. Looks ahead from the start to find any number of characters (.*) followed by at least one lowercase letter.
    # (?=.*[A-Z]) — Contains uppercase. Looks ahead to find any characters followed by at least one uppercase letter.
    # (?=.*\d) — Contains a digit. Looks ahead to find any characters followed by at least one numeric digit (0-9).
    # (?=.*[@$!%*?&]) — Contains a special character. Looks ahead to find any characters followed by at least one special character from this allowed set: @, $, !, %, *, ?, or &.
    # [A-Za-z\d@$!%*?&] — Allowed character dictionary. Once all the lookahead checks pass, this defines the only characters permitted in the password (letters, digits, and your specific special characters). If a user types a space, hashtag #, or period ., the password will fail.
    # {8,} — Minimum length. Quantifies the character dictionary to ensure the password is at least 8 characters long (with no upper bound limit).
    #
    # When a password like SecureP@ss123 is checked, the engine acts like a checklist:
    # At the start (^), is there a lowercase letter ahead? Yes (e). Reset pointer to start.
    # Is there an uppercase letter ahead? Yes (S). Reset pointer to start.
    # Is there a number ahead? Yes (1). Reset pointer to start.
    # Is there a special character ahead? Yes (@). Reset pointer to start.
    # Are all characters from our allowed list, and are there at least 8 of them? Yes (13 characters).
    # Reach the end of the line ($) \(\rightarrow \) Valid!
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(pattern, arg.value))

@validate_input.register(int)
def _(arg: int, verbose=False) -> bool:
    if verbose:
        print(f"Validating integer input: {arg}")
    if arg < 0:
        print("Input must be a non-negative integer.")
        return False
    return True

@validate_input.register(Decimal)
def _(arg: Decimal, verbose=False) -> bool:
    if verbose:
        print(f"Validating decimal input: {arg}")
    if arg < 0:
        print("Invalid input: Input must be a non-negative decimal.")
        return False
    return True

def get_valid_input(target_type: type, prompt: str, err_msg: str):
    raw_text = input(prompt)
    # TODO: Add a feature for enable DEBUG mode for debugging purpose, and print the debug info only when DEBUG mode is enabled
    # maybe we can use a global variable DEBUG_MODE to control the debug output, 
    # and it can be read from config file or environment variable, and can be set by command line argument.
    # print(f"target_type: {target_type}, raw_text: {raw_text}")

    # Define a set of types that are supported for validation
    supported_types = {Username, Password, int, Decimal}

    if target_type not in supported_types:
        print(f"Unsupported type for validation: {target_type}")
        return None

    try:
        # Attempt to create an instance of the target type
        value = target_type(raw_text)
        # print(f"Debug after an instance creation, value is: {value}")
        if validate_input(value):
            return value.value if isinstance(value, (Username, Password)) else value
        else:
            print(err_msg)
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
class BankApp:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def close_connection(self):
        self.connection.close()

    def create_table(self):
        try:
            print("Creating table if not exists")
            # create cursor object to interact with db
            # self.cursor = self.connection.cursor()

            # create customers table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                balance INTEGER DEFAULT 0
                )
            """)

            # create transactions_types table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL
                )
            """)

            # insert default transaction types if they don't exist
            self.cursor.execute("""
                INSERT OR IGNORE INTO transactions_types (id, type) VALUES
                (1, 'deposit'),
                (2, 'withdrawal'),
                (3, 'transfer')
            """)

            # create transactions table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER,
                amount INTEGER,
                type_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES customers (id),
                FOREIGN KEY (receiver_id) REFERENCES customers (id),
                FOREIGN KEY (type_id) REFERENCES transactions_types (id)
                )
            """)
            self.connection.commit()
            # self.connection.close()
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("create table -")
            # self.connection.close()

    def create_account(self, username, password, balance=0):
        try:
            print("create_account +")
            # self.cursor = self.connection.cursor()

            user_data = (username, encrypt_password(password), balance)

            res = self.cursor.execute(
                """
                INSERT INTO customers (username, password, balance) 
                VALUES (?, ?, ?)
                """,
                user_data,
            )
            self.connection.commit()
            if res is not None:
                print(f"Account created for {username}")
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("create_account -")
            # self.connection.close()

    def check_existing_cust(self, username):
        try:
            print("check_existing_cust +")
            # self.cursor = self.connection.cursor()
            res = self.cursor.execute(
                "SELECT * FROM customers WHERE username=?", (username,)
            ).fetchone()
            # self.connection.close()
            print("check_existing_cust DEBUG - res: ", res)
            return res is not None
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("check_existing_cust -")
            # self.connection.close()

    def login(self, username, password):
        hashed_pw = encrypt_password(password)
        try:
            print("Checking login credentials")
            # self.cursor = self.connection.cursor()

            # user_data = (username, hashed_pw)
            print("Checking login credentials 1")
            res = self.cursor.execute(
                "SELECT password FROM customers WHERE username=?", (username,)
            )
            print("Checking login credentials 2")
            res = res.fetchone()
            print(f"Checking login credentials 3 - res: {res}")
            if res is None:
                print(
                    f"User with username {username} does not exist. You need to register"
                )
                print("Checking login credentials -")
                # self.connection.close()
                return False
            if res[0] == hashed_pw:
                print("Login succeeded!")
                print("login -")
                # self.connection.close()
                return True
            else:
                print("Login failed: Incorrect password.")
                print("login -")
                # self.connection.close()
                return False
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("login -")
            # self.connection.close()

    def check_balance(self, username):
        try:
            print("check_balance +")
            # self.cursor = self.connection.cursor()
            res = self.cursor.execute(
                "SELECT balance FROM customers WHERE username=?", (username,)
            )
            print("check_balance -")
            return res.fetchone()[0]
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("check_balance -")
            # self.connection.close()

    def get_balance(self, username):
        try:
            print("get_balance +")
            # self.cursor = self.connection.cursor()
            res = self.cursor.execute(
                "SELECT balance FROM customers WHERE username=?", (username,)
            )
            print("get_balance -")
            return Decimal(res.fetchone()[0])
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
            return 0
        finally:
            print("get_balance -")
            # self.connection.close()

    def deposit(self, username, amount):
        try:
            print("deposit +")
            # self.cursor = self.connection.cursor()
            updated_balance = self.get_balance(username) + Decimal(amount)
            self.cursor.execute(
                "UPDATE customers SET balance=? WHERE username=?",
                (str(updated_balance), username),
            )
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("deposit -")
            # self.connection.close()

    def withdraw(self, username, amount):
        try:
            print("withdraw +")
            current_balance = self.get_balance(username)
            if current_balance < Decimal(amount):
                print(
                    f"Cannot withdraw {amount} due to current balance {current_balance}"
                )
                return False
            else:
                # self.cursor = self.connection.cursor()
                updated_balance = current_balance - Decimal(amount)
                self.cursor.execute(
                    "UPDATE customers SET balance=? WHERE username=?",
                    (str(updated_balance), username),
                )
                self.connection.commit()
                print("withdraw -")
                # self.connection.close()
                return True
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("withdraw -")
            # self.connection.close()

    def transfer(self, sender, receiver, amount):
        try:
            current_sender_balance = self.get_balance(sender)
            if current_sender_balance < Decimal(amount):
                print(
                    f"Cannot transfer {amount} due to insufficient balance {current_sender_balance}"
                )
                return False
            else:
                print("transfer +")
                # self.cursor = self.connection.cursor()
                updated_sender_balance = current_sender_balance - Decimal(amount)
                self.cursor.execute(
                    "UPDATE customers SET balance=? WHERE username=?",
                    (str(updated_sender_balance), sender),
                )
                current_receiver_balance = self.get_balance(receiver)
                updated_receiver_balance = current_receiver_balance + Decimal(amount)
                self.cursor.execute(
                    "UPDATE customers SET balance=? WHERE username=?",
                    (str(updated_receiver_balance), receiver),
                )
                self.connection.commit()
                return True
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("transfer -")
            # self.connection.close()

    def update_customer_info(self, username, new_username=None, new_password=None):
        try:
            print("update_customer_info +")
            # self.cursor = self.connection.cursor()
            cur_username = username
            if new_username:
                self.cursor.execute(
                    "UPDATE customers SET username=? WHERE username=?",
                    (new_username, username),
                )
                cur_username = new_username

            if new_password:
                hashed_pw = encrypt_password(new_password)
                self.cursor.execute(
                    "UPDATE customers SET password=? WHERE username=?",
                    (hashed_pw, cur_username),
                )
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("update_customer_info -")
            # self.connection.close()

    def save_transaction(self, sender_id, receiver_id, amount, trans_type):
        try:
            print("save_transaction +")
            # self.cursor = self.connection.cursor()
            self.cursor.execute(
                """INSERT INTO transactions (sender_id, receiver_id, amount, type_id)
                SELECT ?, ?, ?, id FROM transactions_types WHERE type=?""",
                (sender_id, receiver_id, str(amount), trans_type),
            )
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"A database error occurred: {e}")
        finally:
            print("save_transaction -")
            # self.connection.close()

def main():
    bank_app = BankApp("bankapp.db")
    while True:
        print("Registration: 1")
        print("Login: 2")
        print("Exit: 3")
        choice = get_valid_input(int, "Please input number:", "Invalid input. Please try again.")
        if choice == 3:
            break
        elif choice == 2:
            username = get_valid_input(Username, "username:", "Invalid username.")
            password = get_valid_input(Password, "password:", "Invalid password.")
            if bank_app.check_existing_cust(username) is False:
                print(
                    f"user {username} does not exist. Please register or try with an existing one"
                )
                continue
            if bank_app.login(username, password) is False:
                continue
            
            while True:
                print("Please select one of the below actions with respective number:")
                print("Check balance: 1")
                print("Deposit: 2")
                print("Withdraw: 3")
                print("Transfer: 4")
                print("Update your info: 5")
                print("Exit: 6")
                choice = get_valid_input(int, "Please input number:", "Invalid input. Please try again.")
                match choice:
                    case 1:
                        print(f"balance: {bank_app.get_balance(username)}")
                    case 2:
                        deposit_amount = get_valid_input(Decimal, "Deposit amount:", "Invalid deposit amount.")
                        bank_app.deposit(username, deposit_amount)
                        print(f"balance: {bank_app.get_balance(username)}")
                        bank_app.save_transaction(username, None, deposit_amount, "deposit")
                    case 3:
                        withdraw_amount = get_valid_input(Decimal, "Withdrawal amount:", "Invalid withdrawal amount.")
                        bank_app.withdraw(username, withdraw_amount)
                        print(f"balance: {bank_app.get_balance(username)}")
                        bank_app.save_transaction(username, None, withdraw_amount, "withdrawal")
                    case 4:
                        transfer_amount = get_valid_input(Decimal, "Transfer amount:", "Invalid transfer amount.")
                        receiver = get_valid_input(Username, "receiver's username:", "Invalid username.")
                        bank_app.transfer(username, receiver, transfer_amount)
                        bank_app.save_transaction(username, receiver, transfer_amount, "transfer")
                    case 5:
                        new_username = get_valid_input(Username, "New username (leave blank to keep current):", "Invalid username.")
                        new_password = get_valid_input(Password, "New password (leave blank to keep current):", "Invalid password.")
                        bank_app.update_customer_info(
                            username,
                            new_username if new_username else None,
                            new_password if new_password else None,
                        )
                        if new_username:
                            username = new_username
                    case 6:
                        break
                    case _:
                        print(
                            "Invalid code. Please input the mentioned code above"
                        )
        elif choice == 1:
            username = get_valid_input(Username, "username:", "Invalid username.")
            password = get_valid_input(Password, "password:", "Invalid password.")
            if bank_app.check_existing_cust(username) is True:
                print(f"user {username} already exists. Please try with another one")
                continue
            bank_app.create_account(username, password)
    bank_app.close_connection()
if __name__ == "__main__":
    main()