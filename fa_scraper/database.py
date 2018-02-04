import sqlite3

import logging
logger = logging.getLogger('default')


class Database(object):
    def create_artwork_table(self):
        self.conn.execute('''
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
        self.conn.commit()
        logger.debug('created/retrieved artwork table.')

    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        logger.debug('connected to database "%s".' % database_name)
        self.create_artwork_table()
        logger.debug('database initialized.')
