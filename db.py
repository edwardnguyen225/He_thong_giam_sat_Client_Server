import sqlite3


class Database:
    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOTE EXISTS REPORTS 
                (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    DEVICE_NAME TEXT,
                    IP TEXT,
                    BOOT_TIME TEXT,
                    
                    MEM_TOTAL TEXT,
                    MEM_AVAILABLE TEXT, 
                    MEM_USED TEXT,
                    MEM_PERCENT REAL,
                )
            """)

    def __del__(self):
        self.connection.close()


server_db = Database("server.db")
