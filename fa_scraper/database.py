import sqlite3

from fa_scraper import util

import logging
logger = logging.getLogger('default')


class Database(object):
    """
    Database class to process database transaction.

    Attributes:
        conn - connected object of database
    """
    def create_artwork_table(self):
        """
        Creates artwork table if it not exists.
        Artwork Table:
        +------------+------------+--------------------------------------------+
        |ID          |Int         |ID, cannot be empty                         |
        |------------+------------+--------------------------------------------|
        |Name        |Text        |name                                        |
        |------------+------------+--------------------------------------------|
        |Width       |Int         |width, px                                   |
        |------------+------------+--------------------------------------------|
        |Height      |Int         |height, px                                  |
        |------------+------------+--------------------------------------------|
        |Author      |Text        |author                                      |
        |------------+------------+--------------------------------------------|
        |Posted      |Datetime    |posted time, format: YYYY-mm-DD HH:MM       |
        |------------+------------+--------------------------------------------|
        |Category    |Text        |category, 'Artwork (Digital)' e.g.          |
        |------------+------------+--------------------------------------------|
        |Theme       |Text        |theme, 'Fantasy' e.g.                       |
        |------------+------------+--------------------------------------------|
        |Species     |Text        |species, 'Western Dragon' e.g.              |
        |------------+------------+--------------------------------------------|
        |Gender      |Text        |gender, 'Male' e.g.                         |
        |------------+------------+--------------------------------------------|
        |Favorites   |Int         |number of favorites of the artwork          |
        |------------+------------+--------------------------------------------|
        |Comments    |Int         |number of comments of the artwork           |
        |------------+------------+--------------------------------------------|
        |Views       |Int         |number of views of the artwork              |
        |------------+------------+--------------------------------------------|
        |Adult       |Boolean     |if artwork contains adult content           |
        |------------+------------+--------------------------------------------|
        |Keywords    |Text        |keywords of artwork, 'art dessin ice' e.g.  |
        |------------+------------+--------------------------------------------|
        |Added       |Datetime    |scrapied time, format: YYYY-mm-DD HH:MM     |
        +------------+------------+--------------------------------------------+

        Args:
            self - instance of class Database

        """
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
        # connect database
        self.conn = sqlite3.connect(database_name)
        logger.debug('connected to database "%s".' % database_name)
        # create artwork table if not exists
        self.create_artwork_table()
        logger.debug('database initialized.')

    @staticmethod
    def attribute_dictionary_to_tuple(artwork):
        # given artwork dictionary, convert it to tuple using get ranther than []
        return (artwork.get('ID'), artwork.get('Name'), artwork.get('Width'),
        artwork.get('Height'), artwork.get('Author'), artwork.get('Posted'),
        artwork.get('Category'), artwork.get('Theme'), artwork.get('Species'),
        artwork.get('Gender'), artwork.get('Favorites'), artwork.get('Comments'),
        artwork.get('Views'), artwork.get('Adult'), artwork.get('Keywords'),
        artwork.get('Added'))

    def insert_or_replace_artwork(self, artwork):
        """
        Insert or replace(update) artwork record from given dictionary.

        Args:
            self - instance of class Database
            artwork - dictionary holds attributes of artwork
        """
        artwork['Adult'] = util.convert_boolean(artwork['Adult'])
        attribute_tuple = self.attribute_dictionary_to_tuple(artwork)
        self.conn.execute('INSERT OR REPLACE INTO ARTWORK (ID, NAME, WIDTH, HEIGHT, AUTHOR, '
                          'POSTED, CATEGORY, THEME, SPECIES, GENDER, FAVORITES, '
                          'COMMENTS, VIEWS, ADULT, KEYWORDS, ADDED) VALUES(?, ?, ?, '
                          '?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', attribute_tuple)
        self.conn.commit()
        logger.debug('inserted/replaced artwork information into artwork table.')

    def get_artwork_ids(self):
        """
        Retrieve all records' ID and return a list.

        Args:
            self - instance of class Database

        Returns:
            artwork_ids - a list of artworks' IDs,
            [26350907, 26350909, 26350911] e.g.
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT ID FROM ARTWORK')

        artwork_ids = list(map(lambda x : x.__getitem__(0), cursor.fetchall()))
# use map to get all ids from returned one-element tuples' list
        logger.debug('%u artworks retrieved from database.' % len(artwork_ids))
        return artwork_ids

    def delete_artworks(self, artwork_ids):
        """
        Delete artwork records in database given the artworks' IDs.

        Args:
            self - instance of class Database
            artwork_ids - container holds artwork ids
        """
        delete_count = 0
        for artwork_id in artwork_ids:
            self.conn.execute('DELETE FROM ARTWORK WHERE ID = ?', (artwork_id,))
            delete_count = delete_count + 1

        self.conn.commit() # will not call commit repeatedly
        logger.debug('%u artwork records deleted from database.' % delete_count)

    @staticmethod
    def if_time_expired(id_time_tuple, current_time, expire_time):
        # given (id, added_time), current time and expire time
        # returns True if expired
        # or False if hasn't expired
        if (util.parse_datetime(id_time_tuple[1]) - util.parse_datetime(current_time)) >= expire_time * 86400:
            return True
        else:
            return False

    def get_expired_artwork_ids(self, expire_time):
        """
        Given expire time, and return all expired artwork IDs' list.

        Args:
            self - instance of class method
            expire_time - expire time, days

        Returns:
            expired_artwork_ids - a list of all expired artwork IDs'
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT ID, ADDED FROM ARTWORK')

        current_time = util.get_current_time()

        # use filter and map to simplify code
        expired_records = filter(lambda t : self.if_time_expired(t, current_time, expire_time), cursor.fetchall())
        expired_artwork_ids = list(map(lambda x : x.__getitem__(0), expired_records))

        logger.debug('%u expired records retrieved from database.' % len(expired_artwork_ids))

        return expired_artwork_ids
