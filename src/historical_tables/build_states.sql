DROP TABLE IF EXISTS elections_australia.states;
CREATE TABLE elections_australia.states ( 
   code VARCHAR(3) NOT NULL PRIMARY KEY,
   name VARCHAR(30),
--   created_at DATE,
--   first_election_id INT,
   is_territory BOOLEAN
   );
INSERT INTO elections_australia.states VALUES 
   ('NSW', 'New South Wales', 0),
   ('VIC', 'Victoria', 0),
   ('QLD', 'Queensland', 0),
   ('SA', 'South Australia', 0),
   ('WA', 'Western Australia', 0),
   ('TAS', 'Tasmania', 0),
   ('NT', 'Northern Territory', 1),
   ('ACT', 'Australian Capital Territory', 1)
   ;
