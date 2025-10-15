import sqlite3
import os

class LibraryDBManager:
    """
    Manages all database interactions for the Library Management System.
    Uses SQLite3, which creates a file-based database.
    """

    def __init__(self, db_name="library.db"):
        """Initializes the database connection and creates the 'books' table."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_table()

    def _connect(self):
        """Establishes the connection to the SQLite database file."""
        try:
            # Check if the database file already exists
            db_exists = os.path.exists(self.db_name)
            
            # Connect to the database file
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            
            if not db_exists:
                print(f"Database '{self.db_name}' created successfully.")

        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def _create_table(self):
        """Creates the 'books' table if it doesn't already exist."""
        sql_create_table = """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available'
        );
        """
        try:
            self.cursor.execute(sql_create_table)
            self.conn.commit()
            print("[DB Ready] Table 'books' checked/created.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_book(self, title, author, isbn):
        """Inserts a new book record into the database."""
        sql_insert = "INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)"
        try:
            self.cursor.execute(sql_insert, (title, author, isbn))
            self.conn.commit()
            print(f"\n[SUCCESS] Book '{title}' added successfully.")
        except sqlite3.IntegrityError:
            # IntegrityError occurs if the ISBN already exists (UNIQUE constraint)
            print(f"\n[ERROR] A book with ISBN {isbn} already exists.")
        except sqlite3.Error as e:
            print(f"\n[ERROR] Error adding book: {e}")

    def view_all_books(self):
        """Fetches and returns all books in the database."""
        sql_select_all = "SELECT id, title, author, isbn, status FROM books ORDER BY title"
        try:
            self.cursor.execute(sql_select_all)
            # fetchall() retrieves all rows as a list of tuples
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"\n[ERROR] Error viewing books: {e}")
            return []

    # --- NEW METHOD: Search Book ---
    def search_book(self, search_term):
        """
        Searches for books where the title, author, or ISBN contains the search term.
        Search is case-insensitive (using LOWER()).
        """
        # The LIKE operator is used for pattern matching. 
        # The '%' wildcard matches any sequence of zero or more characters.
        sql_search = """
        SELECT id, title, author, isbn, status FROM books 
        WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR isbn LIKE ?
        ORDER BY title
        """
        # Prepare the search terms for the LIKE operator
        term = '%' + search_term.lower() + '%'
        
        try:
            # Pass the search term three times for the three placeholders (?, ?, ?)
            self.cursor.execute(sql_search, (term, term, term.replace('%', ''))) # ISBN is exact if no wildcard
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"\n[ERROR] Error searching books: {e}")
            return []
    # -----------------------------

    def update_book_status(self, book_id, new_status):
        """Updates the status of a specific book (e.g., 'Loaned' or 'Available')."""
        sql_update = "UPDATE books SET status = ? WHERE id = ?"
        try:
            self.cursor.execute(sql_update, (new_status, book_id))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print(f"\n[SUCCESS] Book ID {book_id} status updated to '{new_status}'.")
                return True
            else:
                print(f"\n[ERROR] Book ID {book_id} not found.")
                return False
        except sqlite3.Error as e:
            print(f"\n[ERROR] Error updating book status: {e}")
            return False

    def loan_book(self, book_id):
        """Loans a book if it is currently 'Available'."""
        # 1. Check current status
        self.cursor.execute("SELECT title, status FROM books WHERE id = ?", (book_id,))
        result = self.cursor.fetchone()
        
        if result is None:
            print(f"\n[FAILURE] Loan failed: Book ID {book_id} not found.")
            return

        title, current_status = result
        if current_status == 'Loaned':
            print(f"\n[FAILURE] '{title}' (ID {book_id}) is already loaned.")
        elif current_status == 'Available':
            self.update_book_status(book_id, 'Loaned')
        else:
            print("\n[ERROR] Invalid book status encountered.")


    def return_book(self, book_id):
        """Marks a book as 'Available' if it is currently 'Loaned'."""
        # 1. Check current status
        self.cursor.execute("SELECT title, status FROM books WHERE id = ?", (book_id,))
        result = self.cursor.fetchone()
        
        if result is None:
            print(f"\n[FAILURE] Return failed: Book ID {book_id} not found.")
            return

        title, current_status = result
        if current_status == 'Available':
            print(f"\n[FAILURE] '{title}' (ID {book_id}) is already available.")
        elif current_status == 'Loaned':
            self.update_book_status(book_id, 'Available')
        else:
            print("\n[ERROR] Invalid book status encountered.")


    def delete_book(self, book_id):
        """Deletes a book record by its ID."""
        sql_delete = "DELETE FROM books WHERE id = ?"
        try:
            self.cursor.execute(sql_delete, (book_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                print(f"\n[SUCCESS] Book ID {book_id} deleted successfully.")
            else:
                print(f"\n[ERROR] Book ID {book_id} not found.")
        except sqlite3.Error as e:
            print(f"\n[ERROR] Error deleting book: {e}")

    def __del__(self):
        """Ensures the connection is closed when the object is destroyed."""
        if self.conn:
            self.conn.close()

# --- Interactive CLI Functions ---

def display_menu():
    """Prints the main menu options."""
    print("\n" + "="*40)
    print("  📚 Library Management System 📚")
    print("="*40)
    print("1. Add New Book")
    print("2. View All Books")
    print("3. Loan Book (Change Status to Loaned)")
    print("4. Return Book (Change Status to Available)")
    print("5. Delete Book")
    print("6. Search Book") # NEW OPTION
    print("7. Exit")
    print("-" * 40)

def prompt_add_book(manager):
    """Prompts user for book details and adds it to the database."""
    print("\n--- Add New Book ---")
    title = input("Enter Title: ").strip()
    author = input("Enter Author: ").strip()
    isbn = input("Enter ISBN (Unique ID): ").strip()
    
    if title and author and isbn:
        manager.add_book(title, author, isbn)
    else:
        print("\n[ALERT] All fields are required. Book not added.")

def display_books_table(books, header_title="Current Inventory"):
    """
    Helper function to display a list of books (used by view_all and search).
    """
    print(f"\n--- {header_title} ---")
    if not books:
        print("[INFO] No books found matching the criteria.")
        return

    # Print Header
    print(f"{'ID':<4} | {'Title':<30} | {'Author':<20} | {'ISBN':<15} | {'Status':<10}")
    print("-" * 85)
    
    # Print Rows
    for book in books:
        book_id, title, author, isbn, status = book
        print(f"{book_id:<4} | {title:<30} | {author:<20} | {isbn:<15} | {status:<10}")
    print("-" * 85)

def prompt_view_books(manager):
    """Displays all books in a formatted table."""
    books = manager.view_all_books()
    display_books_table(books)

# --- NEW FUNCTION: Search Book Prompt ---
def prompt_search_book(manager):
    """Prompts user for a search term and displays matching books."""
    print("\n--- Search Book ---")
    search_term = input("Enter search term (Title, Author, or ISBN): ").strip()
    
    if search_term:
        books = manager.search_book(search_term)
        display_books_table(books, header_title=f"Search Results for '{search_term}'")
    else:
        print("\n[ALERT] Search term cannot be empty.")
# ----------------------------------------

def get_valid_book_id(prompt_message):
    """Helper function to safely get a book ID from the user."""
    while True:
        try:
            book_id_str = input(prompt_message).strip()
            if not book_id_str:
                 return None
            book_id = int(book_id_str)
            if book_id > 0:
                return book_id
            else:
                print("[ALERT] Book ID must be a positive number.")
        except ValueError:
            print("[ALERT] Invalid input. Please enter a valid numerical ID.")

def prompt_loan_book(manager):
    """Prompts for book ID and attempts to loan it."""
    print("\n--- Loan Book ---")
    book_id = get_valid_book_id("Enter the ID of the book to loan: ")
    if book_id is not None:
        manager.loan_book(book_id)

def prompt_return_book(manager):
    """Prompts for book ID and attempts to return it."""
    print("\n--- Return Book ---")
    book_id = get_valid_book_id("Enter the ID of the book to return: ")
    if book_id is not None:
        manager.return_book(book_id)

def prompt_delete_book(manager):
    """Prompts for book ID and attempts to delete it."""
    print("\n--- Delete Book ---")
    book_id = get_valid_book_id("Enter the ID of the book to delete: ")
    if book_id is not None:
        # Ask for confirmation (using print/input instead of alert/confirm)
        confirm = input(f"Are you sure you want to delete Book ID {book_id}? (yes/no): ").strip().lower()
        if confirm == 'yes':
            manager.delete_book(book_id)
        else:
            print("\n[INFO] Deletion cancelled.")


# --- Main Application Loop ---
def main():
    """Initializes the database manager and runs the main menu loop."""
    manager = LibraryDBManager()

    while True:
        display_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == '1':
            prompt_add_book(manager)
        elif choice == '2':
            prompt_view_books(manager)
        elif choice == '3':
            prompt_loan_book(manager)
        elif choice == '4':
            prompt_return_book(manager)
        elif choice == '5':
            prompt_delete_book(manager)
        elif choice == '6': # New handler for Search Book
            prompt_search_book(manager)
        elif choice == '7':
            print("\n[INFO] Exiting Library Management System. Goodbye!")
            # The __del__ method will ensure the connection is closed automatically
            break
        else:
            print("\n[ALERT] Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()
