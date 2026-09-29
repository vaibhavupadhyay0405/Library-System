"""
Smart Library Management System
--------------------------------
A CLI-based library management system built using Python standard-library
modules only.

Major modules:
1. Book Management
2. Member Management
3. Issue / Return Management
4. Reports & Analytics

Database: SQLite (created automatically as library.db)
"""

import sqlite3
from datetime import date, timedelta


DB_NAME = "library.db"


# ----------------------------- DATABASE -----------------------------

def get_connection():
    """Create and return a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def initialize_database():
    """Create all required database tables."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT NOT NULL,
                year INTEGER,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                available INTEGER NOT NULL CHECK(available >= 0)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL,
                due_date TEXT NOT NULL,
                return_date TEXT,
                status TEXT NOT NULL CHECK(status IN ('Issued', 'Returned')),
                FOREIGN KEY(book_id) REFERENCES books(book_id),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        """)


# ----------------------------- HELPERS -----------------------------

def print_line():
    print("-" * 72)


def pause():
    input("\nPress Enter to continue...")


def get_positive_int(prompt):
    while True:
        value = input(prompt).strip()
        try:
            value = int(value)
            if value > 0:
                return value
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")


def get_optional_year():
    while True:
        value = input("Publication year (optional): ").strip()
        if not value:
            return None
        try:
            year = int(value)
            if 0 < year <= date.today().year:
                return year
            print("Enter a valid year.")
        except ValueError:
            print("Enter a valid year.")


# --------------------------- BOOK MANAGEMENT ---------------------------

def add_book():
    print("\nADD BOOK")
    print_line()

    title = input("Title: ").strip()
    author = input("Author: ").strip()
    category = input("Category: ").strip()
    year = get_optional_year()
    quantity = get_positive_int("Quantity: ")

    if not title or not author or not category:
        print("Title, author and category are required.")
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO books (title, author, category, year, quantity, available)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, author, category, year, quantity, quantity))

    print("Book added successfully.")


def list_books():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT book_id, title, author, category, year, quantity, available
            FROM books
            ORDER BY title
        """)
        books = cursor.fetchall()

    print("\nALL BOOKS")
    print_line()

    if not books:
        print("No books found.")
        return

    print(f"{'ID':<5}{'Title':<25}{'Author':<20}{'Category':<15}{'Avail/Total':<12}")
    print_line()

    for book_id, title, author, category, year, quantity, available in books:
        title = title[:23]
        author = author[:18]
        category = category[:13]
        print(f"{book_id:<5}{title:<25}{author:<20}{category:<15}"
              f"{available}/{quantity:<12}")


def search_books():
    keyword = input("\nEnter title, author or category to search: ").strip()

    with get_connection() as conn:
        cursor = conn.cursor()
        pattern = f"%{keyword}%"
        cursor.execute("""
            SELECT book_id, title, author, category, year, available, quantity
            FROM books
            WHERE title LIKE ? OR author LIKE ? OR category LIKE ?
            ORDER BY title
        """, (pattern, pattern, pattern))
        books = cursor.fetchall()

    print("\nSEARCH RESULTS")
    print_line()

    if not books:
        print("No matching books found.")
        return

    for book_id, title, author, category, year, available, quantity in books:
        print(f"ID: {book_id}")
        print(f"Title: {title}")
        print(f"Author: {author}")
        print(f"Category: {category}")
        print(f"Year: {year if year else 'N/A'}")
        print(f"Availability: {available}/{quantity}")
        print_line()


def remove_book():
    list_books()
    book_id = get_positive_int("\nEnter Book ID to remove: ")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT available, quantity FROM books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()

        if not book:
            print("Book not found.")
            return

        available, quantity = book

        if available != quantity:
            print("Cannot remove a book while copies are currently issued.")
            return

        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

    print("Book removed successfully.")


# --------------------------- MEMBER MANAGEMENT ---------------------------

def add_member():
    print("\nREGISTER MEMBER")
    print_line()

    name = input("Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone (optional): ").strip()

    if not name or not email:
        print("Name and email are required.")
        return

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO members (name, email, phone)
                VALUES (?, ?, ?)
            """, (name, email, phone))
        print("Member registered successfully.")
    except sqlite3.IntegrityError:
        print("A member with this email already exists.")


def list_members():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT member_id, name, email, phone
            FROM members
            ORDER BY name
        """)
        members = cursor.fetchall()

    print("\nMEMBERS")
    print_line()

    if not members:
        print("No members found.")
        return

    for member_id, name, email, phone in members:
        print(f"ID: {member_id}")
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Phone: {phone or 'N/A'}")
        print_line()


# --------------------------- ISSUE / RETURN ---------------------------

def issue_book():
    print("\nISSUE BOOK")
    print_line()

    list_books()
    book_id = get_positive_int("\nBook ID: ")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title, available
            FROM books
            WHERE book_id = ?
        """, (book_id,))
        book = cursor.fetchone()

        if not book:
            print("Book not found.")
            return

        title, available = book

        if available <= 0:
            print("No available copies of this book.")
            return

        list_members()
        member_id = get_positive_int("\nMember ID: ")

        cursor.execute(
            "SELECT name FROM members WHERE member_id = ?",
            (member_id,)
        )
        member = cursor.fetchone()

        if not member:
            print("Member not found.")
            return

        # Prevent a member from borrowing the same book twice at once.
        cursor.execute("""
            SELECT loan_id
            FROM loans
            WHERE book_id = ? AND member_id = ? AND status = 'Issued'
        """, (book_id, member_id))

        if cursor.fetchone():
            print("This member already has an active loan for this book.")
            return

        issue_date = date.today()
        due_date = issue_date + timedelta(days=14)

        cursor.execute("""
            INSERT INTO loans
            (book_id, member_id, issue_date, due_date, return_date, status)
            VALUES (?, ?, ?, ?, NULL, 'Issued')
        """, (book_id, member_id, issue_date.isoformat(), due_date.isoformat()))

        cursor.execute("""
            UPDATE books
            SET available = available - 1
            WHERE book_id = ?
        """, (book_id,))

    print(f"'{title}' issued successfully.")
    print(f"Issue date: {issue_date}")
    print(f"Due date:   {due_date}")


def return_book():
    print("\nRETURN BOOK")
    print_line()

    view_active_loans()
    loan_id = get_positive_int("\nLoan ID to return: ")

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT book_id, due_date
            FROM loans
            WHERE loan_id = ? AND status = 'Issued'
        """, (loan_id,))

        loan = cursor.fetchone()

        if not loan:
            print("Active loan not found.")
            return

        book_id, due_date_text = loan
        return_date = date.today()
        due_date = date.fromisoformat(due_date_text)

        overdue_days = max((return_date - due_date).days, 0)
        fine = overdue_days * 5

        cursor.execute("""
            UPDATE loans
            SET return_date = ?, status = 'Returned'
            WHERE loan_id = ?
        """, (return_date.isoformat(), loan_id))

        cursor.execute("""
            UPDATE books
            SET available = available + 1
            WHERE book_id = ?
        """, (book_id,))

    print("Book returned successfully.")
    print(f"Return date: {return_date}")
    print(f"Overdue days: {overdue_days}")
    print(f"Fine: ₹{fine}")


def view_active_loans():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                loans.loan_id,
                books.title,
                members.name,
                loans.issue_date,
                loans.due_date
            FROM loans
            JOIN books ON loans.book_id = books.book_id
            JOIN members ON loans.member_id = members.member_id
            WHERE loans.status = 'Issued'
            ORDER BY loans.due_date
        """)
        loans = cursor.fetchall()

    print("\nACTIVE LOANS")
    print_line()

    if not loans:
        print("No active loans.")
        return

    for loan_id, title, member_name, issue_date, due_date in loans:
        overdue = date.today() > date.fromisoformat(due_date)
        status = "OVERDUE" if overdue else "On time"

        print(f"Loan ID: {loan_id}")
        print(f"Book: {title}")
        print(f"Member: {member_name}")
        print(f"Issued: {issue_date}")
        print(f"Due: {due_date}")
        print(f"Status: {status}")
        print_line()


# --------------------------- REPORTS / ANALYTICS ---------------------------

def dashboard():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantity), 0), COALESCE(SUM(available), 0) FROM books")
        book_count, total_copies, available_copies = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) FROM members")
        member_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM loans WHERE status = 'Issued'")
        active_loans = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM loans
            WHERE status = 'Issued' AND due_date < ?
        """, (date.today().isoformat(),))
        overdue_loans = cursor.fetchone()[0]

    print("\nLIBRARY DASHBOARD")
    print("=" * 72)
    print(f"Unique book titles : {book_count}")
    print(f"Total copies       : {total_copies}")
    print(f"Available copies   : {available_copies}")
    print(f"Registered members : {member_count}")
    print(f"Active loans       : {active_loans}")
    print(f"Overdue loans      : {overdue_loans}")
    print("=" * 72)


def borrowing_report():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT books.title, COUNT(loans.loan_id) AS borrow_count
            FROM loans
            JOIN books ON loans.book_id = books.book_id
            GROUP BY books.book_id
            ORDER BY borrow_count DESC, books.title
        """)

        results = cursor.fetchall()

    print("\nBORROWING REPORT")
    print_line()

    if not results:
        print("No borrowing history available.")
        return

    for title, count in results:
        print(f"{title:<50} {count} loan(s)")


def overdue_report():
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                loans.loan_id,
                books.title,
                members.name,
                loans.due_date
            FROM loans
            JOIN books ON loans.book_id = books.book_id
            JOIN members ON loans.member_id = members.member_id
            WHERE loans.status = 'Issued' AND loans.due_date < ?
            ORDER BY loans.due_date
        """, (date.today().isoformat(),))

        results = cursor.fetchall()

    print("\nOVERDUE REPORT")
    print_line()

    if not results:
        print("No overdue books.")
        return

    for loan_id, title, member, due_date in results:
        overdue_days = (date.today() - date.fromisoformat(due_date)).days
        fine = overdue_days * 5

        print(f"Loan ID: {loan_id}")
        print(f"Book: {title}")
        print(f"Member: {member}")
        print(f"Due date: {due_date}")
        print(f"Overdue by: {overdue_days} day(s)")
        print(f"Current fine: ₹{fine}")
        print_line()


# ----------------------------- MENUS -----------------------------

def book_menu():
    while True:
        print("\nBOOK MANAGEMENT")
        print_line()
        print("1. Add Book")
        print("2. List Books")
        print("3. Search Books")
        print("4. Remove Book")
        print("5. Back")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            add_book()
        elif choice == "2":
            list_books()
        elif choice == "3":
            search_books()
        elif choice == "4":
            remove_book()
        elif choice == "5":
            break
        else:
            print("Invalid option.")

        if choice != "5":
            pause()


def member_menu():
    while True:
        print("\nMEMBER MANAGEMENT")
        print_line()
        print("1. Register Member")
        print("2. List Members")
        print("3. Back")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            add_member()
        elif choice == "2":
            list_members()
        elif choice == "3":
            break
        else:
            print("Invalid option.")

        if choice != "3":
            pause()


def circulation_menu():
    while True:
        print("\nCIRCULATION MANAGEMENT")
        print_line()
        print("1. Issue Book")
        print("2. Return Book")
        print("3. View Active Loans")
        print("4. Back")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            issue_book()
        elif choice == "2":
            return_book()
        elif choice == "3":
            view_active_loans()
        elif choice == "4":
            break
        else:
            print("Invalid option.")

        if choice != "4":
            pause()


def reports_menu():
    while True:
        print("\nREPORTS & ANALYTICS")
        print_line()
        print("1. Dashboard")
        print("2. Borrowing Report")
        print("3. Overdue Report")
        print("4. Back")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            dashboard()
        elif choice == "2":
            borrowing_report()
        elif choice == "3":
            overdue_report()
        elif choice == "4":
            break
        else:
            print("Invalid option.")

        if choice != "4":
            pause()


def main():
    initialize_database()

    while True:
        print("\n" + "=" * 72)
        print("        SMART LIBRARY MANAGEMENT SYSTEM")
        print("=" * 72)
        print("1. Book Management")
        print("2. Member Management")
        print("3. Issue / Return Management")
        print("4. Reports & Analytics")
        print("5. Quick Dashboard")
        print("6. Exit")
        print("=" * 72)

        choice = input("Choose an option: ").strip()

        if choice == "1":
            book_menu()
        elif choice == "2":
            member_menu()
        elif choice == "3":
            circulation_menu()
        elif choice == "4":
            reports_menu()
        elif choice == "5":
            dashboard()
            pause()
        elif choice == "6":
            print("\nThank you for using Smart Library Management System!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
