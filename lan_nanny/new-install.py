from modules import db

def run():
    conn, cursor = db.connect_mysql_no_db()
    db.create_mysql_database(conn, cursor)

    conn, cursor = db.connect_mysql()
    db.create_tables_new(conn, cursor)

if __name__ == "__main__":
    run()