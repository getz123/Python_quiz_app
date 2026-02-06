import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
import ttkbootstrap as ttk
import sqlite3

# Initialize database
def init_db():
    try:
        conn = sqlite3.connect("quiz_app.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            age INTEGER,
            country TEXT,
            city TEXT
        )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            score INTEGER NOT NULL
        )""")
        conn.commit()
        conn.close()
    except sqlite3.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# Register user
def register_user():
    def save_user():
        uname = reg_username.get()
        pword = reg_password.get()
        email = reg_email.get()
        phone = reg_phone.get()
        age = reg_age.get()
        country = reg_country.get()
        city = reg_city.get()

        if not uname or not pword or not email or not phone or not age or not country or not city:
            messagebox.showwarning("Input Error", "All fields are required")
            return

        try:
            conn = sqlite3.connect("quiz_app.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (username, password, email, phone, age, country, city)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (uname, pword, email, phone, age, country, city))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            reg_win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

    reg_win = tk.Toplevel()
    reg_win.title("Register")
    reg_win.geometry("600x500")
    reg_win.configure(bg="#333333")

    container = ttk.Frame(reg_win)
    container.place(relx=0.5, rely=0.5, anchor='center')

    ttk.Label(container, text="Register", font=('Arial', 16), bootstyle="info inverse").pack(pady=10)

    for label, var in [
        ("Username", "reg_username"),
        ("Password", "reg_password"),
        ("Email", "reg_email"),
        ("Phone", "reg_phone"),
        ("Age", "reg_age"),
        ("Country", "reg_country"),
        ("City", "reg_city")
    ]:
        ttk.Label(container, text=label, bootstyle="light").pack()
        entry = ttk.Entry(container, font=('Arial', 12), show='*' if label == "Password" else None)
        entry.pack(pady=5)
        globals()[var] = entry

    ttk.Button(container, text="Register", bootstyle="success", command=save_user).pack(pady=10)

score = 0
current_user = None
correct_answers = {
    1: "Python",
    2: "Guido van Rossum",
    3: "def",
    4: "list",
    5: "if"
}
selected_answers = {}
questions = {
    1: ("Which programming language is used for this app?", ["Java", "Python", "C++", "HTML"]),
    2: ("Who created Python?", ["Dennis Ritchie", "Guido van Rossum", "James Gosling", "Bjarne Stroustrup"]),
    3: ("Which keyword is used to define a function in Python?", ["fun", "define", "def", "func"]),
    4: ("Which of these is a mutable data type in Python?", ["tuple", "int", "list", "str"]),
    5: ("Which statement is used for decision making in Python?", ["switch", "if", "loop", "for"])
}

def check_login():
    global current_user
    uname = username_entry.get()
    pword = password_entry.get()

    if not uname or not pword:
        messagebox.showwarning("Input Error", "Username and password required")
        return

    conn = sqlite3.connect("quiz_app.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pword))
    result = cursor.fetchone()
    conn.close()

    if result:
        current_user = uname
        messagebox.showinfo("Login Success", f"Welcome {uname}!")
        root.destroy()
        show_question(1)
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")

def show_question(qid):
    if qid > len(questions):
        calculate_score()
        return

    question_win = tk.Toplevel()
    question_win.title(f"Question {qid}")
    question_win.geometry("600x500")
    question_win.configure(bg="#333333")

    container = ttk.Frame(question_win)
    container.place(relx=0.5, rely=0.5, anchor='center')

    question, options = questions[qid]
    ttk.Label(container, text=question, font=('Arial', 18, 'bold'), bootstyle="info inverse", wraplength=500, justify="center").pack(pady=20)

    var = tk.StringVar()
    for opt in options:
        ttk.Radiobutton(container, text=opt, variable=var, value=opt, bootstyle="secondary").pack(anchor='w', padx=40, pady=5)

    def next_question():
        selected_answers[qid] = var.get()
        if selected_answers[qid] == correct_answers[qid]:
            global score
            score += 1
        question_win.destroy()
        show_question(qid + 1)

    ttk.Button(container, text="Next", bootstyle="success", command=next_question).pack(pady=20)

def calculate_score():
    show_result()

def show_result():
    global current_user, score
    result_win = tk.Toplevel()
    result_win.title("Quiz Result")
    result_win.geometry('600x500')
    result_win.configure(bg="#222222")

    container = ttk.Frame(result_win)
    container.place(relx=0.5, rely=0.5, anchor='center')

    ttk.Label(container, text=f"Congratulations {current_user}!", font=('Arial', 20, 'bold'), bootstyle="info inverse").pack(pady=15)
    ttk.Label(container, text=f"Your Score: {score}/5", font=('Arial', 24), bootstyle="warning inverse").pack(pady=10)

    conn = sqlite3.connect("quiz_app.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (current_user, score))
    conn.commit()
    conn.close()

    ttk.Label(container, text="Thank you for participating!", font=('Arial', 16), bootstyle="success").pack(pady=15)
    ttk.Button(container, text="Exit", bootstyle="danger", command=result_win.destroy).pack(pady=10)

# Start app
init_db()
style = Style("darkly")
root = ttk.Window(themename="darkly")
root.title("QUIZ LOGIN")
root.geometry('600x500')

frame = ttk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor='center')

ttk.Label(frame, text="Username", font=('Arial', 12), bootstyle="light").grid(row=0, column=0, padx=10, pady=10)
username_entry = ttk.Entry(frame, font=('Arial', 12))
username_entry.grid(row=0, column=1, padx=10, pady=10)

ttk.Label(frame, text="Password", font=('Arial', 12), bootstyle="light").grid(row=1, column=0, padx=10, pady=10)
password_entry = ttk.Entry(frame, show='*', font=('Arial', 12))
password_entry.grid(row=1, column=1, padx=10, pady=10)

ttk.Button(frame, text="Login", bootstyle="primary", command=check_login).grid(row=2, column=1, pady=10)
ttk.Button(frame, text="Register", bootstyle="secondary", command=register_user).grid(row=3, column=1)

root.mainloop()
