import sys
import urllib
from bs4 import BeautifulSoup

BASE_SITE = 'http://psephos.adam-carr.net/countries/a/australia/'
class PsephScraper(object):
  """Web scraper for divisions data, which is 
  irretrievable using wget"""
  def __init__(self, ext_folder='divisions/', ext_page='divisions.shtml'):
    self.base_site = BASE_SITE
    self.ext_folder = ext_folder
    self.base_page = self.base_site + self.ext_folder + ext_page
    return


  def scrape(self):
    base_soup = self.soup_base_page()
    sublinks = self.gather_sublinks(base_soup)
    self.retrieve_data_from_sublinks(sublinks)
    

  def soup_base_page(self):
    return BeautifulSoup(urllib.urlopen(self.base_page))


  def gather_sublinks(self, soup):
    sublinks_full = soup('h3')[0]('a')
    sublinks_divisions = sublinks_full[:-1] # Exclude 'back to top' link
    sublinks = []
    for sublink in sublinks_divisions:
      rel_href = sublink.attrs['href']
      sublinks.append(self.base_site + self.ext_folder + rel_href.split('/')[-1])
    return sublinks


  def retrieve_data_from_sublinks(self, sublinks):
    for sublink in sublinks:
      outfile = 'australia/' + self.ext_folder +sublink.split('/')[-1]
      print sublink, outfile
      urllib.urlretrieve(sublink, filename=outfile)


def main(argv):
  pseph_scraper = PsephScraper()
  pseph_scraper.scrape()


if __name__ == "__main__":
  sys.exit(main(sys.argv[1:]))
