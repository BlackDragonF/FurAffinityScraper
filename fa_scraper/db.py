import sqlite3

import logging
logger = logging.getLogger('default')

def connect_db(db_name):
    conn = sqlite3.connect(db_name)
    logger.debug('connected to database \'%s\'.' % db_name)
    return conn

def close_db(conn):
    conn.close()
    logger.debug('database closed.')

def create_artwork_table(db_conn):
    db_conn.execute('''
                    CREATE TABLE IF NOT EXISTS ARTWORK(
                    ID INT PRIMARY KEY      NOT NULL,
                    NAME           TEXT     NOT NULL,
                    WIDTH          INT      NOT NULL,
                    HEIGHT         INT      NOT NULL,
                    AUTHOR         TEXT     NOT NULL,
                    POSTED         DATETIME,
                    CATEGORY       TEXT,
                    THEME          TEXT,
                    SPECIES        TEXT,
                    GENDER         TEXT,
                    FAVORITES      INT,
                    COMMENTS       INT,
                    VIEWS          INT,
                    ADULT          BOOLEAN,
                    KEYWORDS       TEXT);''')
    db_conn.commit()
    logger.info('created/retrieved artwork table.')
