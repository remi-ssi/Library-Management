from datetime import datetime, timedelta
from tryDatabase import DatabaseSeeder
from PySide6.QtWidgets import QMessageBox

class BorrowBooks:
    def __init__ (self, db_path="bjrsLib.db"):
        self.db_path = db_path
        self.db_seeder = DatabaseSeeder(db_path)
        
    def fetch_books(self, librarian_id):
        try:
            books=self.db_seeder.get_all_records(tableName="Book", id=librarian_id)
            return [book["BookTitle"] for book in books]
            if books:
                book_title = [book['title'] for book in books if 'title' in book]
        except Exception as e:
            print(f"Error fetching books: {e}")
            QMessageBox.warning(None, "Error", "Failed to fetch books.")
            return []

    def add_transaction(self, borrower_name, books_data, borrow_date, due_date, status, librarian_id, member_id=None):
        try: 
            members = self.db_seeder.get_all_records(tableName ="Member", id=librarian_id)
            member = next ((m for m in members if f"{m['MemberFN']} {m['MemberLN']}" == borrower_name), None)
            if not member:
                QMessageBox.warning(None, "Error", "Borrower not found.")
                return False
            member_id = member["MemberID"]

            books = self.db_seeder.get_all_records(tableName = "Book", id=librarian_id)
            book_dict = {book["BookTitle"]:book for book in books}
            for book_data in books_data:
                book_title = book_data["book"]
                quantity = book_data["quantity"]
                if book_title not in book_dict:
                    QMessageBox.warning(None, "Error", f"Book '{book_title}' not found.")
                    return False
                book = book_dict[book_title]
                if book["BookAvailableCopies"] < quantity:
                    QMessageBox.warning(None, "Error", f"Not enough copies of '{book_title}' available.")
                    return False
            transaction_data = [{
                "TransactionType": "Borrow",
                "TransactionDate": borrow_date,
                "Status": status, 
                "Remarks": None,
                "LibrarianID": librarian_id,
                "MemberID": member_id,
                "BookCode": None,
            }]
            transaction_columns = [
                "TransactionType", "TransactionDate", "Status", "Remarks", "LibrarianID", "MemberID", "BookCode"
            ]
            self.db_seeder.seed_data(
                tableName="Transaction",
                data=transaction_data,
                columnOrder=transaction_columns
            )
            transactions = self.db_seeder.get_all_records(tableName="Transaction", id=librarian_id)
            transaction_id = max(t["TransactionID"] for t in transactions) if transactions else None
            if not transaction_id:
                raise Exception("Failed to retrieve TransactionID after insertion.")
            
            for book_data in books_data:
                book_title = book_data["book"]
                quantity = book_data["quantity"]
                book = book_dict[book_title]
                book_code = book["BookCode"]
                details_data = [{
                    "Quantity": quantity,
                    "TransactionID": transaction_id,
                    "BookCode": book_code,
                }]
                details_columns = ["Quantity", "TransactionID", "BookCode"]

                self.db_seeder.seed_data (
                    tableName = "TransactionDetails",
                    data= details_data,
                    columnOrder= details_columns
                )
        except Exception as e:
            print(f"Error adding transaction: {e}")
            QMessageBox.warning(None, "Error", "Failed to add transaction.")
            return False
            