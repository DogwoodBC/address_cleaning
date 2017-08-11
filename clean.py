import csv
import requests
import xml.etree.ElementTree as ET
import xmltodict
import argparse
from pprint import pprint
import googlemaps
import os
import sys

parser = argparse.ArgumentParser(description='Clean addresses using geocoder.ca service.')
parser.add_argument('-f', metavar='N', type=str, help='a name for the file to clean up.  Must be a csv.')
parser.add_argument('-o', metavar='N', type=str, help='a name for the output file.  Must be a csv.')
parser.add_argument('-g', type=bool, help='Include google geocoder.  Rate limit is 2500 requests/day, 50/s.')

args = parser.parse_args()

# This will throw error with no input -f since we're not committing this file
file_name = args.f if args.f else "dogwood_sample_address_data.csv"
write_file_name = args.o if args.o else "output.csv"
google_flag = args.g if args.g else False

gmaps = googlemaps.Client(key=os.environ['GOOGLEMAPS_KEY'])



def query_geocoder_ca(row):
    street = row['Primary Street']
    province = row['Primary Province/State']
    city = row['Primary City']
    query = "addresst=" + street + "&prov=" + province
    if(len(city) > 0):
        query += "&city=" + city
    url =  "http://geocoder.ca/?" + query + "&geoit=XML"
    r = requests.get(url)
    result = xmltodict.parse(r.text)
    return result

def query_google_api(row):
    # TODO modify the query to dict
    street = row['Primary Street']
    province = row['Primary Province/State']
    city = row['Primary City']
    query = street + ' ' + city + ' ' + province
    geocode_result = gmaps.geocode(query)
    return geocode_result

def add_geocoder_result(row, result, prefix):
    geodata = result['geodata']
    error = geodata.get("error", "")
    if(error != ""):
        print(error['description'])
        return row
    else:
        if(float(geodata['standard']['confidence']) > 0.1):
            try:
                row[prefix + 'No.'] = geodata['standard']['stnumber']
                row[prefix + 'Address'] = geodata['standard']['staddress']
                row[prefix + 'City'] = geodata['standard']['city']
                row[prefix + 'Postal Code'] = geodata.get('postal')
                row[prefix + 'Long'] = geodata.get('longt')
                row[prefix + 'Lat'] = geodata.get('latt')
                row[prefix + 'confidence'] = geodata['standard']['confidence']
                return row
            except KeyError as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, exc_tb.tb_lineno)
                print("Information missing in match {}", geodata)
                return row

def add_google_result(row, result, prefix):
    try:
        if(isinstance(result, list)):
            result = result[0]
        address_data = result['address_components']
        geometry = result['geometry']

        # TODO: verity location is in BC
        locality = [item for item in address_data if 'locality' in item['types']][0]
        administrative_area_level_1 = [item for item in address_data if 'administrative_area_level_1' in item['types']][0]
        postal_code = [item for item in address_data if 'postal_code' in item['types']][0]
        row[prefix + 'No.'] = address_data[0]['short_name']
        row[prefix + 'Address'] = address_data[1]['short_name']
        row[prefix + 'City'] = locality['short_name'] if locality else administrative_area_level_1['short_name']
        row[prefix + 'Postal Code'] = postal_code['short_name']
        row[prefix + 'Long'] = geometry['location']['lng']
        row[prefix + 'Lat'] = geometry['location']['lat']
        return row
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("Error processing result returned from Google geocoding API.")
        print(exc_type, exc_tb.tb_lineno)
        print(result)



print("Opening " + file_name)
print("Outputting to " + write_file_name)

with open(file_name) as csvfile:
    addresses = csv.DictReader(csvfile)
    with open(write_file_name, 'w') as csvfile2:
        prefix = "Geocoder "
        google_prefix = "Google "
        fieldnames = ['Primary Street', 'Primary City', 'Primary Province/State', 'Primary Postal Code/Zip', 'Contact ID',
        prefix + 'confidence',
        prefix + 'No.',
        prefix + 'Address',
        prefix + 'City',
        prefix + 'Postal Code',
        prefix + 'Long',
        prefix + 'Lat']
        google_api_fieldnames = [
        google_prefix + 'No.',
        google_prefix + 'Address',
        google_prefix + 'City',
        google_prefix + 'Postal Code',
        google_prefix + 'Long',
        google_prefix + 'Lat'
        ]
        if(google_flag == True):
            fieldnames = fieldnames + google_api_fieldnames
        writer = csv.DictWriter(csvfile2, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        for row in addresses:
            geocoder_result = query_geocoder_ca(row)
            row = add_geocoder_result(row, geocoder_result, prefix)
            if(google_flag):
                google_result = query_google_api(row)
                add_google_result(row, google_result, google_prefix)
            writer.writerow(row)
