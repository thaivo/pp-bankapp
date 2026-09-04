#!/usr/bin/env python3
import sqlite3
import hashlib


def encrypt_password(plain_password):
    password_bytes = plain_password.encode("utf-8")
    return hashlib.sha256(password_bytes).hexdigest()

def validate_input(input_str):
    try:
        value = int(input_str)
        if value < 0:
            raise ValueError("Input must be a non-negative integer.")
        return value
    except ValueError:
        print("Invalid input. Please enter a valid non-negative integer.")
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

            # create a table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                balance INTEGER
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
            return int(res.fetchone()[0])
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
            updated_balance = self.get_balance(username) + int(amount)
            self.cursor.execute(
                "UPDATE customers SET balance=? WHERE username=?",
                (updated_balance, username),
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
            if current_balance < int(amount):
                print(
                    f"Cannot withdraw {amount} due to current balance {current_balance}"
                )
                return False
            else:
                # self.cursor = self.connection.cursor()
                updated_balance = current_balance - int(amount)
                self.cursor.execute(
                    "UPDATE customers SET balance=? WHERE username=?",
                    (updated_balance, username),
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
            if current_sender_balance < int(amount):
                print(
                    f"Cannot transfer {amount} due to insufficient balance {current_sender_balance}"
                )
                return False
            else:
                print("transfer +")
                # self.cursor = self.connection.cursor()
                updated_sender_balance = current_sender_balance - int(amount)
                self.cursor.execute(
                    "UPDATE customers SET balance=? WHERE username=?",
                    (updated_sender_balance, sender),
                )
                current_receiver_balance = self.get_balance(receiver)
                updated_receiver_balance = current_receiver_balance + int(amount)
                self.cursor.execute(
                    "UPDATE customers SET balance=? WHERE username=?",
                    (updated_receiver_balance, receiver),
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


def main():
    bank_app = BankApp("bankapp.db")
    while True:
        print("Registration: 1")
        print("Login: 2")
        print("Exit: 3")
        choice = input("Please input number:")
        validate_input(choice)
        if choice == "3":
            break
        elif choice == "2":
            username = input("username:")
            password = input("password:")
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
                choice = input("Please input number:")
                validate_input(choice)
                match choice:
                    case "1":
                        print(f"balance: {bank_app.get_balance(username)}")
                    case "2":
                        deposit_amount = input("Deposit amount:")
                        bank_app.deposit(username, deposit_amount)
                        print(f"balance: {bank_app.get_balance(username)}")
                    case "3":
                        withdraw_amount = input("Withdrawal amount:")
                        bank_app.withdraw(username, withdraw_amount)
                        print(f"balance: {bank_app.get_balance(username)}")
                    case "4":
                        transfer_amount = input("Transfer amount:")
                        receiver = input("receiver's username:")
                        bank_app.transfer(username, receiver, transfer_amount)
                    case "5":
                        new_username = input("New username (leave blank to keep current):")
                        new_password = input("New password (leave blank to keep current):")
                        bank_app.update_customer_info(
                            username,
                            new_username if new_username else None,
                            new_password if new_password else None,
                        )
                        if new_username:
                            username = new_username
                    case "6":
                        break
                    case _:
                        print(
                            "Invalid code. Please input input the mentioned code above"
                        )
        elif choice == "1":
            username = input("username:")
            password = input("password:")
            if bank_app.check_existing_cust(username) is True:
                print(f"user {username} already exists. Please try with another one")
                continue
            bank_app.create_account(username, password)
    bank_app.close_connection()
if __name__ == "__main__":
    main()