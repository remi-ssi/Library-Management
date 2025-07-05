from datetime import datetime
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
            #retrieve these records from tables
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id) 
            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            members = self.db_seeder.get_all_records(tableName="Member", id=librarian_id)
            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)

            #create dict for mapping member id to formatted name
            member_dict = {m["MemberID"]: f"{m['MemberLN']}, {m['MemberFN']} {m.get('MemberMI', '')} ".strip() for m in members}
            #dictionary for mapping the bookcode to book title
            book_dict = {b["BookCode"]: b["BookTitle"] for b in books}

            formatted_transactions = [] #list to store formatted transactions
            for trans in transactions: #process each transactions
                if trans.get("Status") != "Borrowed": #only process the transactions marked as borrowed
                    continue
                #find all details associated with the transaction
                trans_details = [d for d in details if d["TransactionID"] == trans["TransactionID"]]
                for detail in trans_details:
                    #formatting for UI display and add result to list
                    formatted_transactions.append({
                        "id": trans["TransactionID"],
                        "book_title": book_dict.get(detail["BookCode"], "Unknown Book"), #book title or default
                        "borrower": member_dict.get(trans["MemberID"], "Unknown Member"), # member name or default
                        "action": trans["Status"], #either borrowed or returned
                        "date": trans["BorrowedDate"], #borrowed date
                        #due date (14 days before due). day 1 starts the day after borrow (tomorrow)
                        "due_date": detail.get("DueDate", ""),
                        "returned_date": trans.get("ReturnedDate", ""), # returned date if available
                        "quantity": detail.get("Quantity", 1), #Defaults to 1 if not initialized
                        "remarks": trans.get("Remarks", "")
                    })
            return formatted_transactions # returns formatted transaction. a list of dict
        except Exception as e: #handle occuring error during process
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

            #dictionary mapping member id to fromatted name (FN, MN, LN)
            #handles cases where middle name is null
            member_dict = {m["MemberID"]: f"{m['MemberFN']} {m.get('MemberMI', '')} {m['MemberLN']}".strip() for m in members}
            book_dict = {b["BookCode"]: b["BookTitle"] for b in books} #fetch books with book code

            formatted_transactions = [] # initialize list to store all formatted transaction data
            for trans in transactions: # process each transaction record
                # find all detail records associated with this transaction
                trans_details = [d for d in details if d["TransactionID"] == trans["TransactionID"] ]
                for detail in trans_details:
                    #create a formatted dictionary for each book in the transaction
                    formatted_transactions.append({
                        "id": trans["TransactionID"],
                        "book_title": book_dict.get(detail["BookCode"], "Unknown Book"), #book title with fallback
                        "borrower": member_dict.get(trans["MemberID"], "Unknown Member"), #member id with fal;back
                        "action": trans["Status"], #current status, either borrowed or returned
                        "date": trans["BorrowedDate"], #get original borrow date
                        "due_date": detail.get("DueDate", ""), #get the calculated due date, empty if not set
                        "returned_date": trans.get("ReturnedDate", ""), 
                        "quantity": detail.get("Quantity", 1), #get the borrowed quantity, defaults to 1
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
            #get the transaction using joined query
            transaction_data = self.db_seeder.get_transaction_with_details(librarian_id= librarian_id)
            
            #find the specific transaction. match the transaction id
            transaction = next((t for t in transaction_data if t["TransactionID"]== transaction_id), None)
            if not transaction: #if transaction id not found in databse
                QMessageBox.warning(self, "Error", f"Transaction not found...")
                return False
            #a dictionary mapping formatted member names to their member ids
            members = {f"{t['MemberFN']} {t.get('MemberMI', '')} {t['MemberLN']}".strip(): t['MemberID'] for t in transaction_data}
            member_id = members.get(borrower_name)
            if not member_id: #if member name foesnt exists 
                QMessageBox.warning(self, "Error", f"Member not found...")
                return False
            #a dictionary mapping book title to their book coded and available copies
            books = {t['BookTitle']: {
                "BookCode": t['BookCode'],
                "BookAvailableCopies": t.get("BookAvailableCopies", 0)
            } for t in transaction_data}
            #get all transaction details fro this specific transaction
            transaction_details = [t for t in transaction_data if t["TransactionID"] == transaction_id]
            #return all books from original transactoin to inventory
            for detail in transaction_details:
                self.db_seeder.update_table(
                    tableName = "Book",
                    updates = {"BookAvailableCopies ": detail["BookAvailableCopies"] + detail["Quantity"]},
                    column = "BookCode",
                    value = detail["BookCode"]
                )
                #jupdate the main transaction record with new information
            self.db_seeder.delete_table("TransactionDetails", "TransactionID", transaction_id)
            self.db_seeder.update_table(
                tableName = "BookTransaction",
                updates = {
                    "BorrowedDate": borrow_date.toString("yyyy-MM-dd") if isinstance (borrow_date) else borrow_date,
                    "Status": status,
                    "ReturnedDate": datetime.now().strftime("%Y-%m-%d") if status == "Returned" else None,
                    "MemberID": member_id
                },
                column = "TransactionID",
                value = transaction_id
            ) #process each book in the new transaction data
            for book_data in books_data:
                book_title = book_data["book"]
                quantity = book_data.get('quantity', 1) # default to 1 i quantity not speccified
                book = books.get(book_title) #verify book exists and has sufficient copies
                if not book or book["BookAvailableCopies"] < quantity:
                    QMessageBox.warning(None, "Error", f"Book not available of insufficient copies")
                    return False
                #create new transaction detail record for this book
                self.db_seeder.seed_data(tableName="TransactionDetails",
                            data = [{
                                "Quantity": quantity,
                                "TransactionID": transaction_id,
                                "BookCode" : book["BookCode"]
                            }],
                            columnOrder= ["Quantity", "TransactionID", "BookCode"]
                )
                #if borrowing, reduce available copies
                if status == "Borrowed":
                    self.db_seeder.update_table(tableName = "Book",
                            updates = {"BookAvailableCopies" + book["BookAvailableCopies"] - quantity},
                            column = "BookCode",
                            value = book["BookCode"]
                    )
            return True #success if all are completed
        except Exception as e: 
            QMessageBox.warning(self, "Error", f"Failed to delete transaction, {e}")
            return False #else rturn failure

        
    #CREATE NEW TRANSACTION
    def add_transaction(self, borrower_name, books_data, borrow_date, due_date, status, librarian_id, member_id=None):
        try: 
            #get memebr id from name
            members = self.db_seeder.get_all_records(tableName ="Member", id=librarian_id)
            #find member by matching formatted name
            member = next ((m for m in members if f"{m['MemberFN']} {m.get('MemberMI', '')} {m['MemberLN']}".strip().lower()== borrower_name.lower()), None)
            if not member:
                QMessageBox.warning(None, "Error", "Borrower not found.")
                return False
            member_id = member["MemberID"] #get the validate member id 
            #get all books to verify availability
            books = self.db_seeder.get_all_records(tableName = "Book", id=librarian_id)
            book_dict = {book["BookTitle"]:book for book in books}
            
            # prepare the transaction data  
            transaction_data = [{
                "BorrowedDate": borrow_date,
                "Status": status, 
                "ReturnedDate": None, #initially not returned
                "Remarks": None, # no remarks by default 
                "LibrarianID": librarian_id,
                "MemberID": member_id
            }]
            
            transaction_columns = [
                "BorrowedDate", "Status", "ReturnedDate", "Remarks", "LibrarianID", "MemberID"
            ]
            #insert transaction record
            self.db_seeder.seed_data(
                tableName="BookTransaction",
                data=transaction_data,
                columnOrder=transaction_columns
            )
            #get the transaction id
            transactions = self.db_seeder.get_all_records(tableName="Transaction", id=librarian_id)
            #retrieve all transactions to get the newly created id
            transaction_id = max(t["TransactionID"] for t in transactions) if transactions else None
            if not transaction_id:
                raise Exception("Failed to retrieve TransactionID after insertion.")
            
            #add transaction details and update book quantities
            for book_data in books_data:
                book_title = book_data["book"]
                quantity = book_data["quantity"]
                book = book_dict.get(book_title)
                book_code = book["BookCode"]
                #check book availability
                if not book or book["BookAvailableCopies"] < quantity: #check if available copies can cater the quantity being borrowed
                    #display message if avaible copies is not enough
                    QMessageBox.warning(None, "Error", f"Book '{book_title}' not available or insuficient copies") 
                    return False #if copies are insuddificient
                book_code = book["BookCode"]
                details_data = [{ #create transaction detail record 
                    "Quantity": quantity,
                    "TransactionID": transaction_id,
                    "BookCode": book_code,
                }]
                details_columns = ["Quantity", "TransactionID", "BookCode"]
                #update transaction detail
                self.db_seeder.seed_data ( # seed data to Transaction details table
                    tableName = "TransactionDetails",
                    data= details_data,
                    columnOrder= details_columns
                )
                self.db_seeder.update_table( #update book available copies
                    tableName="Book",
                    updates= {"BookAvailableCopies": book["BookAvailableCopies"] - quantity}, #for borrowing books, subtract the borrowed quantity from avaialable copies
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
            # get all transactions for the given librarian id
            transactions = self.db_seeder.get_all_records(tableName="BookTransaction", id=librarian_id)
            transaction = next((t for t in transactions if t["TransactionID"] == transaction_id), None)
            if not transaction: #check if transaction exists
                QMessageBox.warning(None, "Error", f"Transaction #{transaction_id} not found or already deleted.")
                return False
            if transaction["Status"] != "Borrowed": # check if the status of transaction is Borrowed 
                QMessageBox.warning(None, "Error", f"Transaction #{transaction_id} is not in 'Borrowed' status.")
                return False
            #get transaction details
            details = self.db_seeder.get_all_records(tableName="TransactionDetails", id=librarian_id)
            trans_details = [d for d in details if d["TransactionID"] == transaction_id]
            if not trans_details: #check if there are valid transaction details
                QMessageBox.warning(None, "Error", f"No valid transaction details found for Transaction #{transaction_id}.")
                return False
            #set return ate to current date if not providedd
            returned_date = returned_date or datetime.now().strftime("%Y-%m-%d")
            updates = { #prepare the updates for the transaction
                "Status": "Returned", #update dstatus to 'Returned'
                "ReturnedDate": returned_date #set return date
            }
            if remarks is not None: #add remarks if provided
                updates["Remarks"] = remarks

            self.db_seeder.update_table( #update the transaction record in the database
                tableName="BookTransaction",
                updates=updates,
                column="TransactionID",
                value=transaction_id
            )
            #get all books and create a dict for look up
            books = self.db_seeder.get_all_records(tableName="Book", id=librarian_id)
            book_dict = {b["BookCode"]: b for b in books}
            for detail in trans_details: #process each transaction detail
                book_code = detail["BookCode"]
                quantity = detail["Quantity"]
                book = book_dict.get(book_code)
                if not book: #find the book in the dictionary
                    raise Exception(f"Book with BookCode {book_code} not found.")
                self.db_seeder.update_table(
                    tableName="Book",
                    updates={"BookAvailableCopies": book["BookAvailableCopies"] + quantity}, #update the quantity of available copies. Add the borrowed quantity back
                    column="BookCode",
                    value=book_code
                )
            #show success messsge
            QMessageBox.information(None, "Success", f"Transaction #{transaction_id} marked as returned successfully.")
            return True
        except Exception as e: #handle any errors that occu during the process
            print(f"Error returning book for transaction #{transaction_id}: {e}")
            QMessageBox.warning(None, "Error", f"Failed to return book: {str(e)}")
            return False