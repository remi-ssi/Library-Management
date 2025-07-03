from datetime import datetime, timedelta
from tryDatabase import DatabaseSeeder
from PySide6.QtWidgets import QMessageBox

class BorrowBooks: 
    def __init__ (self, db_path="bjrsLib.db"): 
        # Initialize the database seeder
        self.db_path = db_path
        self.db_seeder = DatabaseSeeder(db_path)
        
    def fetch_books(self, librarian_id): #gets all books for the librarian 
        try:
            books=self.db_seeder.get_all_records(tableName="Book", id=librarian_id)
            return [book["BookTitle"] for book in books] #return list of book title
        except Exception as e:
            print(f"Error fetching books: {e}")
            
            QMessageBox.warning(None, "Error", "Failed to fetch books.")
            return [] #empty list if error
    
    #FETCH ONLY BORROWED TRANSACTIONS
    def fetch_transaction(self, librarian_id):
        try:
            #retrieve records from tables
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id) 
            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            members = self.db_seeder.get_all_records(tableName="Member", id=librarian_id)
            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)

            member_dict = {m["MemberID"]: f"{m['MemberLN']}, {m['MemberFN']} {m.get('MemberMI', '')} ".strip() for m in members}
            book_dict = {b["BookCode"]: b["BookTitle"] for b in books}

            formatted_transactions = []
            for trans in transactions:
                if trans.get("Status") != "Borrowed": #only process the transactions marked as borrowed
                    continue
                #find all details associated with the transaction
                trans_details = [d for d in details if d["TransactionID"] == trans["TransactionID"]]
                for detail in trans_details:
                    #formatting for UI
                    formatted_transactions.append({
                        "id": trans["TransactionID"],
                        "book_title": book_dict.get(detail["BookCode"], "Unknown Book"),
                        "borrower": member_dict.get(trans["MemberID"], "Unknown Member"),
                        "action": trans["Status"], #either borrowed or returned
                        "transaction_type": trans["TransactionType"],
                        "date": trans["BorrowedDate"], #borrowed date
                        #calculate due date (14 days before due)
                        "due_date": detail.get("DueDate", ""),
                        "returned_date": trans.get("ReturnedDate", ""), # returned date if available
                        "quantity": detail.get("Quantity", 1), #Defaults to 1 if not initialized
                        "remarks": trans.get("Remarks", "")
                    })
            return formatted_transactions # returns list of dict
        except Exception as e:
            print(f"Error fetching transaction data: {e}")
            QMessageBox.warning(None, "Error", "Failed to fetch transaction data.")
            return None
    
    #FETCH ALL TRANSACTIONS BORROWED AND RETURNED 
    def fetch_all_transactions(self, librarian_id):
        try:
            #similar to fetch_transactions but includes all status
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id)
            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            members = self.db_seeder.get_all_records(tableName="Member", id=librarian_id)
            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)

            #get member name, check if middle name exists
            member_dict = {m["MemberID"]: f"{m['MemberFN']} {m.get('MemberMi', '')} {m['MemberLN']}".strip() for m in members}
            book_dict = {b["BookCode"]: b["BookTitle"] for b in books} #fetch books with book code

            formatted_transactions = []
            for trans in transactions:
                # fetch all
                trans_details = [d for d in details if d["TransactionID"] == trans["TransactionID"] ]
                for detail in trans_details:
                    formatted_transactions.append({
                        "id": trans["TransactionID"],
                        "book_title": book_dict.get(detail["BookCode"], "Unknown Book"),
                        "borrower": member_dict.get(trans["MemberID"], "Unknown Member"),
                        "action": trans["Status"],
                        "transaction_type": trans["TransactionType"],
                        "date": trans["BorrowedDate"],
                        "due_date": detail.get("DueDate", ""),
                        "returned_date": trans.get("ReturnedDate", ""),
                        "quantity": detail.get("Quantity", 1),
                        "remarks": trans.get("Remarks", "")
                    })
            return formatted_transactions
        except Exception as e:
            print(f"Error fetching all transaction data: {e}")
            QMessageBox.warning(None, "Error", "Failed to fetch transaction data.")
            return []
        
    #UPDATE EXISTING TRANSACTION
    def update_transaction(self, transaction_id, borrower_name, books_data, borrow_date, due_date, status, librarian_id):
        try:
            #get the transaction using join
            transaction_data = self.db_seeder.get_transaction_with_details(librarian_id= librarian_id)
            
            #find the specific transaction. match the transaction id
            transaction = next((t for t in transaction_data if t["TransactionID"]== transaction_id), None)
            if not transaction: #if transaction id not found
                QMessageBox.warning(self, "Error", f"Transaction not found...")
                return False
            #get members from query
            members = {f"{t['MemberFN']} {t.get('MemberMI', '')} {t['MemberLN']}".strip(): t['MemberID'] for t in transaction_data}
            member_id = members.get(borrower_name)
            if not member_id:
                QMessageBox.warning(self, "Error", f"Member not found...")
                return False
            #get books from query
            books = {t['BookTitle']: {
                "BookCode": t['BookCode'],
                "BookAvailableCopies": t.get("BookAvailableCopies", 0)
            } for t in transaction_data}

            transaction_details = [t for t in transaction_data if t["TransactionID"] == transaction_id]

            for detail in transaction_details:
                self.db_seeder.update_table(
                    tableName = "Book",
                    updates = {"BookAvailableCopies ": detail["BookAvailableCopies"] + detail["Quantity"]},
                    column = "BookCode",
                    value = detail["BookCode"]
                )
            self.db_seeder.delete_table("TransactionDetails", "TransactionID", transaction_id)
            self.db_seeder.update_table(
                tableName = "BookTransaction",
                updates = {
                    "BorrowedDate": borrow_date.toString("yyyy-MM-dd") if isinstance (borrow_date, QDate) else borrow_date,
                    "Status": status,
                    "ReturnedDate": datetime.now().strftime("%Y-%m-%d") if status == "Returned" else None,
                    "MemberID": member_id
                },
                column = "TransactionID",
                value = transaction_id
            )
            for book_data in books_data:
                book_title = book_data["book"]
                quantity = book_data.get('quantity', 1)
                book = books.get(book_title)
                if not book or book["BookAvailableCopies"] < quantity:
                    QMessageBox.warning(None, "Error", f"Book not available of insufficient copies")
                    return False
                
                self.db_seeder.seed_data(tableName="TransactionDetails",
                            data = [{
                                "Quantity": quantity,
                                "TransactionID": transaction_id,
                                "BookCode" : book["BookCode"]
                            }],
                            columnOrder= ["Quantity", "TransactionID", "BookCode"]
                )

                if status == "Borrowed":
                    self.db_seeder.update_table(tableName = "Book",
                            updates = {"BookAvailableCopies" + book["BookAvailableCopies"] - quantity},
                            column = "BookCode",
                            value = book["BookCode"]
                    )
            return True
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete transaction")
            return False

        
    #CREATE NEW TRANSACTION
    def add_transaction(self, borrower_name, books_data, borrow_date, due_date, status, librarian_id, member_id=None):
        try: 
            #get memebr id from name
            members = self.db_seeder.get_all_records(tableName ="Member", id=librarian_id)
            member = next ((m for m in members if f"{m['MemberFN']} {m.get('MemberMI', '')} {m['MemberLN']}".strip().lower()== borrower_name.lower()), None)
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
                "BorrowedDate": borrow_date,
                "Status": status, 
                "ReturnedDate": None, #initially not returned
                "Remarks": None,
                "LibrarianID": librarian_id,
                "MemberID": member_id
            }]
            
            transaction_columns = [
                "TransactionType", "BorrowedDate", "Status", "ReturnedDate", "Remarks", "LibrarianID", "MemberID"
            ]
            #insert transaction
            self.db_seeder.seed_data(
                tableName="BookTransaction",
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
                book = book_dict(book_title)
                book_code = book["BookCode"]
                if not book or book["BookAvailableCopies"] < quantity:
                    QMessageBox.warning(None, "Error", f"Book '{book_title}' not available or insuficient copies")
                    return False
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
        
    
    #MARK BORROWED BOOK AS RETURNED
    def return_book(self, transaction_id, librarian_id, returned_date=None, remarks=None):
        try:
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id)
            transaction = next((t for t in transactions if t["TransactionID"] == transaction_id), None)
            if not transaction:
                QMessageBox.warning(None, "Error", f"Transaction #{transaction_id} not found or already deleted.")
                return False
            if transaction["Status"] != "Borrowed":
                QMessageBox.warning(None, "Error", f"Transaction #{transaction_id} is not in 'Borrowed' status.")
                return False

            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            trans_details = [d for d in details if d["TransactionID"] == transaction_id]
            if not trans_details:
                QMessageBox.warning(None, "Error", f"No valid transaction details found for Transaction #{transaction_id}.")
                return False

            returned_date = returned_date or datetime.now().strftime("%Y-%m-%d")
            updates = {
                "Status": "Returned",
                "ReturnedDate": returned_date
            }
            if remarks is not None:
                updates["Remarks"] = remarks

            self.db_seeder.update_table(
                tableName="BookTransaction",
                updates=updates,
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