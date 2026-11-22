import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox

class Node:
    def __init__(self, name, quiz1, quiz2, quiz3):
        self.name = name
        self.quiz1 = int(quiz1)
        self.quiz2 = int(quiz2)
        self.quiz3 = int(quiz3)
        self.average = (self.quiz1 + self.quiz2 + self.quiz3) / 3
        self.remarks = "PASSED" if self.average >= 75 else "FAILED"
        self.next = None
class StudentRecord:
    def __init__(self):
        self.head = None
        self.filename = "students.csv"
        self.loaded = False

    def loadRecords(self):
        if self.loaded:
            return

        self.loaded = True

        if not os.path.exists(self.filename):
            return

        with open(self.filename, "r", newline="") as file:
            reader = csv.reader(file)
            next(reader, None)

            for row in reader:
                if len(row) == 6:
                    newNode = Node(row[0], row[1], row[2], row[3])

                    if self.head is None:
                        self.head = newNode
                    else:
                        current = self.head

                        while current.next:
                            current = current.next

                        current.next = newNode

    def addRecord(self, name, quiz1, quiz2, quiz3):
        self.loadRecords()
        newNode = Node(name, quiz1, quiz2, quiz3)

        if self.head is None:
            self.head = newNode
        else:
            current = self.head

            while current.next:
                current = current.next

            current.next = newNode

        self.saveRecords()

    def deleteRecord(self, name):
        self.loadRecords()
        current = self.head
        previous = None

        while current:
            if current.name.lower() == name.lower():
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next

                self.saveRecords()
                return True

            previous = current
            current = current.next

        return False

    def updateRecord(self, name, quiz1, quiz2, quiz3):
        self.loadRecords()
        current = self.head

        while current:
            if current.name.lower() == name.lower():
                current.quiz1 = int(quiz1)
                current.quiz2 = int(quiz2)
                current.quiz3 = int(quiz3)
                current.average = (current.quiz1 + current.quiz2 + current.quiz3) / 3
                current.remarks = "PASSED" if current.average >= 75 else "FAILED"

                self.saveRecords()
                return True
            current = current.next
        return False

    def saveRecords(self):
        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Quiz 1", "Quiz 2", "Quiz 3", "Average", "Remarks"])

            current = self.head

            while current:
                writer.writerow([
                    current.name,
                    current.quiz1,
                    current.quiz2,
                    current.quiz3,
                    round(current.average, 2),
                    current.remarks
                ])
                current = current.next

    def getRecords(self):
        self.loadRecords()
        records = []
        current = self.head

        while current:
            records.append(current)
            current = current.next

        return records

class StudentRecordGUI:
    def __init__(self):
        self.student = StudentRecord()
        self.student.loadRecords()

        self.window = tk.Tk()
        self.window.title("Student Record Management System")
        self.window.geometry("850x570")
        self.window.minsize(750, 500)

        self.create_widgets()
        self.refreshRecords()

        self.window.protocol("WM_DELETE_WINDOW", self.exitProgram)

    def create_widgets(self):
        self.window["padx"] = 10
        self.window["pady"] = 10

        title = ttk.Label(
            self.window,
            text="STUDENT RECORD MANAGEMENT SYSTEM",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.add_tab = ttk.Frame(self.notebook, padding=15)
        self.update_tab = ttk.Frame(self.notebook, padding=15)
        self.records_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.add_tab, text="Add Record")
        self.notebook.add(self.update_tab, text="Update / Delete")
        self.notebook.add(self.records_tab, text="Display Records")

        self.createAddTab()
        self.createUpdateTab()
        self.createRecordsTab()

    def createAddTab(self):
        form_frame = ttk.LabelFrame(
            self.add_tab,
            text="Student Information",
            padding=20
        )
        form_frame.pack(fill=tk.X, padx=30, pady=30)

        ttk.Label(form_frame, text="Student Name:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.add_name = ttk.Entry(form_frame, width=35)
        self.add_name.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(form_frame, text="Quiz 1:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.add_quiz1 = ttk.Entry(form_frame, width=35)
        self.add_quiz1.grid(row=1, column=1, padx=5, pady=8)

        ttk.Label(form_frame, text="Quiz 2:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.add_quiz2 = ttk.Entry(form_frame, width=35)
        self.add_quiz2.grid(row=2, column=1, padx=5, pady=8)

        ttk.Label(form_frame, text="Quiz 3:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.add_quiz3 = ttk.Entry(form_frame, width=35)
        self.add_quiz3.grid(row=3, column=1, padx=5, pady=8)

        button_frame = ttk.Frame(self.add_tab)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Add Record",
            command=self.addRecord
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clearAddFields
        ).grid(row=0, column=1, padx=5)

    def createUpdateTab(self):
        form_frame = ttk.LabelFrame(
            self.update_tab,
            text="Find Student and Edit Scores",
            padding=20
        )
        form_frame.pack(fill=tk.X, padx=30, pady=20)

        ttk.Label(form_frame, text="Student Name:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.edit_name = ttk.Entry(form_frame, width=35)
        self.edit_name.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(form_frame, text="New Quiz 1:").grid(
            row=1, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.edit_quiz1 = ttk.Entry(form_frame, width=35)
        self.edit_quiz1.grid(row=1, column=1, padx=5, pady=8)

        ttk.Label(form_frame, text="New Quiz 2:").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.edit_quiz2 = ttk.Entry(form_frame, width=35)
        self.edit_quiz2.grid(row=2, column=1, padx=5, pady=8)

        ttk.Label(form_frame, text="New Quiz 3:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=8
        )
        self.edit_quiz3 = ttk.Entry(form_frame, width=35)
        self.edit_quiz3.grid(row=3, column=1, padx=5, pady=8)

        button_frame = ttk.Frame(self.update_tab)
        button_frame.pack(pady=10)

        ttk.Button(
            button_frame,
            text="Update Record",
            command=self.updateRecord
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Delete Record",
            command=self.deleteRecord
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clearEditFields
        ).grid(row=0, column=2, padx=5)

        ttk.Label(
            self.update_tab,
            text="Enter the student's exact name. Name matching is not case-sensitive."
        ).pack(pady=10)

    def createRecordsTab(self):
        paned_window = tk.PanedWindow(
            self.records_tab,
            orient=tk.HORIZONTAL,
            sashwidth=5,
            sashrelief=tk.RAISED
        )
        paned_window.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(paned_window, padding=5)
        action_frame = ttk.LabelFrame(
        paned_window,
        text="Record Options",
        padding=10
        )

        paned_window.add(table_frame, minsize=500)
        paned_window.add(action_frame, minsize=150)

        columns = ("name", "quiz1", "quiz2", "quiz3", "average", "remarks")

        self.record_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        self.record_table.heading("name", text="Name")
        self.record_table.heading("quiz1", text="Quiz 1")
        self.record_table.heading("quiz2", text="Quiz 2")
        self.record_table.heading("quiz3", text="Quiz 3")
        self.record_table.heading("average", text="Average")
        self.record_table.heading("remarks", text="Remarks")
        self.record_table.column("name", width=170)
        self.record_table.column("quiz1", width=65, anchor=tk.CENTER)
        self.record_table.column("quiz2", width=65, anchor=tk.CENTER)
        self.record_table.column("quiz3", width=65, anchor=tk.CENTER)
        self.record_table.column("average", width=80, anchor=tk.CENTER)
        self.record_table.column("remarks", width=90, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.record_table.yview
        )
        self.record_table.configure(yscrollcommand=scrollbar.set)

        self.record_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(
            action_frame,
            text="Refresh(if there is a new csv file)",
            command=self.refreshRecords
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            action_frame,
            text="Save Records",
            command=self.saveRecords
        ).pack(fill=tk.X, pady=5)

        ttk.Button(
            action_frame,
            text="Exit",
            command=self.exitProgram
        ).pack(fill=tk.X, pady=5)

    def getScores(self, quiz1, quiz2, quiz3):
        try:
            return int(quiz1), int(quiz2), int(quiz3)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter whole numbers for all quiz scores.")
            return None

    def addRecord(self):
        name = self.add_name.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter the student's name.")
            return

        scores = self.getScores(
            self.add_quiz1.get(),
            self.add_quiz2.get(),
            self.add_quiz3.get()
        )

        if scores is None:
            return

        self.student.addRecord(name, scores[0], scores[1], scores[2])
        self.refreshRecords()
        self.clearAddFields()
        messagebox.showinfo("Success", "Record added successfully!")

    def updateRecord(self):
        name = self.edit_name.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter the student's name.")
            return

        scores = self.getScores(
            self.edit_quiz1.get(),
            self.edit_quiz2.get(),
            self.edit_quiz3.get()
        )

        if scores is None:
            return

        if self.student.updateRecord(name, scores[0], scores[1], scores[2]):
            self.refreshRecords()
            self.clearEditFields()
            messagebox.showinfo("Success", "Record updated successfully!")
        else:
            messagebox.showerror("Not Found", "Student record not found!")

    def deleteRecord(self):
        name = self.edit_name.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Enter the student's name to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete " + name + "?"
        )

        if confirm:
            if self.student.deleteRecord(name):
                self.refreshRecords()
                self.clearEditFields()
                messagebox.showinfo("Success", "Record deleted successfully!")
            else:
                messagebox.showerror("Not Found", "Student record not found!")

    def refreshRecords(self):
        for item in self.record_table.get_children():
            self.record_table.delete(item)

        for current in self.student.getRecords():
            self.record_table.insert("", tk.END, values=(
                current.name,
                current.quiz1,
                current.quiz2,
                current.quiz3,
                "{:.2f}".format(current.average),
                current.remarks
            ))

    def saveRecords(self):
        self.student.saveRecords()
        messagebox.showinfo("Saved", "Student records saved to students.csv!")

    def clearAddFields(self):
        self.add_name.delete(0, tk.END)
        self.add_quiz1.delete(0, tk.END)
        self.add_quiz2.delete(0, tk.END)
        self.add_quiz3.delete(0, tk.END)

    def clearEditFields(self):
        self.edit_name.delete(0, tk.END)
        self.edit_quiz1.delete(0, tk.END)
        self.edit_quiz2.delete(0, tk.END)
        self.edit_quiz3.delete(0, tk.END)

    def exitProgram(self):
        self.student.saveRecords()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

program = StudentRecordGUI()
program.run()