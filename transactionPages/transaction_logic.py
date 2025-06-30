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
        except Exception as e:
            print(f"Error fetching books: {e}")
            QMessageBox.warning(None, "Error", "Failed to fetch books.")
            return []
    

    def fetch_transaction(self, librarian_id):
        try:
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id)
            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            members = self.db_seeder.get_all_records(tableName="Member", id=librarian_id)
            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)

            member_dict = {m["MemberID"]: f"{m['MemberLN']}, {m['MemberFN']}" for m in members}
            book_dict = {b["BookCode"]: b["BookTitle"] for b in books}

            formatted_transactions = []
            for trans in transactions:
                trans_details = [d for d in details if d["TransactionID"] == trans["TransactionID"]]
                for detail in trans_details:
                    formatted_transactions.append({
                        "id": trans["TransactionID"],
                        "book_title": book_dict.get(detail["BookCode"], "Unknown Book"),
                        "borrower": member_dict.get(trans["MemberID"], "Unknown Member"),
                        "action": trans["Status"],
                        "date": trans["TransactionDate"],
                        "due_date": (datetime.strptime(trans["TransactionDate"], "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d"),
                        "returned_date": trans.get("ReturnedDate", "") if trans["Status"]=="Returned" else ""
                    })
            return formatted_transactions
        except Exception as e:
            print(f"Error fetching transaction data: {e}")
            QMessageBox.warning(None, "Error", "Failed to fetch transaction data.")
            return None
    
    def fetch_all_transactions(self, librarian_id):
        try:
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id)
            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            members = self.db_seeder.get_all_records(tableName="Member", id=librarian_id)
            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)

            member_dict = {m["MemberID"]: f"{m['MemberLN']}, {m['MemberFN']}" for m in members}
            book_dict = {b["BookCode"]: b["BookTitle"] for b in books}

            formatted_transactions = []
            for trans in transactions:
                trans_details = [d for d in details if d["TransactionID"] == trans["TransactionID"] and d["isDeleted"] is None]
                for detail in trans_details:
                    formatted_transactions.append({
                        "id": trans["TransactionID"],
                        "book_title": book_dict.get(detail["BookCode"], "Unknown Book"),
                        "borrower": member_dict.get(trans["MemberID"], "Unknown Member"),
                        "action": trans["Status"],
                        "date": trans["TransactionDate"],
                        "due_date": (datetime.strptime(trans["TransactionDate"], "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d"),
                        "returned_date": trans.get("ReturnedDate", "") if trans["Status"] == "Returned" else "",
                        "quantity": detail.get("Quantity", 1)
                    })
            return formatted_transactions
        except Exception as e:
            print(f"Error fetching all transaction data: {e}")
            QMessageBox.warning(None, "Error", "Failed to fetch transaction data.")
            return []
        
    def update_transaction(self, transaction_id, borrower_name, books_data, borrow_date, due_date, status, librarian_id):
        try:
            members = self.db_seeder.get_all_records(tableName="Member", id=librarian_id)
            member = next((m for m in members if f"{m['MemberLN']}, {m['MemberFN']}" == borrower_name), None)
            if not member:
                QMessageBox.warning(None, "Error", "Borrower not found.")
                return False
            member_id = member["MemberID"]

            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id)
            transaction = next((t for t in transactions if t["TransactionID"] == transaction_id and t["isDeleted"] is None), None)
            if not transaction:
                QMessageBox.warning(None, "Error", f"Transaction #{transaction_id} not found.")
                return False

            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)
            book_dict = {book["BookTitle"]: book for book in books}

            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            trans_details = [d for d in details if d["TransactionID"] == transaction_id and d["isDeleted"] is None]
            for detail in trans_details:
                book = book_dict.get(detail["BookTitle"])
                if book:
                    self.db_seeder.update_table(
                        tableName="Book",
                        updates={"BookAvailableCopies": book["BookAvailableCopies"] + detail["Quantity"]},
                        column="BookCode",
                        value=detail["BookCode"]
                    )
            self.db_seeder.delete_table("TransactionDetails", "TransactionID", transaction_id)

            self.db_seeder.update_table(
                tableName="BookTransaction",
                updates={
                    "TransactionDate": borrow_date.toString("yyyy-MM-dd") if isinstance(borrow_date, QDate) else borrow_date,
                    "Status": status,
                    "ReturnedDate": datetime.now().strftime("%Y-%m-%d") if status == "Returned" else None,
                    "MemberID": member_id
                },
                column="TransactionID",
                value=transaction_id
            )

            for book_data in books_data:
                book_title = book_data["book"]
                quantity = book_data.get("quantity", 1)
                book = book_dict.get(book_title)
                if not book or book["BookAvailableCopies"] < quantity:
                    QMessageBox.warning(None, "Error", f"Book '{book_title}' not available or insufficient copies.")
                    return False
                book_code = book["BookCode"]
                details_data = [{
                    "Quantity": quantity,
                    "TransactionID": transaction_id,
                    "BookCode": book_code,
                }]
                details_columns = ["Quantity", "TransactionID", "BookCode"]
                self.db_seeder.seed_data(
                    tableName="TransactionDetails",
                    data=details_data,
                    columnOrder=details_columns
                )
                self.db_seeder.update_table(
                    tableName="Book",
                    updates={"BookAvailableCopies": book["BookAvailableCopies"] - quantity if status == "Borrowed" else book["BookAvailableCopies"]},
                    column="BookCode",
                    value=book["BookCode"]
                )
            return True
        except Exception as e:
            print(f"Error updating transaction: {e}")
            QMessageBox.warning(None, "Error", "Failed to update transaction.")
            return False

    def add_transaction(self, borrower_name, books_data, borrow_date, due_date, status, librarian_id, member_id=None):
        try: 
            #get memebr id from name
            members = self.db_seeder.get_all_records(tableName ="Member", id=librarian_id)
            member = next ((m for m in members if f"{m['MemberFN']} {m['MemberLN']}" == borrower_name), None)
            if not member:
                QMessageBox.warning(None, "Error", "Borrower not found.")
                return False
            member_id = member["MemberID"]
            #get all books to verify availability
            books = self.db_seeder.get_all_records(tableName = "Book", id=librarian_id)
            book_dict = {book["BookTitle"]:book for book in books}
            
            # create transaction 
            transaction_data = [{
                "TransactionType": "Borrow",
                "TransactionDate": borrow_date,
                "Status": status, 
                "Remarks": None,
                "LibrarianID": librarian_id,
                "MemberID": member_id
            }]
            
            transaction_columns = [
                "TransactionType", "TransactionDate", "Status", "Remarks", "LibrarianID", "MemberID"
            ]
            #insert transaction
            self.db_seeder.seed_data(
                tableName="Transaction",
                data=transaction_data,
                columnOrder=transaction_columns
            )
            #get the transaction id
            transactions = self.db_seeder.get_all_records(tableName="Transaction", id=librarian_id)
            transaction_id = max(t["TransactionID"] for t in transactions) if transactions else None
            if not transaction_id:
                raise Exception("Failed to retrieve TransactionID after insertion.")
            
            #add transaction details and update book quantities
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
                #update transaction detail
                self.db_seeder.seed_data (
                    tableName = "TransactionDetails",
                    data= details_data,
                    columnOrder= details_columns
                )
                self.db_seeder.update_table(
                    tableName="Book",
                    updates= {"BookAvailableCopies": book["BookAvailableCopies"] - quantity},
                    column="BookCode",
                    value=book["BookCode"]
                )
                return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            QMessageBox.warning(None, "Error", "Failed to add transaction.")
            return False
            
    def return_book (self, transaction_id, librarian_id, returned_date=None):
        try:
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id)
            transaction = next((t for t in transactions if t["TransactionID"] == transaction_id and t["isDeleted"] is None), None)
            if not transaction:
                QMessageBox.warning(None, "Error", f"Transaction #{transaction_id} not found or already deleted.")
                return False
            if transaction["Status"] != "Borrowed":
                QMessageBox.warning(None, "Error", f"Transaction #{transaction_id} is not in 'Borrowed' status.")
                return False

            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            trans_details = [d for d in details if d["TransactionID"] == transaction_id and d["isDeleted"] is None]
            if not trans_details:
                QMessageBox.warning(None, "Error", f"No valid transaction details found for Transaction #{transaction_id}.")
                return False

            returned_date = returned_date or datetime.now().strftime("%Y-%m-%d")
            self.db_seeder.update_table(
                tableName="BookTransaction",
                updates={
                    "Status": "Returned",
                    "TransacTionDate": returned_date
                },
                column="TransactionID",
                value=transaction_id
            )
            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)
            book_dict = {b["BookCode"]: b for b in books}
            for detail in trans_details:
                book_code = detail["BookCode"]
                quantity = detail["Quantity"]
                book = book_dict.get(book_code)
                if not book:
                    raise Exception(f"Book with BookCode {book_code} not found.")
                self.db_seeder.update_table(
                    tableName="Book",
                    updates={"BookAvailableCopies": book["BookAvailableCopies"] + quantity},
                    column="BookCode",
                    value=book_code
                )

            QMessageBox.information(None, "Success", f"Transaction #{transaction_id} marked as returned successfully.")
            return True
        except Exception as e:
            print(f"Error returning book for transaction #{transaction_id}: {e}")
            QMessageBox.warning(None, "Error", f"Failed to return book: {str(e)}")
            return False