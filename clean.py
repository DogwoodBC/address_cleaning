import csv
import requests
import xml.etree.ElementTree as ET
import xmltodict
import argparse

parser = argparse.ArgumentParser(description='Clean addresses using geocoder.ca service.')
parser.add_argument('-f', metavar='N', type=str, help='a name for the file to clean up.  Must be a csv.')

args = parser.parse_args()

# This will throw error with no input -f since we're not committing this file
file_name = args.f if args.f else "dogwood_sample_address_data.csv"

with open(file_name) as csvfile:
    addresses = csv.DictReader(csvfile)
    for row in addresses:
        print(row)

        street = row['Primary Street']
        province = row['Primary Province/State']
        query = "addresst=" + street + "&prov=" + province
        url =  "http://geocoder.ca/?" + query + "&geoit=XML"
        r = requests.get(url)

        #parse
        root = ET.fromstring(r.text)
        error = root.findall("./error")
        if(error):
            print(error[0][0].text)
        else:
            root.findall('./standard')
