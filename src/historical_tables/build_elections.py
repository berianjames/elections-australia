import os
import logging
from db_connection import SQLConnection
import utils

BASE_DIR = 'data/australia/'

logging.basicConfig(level=logging.INFO)

class ElectionsTableBuilder(object):
  
  def __init__(self, host, user, database):
    self.db = SQLConnection(host=host, user=user, db=database)


  def build(self):
    self.create_elections_table()
    years = utils.get_election_years(base_dir=BASE_DIR)
    self.populate_elections_table(years)

  
  def __del__(self):
    self.db.close()


  def create_elections_table(self):
    self.db.execute('DROP TABLE IF EXISTS elections;')
    self.db.execute("""
     CREATE TABLE elections (
       id INT NOT NULL AUTO_INCREMENT,
       level ENUM('federal', 'state'),
       chamber ENUM('house', 'senate', 'legislative_assembly', 'legislative_council'),
       election_date DATE,
       is_byelection BOOLEAN,
       PRIMARY KEY(id)
       );
     """ )

  
  def _populate_election_table_element(self, year, chamber):
    if chamber == 'house':
      txtfile = 'reps1.txt'
    elif chamber == 'senate':
      txtfile = 'senate1.txt'
    fname = BASE_DIR + year + '/' + year + txtfile
    if not os.path.isfile(fname):
      logging.info(' '.join(['No', chamber, 'results file in', year, ". Continuing.\n"]))
      return
    with open(fname, 'r') as f:
      headline = f.readline()
      election_day, election_month, election_year = headline.strip().split(' ')[-3:]
      if election_year == '1901':
        election_day = '29'
      election_date_str = ' '.join([election_day, election_month, election_year])
      sql = """
        INSERT INTO elections (level, chamber, election_date)
        VALUES ('%s', '%s', STR_TO_DATE('%s', '%%d %%M %%Y'), %d)
      """ % ('federal', chamber, election_date_str, 0)
      self.db.execute(sql)


  def populate_elections_table(self, election_years):
    for year in election_years:
      self._populate_election_table_element(year, 'house')
      self._populate_election_table_element(year, 'senate')


if __name__ == '__main__':
  table_builder = ElectionsTableBuilder(host='localhost',
                                       user='berian', 
                                       database='elections_australia')
  table_builder.build()




