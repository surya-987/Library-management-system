import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

# ---------------- Database Setup ----------------
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    available INTEGER
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS issued_books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    book_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(book_id) REFERENCES books(id)
)""")

conn.commit()

# ---------------- Main Application ----------------
class LibraryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Library Management System")
        self.master.geometry("600x400")
        self.master.config(bg="#dfe6e9")

        self.login_screen()

    # ---------- Login Screen ----------
    def login_screen(self):
        self.clear()
        tk.Label(self.master, text="Library Management System",
                 font=("Arial", 20, "bold"), bg="#0984e3", fg="white").pack(fill="x")

        frame = tk.Frame(self.master, bg="#dfe6e9")
        frame.pack(pady=50)

        tk.Label(frame, text="Username:", font=("Arial", 12)).grid(row=0, column=0, pady=5)
        self.username_entry = tk.Entry(frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1)

        tk.Label(frame, text="Password:", font=("Arial", 12)).grid(row=1, column=0, pady=5)
        self.password_entry = tk.Entry(frame, font=("Arial", 12), show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(frame, text="Login", command=self.login, bg="#00b894", fg="white", width=15).grid(row=2, columnspan=2, pady=10)
        tk.Button(frame, text="Register", command=self.register, bg="#6c5ce7", fg="white", width=15).grid(row=3, columnspan=2, pady=5)

    # ---------- Clear Frame ----------
    def clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()

    # ---------- Login Function ----------
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            self.current_user = user
            if user[3] == "librarian":
                self.librarian_dashboard()
            else:
                self.user_dashboard()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    # ---------- Register Function ----------
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        role = simpledialog.askstring("Role", "Enter role (user/librarian):")

        try:
            cursor.execute("INSERT INTO users(username, password, role) VALUES(?,?,?)",
                           (username, password, role.lower()))
            conn.commit()
            messagebox.showinfo("Success", "Registration Successful!")
        except:
            messagebox.showerror("Error", "Username already exists")

    # ---------- User Dashboard ----------
    def user_dashboard(self):
        self.clear()
        tk.Label(self.master, text=f"Welcome {self.current_user[1]} (User)", font=("Arial", 16, "bold"),
                 bg="#00cec9", fg="white").pack(fill="x")

        tk.Button(self.master, text="View Books", command=self.view_books, width=25, bg="#0984e3", fg="white").pack(pady=10)
        tk.Button(self.master, text="Borrow Book", command=self.borrow_book, width=25, bg="#00b894", fg="white").pack(pady=10)
        tk.Button(self.master, text="Return Book", command=self.return_book, width=25, bg="#d63031", fg="white").pack(pady=10)
        tk.Button(self.master, text="Logout", command=self.login_screen, width=25, bg="#636e72", fg="white").pack(pady=10)

    # ---------- Librarian Dashboard ----------
    def librarian_dashboard(self):
        self.clear()
        tk.Label(self.master, text=f"Welcome {self.current_user[1]} (Librarian)", font=("Arial", 16, "bold"),
                 bg="#6c5ce7", fg="white").pack(fill="x")

        tk.Button(self.master, text="Add Book", command=self.add_book, width=25, bg="#00b894", fg="white").pack(pady=10)
        tk.Button(self.master, text="Remove Book", command=self.remove_book, width=25, bg="#d63031", fg="white").pack(pady=10)
        tk.Button(self.master, text="View Issued Books", command=self.view_issued_books, width=25, bg="#0984e3", fg="white").pack(pady=10)
        tk.Button(self.master, text="Logout", command=self.login_screen, width=25, bg="#636e72", fg="white").pack(pady=10)

    # ---------- View Books ----------
    def view_books(self):
        self.clear()
        tk.Label(self.master, text="Available Books", font=("Arial", 16, "bold"), bg="#00cec9", fg="white").pack(fill="x")

        tree = ttk.Treeview(self.master, columns=("ID", "Title", "Author", "Available"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Title", text="Title")
        tree.heading("Author", text="Author")
        tree.heading("Available", text="Available")
        tree.pack(fill="both", expand=True)

        cursor.execute("SELECT * FROM books")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

        tk.Button(self.master, text="Back", command=self.user_dashboard, bg="#636e72", fg="white").pack(pady=10)

    # ---------- Borrow Book ----------
    def borrow_book(self):
        book_id = simpledialog.askinteger("Borrow Book", "Enter Book ID to Borrow:")
        if not book_id:
            return

        cursor.execute("SELECT * FROM books WHERE id=? AND available>0", (book_id,))
        book = cursor.fetchone()

        if book:
            cursor.execute("INSERT INTO issued_books(user_id, book_id) VALUES(?,?)", (self.current_user[0], book_id))
            cursor.execute("UPDATE books SET available=available-1 WHERE id=?", (book_id,))
            conn.commit()
            messagebox.showinfo("Success", f"You borrowed '{book[1]}'")
        else:
            messagebox.showerror("Error", "Book not available")

    # ---------- Return Book ----------
    def return_book(self):
        book_id = simpledialog.askinteger("Return Book", "Enter Book ID to Return:")
        if not book_id:
            return

        cursor.execute("SELECT * FROM issued_books WHERE user_id=? AND book_id=?", (self.current_user[0], book_id))
        issue = cursor.fetchone()

        if issue:
            cursor.execute("DELETE FROM issued_books WHERE id=?", (issue[0],))
            cursor.execute("UPDATE books SET available=available+1 WHERE id=?", (book_id,))
            conn.commit()
            messagebox.showinfo("Success", "Book returned successfully")
        else:
            messagebox.showerror("Error", "You did not borrow this book")

    # ---------- Add Book ----------
    def add_book(self):
        title = simpledialog.askstring("Add Book", "Enter Book Title:")
        author = simpledialog.askstring("Add Book", "Enter Author Name:")

        if title and author:
            cursor.execute("INSERT INTO books(title, author, available) VALUES(?,?,?)", (title, author, 1))
            conn.commit()
            messagebox.showinfo("Success", "Book Added Successfully")

    # ---------- Remove Book ----------
    def remove_book(self):
        book_id = simpledialog.askinteger("Remove Book", "Enter Book ID to Remove:")
        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        messagebox.showinfo("Success", "Book Removed Successfully")

    # ---------- View Issued Books ----------
    def view_issued_books(self):
        self.clear()
        tk.Label(self.master, text="Issued Books", font=("Arial", 16, "bold"), bg="#6c5ce7", fg="white").pack(fill="x")

        tree = ttk.Treeview(self.master, columns=("User", "Book"), show="headings")
        tree.heading("User", text="User")
        tree.heading("Book", text="Book")
        tree.pack(fill="both", expand=True)

        cursor.execute("""SELECT users.username, books.title 
                          FROM issued_books 
                          JOIN users ON issued_books.user_id=users.id
                          JOIN books ON issued_books.book_id=books.id""")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

        tk.Button(self.master, text="Back", command=self.librarian_dashboard, bg="#636e72", fg="white").pack(pady=10)


# ---------------- Run App ----------------
root = tk.Tk()
app = LibraryApp(root)
root.mainloop()
