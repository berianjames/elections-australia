import os
import logging
import utils
import re
from db_connection import SQLConnection

BASE_DIR = 'data/australia/'

logging.basicConfig(level=logging.INFO)

class ElectoratesTableBuilder(object):
  
  def __init__(self, host, user, database):
    self.db = SQLConnection(host=host, user=user, db=database)


  def build(self):
    self.base_dir = BASE_DIR + 'divisions/'
    self.create_electorates_table()
    states = utils.get_states()
    election_years = utils.get_election_years(base_dir=BASE_DIR)
    election_files = utils.get_election_files(BASE_DIR, election_years, 'house', states)
    for efile in election_files:
      self.parse_electorate_file(efile)

  
  def __del__(self):
    self.db.close()


  def _parse_counts_line(self, line):
    output = []
    buff = ''
    while len(line) > 0:
      item = line.pop(0)
      if item.isdigit():
        buff += item
        continue
      else:
        if len(buff) > 0:
          output.append(int(buff))
        buff = ''
        continue
    return output

    
  def _to_int(self, string):
    return int(string.replace(',','').replace('.',''))


  def create_electorates_table(self):
    self.db.execute('DROP TABLE IF EXISTS electorates;')
    self.db.execute("""
     CREATE TABLE electorates (
       id INT NOT NULL AUTO_INCREMENT,
       election_id INT,
       state_code VARCHAR(3),
       electorate_name VARCHAR(30),
       enrollments INT,
       ballots INT,
       PRIMARY KEY(id)
       );
     """ )


  def parse_electorate_file(self, fileinfo):
    fname = fileinfo[0]
    state_code = fileinfo[1].upper()
    election_id = utils.get_election_id(self.db, fileinfo[2], 'house')
    with open(fname, 'r') as f:
      lines = [line.strip() for line in f]
      breaks = [i for i,x in enumerate(lines) if '===' in x]
      electorate_chunks = [lines[breaks[i]-1:breaks[i+1]-1] 
                           for i in range(len(breaks[:-1]))]
      electorate_chunks.append(lines[breaks[-1]-1:])
      for chunk in electorate_chunks[2:]:
        headline = re.split('\s\s\s+', chunk[0])
        if len(headline) == 1:
          continue
        electorate_name = headline[0].split(',')[0].title()
        electorate_counts = self._parse_counts_line(re.split('[\s,]',headline[1]))
        electorate_enrolled = electorate_counts[0]
        if len(electorate_counts) > 1:
          electorate_ballots = electorate_counts[1]
        else:
          electorate_ballots = "NULL"
        sql = """
          INSERT INTO electorates (election_id, state_code, electorate_name, enrollments, ballots)
          VALUES (%d, '%s', "%s", %d, %s)
        """ % (election_id, state_code, electorate_name, electorate_enrolled, electorate_ballots)
        self.db.execute(sql)
          

if __name__ == '__main__':
  table_builder = ElectoratesTableBuilder(host='localhost',
                                          user='berian', 
                                          database='elections_australia')
  table_builder.build()




