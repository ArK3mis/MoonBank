class Student:
    def __init__(self, name, student_id, course):
        self.name = name
        self.student_id = student_id
        self.course = course

class StudentADT:
    def __init__(self):
        self.students = []

    def add(self):
        name = input("Enter student name: ")
        student_id = input("Enter student ID: ")
        course = input("Enter course: ")

        student = Student(name, student_id, course)
        self.students.append(student)

        print("Student added successfully!")

    def delete(self):
        student_id = input("Enter student ID to delete: ")

        for student in self.students:
            if student.student_id == student_id:
                self.students.remove(student)
                print("Student deleted successfully!")
                return

        print("Student not found!")

    def display(self):
        if not self.students:
            print("No student records found!")
            return

        print("\n--- STUDENT RECORDS ---")

        for student in self.students:
            print("Name:", student.name)
            print("ID:", student.student_id)
            print("Course:", student.course)
            print("-----------------------")

def main():
    records = StudentADT()

    while True:
        print("\n===== STUDENT MANAGEMENT =====")
        print("1. Add Student")
        print("2. Delete Student")
        print("3. Display Students")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            records.add()
        elif choice == "2":
            records.delete()
        elif choice == "3":
            records.display()
        elif choice == "4":
            print("Program terminated.")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()