#Kenzo Elijah C. Buan
#BSIT 2A
#Project: ATM simulation using python

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
import os #this will detect wheter the user is using linux or windows so the program can handle USB better, I used this because i am using linux and the checker might use windows
import sys #this is for linux USB detection like ctype for windows, I build the program and compiled it using linux

STORAGE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ACCOUNT_FILE = os.path.join(STORAGE_DIRECTORY, "Account.csv")
CARD_FILE_NAME = "ATM_CARD.txt"
ENCRYPTION_KEY = "TUP_ATM_2026"

def detect_usb_drives():
    """Return mounted removable-drive folders on Windows or Linux."""
    drives = []

    if sys.platform.startswith("win"):
        try:
            import ctypes
            bitmask = ctypes.windll.kernel32.GetLogicalDrives()
            for index in range(26):
                if bitmask & (1 << index):
                    drive = chr(ord("A") + index) + ":\\"
                    if ctypes.windll.kernel32.GetDriveTypeW(drive) == 2:
                        drives.append(drive)
        except (AttributeError, OSError):
            pass
    else:
        username = os.environ.get("USER", "")
        mount_roots = [
            os.path.join("/media", username),
            os.path.join("/run/media", username),
            "/media",
            "/run/media"
        ]
        seen = set()
        for root in mount_roots:
            if not os.path.isdir(root):
                continue
            try:
                for name in os.listdir(root):
                    candidate = os.path.join(root, name)
                    if os.path.ismount(candidate) and candidate not in seen:
                        drives.append(candidate)
                        seen.add(candidate)
            except OSError:
                continue

    return drives

def set_storage_directory(directory):
    """Set the folder used for the account database."""
    global STORAGE_DIRECTORY, ACCOUNT_FILE
    STORAGE_DIRECTORY = os.path.abspath(directory)
    os.makedirs(STORAGE_DIRECTORY, exist_ok=True)
    ACCOUNT_FILE = os.path.join(STORAGE_DIRECTORY, "Account.csv")

class Account:
    def __init__(self, num, name, bday, contact, pin, balance):
        self.num = num
        self.name = name
        self.bday = bday
        self.contact = contact
        self.PIN = pin
        self.bal = int(balance)

class Node:
    def __init__(self, account):
        self.acc = account
        self.next = None

class ATM:
    def __init__(self):
        self.head = None
        self.account = None
        self.RetAcc()

    def LocAcc(self, num):
        current = self.head

        while current is not None:
            if current.acc.num == num:
                return current
            current = current.next

        return None

    def InsertAcc(self, account):
        new_node = Node(account)

        if self.head is None or account.name.lower() < self.head.acc.name.lower():
            new_node.next = self.head
            self.head = new_node
            return

        current = self.head

        while (current.next is not None and
               account.name.lower() >= current.next.acc.name.lower()):
            current = current.next

        new_node.next = current.next
        current.next = new_node

    def IsDigit(self, value):
        if value == "":
            return False

        for character in value:
            if character < "0" or character > "9":
                return False

        return True

    def IsAccName(self, name):
        if name.strip() == "":
            return False

        for character in name:
            if not (("A" <= character <= "Z") or
                    ("a" <= character <= "z") or
                    character == " "):
                return False

        return True

    def IsAccNum(self, num):
        return len(num) == 5 and self.IsDigit(num) and self.LocAcc(num) is None

    def IsAccBday(self, bday):
        if len(bday) != 10 or bday[2] != "/" or bday[5] != "/":
            return False

        month_text = bday[0:2]
        day_text = bday[3:5]
        year_text = bday[6:10]

        if not self.IsDigit(month_text + day_text + year_text):
            return False

        month = int(month_text)
        day = int(day_text)
        year = int(year_text)

        if month < 1 or month > 12 or year < 1926 or year > 2026:
            return False

        if month == 2:
            if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
                days = 29
            else:
                days = 28
        elif month in (4, 6, 9, 11):
            days = 30
        else:
            days = 31

        return 1 <= day <= days

    def IsAccContact(self, contact):
        return (len(contact) == 11 and contact.startswith("09")
                and self.IsDigit(contact))

    def IsAccPIN(self, pin):
        return 4 <= len(pin) <= 6 and self.IsDigit(pin)

    def IsValidAmount(self, value):
        return self.IsDigit(value)

    def IsAccDeposit(self, amount):
        return amount >= 5000

    def Encrypt(self, text):
        result = ""
        hex_digits = "0123456789ABCDEF"

        for index in range(len(text)):
            value = ord(text[index]) ^ ord(ENCRYPTION_KEY[index % len(ENCRYPTION_KEY)])
            result += hex_digits[(value >> 4) & 15]
            result += hex_digits[value & 15]

        return result

    def Decrypt(self, text):
        if len(text) % 2 != 0:
            return ""

        result = ""

        for index in range(0, len(text), 2):
            first = text[index]
            second = text[index + 1]

            if first not in "0123456789ABCDEF":
                return ""
            if second not in "0123456789ABCDEF":
                return ""

            high = "0123456789ABCDEF".find(first)
            low = "0123456789ABCDEF".find(second)

            value = (high << 4) | low
            value = value ^ ord(ENCRYPTION_KEY[(index // 2) % len(ENCRYPTION_KEY)])
            result += chr(value)

        return result

    def SaveAcc(self):
        try:
            with open(ACCOUNT_FILE, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                current = self.head

                while current is not None:
                    account = current.acc
                    writer.writerow([
                        account.num,
                        account.name,
                        account.bday,
                        account.contact,
                        self.Encrypt(account.PIN),
                        account.bal
                    ])
                    current = current.next

            return True
        except OSError:
            return False

    def RetAcc(self):
        try:
            with open(ACCOUNT_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.reader(file)

                for row in reader:
                    if len(row) != 6:
                        continue

                    try:
                        pin = self.Decrypt(row[4])
                        if pin == "":
                            continue

                        account = Account(
                            row[0], row[1], row[2], row[3], pin, int(row[5])
                        )
                        if self.LocAcc(account.num) is None:
                            self.InsertAcc(account)
                    except (ValueError, IndexError):
                        continue
        except FileNotFoundError:
            pass
        except OSError:
            pass

    def ReadCardData(self, path):
        card_num = ""
        card_pin = ""

        try:
            with open(path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)

                    if key == "ACCOUNT_NO":
                        card_num = value
                    elif key == "ENCRYPTED_PIN":
                        card_pin = value

            if card_num != "" and card_pin != "":
                return card_num, card_pin

        except OSError:
            return None

        return None

    def WriteCardData(self, path, card_num, encrypted_pin):
        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write("ATM_CARD\n")
                file.write("ACCOUNT_NO=" + card_num + "\n")
                file.write("ENCRYPTED_PIN=" + encrypted_pin + "\n")
            return True
        except OSError:
            return False

    def SaveCard(self, path):
        if self.account is None:
            return False

        return self.WriteCardData(
            path,
            self.account.acc.num,
            self.Encrypt(self.account.acc.PIN)
        )

    def RegisterAccount(self, values):
        num = values["num"].strip()
        name = values["name"].strip()
        bday = values["bday"].strip()
        contact = values["contact"].strip()
        pin = values["pin"].strip()
        balance_text = values["balance"].strip()

        if not self.IsAccNum(num):
            return False, "Account number must be 5 unique digits."

        if not self.IsAccName(name):
            return False, "Name must contain letters and spaces only."

        if not self.IsAccBday(bday):
            return False, "Birthday must be a valid date in MM/DD/YYYY format."

        if not self.IsAccContact(contact):
            return False, "Contact number must contain 11 digits and start with 09."

        if not self.IsAccPIN(pin):
            return False, "PIN must contain 4 to 6 digits."

        if not self.IsValidAmount(balance_text):
            return False, "Initial deposit must contain whole numbers only."

        balance = int(balance_text)

        if not self.IsAccDeposit(balance):
            return False, "The minimum initial deposit is 5000."

        account = Account(num, name, bday, contact, pin, balance)
        self.InsertAcc(account)

        if not self.SaveAcc():
            return False, "Account was created, but the account file could not be saved."

        return True, "Account successfully created."

    def LogIn(self, card_path, entered_pin):
        card_data = self.ReadCardData(card_path)

        if card_data is None:
            return False, "Invalid ATM card file."

        card_num, encrypted_card_pin = card_data
        found = self.LocAcc(card_num)

        if found is None:
            return False, "The account connected to this card was not found."

        if self.Decrypt(encrypted_card_pin) != found.acc.PIN:
            return False, "ATM card information does not match the account database."

        if entered_pin != found.acc.PIN:
            return False, "Incorrect PIN."

        self.account = found
        return True, "Access granted."

    def LogOut(self):
        self.account = None

    def BalInq(self):
        if self.account is None:
            return 0
        return self.account.acc.bal

    def WithdrawBal(self, amount_text):
        if self.account is None:
            return False, "Please insert your card first."

        if not self.IsValidAmount(amount_text):
            return False, "Enter whole numbers only."

        amount = int(amount_text)

        if amount <= 0 or amount % 100 != 0:
            return False, "Withdrawal must be positive and divisible by 100."

        if amount > self.account.acc.bal:
            return False, "Insufficient balance."

        self.account.acc.bal -= amount

        if not self.SaveAcc():
            return False, "Withdrawal processed, but the account file could not be saved."

        return True, "Amount successfully withdrawn."

    def DepositAmount(self, amount_text):
        if self.account is None:
            return False, "Please insert your card first."

        if not self.IsValidAmount(amount_text):
            return False, "Enter whole numbers only."

        amount = int(amount_text)

        if amount <= 0:
            return False, "Deposit amount must be greater than zero."

        self.account.acc.bal += amount

        if not self.SaveAcc():
            return False, "Deposit processed, but the account file could not be saved."

        return True, "Amount successfully deposited."

    def FundTrans(self, receiver_num, amount_text):
        if self.account is None:
            return False, "Please insert your card first."

        receiver = self.LocAcc(receiver_num)

        if receiver is None:
            return False, "The receiver's account was not found."

        if receiver is self.account:
            return False, "You cannot transfer to the same account."

        if not self.IsValidAmount(amount_text):
            return False, "Enter whole numbers only."

        amount = int(amount_text)

        if amount <= 0:
            return False, "Transfer amount must be greater than zero."

        if amount > self.account.acc.bal:
            return False, "Insufficient balance."

        self.account.acc.bal -= amount
        receiver.acc.bal += amount

        if not self.SaveAcc():
            return False, "Transfer processed, but the account file could not be saved."

        return True, "Amount successfully transferred."

    def ChangePIN(self, current_pin, new_pin, confirm_pin):
        if self.account is None:
            return False, "Please insert your card first."

        if current_pin != self.account.acc.PIN:
            return False, "Incorrect current PIN."

        if not self.IsAccPIN(new_pin):
            return False, "New PIN must contain 4 to 6 digits."

        if new_pin != confirm_pin:
            return False, "PIN codes do not match."

        if new_pin == self.account.acc.PIN:
            return False, "New PIN must be different from the current PIN."

        self.account.acc.PIN = new_pin
        self.SaveAcc()
        return True, "PIN successfully changed."

    def DispAcc(self):
        if self.account is None:
            return None

        account = self.account.acc
        return {
            "Number": account.num,
            "Name": account.name,
            "Birthday": account.bday,
            "Contact Number": account.contact
        }

class ATMApp:
    def __init__(self, root):
        self.root = root
        usb_drives = detect_usb_drives()
        if usb_drives:
            set_storage_directory(usb_drives[0])
        self.atm = ATM()

        self.root.title("MoonBank | ATM Simulation")
        self.root.geometry("1100x760")
        self.root.resizable(False, False)
        self.root.configure(bg="#202b38")

        style = ttk.Style()
        style.configure("ATM.Machine.TFrame", background="#d8dde3")
        self.panel_gray = "#aeb6bf"
        style.configure("ATM.Panel.TLabelframe", background=self.panel_gray, borderwidth=3, relief="sunken")
        style.configure("ATM.Panel.TLabelframe.Label", background=self.panel_gray, foreground="#344454", font=("Arial", 9, "bold"))

        self.bg = "#202b38"
        self.machine = "#d8dde3"
        self.panel_gray = "#aeb6bf"
        self.screen_blue = "#087fbd"
        self.dark_blue = "#07558c"
        self.light_blue = "#16a9df"
        self.white = "#ffffff"
        self.text_dark = "#17334a"

        self.inserted_card_path = ""
        self.current_input = ""
        self.current_screen = "welcome"

        self.build_machine()
        self.show_welcome()

    def build_machine(self):

        self.machine_frame = ttk.Frame(
            self.root, style="ATM.Machine.TFrame", relief="raised", borderwidth=4
        )
        self.machine_frame.place(
            relx=0.5, rely=0.5, anchor="center",
            relwidth=0.94, relheight=0.94
        )

        header = ttk.Frame(self.machine_frame)
        header.pack(fill="x", padx=8, pady=8)

        tk.Label(
            header, text="MOONBANK", bg="#edf0f3",
            fg="#07558c", font=("Arial", 22, "bold")
        ).pack(side="left", padx=18)

        tk.Label(
            header, text="WINDOWS  |  LINUX SUPPORTED",
            bg="#edf0f3", fg="#526575",
            font=("Arial", 9, "bold")
        ).pack(side="right", padx=16)

        body = ttk.Frame(self.machine_frame)
        body.pack(fill="both", expand=True, padx=14, pady=8)

        body.grid_columnconfigure(0, weight=2, uniform="atm_columns")
        body.grid_columnconfigure(1, weight=1, uniform="atm_columns")
        body.grid_rowconfigure(0, weight=1)

        screen_group = ttk.LabelFrame(
            body, text="ATM DISPLAY", style="ATM.Panel.TLabelframe", relief=tk.SUNKEN, padding=8
        )
        screen_group.grid(
            row=0, column=0, sticky="nsew", padx=(0, 6)
        )

        self.screen_frame = tk.Frame(screen_group, bg=self.screen_blue)
        self.screen_frame.pack(fill="both", expand=True)

        self.screen_header = tk.Frame(
            self.screen_frame, bg=self.dark_blue, height=48
        )
        self.screen_header.pack(fill="x")
        self.screen_header.pack_propagate(False)

        self.screen_brand = tk.Label(
            self.screen_header, text="MOONBANK",
            bg=self.dark_blue, fg=self.white,
            font=("Arial", 17, "bold")
        )
        self.screen_brand.pack(side="left", padx=18)

        self.status_label = tk.Label(
            self.screen_header, text="WELCOME",
            bg=self.dark_blue, fg="#bfeaff",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(side="right", padx=18)

        self.screen_content = tk.Frame(
            self.screen_frame, bg=self.screen_blue
        )
        self.screen_content.pack(fill="both", expand=True, padx=24, pady=20)

        keypad_group = ttk.LabelFrame(
            body, text="ATM KEYPAD", style="ATM.Panel.TLabelframe", relief=tk.SUNKEN, padding=8
        )
        keypad_group.grid(
            row=0, column=1, sticky="nsew", padx=(6, 0)
        )

        keypad = tk.Frame(keypad_group, bg=self.panel_gray, bd=3, relief="sunken", padx=4, pady=4)
        keypad.pack(expand=True, anchor="center")

        for row in range(3):
            for col in range(3):
                number = str(row * 3 + col + 1)
                button = tk.Button(
                    keypad, text=number, width=4, height=2,
                    font=("Arial", 15, "bold"),
                    bg="#f7f8fa", fg="#174b70",
                    activebackground="#d9eaf5",
                    relief="raised", bd=3,
                    command=lambda value=number: self.key_press(value)
                )
                button.grid(row=row, column=col, padx=4, pady=5)

        tk.Button(
            keypad, text="CLEAR", width=4, height=2,
            font=("Arial", 9, "bold"), bg="#e6e9ed",
            command=self.clear_input
        ).grid(row=3, column=0, padx=4, pady=5)

        tk.Button(
            keypad, text="0", width=4, height=2,
            font=("Arial", 15, "bold"), bg="#f7f8fa",
            fg="#174b70", relief="raised", bd=3,
            command=lambda: self.key_press("0")
        ).grid(row=3, column=1, padx=4, pady=5)

        tk.Button(
            keypad, text="ENTER", width=4, height=2,
            font=("Arial", 9, "bold"), bg="#d4e9d8",
            command=self.enter_action
        ).grid(row=3, column=2, padx=4, pady=5)

        tk.Button(
            keypad_group, text="CANCEL",
            width=19, height=2, font=("Arial", 10, "bold"),
            bg="#f5dada", command=self.cancel_action
        ).pack(pady=(12, 0))

        lower = ttk.Frame(self.machine_frame)
        lower.pack(fill="x", padx=14, pady=(4, 12))

        card_group = ttk.LabelFrame(
            lower, text="CARD SLOT", style="ATM.Panel.TLabelframe", relief=tk.SUNKEN, padding=8
        )
        card_group.pack(side="left", padx=8)

        self.card_slot = tk.Frame(
            card_group, bg="#4a535c", width=230, height=30,
            highlightthickness=2, highlightbackground="#8b969f",
            cursor="hand2"
        )
        self.card_slot.pack()
        self.card_slot.pack_propagate(False)

        self.card_slot_label = tk.Label(
            self.card_slot, text="INSERT ATM CARD",
            bg="#4a535c", fg="#d9e0e6",
            font=("Arial", 9, "bold"), cursor="hand2"
        )
        self.card_slot_label.pack(expand=True)

        self.card_visual = tk.Label(
            lower, text="", bg="#cbd2d9",
            fg="#174b70", font=("Arial", 10, "bold")
        )
        self.card_visual.pack(side="left", padx=8)

        self.card_slot.bind("<Button-1>", lambda event: self.insert_card())
        self.card_slot_label.bind("<Button-1>", lambda event: self.insert_card())

    def clear_screen(self):
        for widget in self.screen_content.winfo_children():
            widget.destroy()

    def set_status(self, text):
        self.status_label.config(text=text.upper())

    def title_label(self, text, size=22):
        tk.Label(
            self.screen_content, text=text,
            bg=self.screen_blue, fg=self.white,
            font=("Arial", size, "bold"),
            justify="center", wraplength=570
        ).pack(pady=(12, 10))

    def body_label(self, text, size=12):
        tk.Label(
            self.screen_content, text=text,
            bg=self.screen_blue, fg=self.white,
            font=("Arial", size),
            justify="center", wraplength=570
        ).pack(pady=5)

    def screen_button(self, text, command, width=23):
        button = tk.Button(
            self.screen_content, text=text, command=command,
            width=width, height=2,
            bg="#f4f6f8", fg="#174b70",
            activebackground="#d9eaf5",
            font=("Arial", 11, "bold"),
            relief="raised", bd=3, cursor="hand2"
        )
        button.pack(pady=6)
        return button

    def show_message(self, title, message, success=True):
        if success:
            messagebox.showinfo(title, message)
        else:
            messagebox.showerror(title, message)

    def key_press(self, value):
        if self.current_screen == "transaction" and hasattr(self, "active_entry"):
            self.active_entry.insert("end", value)
            return

        if self.current_screen == "pin":
            if len(self.current_input) >= 6:
                return
            self.current_input += value
            if hasattr(self, "pin_display_label"):
                self.pin_display_label.config(text="PIN: " + ("*" * len(self.current_input)))
        else:
            self.current_input += value

    def clear_input(self):
        if self.current_screen == "transaction" and hasattr(self, "active_entry"):
            self.active_entry.delete(0, "end")
        self.current_input = ""
        if self.current_screen == "pin" and hasattr(self, "pin_display_label"):
            self.pin_display_label.config(text="PIN: ")

    def enter_action(self):
        if self.current_screen == "pin":
            self.verify_pin_from_keypad()
        elif self.current_screen == "transaction" and hasattr(self, "transaction_action"):
            self.transaction_action()
        else:
            return

    def cancel_action(self):
        self.current_input = ""
        if self.atm.account is not None:
            self.show_main_menu()
        else:
            self.show_welcome()

    def show_welcome(self):
        self.current_screen = "welcome"
        self.current_input = ""
        self.clear_screen()
        self.set_status("WELCOME")
        self.title_label("WELCOME TO MOONBANK", 24)
        self.body_label("Please select a service to continue.", 13)
        self.screen_button("INSERT ATM CARD / LOGIN", self.insert_card, 29)
        self.screen_button("REGISTER NEW ACCOUNT", self.show_registration, 29)
        self.body_label("Please keep your ATM card and PIN secure.", 10)

    def insert_card(self):
        if self.atm.account is not None:
            self.show_message("ATM", "A card is already logged in.", False)
            return

        usb_drives = detect_usb_drives()
        initial_directory = usb_drives[0] if usb_drives else os.path.expanduser("~")
        path = filedialog.askopenfilename(
            title="Select your ATM card file",
            initialdir=initial_directory,
            filetypes=[("ATM Card File", "*.txt"), ("All Files", "*.*")]
        )

        if path == "":
            return

        card_data = self.atm.ReadCardData(path)

        if card_data is None:
            self.show_message("Invalid Card", "The selected file is not a valid ATM card.", False)
            return

        self.inserted_card_path = path
        self.card_visual.config(
            text="ATM CARD INSERTED",
            bg="#e8edf2", relief="raised", bd=2,
            padx=12, pady=8
        )
        self.card_slot_label.config(text="INSERT ATM CARD", fg="#d9e0e6")

        self.current_screen = "pin"
        self.current_input = ""
        self.clear_screen()
        self.set_status("CARD DETECTED")
        self.title_label("CARD SUCCESSFULLY DETECTED", 19)
        self.body_label("Account Number: " + card_data[0], 13)
        self.body_label("Please enter your PIN using the keypad.", 12)
        self.pin_display_label = tk.Label(
            self.screen_content, text="PIN: ",
            bg=self.screen_blue, fg="#ffffff",
            font=("Arial", 18, "bold")
        )
        self.pin_display_label.pack(pady=8)
        self.body_label("Press ENTER when finished.", 10)
        self.screen_button("ENTER PIN", self.verify_pin_from_keypad, 18)
        self.screen_button("CANCEL / EJECT CARD", self.eject_card, 22)

    def verify_pin_from_keypad(self):
        if self.current_screen != "pin":
            return

        if self.current_input == "":
            self.show_message("PIN Required", "Please enter your PIN first.", False)
            return

        success, message = self.atm.LogIn(
            self.inserted_card_path, self.current_input
        )
        self.current_input = ""

        if success:
            self.show_message("Login Successful", message, True)
            self.show_main_menu()
        else:
            self.show_message("Login Failed", message, False)
            self.eject_card()

    def eject_card(self):
        self.atm.LogOut()
        self.inserted_card_path = ""
        self.card_visual.config(text="", bg="#cbd2d9", relief="flat")
        self.card_slot_label.config(text="INSERT ATM CARD", fg="#d9e0e6")
        self.show_welcome()

    def show_registration(self):
        self.current_screen = "registration"
        self.clear_screen()
        self.set_status("REGISTRATION")
        self.title_label("NEW ACCOUNT REGISTRATION", 20)
        self.body_label("Complete all fields to create your account.", 11)

        registration_tabs = ttk.Notebook(self.screen_content)
        registration_tabs.pack(fill="both", expand=True, padx=12, pady=8)

        personal_tab = ttk.Frame(registration_tabs, padding=10)
        security_tab = ttk.Frame(registration_tabs, padding=10)

        registration_tabs.add(personal_tab, text="Personal Details")
        registration_tabs.add(security_tab, text="Account Security")

        self.registration_entries = {}

        personal_fields = [
            ("Account Number (5 digits)", "num"),
            ("Full Name", "name"),
            ("Birthday (MM/DD/YYYY)", "bday"),
            ("Contact Number (09XXXXXXXXX)", "contact")
        ]

        security_fields = [
            ("PIN (4-6 digits)", "pin"),
            ("Initial Deposit (minimum 5000)", "balance")
        ]

        for parent, fields in (
            (personal_tab, personal_fields),
            (security_tab, security_fields)
        ):
            for row, (label_text, key) in enumerate(fields):
                ttk.Label(
                    parent, text=label_text, width=29
                ).grid(row=row, column=0, padx=7, pady=9, sticky="e")

                entry = ttk.Entry(
                    parent, width=27,
                    show="*" if key == "pin" else ""
                )
                entry.grid(row=row, column=1, padx=7, pady=9)
                self.registration_entries[key] = entry

        actions = ttk.Frame(self.screen_content)
        actions.pack(pady=8)

        ttk.Button(
            actions, text="CREATE ACCOUNT",
            command=self.submit_registration
        ).pack(side="left", padx=5)

        ttk.Button(
            actions, text="BACK",
            command=self.show_welcome
        ).pack(side="left", padx=5)

    def submit_registration(self):
        values = {}

        for key, entry in self.registration_entries.items():
            values[key] = entry.get()

        usb_drives = detect_usb_drives()
        if usb_drives:
            storage_folder = usb_drives[0]
        else:
            storage_folder = filedialog.askdirectory(
                title="Choose where to save MoonBank account and card files",
                initialdir=os.path.expanduser("~")
            )
            if not storage_folder:
                self.show_message(
                    "Storage Required",
                    "Choose a USB drive or folder before creating an account.",
                    False
                )
                return

        set_storage_directory(storage_folder)

        self.atm.head = None
        self.atm.RetAcc()

        success, message = self.atm.RegisterAccount(values)
        if not success:
            self.show_message("Registration Error", message, False)
            return

        account_node = self.atm.LocAcc(values["num"].strip())
        self.atm.account = account_node
        card_filename = "ATM_CARD_" + values["num"].strip() + ".txt"
        card_path = os.path.join(STORAGE_DIRECTORY, card_filename)

        if self.atm.SaveCard(card_path):
            self.show_message(
                "Registration Complete",
                message + "\n\nYour ATM card file was saved to:\n" + card_path,
                True
            )
        else:
            self.show_message(
                "Registration Complete",
                message + "\n\nThe account was saved, but the ATM card file could not be created.",
                False
            )

        self.atm.LogOut()
        self.show_welcome()

    def show_main_menu(self):
        if self.atm.account is None:
            self.show_welcome()
            return

        self.current_screen = "menu"
        self.current_input = ""
        self.clear_screen()
        self.set_status("MAIN MENU")

        account = self.atm.account.acc
        tk.Label(
            self.screen_content, text="WELCOME, " + account.name.upper(),
            bg=self.screen_blue, fg=self.white,
            font=("Arial", 18, "bold")
        ).pack(pady=(4, 2))
        tk.Label(
            self.screen_content, text="ACCOUNT NO.: " + account.num + "  |  SELECT A TRANSACTION",
            bg=self.screen_blue, fg=self.white,
            font=("Arial", 10)
        ).pack(pady=(0, 10))

        menu_frame = tk.Frame(self.screen_content, bg=self.screen_blue)
        menu_frame.pack(expand=True)
        menu_items = [
            ("BALANCE INQUIRY", self.balance_inquiry),
            ("WITHDRAW CASH", self.withdraw_screen),
            ("DEPOSIT MONEY", self.deposit_screen),
            ("FUND TRANSFER", self.transfer_screen),
            ("CHANGE PIN", self.change_pin_screen),
            ("ACCOUNT INFORMATION", self.account_information),
            ("EJECT CARD / LOGOUT", self.logout),
            ("EXIT", self.exit_application)
        ]

        for index, (label, command) in enumerate(menu_items):
            row = index // 2
            column = index % 2
            tk.Button(
                menu_frame, text=label, command=command,
                width=22, height=2,
                bg="#f4f6f8", fg="#174b70",
                activebackground="#d9eaf5",
                font=("Arial", 9, "bold"),
                relief="raised", bd=3, cursor="hand2"
            ).grid(row=row, column=column, padx=6, pady=5, sticky="nsew")

    def balance_inquiry(self):
        balance = self.atm.BalInq()
        self.clear_screen()
        self.set_status("BALANCE INQUIRY")
        self.title_label("ACCOUNT BALANCE", 22)
        self.body_label("Your available balance is:", 13)
        self.title_label("₱ " + format(balance, ",") + ".00", 27)
        self.screen_button("BACK TO MAIN MENU", self.show_main_menu)

    def transaction_input_screen(self, title, prompt, action, extra_field=False):
        self.current_screen = "transaction"
        self.current_input = ""
        self.clear_screen()
        self.set_status(title)
        self.title_label(title, 20)
        self.body_label(prompt, 12)

        if extra_field:
            self.body_label("Receiver Account Number:", 10)
            self.receiver_entry = tk.Entry(
                self.screen_content, font=("Arial", 13), width=22
            )
            self.receiver_entry.pack(pady=5)

        self.amount_entry = tk.Entry(
            self.screen_content, font=("Arial", 16), width=22
        )
        self.amount_entry.pack(pady=12)
        self.active_entry = self.amount_entry
        self.transaction_action = action

        tk.Button(
            self.screen_content, text="CONFIRM",
            command=action, width=20, height=2,
            bg="#f4f6f8", fg="#174b70",
            font=("Arial", 11, "bold")
        ).pack(pady=5)

        self.screen_button("BACK TO MAIN MENU", self.show_main_menu)

    def withdraw_screen(self):
        self.transaction_input_screen(
            "WITHDRAW CASH",
            "Enter the amount to withdraw (multiples of 100).",
            self.submit_withdraw
        )

    def submit_withdraw(self):
        amount = self.amount_entry.get().strip()
        success, message = self.atm.WithdrawBal(amount)
        self.show_message("Withdrawal", message, success)

        if success:
            self.clear_screen()
            self.set_status("WITHDRAWAL")
            self.title_label("PLEASE TAKE YOUR CASH", 22)
            self.body_label("₱ " + format(int(amount), ",") + ".00", 20)
            self.screen_button("BACK TO MAIN MENU", self.show_main_menu)
        else:
            self.withdraw_screen()

    def deposit_screen(self):
        self.transaction_input_screen(
            "DEPOSIT MONEY",
            "Enter the amount to deposit.",
            self.submit_deposit
        )

    def submit_deposit(self):
        amount = self.amount_entry.get().strip()
        success, message = self.atm.DepositAmount(amount)
        self.show_message("Deposit", message, success)

        if success:
            self.show_main_menu()
        else:
            self.deposit_screen()

    def transfer_screen(self):
        self.transaction_input_screen(
            "FUND TRANSFER",
            "Enter the receiver's account number and amount.",
            self.submit_transfer,
            True
        )

    def submit_transfer(self):
        receiver_num = self.receiver_entry.get().strip()
        amount = self.amount_entry.get().strip()

        receiver = self.atm.LocAcc(receiver_num)
        if receiver is None:
            self.show_message("Fund Transfer", "The account was not found.", False)
            return

        confirm = messagebox.askyesno(
            "Confirm Transfer",
            "Receiver: " + receiver.acc.name +
            "\nAccount Number: " + receiver.acc.num +
            "\nAmount: ₱ " + amount +
            "\n\nProceed with this transfer?"
        )

        if not confirm:
            return

        success, message = self.atm.FundTrans(receiver_num, amount)
        self.show_message("Fund Transfer", message, success)

        if success:
            self.show_main_menu()

    def change_pin_screen(self):
        self.current_screen = "change_pin"
        self.clear_screen()
        self.set_status("CHANGE PIN")
        self.title_label("CHANGE YOUR PIN", 20)

        form = tk.Frame(self.screen_content, bg=self.screen_blue)
        form.pack(pady=10)

        self.pin_entries = {}

        fields = [
            ("Current PIN", "current"),
            ("New PIN", "new"),
            ("Confirm New PIN", "confirm")
        ]

        for row, (label_text, key) in enumerate(fields):
            tk.Label(
                form, text=label_text, bg=self.screen_blue,
                fg=self.white, font=("Arial", 11, "bold"),
                width=20, anchor="e"
            ).grid(row=row, column=0, padx=6, pady=8)

            entry = tk.Entry(form, show="*", font=("Arial", 13), width=20)
            entry.grid(row=row, column=1, padx=6, pady=8)
            self.pin_entries[key] = entry

        tk.Button(
            self.screen_content, text="UPDATE PIN",
            command=self.submit_change_pin,
            width=20, height=2, bg="#f4f6f8",
            fg="#174b70", font=("Arial", 11, "bold")
        ).pack(pady=8)

        self.screen_button("BACK TO MAIN MENU", self.show_main_menu)

    def submit_change_pin(self):
        current = self.pin_entries["current"].get()
        new = self.pin_entries["new"].get()
        confirm = self.pin_entries["confirm"].get()

        success, message = self.atm.ChangePIN(current, new, confirm)
        self.show_message("Change PIN", message, success)

        if success:
            if self.inserted_card_path:
                updated = self.atm.SaveCard(self.inserted_card_path)
                if not updated:
                    self.show_message(
                        "Card Update",
                        "Your account PIN was changed, but the card file could not be updated.",
                        False
                    )
            self.show_main_menu()

    def account_information(self):
        information = self.atm.DispAcc()

        self.clear_screen()
        self.set_status("ACCOUNT INFORMATION")
        self.title_label("ACCOUNT INFORMATION", 20)

        for label, value in information.items():
            self.body_label(label + ": " + str(value), 12)

        self.screen_button("BACK TO MAIN MENU", self.show_main_menu)

    def logout(self):
        confirm = messagebox.askyesno(
            "Eject Card",
            "Are you sure you want to log out and eject your card?"
        )

        if confirm:
            self.atm.LogOut()
            self.inserted_card_path = ""
            self.card_visual.config(text="", bg="#cbd2d9", relief="flat")
            self.card_slot_label.config(text="INSERT ATM CARD", fg="#d9e0e6")
            self.show_welcome()

    def exit_application(self):
        confirm = messagebox.askyesno(
            "Exit MoonBank",
            "Are you sure you want to close the ATM application?"
        )
        if confirm:
            self.on_close()

    def on_close(self):
        self.atm.SaveAcc()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ATMApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
