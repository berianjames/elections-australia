import os
import logging
import utils
import re
import copy
from db_connection import SQLConnection

BASE_DIR = 'data/australia/'

logging.basicConfig(level=logging.INFO)

class ResultsTableBuilder(object):
  
  def __init__(self, host, user, database):
    self.db = SQLConnection(host=host, user=user, db=database)


  def build(self):
    self.create_results_table()
    states = utils.get_states()
    election_years = utils.get_election_years(base_dir=BASE_DIR)
    house_files = utils.get_election_files(BASE_DIR, election_years, 'house', states)
    for hfile in house_files:
      self.parse_results_data(hfile)

  
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


  def _get_party_dict(self, party_chunk):
    party_dictionary = {}
    for entry in party_chunk:
      if len(entry) == 0:
        continue
      elif entry[0] != '*':
        continue
      split_entry = re.split('\s+',entry)
      party_code = split_entry[1].upper()
      party_name = ' '.join(split_entry[3:])
      party_dictionary[party_code] = party_name
    return party_dictionary


  def _get_electorate_info(self, chunk):
    headline = re.split('\s\s\s+', chunk[0])
    if len(headline) == 1:
      return None, None, None
    electorate_name = headline[0].split(',')[0].title()
    electorate_counts = self._parse_counts_line(re.split('[\s,]',headline[1]))
    electorate_enrolled = electorate_counts[0]
    if len(electorate_counts) > 1:
      electorate_ballots = electorate_counts[1]
    else:
      electorate_ballots = "NULL"
    return electorate_name, electorate_enrolled, electorate_ballots


  def create_results_table(self):
    self.db.execute('DROP TABLE IF EXISTS results;')
    self.db.execute("""
     CREATE TABLE results (
       id INT NOT NULL AUTO_INCREMENT,
       election_id INT,
       electorate_id INT,
       candidate_name_id INT,
       candidacy_id INT,
       ballot_name VARCHAR(50),
       party_code VARCHAR(5),
       votes INT,
       pct DECIMAL(3,1),
       tpp_votes INT,
       tpp_pct DECIMAL(3,1),
       PRIMARY KEY(id)
       );
     """ )

  def _parse_ballot_counts(self, ballot_data):
    ballot_dict = dict()
    pct_exact_pattern = re.compile('^\d{2}\.\d$')
    delta_pct_exact_pattern = re.compile('^\({0,1}[\+\-\s]\d{2}\.\d\){0,1}$')
    pct_pattern = re.compile('\d{2}\.\d')
    delta_pct_pattern = re.compile('\({0,1}[\+\-\s]\d{2}\.\d\){0,1}')
    votes_pattern = re.compile('\d{0,3}\,{0,1}\d{1,3}')
    for entry in ballot_data:
      entry = entry.replace('\x92', "'").replace('\xb9',"'")
      entry_data = re.split('\s{2,}',entry)
      if len(entry) < 20 or len(entry_data) < 1 or ':' in entry or entry.startswith('>'):
        continue
      if entry_data[-1] == 'Unopposed':
        name = entry_data[0]
        namekey = name.translate(None,'*+').strip().title()
        ballot_dict.update({namekey: dict()})
        last_name = name.translate(None,'*+').split()[-1].title()
        ballot_dict[namekey].update({'full_name': namekey.title()})
        is_incumbent = 1 if name.endswith('*') or name.endswith('+') else 0
        ballot_dict[namekey].update({'is_incumbent': is_incumbent})
        ballot_dict[namekey].update({'is_elected': 1})
        ballot_dict[namekey].update({'votes': 'NULL'})
        ballot_dict[namekey].update({'tpp_votes': 'NULL'})
        ballot_dict[namekey].update({'tpp_pct': 100})
        ballot_dict[namekey].update({'pct': 100})
        ballot_dict[namekey].update({'delta_pct': 'NULL'})
        party_code = entry_data[1] if entry_data[1].isalpha() else 'NULL'
        ballot_dict[namekey].update({'party': party_code})
      elif 'informal' in entry and votes_pattern.search(entry) is not None:
        namekey = 'Informal'
        ballot_dict.update({namekey: dict()})
        ballot_dict[namekey].update({'tpp_votes': 'NULL'})
        if 'unknown' in entry:
          ballot_dict[namekey].update({'votes': 'NULL'})
          ballot_dict[namekey].update({'pct': 'NULL'})
        else:
          votes = int(votes_pattern.match(entry).group().replace(',',''))
          pct = float(pct_pattern.search(entry).group())
          ballot_dict[namekey].update({'votes': votes})
          ballot_dict[namekey].update({'pct': pct})
      elif (pct_exact_pattern.match(entry_data[-1]) is not None or
            delta_pct_exact_pattern.match(entry_data[-1]) is not None
            ):
        name = entry_data[0]
        if name.replace(',','').isdigit():
          continue
        name_parts = name.translate(None,'*+').split()
        last_name = name.translate(None,'*+').split()[-1]
        if len(name_parts[0]) == 1: 
          namekey = ' '.join(name_parts).title()
          if namekey in ballot_dict:
            namekey = ' '.join(name_parts).title()
            _ = name_parts.pop(0)
          else:
            namekey = last_name.title()
        else:
          namekey = last_name.title()

        if len(name_parts) > 1 or name == 'Strider':
          if namekey in ballot_dict:
            prev_name = copy.deepcopy(ballot_dict[namekey]['full_name'])
            if name_parts[0] != 'Hon':
              new_name = ' '.join([prev_name[0], prev_name.split()[-1]])
            else:
              new_name = ' '.join([prev_name[1], prev_name.split()[-1]])
            ballot_dict.update({new_name: copy.deepcopy(ballot_dict[namekey])})
            del ballot_dict[namekey]
            namekey = ' '.join([name[0], namekey])
          ballot_dict.update({namekey: dict()})
          ballot_dict[namekey].update({'full_name': ' '.join(name_parts).title()})
          is_incumbent = 1 if name.endswith('*') else 0
          ballot_dict[namekey].update({'is_incumbent': is_incumbent})
          is_elected = 1 if last_name == last_name.upper() else 0
          ballot_dict[namekey].update({'is_elected': is_elected})
          votes = int(votes_pattern.search(entry).group().replace(',',''))
          ballot_dict[namekey].update({'votes': votes})
          ballot_dict[namekey].update({'tpp_votes': votes})
          pct = float(pct_pattern.search(entry).group())
          ballot_dict[namekey].update({'pct': pct})
          party_code = entry_data[1] if entry_data[1].isalpha() else 'NULL'
          ballot_dict[namekey].update({'party': party_code})
          try:
            delta_pct = float(delta_pct_pattern.search(entry).group().translate(None,'()'))
          except AttributeError:
            delta_pct = 'NULL'
          ballot_dict[namekey].update({'delta_pct': delta_pct})
        else:
          pref_votes = int(votes_pattern.search(entry).group().replace(',',''))
          ballot_dict[namekey]['tpp_votes'] += pref_votes
          is_elected = 1 if last_name == last_name.upper() else 0
          ballot_dict[namekey].update({'is_elected': is_elected})

    if len(ballot_dict) >= 2:
      tpp_dict = dict()
      for k, v in ballot_dict.iteritems():
        if k != 'Informal':
          tpp_dict.update({k: v['tpp_votes']})
      top_tpp = sorted(tpp_dict.items(), key=lambda x: x[1], reverse=True)[:2]
      top_names, top_votes = zip(*top_tpp)
      vote_total = top_votes[0] + top_votes[1]
      for k in ballot_dict.iterkeys():
        if k not in top_names:
          ballot_dict[k].update({'tpp_votes': "NULL"})
          ballot_dict[k].update({'tpp_pct': "NULL"})
        else:
          tpp_pct = float(tpp_dict[k]) / vote_total * 100
          ballot_dict[k].update({'tpp_pct': tpp_pct })
    return ballot_dict

  def parse_results_data(self, fileinfo):
    fname = fileinfo['fname']
    election_id = utils.get_election_id(self.db, fileinfo['year'], fileinfo['chamber'])
    with open(fname, 'r') as f:
      lines = [line.strip() for line in f]
      breaks = [i for i,x in enumerate(lines) if '===' in x]
      electorate_data = [lines[breaks[i]-1:breaks[i+1]-1] 
                         for i in range(len(breaks[:-1]))]
      electorate_data.append(lines[breaks[-1]-1:])
      party_dict = self._get_party_dict(electorate_data[0])
      for electorate in electorate_data[3:]:
        electorate_name, _, _ = self._get_electorate_info(electorate)
        if electorate_name is None:
          continue
        electorate_id = utils.get_electorate_id(self.db, electorate_name, fileinfo['state'], election_id)
        logging.info(electorate_name + ' ' +fileinfo['year'])
        ballot_counts = self._parse_ballot_counts(electorate)
        logging.info(ballot_counts)
        for candidate in ballot_counts.iterkeys():
          if candidate != 'Informal':
            ballot_name = ballot_counts[candidate]['full_name']
            candidate_name_id = utils.get_candidate_name_id(self.db, ballot_counts[candidate]['full_name'])
            candidacy_id = utils.get_candidacy_id(self.db, election_id, electorate_id, candidate_name_id)
            party_code = ballot_counts[candidate]['party']
            votes = ballot_counts[candidate]['votes']
            pct = ballot_counts[candidate]['pct']
            tpp_votes = ballot_counts[candidate]['tpp_votes']
            tpp_pct = ballot_counts[candidate]['tpp_pct']
          else:
            ballot_name = 'NULL'
            candidate_name_id = 'NULL'
            candidacy_id = 'NULL'
            party_code = 'NULL'
            votes = ballot_counts[candidate]['votes']
            pct = ballot_counts[candidate]['pct']
            tpp_votes = 'NULL'
            tpp_pct = 'NULL'
          sql = """
            INSERT INTO results (election_id, electorate_id, candidate_name_id, candidacy_id, ballot_name, party_code, votes, pct, tpp_votes, tpp_pct)
            VALUES (%s, %s, %s, %s, """ % (election_id, electorate_id, candidate_name_id, candidacy_id)
          sql += '"%s", ' % ballot_name if ballot_name != 'NULL' else 'NULL, '
          sql += '"%s", ' % party_code if party_code != 'NULL' else 'NULL, '
          sql += "%s, %s, %s, %s)" % (votes, pct, tpp_votes, tpp_pct)
          self.db.execute(sql)
          

if __name__ == '__main__':
  table_builder = ResultsTableBuilder(host='localhost',
                                      user='berian',
                                      database='elections_australia')
  table_builder.build()




