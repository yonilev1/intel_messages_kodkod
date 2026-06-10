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


    def setup(self, connection)-> None:
        # Create the intel_messages table if it does not exist
        # Column definitions: id, unit, classification (ENUM), content,source, created_at
        # Commit after execution...
        # ------------------------------------------------------------------schema
        cur = connection.cursor()
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
        connection.commit()
        connection.close()


    def get_schema(self, connection)-> list[dict]:
        # Query INFORMATION_SCHEMA.COLUMNS for the intel_messages table
        # Return a list of dicts: [{"column": ..., "type": ...}, ...]...
        # ------------------------------------------------------------ read (all)
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT COLUMN_NAME as `column`, DATA_TYPE as `data type`
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s and TABLE_NAME = 'intel_messages';
        """, (self.database,))
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows


    def get_all(self, connection)-> list[dict]:
        # Return every row in intel_messages as a list of dicts...
        # --------------------------------------------------------- read (by id)
        """
        returns list of all messages
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT * FROM intel_messages;
        """)
        rows = cursor.fetchall()
        cursor.close()
        connection.close()
        return rows


    def get_by_id(self, message_id: int, connection)-> dict | None:
        # Return the single row where id = message_id, or None if not found...
        # ----------------------------------------------------------------- create
        """
        get message by id
        """
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM intel_messages WHERE id = %s", (message_id,))
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return row


    def create(self, unit: str, classification: str, content: str, source: str
    | None, connection)-> int:
        # Insert a new row (do NOT pass created_at — let MySQL set it)
        # Commit the transaction
        # Return the auto-generated id (lastrowid)...
        # ----------------------------------------------------------------- update
        """
        create new message, returns new message id
        """
        cursor = connection.cursor()
        if classification not in IntelMessagesDAL.VALID_CLASSIFICATIONS:
            raise ValueError(f'classification should be 1-4')
        try:
            cursor.execute("""
            INSERT INTO intel_messages (unit, classification, content, source) VALUES (%s, %s, %s, %s)
            """, (unit, classification, content, source))
            new_id = cursor.lastrowid
            connection.commit()
            cursor.close()
            connection.close()
            return new_id
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)


    def update(self, message_id: int, data: dict, connection)-> bool:
        # Build a dynamic SET clause from the keys in data
        # Only update the columns that are present in data
        # Commit the transaction
        # Return True if a row was changed, False if the id did not exist
        # Never use f-strings for values — only %s...
        # ----------------------------------------------------------------- delete
        """
        update message data
        """
        cursor = connection.cursor()
        if  'classification' in data.keys():
            if data['classification'] not in IntelMessagesDAL.VALID_CLASSIFICATIONS:
                raise ValueError(f'classification should be 1-4')

        in_parts = [f'{key} = %s' for key in data.keys()]
        in_str = ", ".join(in_parts)
        parsed_data = list(data.values()) + [message_id]
        try:
            cursor.execute(f"""
        UPDATE intel_messages SET {in_str} WHERE id = %s
        """, parsed_data)
            connection.commit()
            did_update = cursor.rowcount
            cursor.close()
            connection.close()
            return did_update > 0
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)


    def delete(self, message_id: int, connection)-> bool:
        # Delete the row where id = message_id
        # Commit the transaction
        # Return True if a row was deleted, False if the id did not exist...
        # --------------------------------------------------------------- queries
        """
        delete message from db
        """
        try:
            cursor = connection.cursor()
            cursor.execute(f"""
            DELETE FROM intel_messages WHERE id = %s
            """, (message_id,))
            connection.commit()
            did_delete = cursor.rowcount
            cursor.close()
            connection.close()
            return did_delete > 0
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)
        

    def get_by_unit(self, unit: str, connection)-> list[dict]:
        # All messages where unit matches, ordered by created_at DESC...
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
            SELECT * FROM intel_messages WHERE unit  = %s
            ORDER BY created_at desc""", (unit,))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)


    def get_by_classification(self, classification: str, connection)-> list[dict]:
        # All messages at the given classification level...
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
            SELECT * FROM intel_messages WHERE classification = %s
            """, (classification,))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)


    def get_by_unit_and_classification(self, unit: str, classification: str, connection)-> list[dict]:
    # Both filters combined with AND...
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
            SELECT * FROM intel_messages WHERE classification = %s AND unit = %s
            """, (classification, unit))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)


    def get_distinct_units(self, connection)-> list[str]:
    # All unique unit values — return a plain list of strings, not dicts
        """
        get all distinct units
        """
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"""
            SELECT DISTINCT unit FROM intel_messages
            """)
            rows = cursor.fetchall()
            rows = [row['unit'] for row in rows]
            cursor.close()
            connection.close()
            return rows
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)
        

    def search_content(self, term: str, connection)-> list[dict]:
    # Rows where content contains term (partial match)...
        """
        get by content
        """
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
            SELECT * FROM intel_messages WHERE content LIKE %s
            """, (f'%{term}%',))
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)


    def get_missing_source(self, connection)-> list[dict]:
    # Rows where source IS NULL...
    # ----------------------------------------------------------------- close
        """
        get messages with missing source
        """
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"""
            SELECT * FROM intel_messages WHERE source IS NULL
            """)
            rows = cursor.fetchall()
            cursor.close()
            connection.close()
            return rows
        except Exception as e:
            cursor.close()
            connection.close()
            raise Exception(e)
        