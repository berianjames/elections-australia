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
    self.base_dir = BASE_DIR + 'candidates/'


  def __del__(self):
    self.db.close()


  def build(self):
    self.create_candidates_tables()
    candidate_files = self.get_candidate_files()
    candidate_index_raw = self.get_candidate_index(candidate_files)
    candidate_index, cross_ref = self.parse_index_and_cross_reference(candidate_index_raw)
    self.write_candidates_table(candidate_index)


  def create_candidates_tables(self):
    self.db.execute('DROP TABLE IF EXISTS candidates;')
    self.db.execute("""
     CREATE TABLE candidates (
       id INT NOT NULL AUTO_INCREMENT,
       election_id INT,
       electorate_id INT,
       candidate_name_id INT,
       was_elected BOOLEAN,
       PRIMARY KEY(id)
       );
     """ )
    self.db.execute('DROP TABLE IF EXISTS candidate_names;')
    self.db.execute("""
     CREATE TABLE candidate_names (
       id INT NOT NULL AUTO_INCREMENT,
       candidate_name VARCHAR(50),
       PRIMARY KEY(id)
       );
     """ )


  def get_candidate_files(self):
    fnames = []
    for root, _, files in os.walk(self.base_dir):
      [fnames.append(root + end) for end in files 
       if 'intro.txt' not in end and '.shtml' not in end]
    return fnames


  def get_candidate_index(self, fnames):
    candidate_index_raw = []
    for fname in fnames:
      with open(fname, 'r') as candidate_file:
        for line in candidate_file.readlines():
          if line.startswith('>') or line.startswith('<'):
            candidate_index_raw.append(line.strip())
          elif line.startswith('   '):
            candidate_index_raw[-1] += ' '+line.strip()
    return candidate_index_raw


  def cross_reference(self, candidate_index_raw):
    index = []
    for entry in candidate_index_raw:
      index_content = []
      if entry.startswith('>'):
        g = re.search('>\s(.+, .+ \(.+, .+\)):\s(.+)|>\s(.+, .+):\s(.+)|>\s(.+, .+):|>\s(.+, .+),\s(.+)|>\s(.+):\s(.+)|>\s(.+, .+)\s(.+)', entry)
        for group in g.groups():
          if group is not None:
            index_content.append(group)
        if len(index_content) == 2:
          index.append({index_content[0]: index_content[1]})
      elif entry.startswith('<'):
        print entry
    return index


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
  table_builder = CandidatesTableBuilder(host='localhost',
                                          user='berian', 
                                          database='elections_australia')
  table_builder.build()




