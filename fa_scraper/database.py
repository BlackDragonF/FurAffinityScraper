import sqlite3

from fa_scraper import util

import logging
logger = logging.getLogger('default')


class Database(object):
    def create_artwork_table(self):
        self.conn.execute('CREATE TABLE IF NOT EXISTS ARTWORK('
                          'ID INT PRIMARY KEY          NOT NULL, '
                          'NAME           TEXT, '
                          'WIDTH          INT, '
                          'HEIGHT         INT, '
                          'AUTHOR         TEXT, '
                          'POSTED         DATETIME, '
                          'CATEGORY       TEXT, '
                          'THEME          TEXT, '
                          'SPECIES        TEXT, '
                          'GENDER         TEXT, '
                          'FAVORITES      INT, '
                          'COMMENTS       INT, '
                          'VIEWS          INT, '
                          'ADULT          BOOLEAN, '
                          'KEYWORDS       TEXT, '
                          'ADDED          DATETIME);')
        self.conn.commit()
        logger.debug('created/retrieved artwork table.')

    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        logger.debug('connected to database "%s".' % database_name)
        self.create_artwork_table()
        logger.debug('database initialized.')

    @staticmethod
    def attribute_dictionary_to_tuple(artwork):
        return (artwork.get('ID'), artwork.get('Name'), artwork.get('Width'),
        artwork.get('Height'), artwork.get('Author'), artwork.get('Posted'),
        artwork.get('Category'), artwork.get('Theme'), artwork.get('Species'),
        artwork.get('Gender'), artwork.get('Favorites'), artwork.get('Comments'),
        artwork.get('Views'), artwork.get('Adult'), artwork.get('Keywords'),
        artwork.get('Added'))

    def insert_or_replace_artwork(self, artwork):
        artwork['Adult'] = util.convert_boolean(artwork['Adult'])
        attribute_tuple = self.attribute_dictionary_to_tuple(artwork)
        print(attribute_tuple)
        self.conn.execute('INSERT OR REPLACE INTO ARTWORK (ID, NAME, WIDTH, HEIGHT, AUTHOR, '
                          'POSTED, CATEGORY, THEME, SPECIES, GENDER, FAVORITES, '
                          'COMMENTS, VIEWS, ADULT, KEYWORDS, ADDED) VALUES(?, ?, ?, '
                          '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', attribute_tuple)
        self.conn.commit()
        logger.debug('inserted artwork information into artwork table.')

    def get_artwork_ids(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT ID FROM ARTWORK')

        artwork_ids = list(map(lambda x : x.__getitem__(0), cursor.fetchall()))
        logger.debug('%u artworks retrieved from database.' % len(artwork_ids))
        return artwork_ids

    def delete_artworks(self, artwork_ids):
        delete_count = 0
        for artwork_id in artwork_ids:
            # self.conn.execute('DELETE FROM ARTWORK WHERE ID = ?;' % artwork_id)
            delete_count = delete_count + 1

        self.conn.commit()
        logger.debug('%u artwork records deleted from database.' % delete_count)

    @staticmethod
    def if_time_expired(id_time_tuple, current_time, expire_time):
        if (util.parse_datetime(id_time_tuple[1]) - util.parse_datetime(current_time)) >= expire_time * 86400:
            return True
        else:
            return False

    def get_expired_artwork_ids(self, expire_time):
        cursor = self.conn.cursor()
        cursor.execute('SELECT ID, ADDED FROM ARTWORK')

        current_time = util.get_current_time()

        expired_records = filter(lambda t : self.if_time_expired(t, current_time, expire_time), cursor.fetchall())
        expired_artwork_ids = list(map(lambda x : x.__getitem__(0), expired_records))

        return expired_artwork_ids
