# coding=utf-8

import scraperwiki
import lxml.html
import sqlite3

BASE_URL = 'http://www.legiscba.gob.ar/'

# Read in a page
html = scraperwiki.scrape(BASE_URL + 'legisladores/')
#
# # Find something on the page using css selectors
root = lxml.html.fromstring(html)
members = root.cssselect('div[class=\'listados\']')

parsedMembers = []

for member in members:

    memberData = {}

    url = member.cssselect('a')[0].attrib['href']

    # From the URL we can parse an ID
    memberData['id'] = url.split('=')[1]

    name = member.cssselect('p')[0].text

    #  This seems to be very consistently Last, First
    nameParts = name.split(', ')

    memberData['name'] = u'{} {}'.format(nameParts[1], nameParts[0])
    memberData['first_name'] = nameParts[1]
    memberData['last_name'] = nameParts[0]

    memberData['image'] = BASE_URL + member.cssselect('img')[0].attrib['src'].replace('../', '')

    # Now, go get the extra data!

    memberPageUrl = BASE_URL + url.replace('../', '')

    memberHtml = scraperwiki.scrape(memberPageUrl)
    memberRoot = lxml.html.fromstring(memberHtml)

    dataTable = memberRoot.cssselect('table[class=\'tabla-mis-datos\']')[0]

    tableRows = dataTable.cssselect('tr')

    for row in tableRows:
        rowParts = row.cssselect('td')

        label = rowParts[0]

        if label.text != 'Oficina':
            label = label.cssselect('span')[0].text.encode('utf-8')

            if label == 'Bloque Político:':
                memberData['party'] = rowParts[1].text

            if label == 'Distrito:':
                memberData['district'] = rowParts[1].text

    print memberData

    parsedMembers.append(memberData)

print 'Counted {} Members'.format(len(parsedMembers))

try:
    scraperwiki.sqlite.execute('DELETE FROM data')
except sqlite3.OperationalError:
    pass
scraperwiki.sqlite.save(
    unique_keys=['id'],
    data=parsedMembers)
