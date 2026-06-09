import mysql.connector
'''
cur = conn.cursor()
cur.execute('USE soldiers_db')
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
conn.commit()
print('Table created')

'''

conn = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='root',
    database = 'soldiers_db'
)

def delete(message_id: int, connection)-> bool:
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
        
print(delete(7, conn))