
from bs4 import BeautifulSoup
import requests, re

soup1 = BeautifulSoup(requests.get('https://www.va.gov/directory/guide/division.asp?dnum=1').text, 'html.parser')

VISN_URL_List = []
for link in soup1.find_all(class_='reglink'):
    VISN_URL_List.append(link.get('href'))


VISN_dict = {} #this has the cities for each VISN, with the VISN as the key

for i in range(0, len(VISN_URL_List)):
    soup2 = BeautifulSoup(requests.get('https://www.va.gov/directory/guide/' + VISN_URL_List[i]).text, 'html.parser')
    loc_set = set()
    table = soup2.find(summary='This table for formatting purposes only')

    category = ''
    for r in table.find_all('tr'):
        if not r.find('strong') == None:
            category = r.find('strong').contents[0]
        if category == 'VA Medical Center' or category == 'VA Health Care System':
            str = r.td.contents[-1].string
            if str != None and str != 'VA Health Care System' and str != 'VA Medical Center':
                loc = re.sub('[^a-zA-Z]', '', str.strip('()\r\n\t')[0:-4].lower())
                loc_set.add(loc)
        if category == 'Outpatient Clinic':
            break
    VISN_num = int(VISN_URL_List[i][-4:]) - 1000
    VISN_dict[VISN_num] = loc_set

print(VISN_dict)


