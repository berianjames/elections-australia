# Retrieves election data for Australia, in countries/a/australia
wget -r -np -nH –cut-dirs=3 -R index.html http://psephos.adam-carr.net/countries/a/australia/

# Shift data down directory hierarchy
mv countries/a/australia .

# Fetch divisional data that is inaccessible with wget
python scrape-divisions-data.py

