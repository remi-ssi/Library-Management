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
    
    def preSeed_all_tables(self):
        
        # ----Librarian Table----
        librarian_table = """CREATE TABLE IF NOT EXISTS Librarian (
            LibrarianID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            LibUsername VARCHAR(20) NOT NULL,
            FName VARCHAR(30) NOT NULL,
            LName VARCHAR(20) NOT NULL,
            MName VARCHAR(20), 
            LibPass BLOB NOT NULL
            )"""       
        librarian_data = [
            {'LibUsername': 'admin', 'LibPass': 'admin123', 'FName': 'Shelley', 'LName': 'Sesante', 'MName': 'Hi'},
            {'LibUsername': 'jas', 'LibPass': 'qtqt', 'FName': 'Jasmine', 'LName': 'Aninion', 'MName': 'Anne'}
        ]

        self.initialize_table(tableName="Librarian", sqlTable= librarian_table, data=librarian_data, columns= ["LibUsername", "LibPass", "FName", "LName", "MName"], password="LibPass", clear=True) #assumes that table exists that's why clear=TRUE

        # ----Member Table ------
        member_table = """CREATE TABLE IF NOT EXISTS Member(
                MemberID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                MemberLN VARCHAR(20) NOT NULL,
                MemberMI VARCHAR(20),
                MemberFN VARCHAR (20) NOT NULL,
                MemberContact INTEGER(11) NOT NULL,
                CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, 
                LibrarianID INTEGER,
                FOREIGN KEY (LibrarianID) REFERENCES Librarian (LibrarianID)
                )"""

    def initialize_table(self, tableName, sqlTable, data, columns, password=None, clear=False):
        #Calls check_table to see if the table is already in the database.
        if not self.check_table(tableName): 
            print(f"{tableName} not found.")
            if not self.create_table(sqlTable):
                print(f"Failed to create {tableName}")
                return

        if clear: #IF CLEAR=TRUE
            self.clear_table(tableName)

        #seed all the data to the database    
        self.seed_data(tableName, data, columnOrder = columns, hashPass = password)
        print(f"{tableName} completed.")

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
    def create_table(self, sqlTable):
        conn, cursor = self.get_connection_and_cursor()
        conn.execute("PRAGMA foreign_keys = ON;")

        try:
            cursor.execute(sqlTable)
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
    def get_all_records(self, tableName):
        conn, cursor = self.get_connection_and_cursor()
        try:
            cursor.execute(f"SELECT * FROM {tableName}")
            rows = cursor.fetchall()

            # Get column names from the cursor description
            columns = [desc[0] for desc in cursor.description]

            # Convert rows to list of dictionaries
            records = [dict(zip(columns, row)) for row in rows]

            return records #return the list to display in the UI
        except Exception as e:
            print(f"✗ Error fetching records from {tableName}: {e}")
            return []
        finally:
            conn.close()

    #update the row of a specific table
    def update_table(self, tableName, updates: dict, column, value):
        conn, cursor = self.get_connection_and_cursor()
        try:
            set_clause = ', '.join([f"{col} = ?" for col in updates])
            values = list(updates.values()) + [value]
            #update statement
            query = f"UPDATE {tableName} SET {set_clause} WHERE {column} = ?"
            cursor.execute(query, values)
            conn.commit()
            print(f"✓ Row in '{tableName}' where {column} = {value} updated successfully.")
        except Exception as e:
            print(f"✗ Error updating row in '{tableName}': {e}")
        finally:
            conn.close()

    #delete a record/row in a specific table
    def delete_table(self, tableName, column, value):
        conn, cursor = self.get_connection_and_cursor()
        try:
            query = f"DELETE FROM {tableName} WHERE {column} = ?"
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
        query = "SELECT COUNT (*) FROM Librarian WHERE LibUsername = ?"
        result = cursor.execute(query, (username,)).fetchone()
        return result[0]>0
    
if __name__ == "__main__":
    seeder = DatabaseSeeder()

    #seed all tablles
    seeder.preSeed_all_tables()

    #for debugging purposes only
    all_librarians = seeder.get_all_records("Librarian")
    print("\n📚 All Librarians:")
    for librarian in all_librarians:
        print(librarian)

    # Retrieve and print all data from the Member table
    all_members = seeder.get_all_records("Member")
    print("\n👥 All Members:")
    for member in all_members:
        print(member)


