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
    self.db.execute('DROP TABLE IF EXISTS candidacies;')
    self.db.execute("""
     CREATE TABLE candidacies (
       id INT NOT NULL AUTO_INCREMENT,
       election_id INT,
       electorate_id INT,
       state_code VARCHAR(3),
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


  def _re_parse_index_entry(self, entry):
    index_content = list()
    g = re.search('>\s(.+, .+ \(.+, .+\)):\s(.+)|>\s(.+, .+):\s(.+)|>\s(.+, .+):|>\s(.+, .+),\s(.+)|>\s(.+):\s(.+)|>\s(.+, .+)\s(.+)', entry)
    for group in g.groups():
      if group is not None:
        index_content.append(group)
    return {index_content[0]: index_content[1]} if len(index_content) == 2 else None


  def _re_parse_index_alias(self, entry):
    alias_content = list()
    g = re.search('<\s(.+): see (.+)|<\s(.+) \(see (.+)\)', entry)
    for group in g.groups():
      if group is not None:
        alias_content.append(group)
    return {alias_content[0]: alias_content[1]} if len(alias_content) == 2 else None


  def _re_parse_mistaken_entry(self, entry):
    index_content = list()
    g = re.search('<\s(.+): (.+)', entry)
    for group in g.groups():
      if group is not None:
        index_content.append(group)
    return {index_content[0]: index_content[1]} if len(index_content) == 2 else None


  def parse_index_and_cross_reference(self, candidate_index_raw):
    index = dict()
    cross_ref = dict()
    for entry in candidate_index_raw:
      if entry.startswith('>'):
        try:
          index.update(self._re_parse_index_entry(entry))
        except:
          logging.warn('Cannot parse: ' + entry)
      elif entry.startswith('<') and len(re.findall('\d+', entry)) == 0:
        cross_ref.update(self._re_parse_index_alias(entry))
      elif entry.startswith('<') and len(re.findall('\d+', entry)) != 0:
        index.update(self._re_parse_mistaken_entry(entry))
    return index, cross_ref


  def write_candidates_table(self, candidate_index):
    states_short, states_long = zip(*self.db.fetch('SELECT code, state_name FROM states'))
    for candidate, elections in candidate_index.iteritems():
      self.db.execute("""INSERT INTO candidate_names (candidate_name) VALUES ("%s")""" % candidate)
      for electorates in elections.split(','):
        electorate_years = electorates.split()
        state = [el for el in electorate_years if el.upper() in states_short]
        if len(state) == 1:
          state = state[0]
          state_ix = electorate_years.index(state)
          electorate = ' '.join(electorate_years[:state_ix])
          state_code = state.upper()
          years = electorate_years[state_ix+1:]
        else:
          state = [state for state in states_long if state in electorates]
          if len(state) == 1:
            state = state[0]
            electorate, allyears = electorates.split(state)
            state_code = states_short[states_long.index(state)]
            years = allyears.split()
            if len(electorate) == 0: electorate = state
          else:
            try:
              state = 'NULL'
              state_code = 'NULL'
              electorate, allyears = electorates.split(' ',1)
              years = allyears.split()
            except:
              continue
        for year in years:
          if not (year.startswith('1') or year.startswith('2')):
            continue # Catch bad parsing
          if year.endswith('b') or year.endswith('b*'):
            continue # Exclude bielections
          safe_year = year[:4]
          was_elected = 1 if year.endswith('*') else 0
          if electorate == 'Senate':
            election_id = utils.get_election_id(self.db, safe_year, 'senate')
            electorate_id = "NULL"
          else:
            election_id = utils.get_election_id(self.db, safe_year, 'house')
            electorate_id = utils.get_electorate_id(self.db, electorate, state_code, election_id) if election_id is not "NULL" else "NULL"
          if election_id is "NULL":
            logging.warn(candidate+' '+electorate+' '+state+' '+year)
          candidate_sql = """SELECT id FROM candidate_names WHERE candidate_name = "%s" """ % candidate
          candidate_name_id = utils.safe_id(self.db.fetch(candidate_sql))
          insert_str = """INSERT INTO candidacies (election_id, electorate_id, state_code, candidate_name_id, was_elected)
                          VALUES ({election_id}, {electorate_id}, '{state_code}', "{candidate_name_id}", {was_elected})"""
          insert_sql = insert_str.format(election_id=election_id, electorate_id=electorate_id, state_code=state_code, candidate_name_id=candidate_name_id, was_elected=was_elected)
          self.db.execute(insert_sql)
          

if __name__ == '__main__':
  table_builder = CandidatesTableBuilder(host='localhost',
                                          user='berian', 
                                          database='elections_australia')
  table_builder.build()




