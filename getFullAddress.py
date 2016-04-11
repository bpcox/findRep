import urllib
import json

url ="https://www.govtrack.us/api/v2/role?current=true&limit=542&fields=person__bioguideid,extra__address"
response = urllib.urlopen(url)
address = json.loads(response.read())
addressDict = dict()
for i in range(0,len(address['objects'])-1):
    try:
        addressDict[address['objects'][i]['person']['bioguideid']]=address['objects'][i]['extra']['address']
    except Exception as e:
        addressDict[address['objects'][i]['person']['bioguideid']]="not currently known"

with open('addressDict.json','w') as f:
    json.dump(addressDict,f)
