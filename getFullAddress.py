import urllib
import json

url ="https://www.govtrack.us/api/v2/role?current=true&limit=542&fields=person__bioguideid,extra__address"
response = urllib.urlopen(url)
address = json.loads(response.read())
addressDict = dict()

for i in range(len(address['objects'])):
    if address['objects'][i]['extra']:
        try:
            addressDict[address['objects'][i]['person']['bioguideid']]=address['objects'][i]['extra']['address'].replace("HOB","House Office Building")
        except KeyError:
            addressDict[address['objects'][i]['person']['bioguideid']]="not currently known"
	except:
   	    print "Unexpected error"
	    print addressDict[address['objects'][i]['person']['bioguideid']]
with open('addressDict.json','w') as f:
    json.dump(addressDict,f)
