def create_data_base():
    import sqlite3

    con = sqlite3.connect("tetris.db")
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            time TEXT,
            score TEXT
        );
    """)
    con.commit()

    add_record_data_base(0, '00:00:00')


def add_record_data_base(record_score, record_time):
    import sqlite3

    con = sqlite3.connect("tetris.db")
    cur = con.cursor()

    cur.execute("""
        DELETE FROM user;
    """)
    con.commit()

    cur.execute(f"""
            INSERT INTO user VALUES ('{record_time}', '{record_score}')""")
    con.commit()


def get_record_data_base():
    import sqlite3

    con = sqlite3.connect("tetris.db")
    cur = con.cursor()

    records = cur.execute("""
        SELECT * FROM user
    """).fetchall()

    return records[0]
