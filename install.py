"""Install
Creates the lan nanny db and tables, as well as populating options and their defaults.

"""


from modules import db

NMAP_DB = "lan_nanny.db"

conn, cursor = db.create_connection(NMAP_DB)


def run():
    """
    Main entry point to scanning script.

    """
    conn, cursor = db.create_connection(NMAP_DB)
    db.create_tables(cursor)
    db.populate_options(conn, cursor)


if __name__ == '__main__':
    run()

# End File: lan-nanny/install.py
