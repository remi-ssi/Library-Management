import os
import sqlite3
import bcrypt

class DatabaseSeeder:
    #initialize the path of the sqlite database
    def __init__(self, db_path='bjrsLib.db'):
        self.db_path = db_path

# This method returns a connection and cursor to the SQLite database.
    def get_connection_and_cursor(self):
        conn = sqlite3.connect(self.db_path)
        return conn, conn.cursor() 
    
  # This method returns the SQL query to create a table based on the table name provided.  
    def query(self, tableName):
        conn, cursor = self.get_connection_and_cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # ----Librarian Table----
        if tableName == "Librarian":
            return """CREATE TABLE IF NOT EXISTS Librarian (
                LibrarianID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                LibUsername VARCHAR(20) NOT NULL,
                FName VARCHAR(30) NOT NULL,
                LName VARCHAR(20) NOT NULL,
                MName VARCHAR(20), 
                LibPass BLOB NOT NULL
                )"""      

        # ----Member Table ------
        elif tableName == "Member":
            return """CREATE TABLE Member(
                    MemberID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    MemberLN VARCHAR(20) NOT NULL,
                    MemberMI VARCHAR(20),
                    MemberFN VARCHAR (20) NOT NULL,
                    MemberContact TEXT(11) NOT NULL,
                    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
                    isDeleted TIMESTAMP DEFAULT NULL,
                    LibrarianID INTEGER,
                    FOREIGN KEY (LibrarianID) REFERENCES Librarian (LibrarianID)
                    )"""
        elif tableName == "Book":
            book =  """CREATE TABLE Book(
                    BookCode INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    BookTitle VARCHAR NOT NULL,
                    Publisher VARCHAR NOT NULL,
                    BookDescription VARCHAR NOT NULL,
                    ISBN INTEGER NOT NULL,
                    BookTotalCopies INTEGER NOT NULL,
                    BookAvailableCopies INTEGER NOT NULL,
                    BookCover BLOB,
                    isDeleted TIMESTAMP DEFAULT NULL,
                    LibrarianID INTEGER, 
                    BookShelf VARCHAR(6),
                    FOREIGN KEY (LibrarianID) REFERENCES Librarian (LibrarianID),
                    FOREIGN KEY (BookShelf) REFERENCES BookShelf(ShelfId))"""
            Author = """CREATE TABLE BookAuthor(
                    BookCode INTEGER,
                    bookAuthor VARCHAR NOT NULL,
                    PRIMARY KEY (BookCode, bookAuthor),
                    FOREIGN KEY (BookCode) REFERENCES Book (BookCode))"""
            Genre = """CREATE TABLE Book_Genre(
                    BookCode INTEGER,
                    Genre VARCHAR,
                    PRIMARY KEY (BookCode, Genre), 
                    FOREIGN KEY (BookCode) REFERENCES Book (BookCode))"""
            Shelf = """CREATE TABLE BookShelf(
                    ShelfId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    ShelfName VARCHAR(6) NOT NULL,
                    LibrarianID INTEGER,
                    isDeleted TIMESTAMP DEFAULT NULL,
                    FOREIGN KEY (LibrarianID) REFERENCES Librarian (LibrarianID))"""
            return book, Author, Genre, Shelf
        # ----BookTransaction Table ------
        elif tableName == "BookTransaction":
            return """CREATE TABLE IF NOT EXISTS BookTransaction(
                    TransactionID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    BorrowedDate TIMESTAMP NOT NULL,
                    ReturnedDate TIMESTAMP DEFAULT NULL,
                    Status VARCHAR(20) NOT NULL,
                    Remarks VARCHAR(100) DEFAULT NULL,
                    LibrarianID INTEGER,
                    MemberID INTEGER,
                    FOREIGN KEY (LibrarianID) REFERENCES Librarian (LibrarianID),
                    FOREIGN KEY (MemberID) REFERENCES Member (MemberID))"""
        elif tableName == "TransactionDetails":
            return """CREATE TABLE IF NOT EXISTS TransactionDetails (
                    DetailsID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    Quantity INTEGER NOT NULL,
                    DueDate TIMESTAMP NOT NULL,
                    TransactionID INTEGER,
                    BookCode INTEGER,
                    FOREIGN KEY (TransactionID) REFERENCES BookTransaction (TransactionID),
                    FOREIGN KEY (BookCode) REFERENCES Book (BookCode))"""
        else:
            return

    #create a table if it doest exists in the database
    def create_table(self, tableName):
        conn, cursor = self.get_connection_and_cursor()
        conn.execute("PRAGMA foreign_keys = ON;")

        try:
            if tableName == "Book":
                bookCreate, authorCreate, genreCreate, shelfCreate = self.query(tableName)
                cursor.execute(bookCreate)
                cursor.execute(authorCreate)
                cursor.execute(genreCreate)
                cursor.execute(shelfCreate)
                conn.commit()
                print("Book table created")
            else:
                create = self.query(tableName)
                cursor.execute(create)
                conn.commit()
                print("Table created")
                return True
        except Exception as e: 
            print(f"Error creating table: {e}")
            return False
        finally:
            conn.close()

    #insert the data into the database
    def seed_data(self, tableName, data, columnOrder, hashPass=None):
        conn, cursor = self.get_connection_and_cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            last_id = None
            for i in data:
                values = []
                for col in columnOrder:
                    value = i[col]
                    if col == hashPass:
                        value = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                    values.append(value)
                placeholders = ', '.join(['?'] * len(columnOrder))
                columns = ', '.join(columnOrder)

                cursor.execute(f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders})", values)
                if tableName == "BookTransaction":
                    last_id = cursor.lastrowid  # Capture the TransactionID
                # If seeding BookTransaction with BookCode, add to TransactionDetails
                if tableName == "BookTransaction" and "BookCode" in i:
                    book_code = i["BookCode"]
                    transaction_id = cursor.lastrowid
                    due_date = i.get("DueDate", "")
                    quantity = i.get("Quantity", 1)
                    cursor.execute(
                        "INSERT INTO TransactionDetails (Quantity, DueDate, TransactionID, BookCode) VALUES (?, ?, ?, ?)",
                        (quantity, due_date, transaction_id, book_code)
                    )
            conn.commit()
            print(f"✓ Seeded {len(data)} rows into {tableName}")
            return last_id if tableName == "BookTransaction" else True
        except Exception as e:
            print(f"Error seeding data into {tableName}: {e}")
            return None
        finally:
            conn.close()

    #get borrowed transaction from joined tables
    def get_borrowed_transactions(self, librarian_id):
        try:
            conn, cursor = self.get_connection_and_cursor()
            query = """
                SELECT t.TransactionID, t.BorrowedDate, t.Status, t.ReturnedDate, t.Remarks,
                       m.MemberID, m.MemberFN || ' ' || m.MemberLN AS borrower,
                       b.BookCode, b.BookTitle, td.Quantity, td.DueDate
                FROM BookTransaction t
                JOIN TransactionDetails td ON t.TransactionID = td.TransactionID
                JOIN Member m ON t.MemberID = m.MemberID
                JOIN Book b ON td.BookCode = b.BookCode
                WHERE t.Status = 'Borrowed'
                AND b.isDeleted IS NULL
                AND m.isDeleted IS NULL
                AND t.LibrarianID = ?
                ORDER BY t.BorrowedDate DESC
            """
            cursor.execute(query, (librarian_id,))
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in rows]
            return records
        except Exception as e:
            print(f"✗ Error fetching borrowed transactions: {e}")
            return []
        finally:
            conn.close()

    #RETRIEVE TRANSCTION RECORDS WITH ALL RELATED DETAILS  
    def get_transaction_with_details(self, member_id=None, librarian_id=None):
        try:
            #get database connection and curosr
            conn, cursor = self.get_connection_and_cursor()
            #query joining all related table
            query = """
                SELECT t.TransactionID, t.BorrowedDate, t.Status, t.ReturnedDate, t.Remarks,
                    m.MemberID, m.MemberFN || ' ' || m.MemberLN AS borrower,
                    b.BookCode, b.BookTitle, td.Quantity, td.DueDate
                FROM BookTransaction AS t
                JOIN TransactionDetails td ON t.TransactionID = td.TransactionID
                JOIN Member m ON t.MemberID = m.MemberID
                JOIN Book b ON td.BookCode = b.BookCode
                AND b.isDeleted IS NULL
                AND m.isDeleted IS NULL
            """
            parameters = [] #parameters can etiher be member or librarian for conditional filtering
            if member_id: #add member filter if specified
                query += " AND t.MemberID = ?"
                parameters.append(member_id)
            if librarian_id: #add librarian filter if specified
                query += " AND t.LibrarianID = ?"
                parameters.append(librarian_id) 
            query += " ORDER BY t.BorrowedDate DESC" #sort by most recenet transaction first
            cursor.execute(query, parameters)  #execute query with parameters
            rows = cursor.fetchall() #get all results in tuple and convert to dict format
            columns = [desc[0] for desc in cursor.description] #get corresponding column
            records = [dict(zip(columns, row)) for row in rows] #map the rows to columns then convert to dict
            return records
        except Exception as e:
            print(f"✗ Error fetching transactions with details: {e}")
            return [] #return empty list if error
        finally:
            conn.close()
    
    
    #to get all the records/rows inside the certain table
    def get_all_records(self, tableName, id):
        conn, cursor = self.get_connection_and_cursor()
        try:
            if tableName == "Librarian":
                cursor.execute(f"SELECT * FROM {tableName}")
            elif tableName in ["BookAuthor", "Book_Genre", "BookShelf"]:
                if tableName == "BookAuthor":
                    query = """SELECT BA.* FROM BookAuthor AS BA 
                            JOIN Book AS BK ON BA.BookCode = BK.BookCode
                            WHERE BK.isDeleted IS NULL AND BK.LibrarianID = ?"""
                elif tableName == "BookShelf":
                    query = """SELECT * FROM BookShelf WHERE isDeleted IS NULL AND LibrarianID = ? ORDER BY ShelfId"""
                else:  # Book_Genre
                    query = """SELECT BG.* FROM Book_Genre AS BG
                            JOIN Book AS BK ON BG.BookCode = BK.BookCode
                            WHERE BK.isDeleted IS NULL AND BK.LibrarianID = ?"""
                cursor.execute(query, (id,))
            elif tableName == "TransactionDetails":
                #for TransactionDetails table, joined with BookTransaction table
                query = """
                    SELECT td.* 
                    FROM TransactionDetails AS td
                    JOIN BookTransaction bt ON td.TransactionID = bt.TransactionID
                    WHERE bt.LibrarianID = ?
                """
                cursor.execute(query, (id,))
            elif tableName == "BookTransaction":
                #for BookTransaction tabele sorted by ID
                query = f"SELECT * FROM {tableName} WHERE LibrarianID = ? ORDER BY TransactionID DESC"
                cursor.execute(query, (id,))
            else:  # Member and Book tables
                query = f"SELECT * FROM {tableName} WHERE isDeleted IS NULL AND LibrarianID = ?"
                cursor.execute(query, (id,))
            #convert results to list of dictionaries
            rows = cursor.fetchall() 
            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in rows]
            return records
        except Exception as e:
            print(f"✗ Error fetching records from {tableName}: {e}")
            return []
        finally:
            conn.close()

    #update the row of a specific table
    def update_table(self, tableName, updates: dict, column, value):
        conn, cursor = self.get_connection_and_cursor()
        try:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON;")
            
            set_clause = ', '.join([f"{col} = ?" for col in updates])
            values = list(updates.values()) + [value]
            #update statement
            query = f"UPDATE {tableName} SET {set_clause} WHERE {column} = ?"
            
            print(f"🔄 Executing update query: {query}")
            print(f"   Values: {values}")
            
            cursor.execute(query, values)
            rows_affected = cursor.rowcount
            conn.commit()
            
            if rows_affected > 0:
                print(f"✓ Row in '{tableName}' where {column} = {value} updated successfully. ({rows_affected} row(s) affected)")
                return True
            else:
                print(f"⚠️ No rows were updated in '{tableName}' where {column} = {value}")
                return False
                
        except Exception as e:
            print(f"✗ Error updating row in '{tableName}': {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    #delete a record/row in a specific table
    def delete_table(self, tableName, column, value, librarian_id=None):
        try:
            conn, cursor = self.get_connection_and_cursor()
            cursor = conn.cursor()

            if tableName == "BookTransaction": # hard deleting transaction records
                #get transactiondetails to restore book quantities
                cursor.execute("SELECT BookCode, Quantity FROM TransactionDetails WHERE TransactionID = ?", (value, ))
                details = cursor.fetchall()
                #restore book quantities
                for book_code, quantity in details:
                    cursor.execute("UPDATE Book SET BookAvailableCopies = BookAvailableCopies + ? WHERE BookCode = ?", (quantity, book_code))
                #delete related TransactionDetailss
                cursor.execute("DELETE FROM TransactionDetails WHERE TransactionID = ? ", (value,))
                #delete the BookTransaction record
                cursor.execute(f"DELETE FROM BookTransaction WHERE {column} = ?", (value,))
                conn.commit()
                print(f"Successfully deleted from {tableName} and TransactionDetails WHERE {column} ={value}")
                return True
            
            elif tableName == "BookShelf": # for bookshelves, we soft delete the shelf
                # Soft delete the shelf using ShelfId
                query = f"UPDATE {tableName} SET isDeleted = CURRENT_TIMESTAMP WHERE {column} = ? AND LibrarianID = ?"
                cursor.execute(query, (value, librarian_id)) 
                
                # Update books to remove shelf reference using ShelfId
                updateBook = "UPDATE Book SET BookShelf = NULL WHERE BookShelf = ? AND LibrarianID = ?"
                cursor.execute(updateBook, (value, librarian_id))
                
                conn.commit()
                print(f"✓ Soft deleted shelf from {tableName} where {column} = {value}")
                print(f"✓ Updated books to set BookShelf = NULL for ShelfId {value} and librarian {librarian_id}")
                return True
            
            else: # for books and other tables
                query = f"UPDATE {tableName} SET isDeleted = CURRENT_TIMESTAMP WHERE {column} = ?"
                cursor.execute(query, (value,))
                conn.commit()
                print(f"✓ Deleted from {tableName} where {column} = {value}")

        except Exception as e:
            print(f"✗ Error deleting from {tableName}: {e}")
            conn.rollback()
            raise e  # Re-raise the exception so the UI can handle it
        finally:
            conn.close()

    # Verify librarian login credentials
    # This method checks if the provided username and password match the stored credentials in the database.
    def verify_librarian_login(self, username, password):
        conn, cursor = self.get_connection_and_cursor()
        try:
            cursor.execute("SELECT LibPass FROM Librarian WHERE LibUsername = ?", (username,))
            result = cursor.fetchone()

            if result:
                stored_hashed_password = result[0]

                if isinstance(stored_hashed_password, str):
                    # If it was stored as TEXT, convert to bytes
                    stored_hashed_password = stored_hashed_password.encode('utf-8')

                return bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password)
            else:
                return False
        except Exception as e:
            print(f"✗ Error during librarian login verification: {e}")
            return False
        finally:
            conn.close()

    # Find if a librarian username exists in the database. This ensures that the username is unique for each librarian.
    # This method returns True if the username exists, otherwise False.
    def findUsername(self, username):
        conn, cursor = self.get_connection_and_cursor()
        try:
            query = "SELECT COUNT (*) FROM Librarian WHERE LibUsername = ?"
            result = cursor.execute(query, (username,)).fetchone()
            return result[0] > 0
        except Exception as e:
            print(f"✗ Error finding username: {e}")
            return False
        finally:
            conn.close()

    # Find if a member contact exists in the database. This ensures that the contact number is unique for each member.
    # This method returns True if the contact exists, otherwise False.
    def findMemberContact(self, contact):
        conn, cursor = self.get_connection_and_cursor()
        try:
            query = "SELECT COUNT (*) FROM Member WHERE MemberContact = ?"
            result = cursor.execute(query, (contact,)).fetchone()
            return result[0] > 0
        except Exception as e:
            print(f"Error finding member contact: {e}")
            return False
        finally:
            conn.close()
    
    # Filter books based on shelf number or sort order
    def filterBooks(self, filter, librarian_id=None):
        conn, cursor = self.get_connection_and_cursor()
        try:
            if filter == "ascendingTitle":  # sort by ascending order
                query = "SELECT * FROM Book WHERE isDeleted IS NULL AND LibrarianID = ? ORDER BY BookTitle ASC"
                cursor.execute(query, (librarian_id,))
            elif filter == "descendingTitle":  # sort by descending order
                query = "SELECT * FROM Book WHERE isDeleted IS NULL AND LibrarianID = ? ORDER BY BookTitle DESC"
                cursor.execute(query, (librarian_id,))
            elif filter == "ascendingAuthor":  # sort by ascending order of author
                # For author sorting, we need to join with BookAuthor table
                query = """SELECT DISTINCT b.* FROM Book b 
                           LEFT JOIN BookAuthor ba ON b.BookCode = ba.BookCode 
                           WHERE b.isDeleted IS NULL AND b.LibrarianID = ? 
                           ORDER BY ba.bookAuthor ASC"""
                cursor.execute(query, (librarian_id,))
            elif filter == "descendingAuthor":  # sort by descending order of author
                # For author sorting, we need to join with BookAuthor table
                query = """SELECT DISTINCT b.* FROM Book b 
                           LEFT JOIN BookAuthor ba ON b.BookCode = ba.BookCode 
                           WHERE b.isDeleted IS NULL AND b.LibrarianID = ? 
                           ORDER BY ba.bookAuthor DESC"""
                cursor.execute(query, (librarian_id,))
            elif filter == "mostCopies":  # sort by most copies
                query = "SELECT * FROM Book WHERE isDeleted IS NULL AND LibrarianID = ? ORDER BY BookTotalCopies DESC"
                cursor.execute(query, (librarian_id,))
            elif filter == "leastCopies":  # sort by least copies
                query = "SELECT * FROM Book WHERE isDeleted IS NULL AND LibrarianID = ? ORDER BY BookTotalCopies ASC"
                cursor.execute(query, (librarian_id,))
            else:  # assume filter is a shelf number or "No Shelf"
                if filter == "No Shelf":
                    query = "SELECT * FROM Book WHERE BookShelf IS NULL AND isDeleted IS NULL AND LibrarianID = ?"
                    cursor.execute(query, (librarian_id,))
                else:
                    # Convert shelf name to ShelfId for filtering
                    try:
                        shelf_query = "SELECT ShelfId FROM BookShelf WHERE ShelfName = ? AND LibrarianID = ? AND isDeleted IS NULL"
                        cursor.execute(shelf_query, (filter, librarian_id))
                        shelf_result = cursor.fetchone()
                        if shelf_result:
                            shelf_id = shelf_result[0]
                            query = "SELECT * FROM Book WHERE BookShelf = ? AND isDeleted IS NULL AND LibrarianID = ?"
                            cursor.execute(query, (shelf_id, librarian_id))
                        else:
                            # Shelf not found, return empty result
                            return []
                    except Exception as e:
                        print(f"Error finding ShelfId for shelf '{filter}': {e}")
                        return []

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in rows]
            return records

        except Exception as e:
            print(f"✗ Error in filterBooks: {e}")
            return []
        finally:
            conn.close()

    # Change the password of a librarian
    def changePassword(self, username, new_password):
        conn, cursor = self.get_connection_and_cursor()
        try:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE Librarian SET LibPass = ? WHERE LibUsername = ?", (hashed_password, username))
            conn.commit()
            if cursor.rowcount > 0:
                print(f" Password for {username} updated successfully.")
                return True
            else:
                print(f" No rows updated for {username}. Username may not exist.")
                return False
        except Exception as e:
            print(f" Error changing password for {username}: {e}")
            return False
        finally:
            conn.close()


     #Ito inadd ko rems hehe 
    
    def verify_current_password(self, email, current_password):
        import sqlite3
        import bcrypt
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT LibPass FROM Librarian WHERE LibUsername = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            stored_hash = row[0]
            # Make sure stored_hash is bytes
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            return bcrypt.checkpw(current_password.encode("utf-8"), stored_hash)
        return False

    
    def archiveTable(self, tableName, id):
        conn, cursor = self.get_connection_and_cursor()
        try:
            if tableName == "Book":
                bookquery = """SELECT * FROM Book WHERE Book.isDeleted IS NOT NULL AND Book.LibrarianID = ? ORDER BY Book.isDeleted DESC"""
                cursor.execute(bookquery, (id,))
            elif tableName == "BookAuthor":
                query = """SELECT BA.* FROM BookAuthor AS BA 
                        JOIN Book AS BK ON BA.BookCode = BK.BookCode
                        where BK.isDeleted IS NOT NULL AND BK.LibrarianID = ?"""
                cursor.execute(query, (id,))
            elif tableName == "Book_Genre":
                query = """SELECT BG.* FROM Book_Genre AS BG 
                        JOIN Book AS BK ON BG.BookCode = BK.BookCode
                        WHERE BK.isDeleted IS NOT NULL AND BK.LibrarianID = ?"""
                cursor.execute(query, (id,))

            elif tableName == "Member":
                query = """SELECT * FROM Member WHERE isDeleted IS NOT NULL AND LibrarianID = ? ORDER BY isDeleted DESC"""
                cursor.execute(query, (id,))

            else:
                query = """SELECT * FROM BookShelf WHERE isDeleted IS NOT NULL AND LibrarianID = ? ORDER BY isDeleted DESC"""
                cursor.execute(query, (id,))

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in rows]
            
            print(f"✓ Retrieved {len(records)} archived records from {tableName}")
            return records

        except Exception as e:
            print(f"✗ Error fetching archived records from {tableName}: {e}")
            return []
        finally:
            conn.close()

    def restoreArchive(self, tableName, PKColumn, Librarianid):
        conn, cursor = self.get_connection_and_cursor()
        try:
            if tableName == "Book":
                query = "UPDATE Book SET isDeleted = NULL WHERE BookCode = ? and LibrarianID = ?"
                cursor.execute(query, (PKColumn, Librarianid))
                print(f"✓ Restored Book with BookCode {PKColumn}")
            elif tableName == "Member":
                query = "UPDATE Member SET isDeleted = NULL WHERE MemberID = ? and LibrarianID = ?"
                cursor.execute(query, (PKColumn, Librarianid))
                print(f"✓ Restored Member with MemberID {PKColumn}")
            elif tableName == "BookShelf":
                query = "UPDATE BookShelf SET isDeleted = NULL WHERE ShelfId = ? and LibrarianID = ?"
                cursor.execute(query, (PKColumn, Librarianid))
                print(f"✓ Restored BookShelf with ShelfId {PKColumn}")
            
            conn.commit()
            return True
        except Exception as e:
            print(f"✗ Error restoring archive from {tableName}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def handleDuplication(self, tableName, librarianID, column, value):
        conn, cursor = self.get_connection_and_cursor()
        try:
            query = f"SELECT {column} FROM {tableName} WHERE LibrarianID = ?"
            cursor.execute(query, (librarianID,))
            results = cursor.fetchall()
            
            # Check all results for the specific value
            for item in results:
                db_value = item[0]
                # Handle type mismatches - compare both as strings and as original types
                if db_value == value or str(db_value) == str(value):
                    print(f"Duplicate found in {tableName} for {column} = {value} (matched with {db_value})")
                    return False  # Return False when duplicate is found (duplication handling failed)
            
            # If we've checked all items and found no duplicate
            print(f"No duplicate found in {tableName} for {column} = {value} - safe to proceed")
            return True  # Return True when no duplicate is found (safe to proceed)
            
        except Exception as e:
            print(f"✗ Error checking duplication in {tableName}: {e}")
            return False  # Return False on error (assume duplication to be safe)
        finally:
            conn.close()

    #GET COUNT STATS FOR DASHBOARD DISPLAY BASED ON TABLE NAME
    def dashboardCount (self, tableName, id):
        #get databse connecttion and curosr
        conn, cursor = self.get_connection_and_cursor()
        try:
            #create table after log in entry
            self.create_table("Book")
            self.create_table("Member")
            self.create_table("BookTransaction")
            self.create_table("BookShelf")
            self.create_table("BookAuthor")
            self.create_table("Book_Genre")
            self.create_table("TransactionDetails")

            if tableName == "Book": 
                #query to get total boo copies (dont innclude deleted ones)
                query = "SELECT SUM(BookTotalCopies) FROM Book WHERE isDeleted is NULL AND LibrarianID = ?" 
                result = cursor.execute(query, (id, ))
                count = result.fetchone()[0] #get column of first row
                return count if count is not None else 0 #return 0 if null
            elif tableName == "Member":
                #query to get the active members
                query = "SELECT COUNT(*) FROM Member WHERE isDeleted is NULL and LibrarianID = ?"
                result = cursor.execute(query, (id, ))
                count = result.fetchone()[0] 
                return count if count is not None else 0 #return 0 if null
            elif tableName == "BookTransaction":
                #query to sum the quantity of all currently borrowed books
                #join BookTransaction table and TransactionDetails table
                query = """SELECT SUM(td.Quantity) FROM BookTransaction AS t
                JOIN TransactionDetails AS td ON t.TransactionID = td.transactionID
                WHERE t.ReturnedDate IS NULL
                AND t.Status = 'Borrowed'
                AND t.LibrarianID = ?"""
                result = cursor.execute(query, (id,))
                count = result = result.fetchone()[0]
                return count if count is not None else 0 #return 0 if null
        
        finally:
            conn.close() #close the db
            
    def search_archived_records(self, tableName, search_text, librarian_id):
        """Search archived records based on search text"""
        conn, cursor = self.get_connection_and_cursor()
        try:
            search_pattern = f"%{search_text}%"
            
            if tableName == "Book":
                query = """
                    SELECT * FROM Book 
                    WHERE isDeleted IS NOT NULL 
                    AND LibrarianID = ? 
                    AND (
                        BookTitle LIKE ? OR 
                        ISBN LIKE ? OR 
                        Publisher LIKE ? OR
                        BookDescription LIKE ?
                    )
                    ORDER BY isDeleted DESC 
                """
                cursor.execute(query, (librarian_id, search_pattern, search_pattern, search_pattern, search_pattern))
                
            elif tableName == "Member":
                query = """
                    SELECT * FROM Member 
                    WHERE isDeleted IS NOT NULL 
                    AND LibrarianID = ? 
                    AND (
                        MemberFN LIKE ? OR 
                        MemberLN LIKE ? OR 
                        MemberMI LIKE ? OR
                        MemberContact LIKE ?
                    )
                    ORDER BY isDeleted DESC
                """
                cursor.execute(query, (librarian_id, search_pattern, search_pattern, search_pattern, search_pattern))
                
            elif tableName == "BookShelf":
                query = """
                    SELECT * FROM BookShelf 
                    WHERE isDeleted IS NOT NULL 
                    AND LibrarianID = ? 
                    AND ShelfName LIKE ?
                    ORDER BY isDeleted DESC
                """
                cursor.execute(query, (librarian_id, search_pattern))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in rows]
            
            print(f"✓ Found {len(records)} archived {tableName} records matching '{search_text}'")
            return records
            
        except Exception as e:
            print(f"✗ Error searching archived {tableName} records: {e}")
            return []
        finally:
            conn.close()

    def search_records(self, tableName, search_text, librarian_id):
        """Search active records based on search text"""
        conn, cursor = self.get_connection_and_cursor()
        try:
            search_pattern = f"%{search_text}%"
            
            if tableName == "Book":
                # Search in Book table with author and genre joins
                query = """
                    SELECT DISTINCT b.* FROM Book b
                    LEFT JOIN BookAuthor ba ON b.BookCode = ba.BookCode
                    LEFT JOIN Book_Genre bg ON b.BookCode = bg.BookCode
                    WHERE b.isDeleted IS NULL 
                    AND b.LibrarianID = ? 
                    AND (
                        b.BookTitle LIKE ? OR 
                        b.ISBN LIKE ? OR 
                        b.Publisher LIKE ? OR
                        b.BookDescription LIKE ? OR
                        ba.bookAuthor LIKE ? OR
                        bg.Genre LIKE ?
                    )
                    ORDER BY b.BookTitle ASC
                """
                cursor.execute(query, (librarian_id, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
                
            elif tableName == "Member":
                query = """
                    SELECT * FROM Member 
                    WHERE isDeleted IS NULL 
                    AND LibrarianID = ? 
                    AND (
                        MemberFN LIKE ? OR 
                        MemberLN LIKE ? OR 
                        MemberMI LIKE ? OR
                        MemberContact LIKE ?
                    )
                    ORDER BY MemberLN ASC, MemberFN ASC
                """
                cursor.execute(query, (librarian_id, search_pattern, search_pattern, search_pattern, search_pattern))
                
            elif tableName == "BookTransaction":
                # Search in transactions with related book and member data
                query = """
                    SELECT t.TransactionID, t.BorrowedDate, t.Status, t.ReturnedDate, t.Remarks,
                           m.MemberID, m.MemberFN || ' ' || m.MemberLN AS borrower,
                           b.BookCode, b.BookTitle, td.Quantity, td.DueDate
                    FROM BookTransaction t
                    JOIN TransactionDetails td ON t.TransactionID = td.TransactionID
                    JOIN Member m ON t.MemberID = m.MemberID
                    JOIN Book b ON td.BookCode = b.BookCode
                    WHERE b.isDeleted IS NULL
                    AND m.isDeleted IS NULL
                    AND t.LibrarianID = ?
                    AND (
                        b.BookTitle LIKE ? OR
                        m.MemberFN LIKE ? OR
                        m.MemberLN LIKE ? OR
                        t.Status LIKE ? OR
                        t.Remarks LIKE ?
                    )
                    ORDER BY t.BorrowedDate DESC
                """
                cursor.execute(query, (librarian_id, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
                
            elif tableName == "BookShelf":
                query = """
                    SELECT * FROM BookShelf 
                    WHERE isDeleted IS NULL 
                    AND LibrarianID = ? 
                    AND ShelfName LIKE ?
                    ORDER BY ShelfName ASC
                """
                cursor.execute(query, (librarian_id, search_pattern))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            records = [dict(zip(columns, row)) for row in rows]
            
            # Add additional mappings for transaction records
            if tableName == "BookTransaction":
                for rec in records:
                    rec['date'] = rec.get('BorrowedDate', '')
                    rec['remarks'] = rec.get('Remarks', '')
                    rec['returned_date'] = rec.get('ReturnedDate', '') 
                    rec['quantity'] = rec.get('Quantity', 1)
                    rec['due_date'] = rec.get('DueDate', '')
            
            print(f"✓ Found {len(records)} {tableName} records matching '{search_text}'")
            return records
            
        except Exception as e:
            print(f"✗ Error searching {tableName} records: {e}")
            return []
        finally:
            conn.close()

if __name__ == "__main__":
    seeder = DatabaseSeeder()