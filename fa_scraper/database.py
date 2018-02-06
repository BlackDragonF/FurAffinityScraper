import sqlite3

from fa_scraper import util

import logging
logger = logging.getLogger('default')


class Database(object):
    def create_artwork_table(self):
        self.conn.execute('''
                        CREATE TABLE IF NOT EXISTS ARTWORK(
                        ID INT PRIMARY KEY          NOT NULL,
                        NAME           TEXT         NOT NULL,
                        WIDTH          INT          NOT NULL,
                        HEIGHT         INT          NOT NULL,
                        AUTHOR         TEXT         NOT NULL,
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

    def insert_artwork(self, artwork):
        artwork['ADULT'] = util.convert_boolean(artwork['ADULT'])
        self.conn.execute('''
                          INSERT INTO ARTWORK (ID, NAME, WIDTH, HEIGHT, AUTHOR,
                          POSTED, CATEGORY, THEME, SPECIES, GENDER, FAVORITES, COMMENTS,
                          VIEWS, ADULT, KEYWORDS) VALUES(%d, %s, %d, %d, %s, %s,
                           %s, %s, %s, %s, %d, %d, %d, %d, %s) % (artwork['ID'],
                           artwork['Name'], artwork['Width'], artwork['Height'],
                           artwork['Author'], artwork['Posted'], artwork['Category'],
                           artwork['Theme'], artwork['Species'], artwork['Gender'],
                           artwork['Favorites'], artwork['Comments'], artwork['Views'],
                           artwork['Adult'], artwork['Keywords'])''')
