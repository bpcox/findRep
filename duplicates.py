import sunlight
from collections import Counter
from unidecode import unidecode

legislators = sunlight.congress.all_legislators_in_office()

senate = list()
house = list()
both = list()
for legislator in legislators:
    if legislator['chamber'] == 'senate':
        senate.append(unidecode(legislator['last_name']))
    if legislator['chamber'] == 'house':
        house.append(unidecode(legislator['last_name']))
    both.append(unidecode(legislator['last_name']))

senate = [senator.encode('utf-8') for senator in senate]
house = [rep.encode('utf-8') for rep in house]
both = [bothrep.encode('utf-8') for bothrep in both]

senateduplicates = [k for k, v in Counter(senate).items() if v>1]
houseduplicates = [l for l, m in Counter(house).items() if m>1]
bothduplicates = [x for x, p in Counter(both).items() if p>1]

print senateduplicates
print houseduplicates
print bothduplicates

