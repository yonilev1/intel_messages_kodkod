import mysql.connector
conn = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='root'
)

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

