import os
import logging
import utils
import re
from db_connection import SQLConnection

BASE_DIR = 'data/australia/'

logging.basicConfig(level=logging.INFO)

class PartiesTableBuilder(object):
  
  def __init__(self, host, user, database):
    self.db = SQLConnection(host=host, user=user, db=database)


  def build(self):
    self.create_parties_table()
    states = utils.get_states()
    election_years = utils.get_election_years(base_dir=BASE_DIR)
    house_files = utils.get_election_files(BASE_DIR, election_years, 'house', states)
    senate_files = utils.get_election_files(BASE_DIR, election_years, 'senate', states)
    party_dictionary = {}
    for fdata in house_files:
      self.parse_party_data(fdata, party_dictionary)
    for sdata in senate_files:
      self.parse_party_data(sdata, party_dictionary)
    self.insert_party_data(party_dictionary)
  
  def __del__(self):
    self.db.close()


  def _get_election_id(self, year, chamber):
    sql = "SELECT id FROM elections WHERE YEAR(election_date) = %s AND chamber = '%s'" % (
      year, chamber
      )
    id_raw = self.db.fetch(sql)
    return int(id_raw[0][0])


  def create_parties_table(self):
    self.db.execute('DROP TABLE IF EXISTS parties;')
    self.db.execute("""
     CREATE TABLE parties (
       id INT NOT NULL AUTO_INCREMENT,
       party_code VARCHAR(5),
       party_name VARCHAR(50),
       party_code_alt VARCHAR(5),
       PRIMARY KEY(id)
       );
     """ )


  def parse_party_data(self, fileinfo, party_dictionary):
    fname = fileinfo['fname']
    with open(fname, 'r') as f:
      lines = [line.strip() for line in f]
      breaks = [i for i,x in enumerate(lines) if '===' in x]
      if len(breaks) < 2:
        return
      party_chunk = lines[breaks[0]-1:breaks[1]-1]
      for entry in party_chunk:
        if len(entry) == 0:
          continue
        elif entry[0] != '*':
          continue
        split_entry = re.split('\s+',entry)
        party_code = split_entry[1]
        party_name = ' '.join(split_entry[3:])
        if party_name not in party_dictionary:
          party_dictionary[party_name] = [party_code]
        elif party_code not in party_dictionary[party_name]:
          party_dictionary[party_name].append(party_code)


  def insert_party_data(self, party_dictionary):
    for party in party_dictionary:
      if len(party_dictionary[party])==1:
        party_code = party_dictionary[party][0]
        party_code_alt = 'NULL'
      else:
        party_code = party_dictionary[party][0]
        party_code_alt = party_dictionary[party][1]
      if 'Emergency Committee' in party:
        party = 'Emergency Committee'
      sql = """
        INSERT INTO parties (party_name, party_code, party_code_alt)
        VALUES ('%s', '%s', '%s')
      """ % (party, party_code, party_code_alt)
      self.db.execute(sql)
          

if __name__ == '__main__':
  table_builder = PartiesTableBuilder(host='localhost',
                                      user='berian', 
                                      database='elections_australia')
  table_builder.build()




