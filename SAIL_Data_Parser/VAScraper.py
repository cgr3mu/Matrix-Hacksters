
from bs4 import BeautifulSoup
import requests, re, json, time, sys


if __name__ == '__main__':


    googleAPItoken = 'AIzaSyCgHDtwyWEUP-Cxl6x-IT03ZVVRikxwDi8'
    VISN_dict = {} #this has the cities for each VISN, with the VISN as the key

    t1 = time.clock()

    soup = BeautifulSoup(requests.get('https://www.va.gov/QUALITYOFCARE/measure-up/Strategic_Analytics_for_Improvement_and_Learning_SAIL.asp').text, 'html.parser')
    table = soup.find_all('tr')

    #HTML copied from the site https://www.va.gov/directory/guide/rpt_fac_list.cfm, since form submission is required.
    with open('AddressListHTML.txt', 'r') as f:
        addressListHTML = f.read()

    #this finds the top of the table listing the VISN's and the respective locations.
    VISN_iterator = BeautifulSoup(addressListHTML, 'html.parser').find(id='rpt')

    loc_count = 0

    # Overall strategy: get a list of addresses with their corresponding facility names for each VISN.
    # The SAIL data excel file names (variable location) correspond to either the city the facility is located in,
    # or a part of the facility name.  Therefore, to get the address for each location, cross-check the location
    # with each city in the VISN address list, and if that fails, cross-check the location with the facility
    # name.  This algorithm handles 142/145 cases, which is more than adequate for producing a visualization.

    for row in table:
        for element in row.find_all('td'):

            #each VISN header is an h3.
            VISN = element.find('h3').string.strip('\r\n\t ')

            #{"VISN 1": {"bedford": (34.1231, 92.3213), ...} , "VISN 2": {}, ...}
            VISN_dict[VISN] = {}

            #{"XYZ VA Medical Center": "1234 main street, Somewhere, MA, 01234"}
            addressMap = {}

            #This will effectively iterate through the next part of the table, i.e. the VISN.
            VISN_iterator = VISN_iterator.findNext('tbody')

            #Stop before outpatient clinics are analyzed (i.e. only parse VA health systems and medical centers.)
            while VISN_iterator.findNext('tr').getText() != 'Outpatient Clinic':
                #Advance VISN_iterator through each row that contains an address, recording the facility name
                #and the corresponding address.
                VISN_iterator = VISN_iterator.findNext('tr', {'class': ['hrpt hrptbgeven', 'hrpt hrptbgodd']})
                childList = VISN_iterator.findChildren()
                facilityName = childList[2].getText()
                cleanedAddress = re.sub('[\n\r\t\xa0]','',childList[3].getText().strip())

                #Some addresses have a hospital address + a mailing address -- only use the hospital address
                cleanedAddressArray = cleanedAddress.split(' ')
                if 'Mailing' in cleanedAddressArray:
                    cleanedAddress = ' '.join(cleanedAddressArray[0:cleanedAddressArray.index('Mailing')])

                #add the facilityName:cleanedAddress pair to the addressMap
                addressMap[facilityName] = cleanedAddress

            for location in element.find_all(target='_blank'):
                loc = re.sub('[^a-zA-Z]','',location.getText().lower())
                address = '-1'

                #The algorithm is as follows:
                #1) check if the location corresponds to a city in the list of facility addresses for the VISN. Since
                #some cities have multiple words, and some of the locations have the state abbr attached, check if location
                #exists in the city/state/zip part of the address.
                #2) If this fails, check if location is in the facility name.
                #
                #After this pattern matching, geocode the location, and add to the dictionary.

                for a in addressMap.values():
                    poss_address = re.split(' |,',a.lower())
                    if loc in ''.join(poss_address[-5:]).lower():
                        address = a
                if address == '-1':
                    for f in addressMap:
                        if loc in re.sub('[.|-]','',''.join(f.lower().split())):
                            address = addressMap[f]
                if address != '-1':
                    #geocode address using google maps API
                    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+address+'&key='+googleAPItoken)
                    latlong = response.json()['results'][0]['geometry']['location']
                    #add location:coordinates pair to the VISN
                    VISN_dict[VISN][loc] = (float(latlong['lat']), float(latlong['lng']))
                    loc_count += 1

            #monitor progress -- runtime takes ~60 s
            sys.stdout.write('\r' + VISN + ' analyzed. ' + 'Total Locations Geocoded: ' +  str(loc_count) +
                             '. Time Elapsed: ' + str(round(time.clock() - t1, 1)) + 's.')
            sys.stdout.flush()

    #write to text file for the other two scripts to use.
    with open('VISN_dict.txt','w') as f:
        f.write(json.dumps(VISN_dict, indent=4))