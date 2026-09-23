import json
import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = "mobile_money_data.json"

DEFAULT_DATA = {
    "zwg": {"pin": "1234", "balance": 2500.00, "history": []},
    "usd": {"pin": "4321", "balance": 500.00, "history": []},
}

BUNDLES = {
    "100 MB": 1.00,
    "500 MB": 3.00,
    "1 GB": 5.00,
    "2 GB": 9.00,
    "5 GB": 20.00,
}

MOBILE_RE = re.compile(r"07\d{8}")

def load_data():
    if not os.path.exists(DATA_FILE):
        fresh = json.loads(json.dumps(DEFAULT_DATA))
        save_data(fresh)
        return fresh
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def record_transaction(data, wallet_name, ttype, amount):
    entry = {
        "date": datetime.now().strftime("%d/%m/%y"),
        "type": ttype,
        "amount": round(amount, 2),
        "balance": round(data[wallet_name]["balance"], 2),
    }
    data[wallet_name]["history"].append(entry)
    save_data(data)


def valid_mobile_number(number):
    return bool(MOBILE_RE.fullmatch(number))



class MobileMoneyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("E.B And Friends Ecocash")
        self.geometry("460x440")
        self.resizable(False, False)

        self.data = load_data()
        self.wallet_name = None
        self.currency = None
        self.pin_attempts = 3

        self.container = ttk.Frame(self, padding=16)
        self.container.pack(fill="both", expand=True)

        self.show_currency_screen()


    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def finish(self, message):
        """Show a final confirmation, then close the whole app."""
        messagebox.showinfo("E.B and Friends Ecocash", message)
        self.destroy()


    def show_currency_screen(self):
        self.clear()
        ttk.Label(self.container, text="E.B and Friends Ecocash",
                  font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))
        ttk.Label(self.container, text="Please select your currency").pack(pady=(0, 12))

        ttk.Button(self.container, text="1. Zimbabwe Gold (ZWG)",
                   command=lambda: self.show_pin_screen("zwg", "ZWG")).pack(fill="x", pady=4)
        ttk.Button(self.container, text="2. United States Dollar (USD)",
                   command=lambda: self.show_pin_screen("usd", "USD")).pack(fill="x", pady=4)
        ttk.Button(
            self.container, text="3. Exit",
            command=lambda: self.finish("Thank you for using Mobile Money Banking System. Goodbye!")
        ).pack(fill="x", pady=4)


    def show_pin_screen(self, wallet_name, currency):
        self.wallet_name = wallet_name
        self.currency = currency
        self.pin_attempts = 3
        self.clear()

        ttk.Label(self.container, text=f"Welcome to XXXXXXX {currency} Wallet",
                  font=("Segoe UI", 12, "bold")).pack(pady=(0, 16))
        ttk.Label(self.container, text="Enter your PIN:").pack()

        pin_var = tk.StringVar()
        pin_entry = ttk.Entry(self.container, textvariable=pin_var, show="*")
        pin_entry.pack(pady=8)
        pin_entry.focus()

        status = ttk.Label(self.container, text="", foreground="red")
        status.pack()

        def submit():
            if pin_var.get().strip() == self.data[wallet_name]["pin"]:
                self.show_wallet_menu()
            else:
                self.pin_attempts -= 1
                if self.pin_attempts <= 0:
                    self.finish("Too many incorrect PIN attempts. Goodbye!")
                else:
                    status.config(text=f"Incorrect PIN. {self.pin_attempts} attempt(s) remaining.")
                    pin_var.set("")

        ttk.Button(self.container, text="Submit", command=submit).pack(pady=8)
        pin_entry.bind("<Return>", lambda e: submit())


    def show_wallet_menu(self):
        self.clear()
        ttk.Label(self.container, text=f"{self.currency} WALLET",
                  font=("Segoe UI", 14, "bold")).pack(pady=(0, 8))

        bal = self.data[self.wallet_name]["balance"]
        ttk.Label(self.container, text=f"Balance: {self.currency} {bal:.2f}").pack(pady=(0, 16))

        ttk.Button(self.container, text="1. Send Money",
                   command=self.show_send_money_screen).pack(fill="x", pady=4)
        ttk.Button(self.container, text="2. Airtime and Bundles",
                   command=self.show_airtime_bundles_screen).pack(fill="x", pady=4)
        ttk.Button(self.container, text="3. Check Balance",
                   command=self.show_check_balance).pack(fill="x", pady=4)
        ttk.Button(self.container, text="4. Transaction History",
                   command=self.show_transaction_history).pack(fill="x", pady=4)
        ttk.Button(
            self.container, text="5. Logout",
            command=lambda: self.finish("Logged out. Thank you for using Mobile Money Banking System.")
        ).pack(fill="x", pady=4)


    def show_send_money_screen(self):
        self.clear()
        ttk.Label(self.container, text="SEND MONEY", font=("Segoe UI", 13, "bold")).pack(pady=(0, 16))

        ttk.Label(self.container, text="Recipient mobile number (07XXXXXXXX):").pack(anchor="w")
        number_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=number_var).pack(fill="x", pady=(0, 10))

        ttk.Label(self.container, text="Amount:").pack(anchor="w")
        amount_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=amount_var).pack(fill="x", pady=(0, 10))

        error = ttk.Label(self.container, text="", foreground="red")
        error.pack()

        def submit():
            number = number_var.get().strip()
            raw_amount = amount_var.get().strip()

            if not valid_mobile_number(number):
                error.config(text="Invalid mobile number. Use format 07XXXXXXXX.")
                return
            try:
                amount = float(raw_amount)
            except ValueError:
                error.config(text="Invalid amount. Please enter a valid number.")
                return
            if amount <= 0:
                error.config(text="Amount must be greater than zero.")
                return
            if amount > self.data[self.wallet_name]["balance"]:
                self.finish(
                    f"Insufficient balance. Your balance is {self.currency} "
                    f"{self.data[self.wallet_name]['balance']:.2f}, which is not enough "
                    f"to send {self.currency} {amount:.2f}."
                )
                return

            self.data[self.wallet_name]["balance"] -= amount
            record_transaction(self.data, self.wallet_name, "Send Money", amount)
            self.finish(
                f"Transaction successful!\nYou have sent {self.currency} {amount:.2f} to {number}.\n"
                f"New Balance: {self.currency} {self.data[self.wallet_name]['balance']:.2f}"
            )

        ttk.Button(self.container, text="Send", command=submit).pack(pady=8)
        ttk.Button(self.container, text="Back", command=self.show_wallet_menu).pack()


    def show_airtime_bundles_screen(self):
        self.clear()
        ttk.Label(self.container, text="AIRTIME AND BUNDLES",
                  font=("Segoe UI", 13, "bold")).pack(pady=(0, 16))

        ttk.Button(self.container, text="1. Buy Airtime",
                   command=self.show_buy_airtime_screen).pack(fill="x", pady=4)
        ttk.Button(self.container, text="2. Buy Data Bundle",
                   command=self.show_buy_bundle_screen).pack(fill="x", pady=4)
        ttk.Button(self.container, text="3. Back", command=self.show_wallet_menu).pack(fill="x", pady=4)

    def show_buy_airtime_screen(self):
        self.clear()
        ttk.Label(self.container, text="BUY AIRTIME", font=("Segoe UI", 13, "bold")).pack(pady=(0, 16))

        ttk.Label(self.container, text="Mobile number (07XXXXXXXX):").pack(anchor="w")
        number_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=number_var).pack(fill="x", pady=(0, 10))

        ttk.Label(self.container, text="Airtime amount:").pack(anchor="w")
        amount_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=amount_var).pack(fill="x", pady=(0, 10))

        error = ttk.Label(self.container, text="", foreground="red")
        error.pack()

        def submit():
            number = number_var.get().strip()
            raw_amount = amount_var.get().strip()

            if not valid_mobile_number(number):
                error.config(text="Invalid mobile number. Use format 07XXXXXXXX.")
                return
            try:
                amount = float(raw_amount)
            except ValueError:
                error.config(text="Invalid amount. Please enter a valid number.")
                return
            if amount <= 0:
                error.config(text="Amount must be greater than zero.")
                return
            if amount > self.data[self.wallet_name]["balance"]:
                self.finish(
                    f"Insufficient balance. Your balance is {self.currency} "
                    f"{self.data[self.wallet_name]['balance']:.2f}."
                )
                return

            self.data[self.wallet_name]["balance"] -= amount
            record_transaction(self.data, self.wallet_name, "Airtime", amount)
            self.finish(
                f"Airtime purchase successful!\nYou have topped up {self.currency} {amount:.2f} "
                f"airtime for {number}.\nNew Balance: {self.currency} "
                f"{self.data[self.wallet_name]['balance']:.2f}"
            )

        ttk.Button(self.container, text="Buy", command=submit).pack(pady=8)
        ttk.Button(self.container, text="Back", command=self.show_airtime_bundles_screen).pack()

    def show_buy_bundle_screen(self):
        self.clear()
        ttk.Label(self.container, text="BUY DATA BUNDLE", font=("Segoe UI", 13, "bold")).pack(pady=(0, 16))

        choice_var = tk.StringVar(value=list(BUNDLES.keys())[0])
        for label, price in BUNDLES.items():
            ttk.Radiobutton(
                self.container, text=f"{label} - {self.currency} {price:.2f}",
                variable=choice_var, value=label
            ).pack(anchor="w", pady=2)

        def submit():
            label = choice_var.get()
            price = BUNDLES[label]
            if price > self.data[self.wallet_name]["balance"]:
                self.finish(
                    f"Insufficient balance. Your balance is {self.currency} "
                    f"{self.data[self.wallet_name]['balance']:.2f}."
                )
                return
            self.data[self.wallet_name]["balance"] -= price
            record_transaction(self.data, self.wallet_name, f"Data Bundle ({label})", price)
            self.finish(
                f"Bundle purchase successful!\nYou have purchased the {label} bundle for "
                f"{self.currency} {price:.2f}.\nNew Balance: {self.currency} "
                f"{self.data[self.wallet_name]['balance']:.2f}"
            )

        ttk.Button(self.container, text="Buy", command=submit).pack(pady=14)
        ttk.Button(self.container, text="Back", command=self.show_airtime_bundles_screen).pack()


    def show_check_balance(self):
        bal = self.data[self.wallet_name]["balance"]
        self.finish(f"{self.currency} Balance: {self.currency} {bal:.2f}")


    def show_transaction_history(self):
        self.clear()
        ttk.Label(self.container, text="TRANSACTION HISTORY",
                  font=("Segoe UI", 13, "bold")).pack(pady=(0, 12))

        history = self.data[self.wallet_name]["history"]

        columns = ("date", "type", "amount", "balance")
        tree = ttk.Treeview(self.container, columns=columns, show="headings", height=8)
        for col, label in zip(columns, ("Date", "Type", "Amount", "Balance")):
            tree.heading(col, text=label)
            tree.column(col, width=130 if col == "type" else 95)
        tree.pack(fill="both", expand=True, pady=(0, 12))

        if not history:
            tree.insert("", "end", values=("-", "No transactions yet", "-", "-"))
        else:
            for entry in history:
                tree.insert("", "end", values=(
                    entry["date"], entry["type"],
                    f"{self.currency} {entry['amount']:.2f}",
                    f"{self.currency} {entry['balance']:.2f}",
                ))

        ttk.Button(
            self.container, text="Close",
            command=lambda: self.finish("Thank you for using Mobile Money Banking System. Goodbye!")
        ).pack()


if __name__ == "__main__":
    app = MobileMoneyApp()
    app.mainloop()
