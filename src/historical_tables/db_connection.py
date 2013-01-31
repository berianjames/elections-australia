import MySQLdb
import logging

class SQLConnection(object):

  def __init__(self, host='localhost', user='', password='', db=''):
    self.db = MySQLdb.connect(host, user, password, db)
  
  
  def execute(self, sql):
    c = self.db.cursor()
    logging.info(sql)
    c.execute(sql)
    c.close()


  def fetch(self, sql):
    c = self.db.cursor()
    logging.info(sql)
    c.execute(sql)
    return [result for result in c.fetchall()]

    
  def close(self):
    self.db.commit()
    self.db.close()
