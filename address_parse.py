import usaddress
from uszipcode import SearchEngine

#Use zip code to get info; most reliable
def zip_coder(zipcode):
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
