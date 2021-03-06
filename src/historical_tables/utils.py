import os

def safe_id(id_raw):
  try:
    id = int(id_raw[0][0])
  except:
    id = "NULL"
  return id


def get_election_id(db, year, chamber):
  sql = "SELECT id FROM elections WHERE YEAR(election_date) = %s AND chamber = '%s'" % (
    year, chamber
    )
  id_raw = db.fetch(sql)
  return safe_id(id_raw)


def get_electorate_id(db, electorate, state, election_id):
  sql = """SELECT id FROM electorates WHERE election_id = %d AND electorate_name = "%s" AND state_code = '%s'""" % (
    election_id, electorate, state
    )
  id_raw = db.fetch(sql)
  return safe_id(id_raw)


def get_candidate_name_id(db, full_name):
  name_parts = full_name.split()
  last_name = name_parts[-1]
  first_name = name_parts[0] if name_parts[0] != 'Hon' else name_parts[1]
  sql = """SELECT id FROM candidate_names WHERE candidate_name LIKE "%s%%" AND candidate_name LIKE "%%%s%%" """ % (
    last_name, first_name
    )
  id_raw = db.fetch(sql)
  return safe_id(id_raw)


def get_candidacy_id(db, election_id, electorate_id, candidate_name_id):
  sql = """SELECT id FROM candidacies WHERE election_id = %s AND electorate_id = %s AND candidate_name_id = %s""" % (
    election_id, electorate_id, candidate_name_id
    )
  id_raw = db.fetch(sql)
  return safe_id(id_raw)


def get_election_years(base_dir):
  election_years = []
  for root, _, _ in os.walk(base_dir):
    lastdir = root.split('/')[-1]
    if lastdir.isdigit() is False:
      continue
    election_years.append(lastdir)
  return election_years


def get_election_files(base_dir, years, chamber, states=None):
  election_files = []
  if states is None:
    if chamber == 'house':
      txtfile = 'reps1.txt'
    elif chamber == 'senate':
      txtfile = 'senate1.txt'
    for year in years:
      election_files.append(base_dir + year + '/' + year + txtfile)
  else:
    for year in years:
      for state in states:
        if chamber == 'house':
          txtfile = 'reps' + state + '.txt'
        elif chamber == 'senate':
          txtfile = 'senate' + state + '.txt'
        fname = base_dir + year + '/' + year + txtfile
        if os.path.isfile(fname):
          election_files.append({'fname': fname, 'state': state, 'year': year, 'chamber': chamber})
  return election_files


def get_electorate_names(base_dir):
  electorate_names = []
  for root, d, files in os.walk(base_dir):
    for f in files:
      if f.endswith('.txt'):
        electorate_names.append(f)
  return electorate_names


def get_states():
  return ['act','nsw','sa','wa','qld','tas','nt','vic']
