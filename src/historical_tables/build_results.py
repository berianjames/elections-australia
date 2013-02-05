import os
import logging
import utils
import re
from db_connection import SQLConnection

BASE_DIR = 'data/australia/'

logging.basicConfig(level=logging.INFO)

class CandidatesTableBuilder(object):
  
  def __init__(self, host, user, database):
    self.db = SQLConnection(host=host, user=user, db=database)


  def build(self):
    self.create_electorates_table()
    states = utils.get_states()
    election_years = utils.get_election_years(base_dir=BASE_DIR)
    house_files = utils.get_election_files(BASE_DIR, election_years, 'house', states)
    for hfile in election_files:
      self.parse_candidate_data(hfile)

  
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


  def _get_election_id(self, year, chamber):
    sql = "SELECT id FROM elections WHERE YEAR(election_date) = %s AND chamber = '%s'" % (
      year, chamber
      )
    id_raw = self.db.fetch(sql)
    return int(id_raw[0][0])


  def _get_electorate_id(self, electorate_name, election_id):
    sql = "SELECT id FROM electorates WHERE election_id = %d AND electorate_name = '%s'" % (
      election_id, electorate_name
      )
    id_raw = self.db.fetch(sql)
    return int(id_raw[0][0])


  def _get_party_dict(self, party_chunk):
    party_dictionary = {}
    for entry in party_chunk:
      if len(entry) == 0:
        continue
      elif entry[0] != '*':
        continue
      split_entry = re.split('\s+',entry)
      party_code = split_entry[1]
      party_name = ' '.join(split_entry[3:])
      party_dictionary[party_name] = [party_code]
    return party_dictionary


  def _get_electorate_info(self, chunk):
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
    return electorate_name, electorate_enrolled, electorate_ballots


  def create_candidates_table(self):
    self.db.execute('DROP TABLE IF EXISTS candidates;')
    self.db.execute("""
     CREATE TABLE candidates (
       id INT NOT NULL AUTO_INCREMENT,
       election_id INT,
       electorate_id INT,
       party_id INT,
       candidate_name VARCHAR(50),
       PRIMARY KEY(id)
       );
     """ )


  def parse_candidate_data(self, fileinfo):
    fname = fileinfo[0]
    election_id = self._get_election_id(fileinfo[2], fileinfo[3])
    with open(fname, 'r') as f:
      lines = [line.strip() for line in f]
      breaks = [i for i,x in enumerate(lines) if '===' in x]
      electorate_chunks = [lines[breaks[i]-1:breaks[i+1]-1] 
                           for i in range(len(breaks[:-1]))]
      electorate_chunks.append(lines[breaks[-1]-1:])
      electorate_party_dict = self._get_party_dict(electorate_chunk[0])
      for chunk in electorate_chunks[2:]:
        electorate_name, _, _ = self._get_electorate_info(chunk)
        electorate_id = self._get_electorate_id(electorate_name, election_id)
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




