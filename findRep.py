import sys
import sunlight
import geopy
from geopy.geocoders import GoogleV3

address=raw_input("Enter your address:")

geocoder = GoogleV3()
location=geocoder.geocode(address)

print location.latitude
print location.longitude

stateLegislators = sunlight.openstates.legislator_geo_search(location.latitude,location.longitude)

federalLegislators = sunlight.congress.locate_legislators_by_lat_lon(location.latitude,location.longitude)

if not(federalLegislators or stateLegislators):
    print "Non US Address, try again"
    quit()


print "State Legislators:"
for stateRep in stateLegislators:
    print "Rep. {} is a {} member of the {} house".format(stateRep['last_name'],stateRep['party'],stateRep['chamber'])


print "Federal Legislators:"

for federalRep in federalLegislators:
    if federalRep['chamber']=='senate':
        print "Senator {} is a {} member of the {} from {}".format(federalRep['last_name'],federalRep['state_rank'],federalRep['chamber'],federalRep['state_name'])
    if federalRep['chamber']=='house':
        print "Representative {} is a member of the {} from {}".format(federalRep['last_name'],federalRep['chamber'],federalRep['state_name'])


