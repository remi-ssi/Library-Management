import sqlite3
import bcrypt

class DatabaseSeeder:
    def __init__(self, db_path='bjrsLib.db'):
        # Initialize with the path to the SQLite database
        self.db_path = db_path

    def connect(self):
        # Connect to the SQLite database
        return sqlite3.connect(self.db_path)
    
    def get_cursor_and_connection(self):
        conn = self.connect()
        return conn.cursor(), conn

    #check if table exists
    def check_table_exists(self, table_name):
        """Check if a table exists in the database"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return bool(cursor.fetchone())
        except Exception as e:
            print(f"Error checking table {table_name}: {e}")
            return False
        finally:
            conn.close()

    #create table if it doesnt exist
    def create_table(self, create_sql):
        """Create a table using provided SQL statement"""
        conn = self.connect()
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        try:
            cursor.execute(create_sql)
            conn.commit()
            print("✓ Table created successfully")
            return True
        except Exception as e:
            print(f"Error creating table: {e}")
            return False
        finally:
            conn.close()

    def clear_table(self, table_name):
        """Delete all rows from the specified table"""
        conn = self.connect()
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        try:
            cursor.execute(f"DELETE FROM {table_name}")
            conn.commit()
            print(f"✓ Cleared all data from {table_name}")
        except Exception as e:
            print(f"Error clearing {table_name}: {e}")
        finally:
            conn.close()

    #create an instance in database
    def seed_data(self, table_name, data_list, column_order, hash_password_field=None):
        """
        Seed data into any table

        Parameters:
        - table_name: str, name of the table
        - data_list: list of dicts containing row data
        - column_order: list of column names in order
        - hash_password_field: optional str, name of the column to hash (like password)
        """
        conn = self.connect()
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        try:
            for data in data_list:
                values = []
                for col in column_order:
                    value = data[col]
                    if col == hash_password_field:
                        value = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                    values.append(value)

                placeholders = ', '.join(['?'] * len(column_order))
                columns = ', '.join(column_order)

                cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)

            conn.commit()
            print(f"✓ Seeded {len(data_list)} rows into {table_name}")
        except Exception as e:
            print(f"Error seeding data into {table_name}: {e}")
        finally:
            conn.close()

    #for log in verification
    def verify_login(self, table_name, username_column, password_column, username, password):
        """Simple login test based on hashed password"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT {password_column} FROM {table_name} WHERE {username_column} = ?", (username,))
            result = cursor.fetchone()

            if result:
                stored_password = result[0]
                if isinstance(stored_password, str):
                    stored_password = stored_password.encode('utf-8')

                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    print(f"✓ Login successful for {username}")
                    return True
                else:
                    print("✗ Incorrect password")
                    return False
            else:
                print("✗ User not found")
                return False
        except Exception as e:
            print(f"Login error for {username}: {e}")
            return False
        finally:
            conn.close()

    #to update table
    def update_member_full(self, member_id, new_last_name, new_first_name, new_middle_name, new_contact):
        conn = self.connect()
        cursor = conn.cursor()
        try:
            update_query = """
                UPDATE Member
                SET MemberLN = ?, MemberFN = ?, MemberMI = ?, MemberContact = ?
                WHERE MemberID = ?
            """
            cursor.execute(update_query, (new_last_name, new_first_name, new_middle_name, new_contact, member_id))
            conn.commit()
            print(f"✓ Member {member_id} updated successfully.")
        except Exception as e:
            print(f"✗ Error updating member {member_id}: {e}")
        finally:
            conn.close()

    #get the records of members
    def get_all_members(self):
        """Fetch all members from the Member table"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MemberID, MemberLN, MemberFN, MemberMI, MemberContact FROM Member")
            rows = cursor.fetchall()

            members = []
            for row in rows:
                member_id, ln, fn, mi, contact = row
                full_name = f"{fn} {mi} {ln}" if mi else f"{fn} {ln}"
                members.append({
                    "id": member_id,
                    "name": full_name,
                    "contact": contact
                })

            return members  # return the members to display in UI
        except Exception as e:
            print(f"✗ Error fetching members: {e}")
            return []  # Return an empty list instead of None to avoid crashes
        finally:
            conn.close()

    #seed all the data in database on their respective tables
    def seed_all(self):
        """Seed all required tables using generalized logic"""

        # --- Librarian Table ---
        librarian_sql = '''CREATE TABLE IF NOT EXISTS Librarian (
            LibrarianID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            LibUsername VARCHAR NOT NULL,
            FName VARCHAR NOT NULL,
            LName VARCHAR NOT NULL,
            MName VARCHAR NOT NULL,
            LibPass BLOB NOT NULL
        )'''

        librarian_data = [
            {'LibUsername': 'admin', 'LibPass': 'admin123', 'FName': 'Shelley', 'LName': 'Sesante', 'MName': 'Hi'},
            {'LibUsername': 'jas', 'LibPass': 'qtqt', 'FName': 'Jasmine', 'LName': 'Aninion', 'MName': 'Anne'}
        ]

        self._initialize_table(
            table_name="Librarian",
            create_sql=librarian_sql,
            data=librarian_data,
            columns=["LibUsername", "LibPass", "FName", "LName", "MName"],
            hash_password_column="LibPass",
            clear=True
        )

        # --- Member Table ---
        member_sql = '''CREATE TABLE IF NOT EXISTS Member (
            MemberID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            MemberLN VARCHAR NOT NULL,
            MemberMI VARCHAR,
            MemberFN VARCHAR NOT NULL,
            MemberContact INTEGER NOT NULL,
            CreatedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            LibrarianID INTEGER,
            FOREIGN KEY (LibrarianID) REFERENCES Librarian(LibrarianID)
        )'''

        member_data = [
            {'MemberLN': 'Gonzaga', 'MemberMI': 'Lovete', 'MemberFN': 'Reymie', 'MemberContact': '0912345678'},
            {'MemberLN': 'Sesante', 'MemberMI': 'Losinada', 'MemberFN': 'Shelley', 'MemberContact': '0923456789'}
        ]

        self._initialize_table(
            table_name="Member",
            create_sql=member_sql,
            data=member_data,
            columns=["MemberLN", "MemberMI", "MemberFN", "MemberContact"],
            clear=True
        )

    #initialize the table / for debugging purposes only
    def _initialize_table(self, table_name, create_sql, data, columns, hash_password_column=None, clear=False):
        """Helper function to check, create, clear, and seed a table"""
        print(f"\n🔧 Initializing {table_name}...")

        if not self.check_table_exists(table_name):
            print(f"{table_name} table not found. Creating...")
            if not self.create_table(create_sql):
                print(f"✗ Failed to create {table_name}")
                return

        if clear:
            self.clear_table(table_name)

        self.seed_data(table_name, data, column_order=columns, hash_password_field=hash_password_column)
        print(f"✅ {table_name} setup complete.")

if __name__ == "__main__":
    seeder = DatabaseSeeder()

    # Seed all tables
    seeder.seed_all()

    # Test login
    print("\n🔐 Testing login:")
    seeder.verify_login("Librarian", "LibUsername", "LibPass", "admin", "admin123")
    seeder.verify_login("Librarian", "LibUsername", "LibPass", "jas", "qtqt")
