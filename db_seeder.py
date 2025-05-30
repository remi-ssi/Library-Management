import sqlite3
import bcrypt


class DatabaseSeeder:
    def __init__(self, db_path='bjrsLib.db'):
        #initializing seede with db path
        self.db_path = db_path
    
    def connect(self):
        #connecting db
        return sqlite3.connect(self.db_path)
    
    def check_librarian_table(self):
        #check librarian table if it exists
        conn= self.connect()
        cursor = conn.cursor()

        try: 
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Librarian'")
            result = cursor.fetchone()

            if result:
                print("Librarian table found")
                return True
            else:
                print("Librarian table not found")
                return False
        except Exception as e:
                print(f"Error checking librarian table: {e}")
                return False
        finally:
             conn.close()

    def seed_librarians(self):
        #seeding librarian table with sample data
        conn= self.connect()
        cursor = conn.cursor()

        sample_librarian = [
           {
                   'username' : 'admin',
                   'password' : 'admin123'
           }
        ]
        try:
            for lib_data in sample_librarian:
                hashed_password = bcrypt.hashpw(
                    lib_data['password'].encode('utf-8'),
                    bcrypt.gensalt()
                )

                cursor.execute("INSERT INTO Librarian (LibUsername, LibPass) VALUES(?, ?)", 
                                (lib_data['username'],
                                  hashed_password))
                conn.commit()
                print(f"Seeder {len(sample_librarian)} librarian")   
                print("Login credentials")
                for lib_data in sample_librarian:
                     print(f"Username: {lib_data['username']}, Password: {lib_data['password']}")
        
        except Exception as e:
            print(f"error seeding librarians: {e}")
        
        finally:
            conn.close()

    # def seed_all(self, clear_first=False):
    #     #Initialize Librarian table and seed with data
    #     if clear_first:
    #         self.clear_librarian_data()
        
    #     print("Starting BJRS Library database initialization...")
        
    #     # Check if Librarian table exists
    #     if not self.check_librarian_table():
    #         print("ERROR: Librarian table not found! Please create it in SQLite Studio first.")
    #         return
        
    #     # Seed librarian data
    #     self.seed_librarians()
        
    #     print("✓ Librarian initialization completed!")
    #     print("\nYou can now log in with:")
    #     print("  Username: jas")
    #     print("  Password: qtqt")
    
    def verify_login(self, username, password):
        #test login 
        conn= self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute ("SELECT password FROM Librarian WHERE username = ?", (username))
            result = cursor.fetchone()

            if result:
                stored_hashed_password = result[0]

                if isinstance(stored_hashed_password, str):
                    stored_hashed_password= stored_hashed_password.encode("utf-8")
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    print("Login test successful")
                    return True
                else: 
                    print("Login test failed - incorrect password")
                    return False
            else: 
                print("Login test failed - incorrect password")
                return False
            
        except Exception as e:
            print(f"Error testing login: {e}")
            return False

        finally: 
            conn.close()


if __name__ == "__main__":
    seeder = DatabaseSeeder()

