import sqlite3
from sqlite3 import Error, IntegrityError


def create_connection(database):
    """Creates a connection to the specified database"""

    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)

    return conn


def create_tables(conn):
    """Creates the database tables if they do not exist"""

    query_passing = """CREATE TABLE IF NOT EXISTS passing (
                        name PRIMARY KEY,
                        position TEXT,
                        age REAL,
                        date TEXT,
                        team TEXT,
                        opponent TEXT,
                        home_or_away TEXT,
                        result TEXT,
                        week INTEGER,
                        day TEXT,
                        completions INTEGER,
                        attempts INTEGER,
                        yards REAL,
                        touchdowns INTEGER,
                        interceptions INTEGER,
                        qb_rating REAL,
                        sacks INTEGER,
                        sacked_yards INTEGER,
                        CONSTRAINT unique_uc UNIQUE(player, team, date)
                        ); """

    query_rushing = """CREATE TABLE IF NOT EXISTS rushing (
                        name PRIMARY KEY,
                        position TEXT,
                        age REAL,
                        date TEXT,
                        team TEXT,
                        opponent TEXT,
                        home_or_away TEXT,
                        result TEXT,
                        week INTEGER,
                        day TEXT,
                        attempts INTEGER,
                        yards REAL,
                        touchdowns INTEGER,
                        CONSTRAINT unique_uc UNIQUE(player, team, date)
                        ); """

    query_receiving = """CREATE TABLE IF NOT EXISTS receiving (
                        name PRIMARY KEY,
                        position TEXT,
                        age REAL,
                        date TEXT,
                        team TEXT,
                        opponent TEXT,
                        home_or_away TEXT,
                        result TEXT,
                        week INTEGER,
                        day TEXT,
                        targets INTEGER,
                        receptions INTEGER,
                        yards REAL,
                        touchdowns INTEGER,
                        CONSTRAINT unique_uc UNIQUE(player, team, date)
                        ); """

    try:
        c = conn.cursor()
        c.execute(query_passing)
        c.execute(query_rushing)
        c.execute(query_receiving)
    except Error as e:
        print(e)

