import sqlite3
import bcrypt


class DatabaseSeeder:
    def __init__(self, db_path='bjrsLib.db'):
        #initializing seeder with db path
        self.db_path = db_path
    
    def connect(self):
        #connecting db
        return sqlite3.connect(self.db_path)
    
    def check_librarian_table(self):
        #check librarian table if it exists
        conn = self.connect()
        cursor = conn.cursor()

        try: 
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Librarian'")
            result = cursor.fetchone()

            if result:
                print("✓ Librarian table found")
                return True
            else:
                print("✗ Librarian table not found")
                return False
        except Exception as e:
            print(f"Error checking librarian table: {e}")
            return False
        finally:
            conn.close()

    def seed_librarians(self):
        #seeding librarian table with sample data
        conn = self.connect()
        cursor = conn.cursor()

        sample_librarians = [
            {
                'username': 'admin',
                'password': 'admin123'
            },
            {
                'username': 'jas',
                'password': 'qtqt'
            }
        ]
        
        try:
            for lib_data in sample_librarians:
                hashed_password = bcrypt.hashpw(
                    lib_data['password'].encode('utf-8'),
                    bcrypt.gensalt()
                )

                cursor.execute("INSERT INTO Librarian (LibUsername, LibPass) VALUES(?, ?)", 
                              (lib_data['username'], hashed_password))
            
            conn.commit()
            print(f"✓ Seeded {len(sample_librarians)} librarians")   
            print("Login credentials:")
            for lib_data in sample_librarians:
                print(f"  Username: {lib_data['username']}, Password: {lib_data['password']}")
        
        except Exception as e:
            print(f"Error seeding librarians: {e}")
        
        finally:
            conn.close()

    def clear_librarian_data(self):
        """Clear all data from Librarian table"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM Librarian")
            conn.commit()
            print("✓ Cleared all data from Librarian table")
        except Exception as e:
            print(f"Error clearing Librarian data: {e}")
        finally:
            conn.close()

    def seed_all(self, clear_first=False):
        #Initialize Librarian table and seed with data
        if clear_first:
            self.clear_librarian_data()
        
        print("Starting BJRS Library database initialization...")
        
        # Check if Librarian table exists
        if not self.check_librarian_table():
            print("ERROR: Librarian table not found! Please create it in SQLite Studio first.")
            return
        
        # Seed librarian data
        self.seed_librarians()
        
        print("✓ Librarian initialization completed!")
        print("\nYou can now log in with:")
        print("  Username: admin, Password: admin123")
        print("  Username: jas, Password: qtqt")
    
    def verify_login(self, username, password):
        #test login functionality
        conn = self.connect()
        cursor = conn.cursor()

        try:
            # Fixed: Use correct column names and proper tuple syntax
            cursor.execute("SELECT LibPass FROM Librarian WHERE LibUsername = ?", (username,))
            result = cursor.fetchone()

            if result:
                stored_hashed_password = result[0]

                if isinstance(stored_hashed_password, str):
                    stored_hashed_password = stored_hashed_password.encode("utf-8")
                
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    print(f"✓ Login test successful for {username}")
                    return True
                else: 
                    print("✗ Login test failed - incorrect password")
                    return False
            else: 
                print("✗ Login test failed - user not found")
                return False
            
        except Exception as e:
            print(f"Error testing login: {e}")
            return False

        finally: 
            conn.close()


if __name__ == "__main__":
    seeder = DatabaseSeeder()
    
    # Seed the database
    seeder.seed_all(clear_first=True)
    
    # Test login
    print("\nTesting login:")
    seeder.verify_login("admin", "admin123")
    seeder.verify_login("jas", "qtqt")