import os
import sqlite3
import bcrypt

class DatabaseSeeder:
    #initialize the path of the sqlite database
    def __init__(self, db_path='bjrsLib.db'):
        self.db_path = db_path

    def get_connection_and_cursor(self):
        conn = sqlite3.connect(self.db_path)
        return conn, conn.cursor() 
    
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
            return """CREATE TABLE IF NOT EXISTS Member(
                    MemberID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    MemberLN VARCHAR(20) NOT NULL,
                    MemberMI VARCHAR(20),
                    MemberFN VARCHAR (20) NOT NULL,
                    MemberContact INTEGER(11) NOT NULL,
                    CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
                    isDeleted TIMESTAMP DEFAULT NULL,
                    LibrarianID INTEGER,
                    FOREIGN KEY (LibrarianID) REFERENCES Librarian (LibrarianID)
                    )"""
        elif tableName == "Book":
            book =  """CREATE TABLE IF NOT EXISTS Book(
                    BookCode INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    BookTitle VARCHAR NOT NULL,
                    Publisher VARCHAR NOT NULL,
                    BookDescription VARCHAR NOT NULL,
                    shelfNo VARCHAR(6) NOT NULL,
                    ISBN INTEGER NOT NULL,
                    BookTotalCopies INTEGER NOT NULL,
                    BookAvailableCopies INTEGER,
                    BookCover BLOB,
                    isDeleted TIMESTAMP DEFAULT NULL,
                    LibrarianID INTEGER, 
                    FOREIGN KEY (LibrarianID) REFERENCES Librarian (LibrarianID))"""
            Author = """CREATE TABLE IF NOT EXISTS BookAuthor(
                    BookCode INTEGER,
                    bookAuthor VARCHAR NOT NULL,
                    PRIMARY KEY (BookCode, bookAuthor),
                    FOREIGN KEY (BookCode) REFERENCES Book (BookCode))"""
            Genre = """CREATE TABLE IF NOT EXISTS Book_Genre(
                    BookCode INTEGER,
                    Genre VARCHAR,
                    PRIMARY KEY (BookCode, Genre), 
                    FOREIGN KEY (BookCode) REFERENCES Book (BookCode))"""
            return book, Author, Genre

    #check if the table exists in the database
    def check_table(self, tableName):
        conn, cursor = self.get_connection_and_cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tableName,))
            return bool(cursor.fetchone()) #if it retrieves one row/instance, it returns true
        except Exception as e:
            print(f"Error checking table {tableName}: {e}")
            return False
        #close the database
        finally:
            conn.close() 

    #create a table if it doest exists in the database
    def create_table(self, tableName):
        conn, cursor = self.get_connection_and_cursor()
        conn.execute("PRAGMA foreign_keys = ON;")

        try:
            if tableName == "Book":
                bookCreate, authorCreate, genreCreate = self.query(tableName)
                cursor.execute(bookCreate)
                cursor.execute(authorCreate)
                cursor.execute(genreCreate)
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

        #Calls check_table to see if the table is already in the database.
        if not self.check_table(tableName): 
            print(f"{tableName} not found.")
            if not self.create_table(tableName):
                print(f"Failed to create {tableName}")
                return

        try:
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
                #cursor.execute("INSERT INTO Librarian (LibUsername, LibPass, FName, LName, MName) VALUES (?, ?, ?, ?, ?)", ["admin", b"$2b$12$abc123...hashed", "Shelley", "Sesante", "Hi"])
            
            conn.commit()
            print(f"✓ Seeded {len(data)} rows into {tableName}")
        except Exception as e:
            print(f"Error seeding data into {tableName}: {e}")
        finally:
            conn.close()

    def clear_table(self, tableName):
        conn, cursor = self.get_connection_and_cursor()
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            cursor.execute(f"DELETE FROM {tableName}")
            conn.commit()
            print(f"✓ Cleared all data from {tableName}")
        except Exception as e:
            print(f"Error clearing {tableName}: {e}")
        finally:
            conn.close()

    #to get all the records/rows inside the certain table
    def get_all_records(self, tableName, id):
        conn, cursor = self.get_connection_and_cursor()
        try:
            if tableName == "Librarian":
                cursor.execute(f"SELECT * FROM {tableName}")
            elif tableName in ["BookAuthor", "Book_Genre"]:
                # Filter by books that are not deleted and owned by the specified librarian
                if tableName == "BookAuthor":  # BA is the alias for BookAuthor
                    query = """SELECT BA.* FROM BookAuthor AS BA 
                            JOIN Book AS BK ON BA.BookCode = BK.BookCode
                            WHERE BK.isDeleted IS NULL AND BK.LibrarianID = ?""" 
                else:  # Book_Genre  BG is the alias for Book_Genre
                    query = """SELECT BG.*FROM Book_Genre AS BG
                            JOIN Book AS BK ON BG.BookCode = BK.BookCode
                            WHERE BK.isDeleted IS NULL AND BK.LibrarianID = ?"""
                cursor.execute(query, (id,))
            else: # for member and book table
                # Filter by records that are not deleted and owned by the specified librarian
                query = f"SELECT * FROM {tableName} WHERE isDeleted IS NULL AND LibrarianID = ?"
                cursor.execute(query, (id,))
            
            rows = cursor.fetchall()

            # Get column names from the cursor description
            columns = [desc[0] for desc in cursor.description]

            # Convert rows to list of dictionaries
            records = [dict(zip(columns, row)) for row in rows]

            return records  # Return the list to display in the UI
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
    def delete_table(self, tableName, column, value):
        conn, cursor = self.get_connection_and_cursor()
        try:
            query = f"UPDATE {tableName} SET isDeleted = CURRENT_TIMESTAMP WHERE {column} = ?"
            cursor.execute(query, (value,))
            conn.commit()
            print(f"✓ Deleted from {tableName} where {column} = {value}")
        except Exception as e:
            print(f"✗ Error deleting from {tableName}: {e}")
        finally:
            conn.close()

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
    
   
if __name__ == "__main__":
    seeder = DatabaseSeeder()