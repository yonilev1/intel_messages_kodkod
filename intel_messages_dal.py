import mysql.connector
import logger

class IntelMessagesDAL:
    VALID_CLASSIFICATIONS = ('unclassified', 'confidential', 'secret','top_secret')
    def __init__(self, host: str, user: str, password: str, database: str,logger: logger):
        # Store connection parameters on self
        # store logger object reference in self...
        # ------------------------------------------------------------------ setup
        self.conn = None
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.logger = logger
        self.connection = self.get_conn()


    def get_conn(self):
        #create connection from params stored in self 
        #store the connection in self 
        #return conn
        self.conn = mysql.connector.connect(
        host=self.host,
        port=3306,
        user=self.user,
        password=self.password,
        database=self.database)
        return self.conn
    

    def setup(self)-> None:
        # Create the intel_messages table if it does not exist
        # Column definitions: id, unit, classification (ENUM), content,source, created_at
        # Commit after execution...
        # ------------------------------------------------------------------schema
        cur = self.connection.cursor()
        cur.execute(f'USE {self.database}')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS intel_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    unit VARCHAR(100) NOT NULL,
                    classification  ENUM('unclassified','confidential','secret','top_secret'),
                    content  TEXT NOT NULL,
                    source  VARCHAR(100),
                    created_at DATETIME DEFAULT NOW()
                    )
                    """)
        self.connection.commit()


    def get_schema(self)-> list[dict]:
        # Query INFORMATION_SCHEMA.COLUMNS for the intel_messages table
        # Return a list of dicts: [{"column": ..., "type": ...}, ...]...
        # ------------------------------------------------------------ read (all)



    def get_all(self)-> list[dict]:
        # Return every row in intel_messages as a list of dicts...
        # --------------------------------------------------------- read (by id)
        """
        returns list of all messages
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT * FROM intel_messages;
        """)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def get_by_id(self, message_id: int)-> dict | None:
        # Return the single row where id = message_id, or None if not found...
        # ----------------------------------------------------------------- create
    def create(self, unit: str, classification: str, content: str, source: str
    | None)-> int:
        # Insert a new row (do NOT pass created_at — let MySQL set it)
        # Commit the transaction
        # Return the auto-generated id (lastrowid)...
        # ----------------------------------------------------------------- update
    def update(self, message_id: int, data: dict)-> bool:
        # Build a dynamic SET clause from the keys in data
        # Only update the columns that are present in data
        # Commit the transaction
        # Return True if a row was changed, False if the id did not exist
        # Never use f-strings for values — only %s...
        # ----------------------------------------------------------------- delete
    def delete(self, message_id: int)-> bool:
        # Delete the row where id = message_id
        # Commit the transaction
        # Return True if a row was deleted, False if the id did not exist...
        # --------------------------------------------------------------- queries
    def get_by_unit(self, unit: str)-> list[dict]:
        # All messages where unit matches, ordered by created_at DESC...
    def get_by_classification(self, classification: str)-> list[dict]:
        # All messages at the given classification level...
    def get_by_unit_and_classification(self, unit: str, classification: str)
    > list[dict]:
    # Both filters combined with AND
    ...
    def get_distinct_units(self)-> list[str]:
    # All unique unit values — return a plain list of strings, not dicts
    ...
    def search_content(self, term: str)-> list[dict]:
    # Rows where content contains term (partial match)
    ...
    def get_missing_source(self)-> list[dict]:
    # Rows where source IS NULL
    ...
    # ----------------------------------------------------------------- close
    def close(self)-> None:
    # Close the cursor and the connection
    ...