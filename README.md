# Smart Library Management System

A **CLI-based Smart Library Management System** developed using **Python standard-library modules only**.

## Project Overview

The system helps a small library manage books, members, book circulation, and library analytics through a simple command-line interface.

The application uses **SQLite** for persistent data storage. The database is automatically created when the program is first executed.

## Major Functional Modules

### 1. Book Management
- Add books
- View all books
- Search books by title, author, or category
- Remove books
- Track total and available copies

### 2. Member Management
- Register library members
- View registered members
- Store member contact information

### 3. Circulation Management
- Issue books
- Return books
- Automatically calculate due dates
- Detect overdue books
- Calculate overdue fines
- Prevent the same member from borrowing the same book twice simultaneously

### 4. Reports & Analytics
- Library dashboard
- Total books and copies
- Available copies
- Registered members
- Active loans
- Overdue loans
- Borrowing history report
- Overdue report

## Technologies Used

Only Python's built-in standard library is used.

| Module | Purpose |
|---|---|
| `sqlite3` | Database and persistent storage |
| `datetime` | Issue dates, due dates and overdue calculations |
| `timedelta` | 14-day loan period |
| Python functions | Modular program structure |

**No external Python packages are required.**

## Requirements

- Python 3.8 or newer
- Visual Studio Code (recommended)
- Python extension for VS Code (optional but recommended)

## Project Structure

```text
smart_library_management/
│
├── main.py
├── README.md
└── library.db        # Automatically created after first run
```

## How to Run in VS Code

### Step 1 — Open the project

Open the `smart_library_management` folder in VS Code.

### Step 2 — Open the terminal

In VS Code:

```text
Terminal → New Terminal
```

### Step 3 — Run the program

Windows:

```bash
python main.py
```

If `python` does not work, try:

```bash
py main.py
```

Linux/macOS:

```bash
python3 main.py
```

## Database

The application automatically creates:

```text
library.db
```

The database contains three tables:

- `books`
- `members`
- `loans`

No manual database setup is required.

## Loan Rules

- Default loan period: **14 days**
- Overdue fine: **₹5 per overdue day**
- A book cannot be removed while one or more copies are issued.
- A member cannot have two active loans for the same book.

## Example Workflow

```text
Start Program
      ↓
Main Menu
      ↓
Register Member
      ↓
Add Book
      ↓
Issue Book
      ↓
View Active Loans
      ↓
Return Book
      ↓
View Reports
```

## Functional Requirements

1. The system shall allow the librarian to add and manage books.
2. The system shall allow the librarian to register members.
3. The system shall allow books to be issued and returned.
4. The system shall track book availability.
5. The system shall identify overdue books.
6. The system shall calculate overdue fines.
7. The system shall provide library statistics and reports.

## Non-Functional Requirements

### Usability
The application uses a menu-driven CLI so users can operate it without additional software.

### Reliability
Data is stored in SQLite, allowing records to persist between program executions.

### Maintainability
The program is divided into logical functions and modules such as book management, member management, circulation, and analytics.

### Error Handling
Invalid menu selections, invalid numbers, duplicate member emails, missing records, and invalid book operations are handled through validation messages.

### Resource Efficiency
The application uses SQLite and Python standard-library functionality without requiring external services.

## Testing

Test the following scenarios:

| Test | Expected Result |
|---|---|
| Add a valid book | Book is stored |
| Search for an existing book | Book appears in results |
| Register a member | Member is stored |
| Register duplicate email | Error message appears |
| Issue available book | Available count decreases |
| Issue unavailable book | Operation is rejected |
| Return active loan | Available count increases |
| Return invalid loan | Error message appears |
| View dashboard | Statistics are displayed |
| View overdue report | Overdue records are displayed |

## Future Enhancements

Possible future versions could include:

- Graphical user interface
- Barcode/QR code scanning
- Email reminders
- Fine payment tracking
- Advanced librarian authentication
- Book recommendation system
- Exporting reports to CSV
- Multi-user support

## Author

**Student Project — Python Essentials**

## License

This project is created for academic/educational purposes.
