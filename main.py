import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkinter import font
import re

class StudentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1200x700")
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.bg_color = "#f0f3f5"
        self.button_color = "#4a7a8c"
        self.header_color = "#2c3e50"
        self.accent_color = "#3498db"
        
        self.configure_styles()
        self.create_db()
        self.create_widgets()
        self.load_students()

    def configure_styles(self):
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TButton', background=self.button_color, foreground='white', 
                           font=('Helvetica', 10, 'bold'), borderwidth=1)
        self.style.map('TButton', 
                      background=[('active', self.accent_color), ('pressed', '!disabled', self.accent_color)])
        self.style.configure('Header.TLabel', background=self.header_color, foreground='white',
                           font=('Helvetica', 12, 'bold'))
        self.style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'), background='#e8e8e8')
        self.style.configure('Treeview', rowheight=25)

    def create_db(self):
        self.conn = sqlite3.connect('students.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS students
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          age INTEGER,
                          grade TEXT,
                          email TEXT,
                          phone TEXT,
                          course TEXT)''')
        self.conn.commit()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=20, padx=20, fill=tk.X)

        fields = ['Name', 'Age', 'Grade', 'Email', 'Phone', 'Course']
        self.entries = {}
        for i, field in enumerate(fields):
            lbl = ttk.Label(form_frame, text=f"{field}:", style='Header.TLabel')
            lbl.grid(row=i//2, column=(i%2)*2, padx=5, pady=5, sticky=tk.E)
            
            ent = ttk.Entry(form_frame, width=25)
            ent.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5, sticky=tk.W)
            self.entries[field.lower()] = ent

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        buttons = [
            ('Add Student', self.add_student),
            ('Update Student', self.update_student),
            ('Delete Student', self.delete_student),
            ('Clear Fields', self.clear_fields),
            ('Search Student', self.search_student)
        ]
        
        for i, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(btn_frame, text=text, command=cmd, style='TButton')
            btn.grid(row=0, column=i, padx=5)

        # Search Box
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.search_student)
        
        ttk.Button(search_frame, text="Clear Search", command=self.clear_search).pack(side=tk.LEFT)

        # Student Table
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Age', 'Grade', 'Email', 'Phone', 'Course'),
                               show='headings', selectmode='browse')
        
        columns = [
            ('ID', 50), ('Name', 150), ('Age', 50), 
            ('Grade', 100), ('Email', 200), ('Phone', 120), ('Course', 150)
        ]
        
        for col, width in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_student)

    def load_students(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        self.c.execute("SELECT * FROM students")
        students = self.c.fetchall()
        for student in students:
            self.tree.insert('', tk.END, values=student)

    def validate_fields(self):
        # Simple validation example
        if not self.entries['name'].get().strip():
            messagebox.showerror("Error", "Name is required")
            return False
        
        if not self.entries['age'].get().isdigit():
            messagebox.showerror("Error", "Age must be a number")
            return False
        
        email = self.entries['email'].get()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email format")
            return False
        
        return True

    def get_student_data(self):
        return (
            self.entries['name'].get().strip(),
            int(self.entries['age'].get()),
            self.entries['grade'].get().strip(),
            self.entries['email'].get().strip(),
            self.entries['phone'].get().strip(),
            self.entries['course'].get().strip()
        )

    def add_student(self):
        if not self.validate_fields():
            return
        
        data = self.get_student_data()
        self.c.execute('''INSERT INTO students 
                        (name, age, grade, email, phone, course)
                        VALUES (?,?,?,?,?,?)''', data)
        self.conn.commit()
        self.load_students()
        self.clear_fields()
        messagebox.showinfo("Success", "Student added successfully!")

    def update_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to update")
            return
        
        if not self.validate_fields():
            return
        
        data = self.get_student_data() + (self.tree.item(selected)['values'][0],)
        self.c.execute('''UPDATE students SET 
                        name=?, age=?, grade=?, email=?, phone=?, course=?
                        WHERE id=?''', data)
        self.conn.commit()
        self.load_students()
        messagebox.showinfo("Success", "Student updated successfully!")

    def delete_student(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        student_id = self.tree.item(selected)['values'][0]
        if messagebox.askyesno("Confirm Delete", "Delete this student record?"):
            self.c.execute("DELETE FROM students WHERE id=?", (student_id,))
            self.conn.commit()
            self.load_students()
            self.clear_fields()

    def search_student(self, event=None):
        query = self.search_var.get()
        self.c.execute('''SELECT * FROM students WHERE 
                        name LIKE ? OR 
                        grade LIKE ? OR 
                        course LIKE ? OR 
                        email LIKE ?''', 
                     (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
        results = self.c.fetchall()
        
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        for student in results:
            self.tree.insert('', tk.END, values=student)

    def clear_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def clear_search(self):
        self.search_var.set("")
        self.load_students()

    def load_selected_student(self, event):
        selected = self.tree.selection()
        if selected:
            student_data = self.tree.item(selected)['values'][1:]  # Exclude ID
            for entry, value in zip(self.entries.values(), student_data):
                entry.delete(0, tk.END)
                entry.insert(0, value)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManager(root)
    root.mainloop()