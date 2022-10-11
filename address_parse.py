import usaddress
from uszipcode import SearchEngine
import re

def zip_tester(zipcode):
    search = SearchEngine()
    zipcode_info = search.by_zipcode(zipcode)
    print(zipcode_info.to_dict())

#Use zip code to get info; most reliable
def zip_coder(address):
    zipcode = address[address.rfind(' ') + 1:]
    if len(zipcode) > 5:
        zipcode = zipcode[:5]
    search = SearchEngine()
    zipcode_info = search.by_zipcode(zipcode)
    try:
        zip_dict = zipcode_info.to_dict()
        return [zip_dict['major_city'], zipcode, zip_dict['state']]
    except AttributeError as error:
        # Some local zip codes are missing
        if zipcode == '37423':
            return ['Chattanooga', zipcode, 'TN']
        return ['', '', '']
    

def address_parser(address):
    address = address.replace(',', '')
    street_address = ''
    city = ''
    if 'homeless' in address.lower():
        street_address = 'homeless'
        address = address.lower().replace('homeless', '')
    
    parsed_address = usaddress.parse(address)
    #print(parsed_address)
    for addr_bit in parsed_address:
        tag = addr_bit[1]
        info = addr_bit[0]
        if tag == 'AddressNumber':
            street_address += info + ' '
        elif 'StreetName' in tag:
            street_address += info + ' '
        elif 'Occupancy' in tag:
            street_address += info + ' '
        elif 'PlaceName' in tag:
            city += info + ' '
    return [street_address.strip(), city.strip()]

#print(address_parser('HOMELESS CHATTANOOGA, TN 37416'))
#print(zip_coder(address='201 E ST CHATTANOOGA, 37423'))
#zip_tester('37423')