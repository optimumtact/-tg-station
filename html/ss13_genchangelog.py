'''
'''

from __future__ import print_function
import yaml, os, glob, sys, re, time, argparse, json, pprint
from datetime import datetime, date, timedelta
from time import time
import re

regex = re.compile(r'(?P<date>\d\d?)(rd|th|nd|st)')
today = date.today()
dateformat = "%d %B %Y"
dateformat1 = "%B %d %Y"
dateformat2 = "%A %B %d %Y"
dateformat3 = "%A %B %d"
dateformat4 = "%d %B %Y %A"
dateformat5 = "%d.%m.%Y"
dateformat6 = "%A %B %d %Y"

from bs4 import BeautifulSoup
from bs4.element import NavigableString

opt = argparse.ArgumentParser()
opt.add_argument('-t', '--type', dest='type', default=1, type=int, help='Parser type to use')
opt.add_argument('targetFile', help='The HTML changelog we wish to parse')
opt.add_argument('destFile', help='Where to write the yaml')

args = opt.parse_args()
all_changelog_entries = {}

def validate(e, dateformat):
    try:
        date = datetime.strptime(e, dateformat).date()  # key
        return True
    except ValueError as ve:
        return False

#first type of changelog
if args.type == 1 and os.path.isfile(args.targetFile):
    with open(args.targetFile, 'r') as f:
        soup = BeautifulSoup(f)
        for e in soup.find_all('h2', {'class':'date'}):
            datestring = e.string.strip(' ,').replace(',', '')
            datestring = re.sub(regex, '\g<date>', datestring)
            date = datetime.strptime(datestring, dateformat).date()  # key
            ulT = e.next_sibling
            while ulT and ulT.name != "h2":
                print(ulT)
                changes = []
                entry = {}
                author = ''
                if ulT.name == "h3":
                    author = ulT.string
                    # Strip suffix
                    if author.endswith('updated:'):
                        author = author[:-8]
                    author = author.strip()
                    sublistT = ulT.next_sibling.next_sibling
                    print(sublistT)
                    for changeT in sublistT.children:
                        if changeT.name != 'li': continue
                        val = changeT.decode_contents(formatter="html")
                        newdat = {changeT['class'][0] + '': val + ''}
                        if newdat not in changes:
                            changes += [newdat]
                    if len(changes) > 0 and author:
                        entry[author] = changes
                        if date in all_changelog_entries:
                            all_changelog_entries[date].update(entry)
                        else:
                            all_changelog_entries[date] = entry
                
                ulT = ulT.next_sibling

#Second type of changelog
if args.type == 2 and os.path.isfile(args.targetFile):
    with open(args.targetFile, 'r') as f:
        soup = BeautifulSoup(f)
        for e in soup.find_all('div', {'class':'commit'}):
            entry = {}
            datestring = e.h2.string.strip(' ,').replace(',', '')
            datestring = re.sub(regex, '\g<date>', datestring)
            if validate(datestring, dateformat):
                date = datetime.strptime(datestring, dateformat).date()  # key
            elif validate(datestring, dateformat1):
                date = datetime.strptime(datestring, dateformat1).date()  # key
            elif validate(datestring, dateformat3):
                datestring = datestring + ' 2012' #forge date
                date = datetime.strptime(datestring, dateformat2).date()  # key
            else:
                date = datetime.strptime(datestring, dateformat2).date()  # key

            for authorT in e.find_all('h3', {'class':'author'}):
                author = authorT.string
                # Strip suffix
                if author.endswith('updated:'):
                    author = author[:-8]
                author = author.strip()
                
                # Find <ul>
                ulT = authorT.next_sibling
                while(ulT.name != 'ul'):
                    ulT = ulT.next_sibling
                changes = []
                if ulT: #in case we never got one
                    for changeT in ulT.children:
                        if changeT.name != 'li': continue
                        val = changeT.decode_contents(formatter="html")
                        newdat = {changeT['class'][0] + '': val + ''}
                        if newdat not in changes:
                            changes += [newdat]
                    
            if len(changes) > 0:
                entry[author] = changes
                if date in all_changelog_entries:
                    all_changelog_entries[date].update(entry)
                else:
                    all_changelog_entries[date] = entry

#third type of changelog
if args.type == 3 and os.path.isfile(args.targetFile):
    with open(args.targetFile, 'r') as f:
        soup = BeautifulSoup(f)
        for e in soup.find_all('font', {'color':'blue'}):
            datestring = e.string
            dssplit = datestring.split(',')
            if len(dssplit) > 1:
                datestring = dssplit[0]
            datestring = datestring.strip(' ,:.)(').replace(',', '')
            datestring = re.sub(regex, '\g<date>', datestring)
            print(datestring)
            if validate(datestring, dateformat):
                date = datetime.strptime(datestring, dateformat).date()  # key
            else:
                date = datetime.strptime(datestring, dateformat4).date()
            if len(dssplit) > 1:
                changes = [{'unknown':dssplit[1]}]
                entry = {'/tg/station team':changes}
                if date in all_changelog_entries:
                    all_changelog_entries[date].update(entry)
                else:
                    all_changelog_entries[date] = entry

            ulT = e.parent #walk up one to the b node
            ulT = ulT.next_sibling.next_sibling #get actual ul node containing authors/changes
            for authorT in ulT.children:
                #author
                changes = []
                entry = {}
                author = ''
                if authorT.name == 'li':
                    if authorT.a and authorT.a.span:
                        author = authorT.a.span.string #someone tried to do some funky linking
                    else:
                        author = authorT.b.string #they're in a bold below the li element
                    print(author)
                    # Strip suffix
                    if author.endswith('updated:'):
                        author = author[:-8]
                    author = author.strip()

                    #changes are the ul below the li for author
                    for itemT in authorT.ul:
                        if itemT.name != 'li': continue
                        val = itemT.decode_contents(formatter="html")
                        newdat = {'unknown' + '': val + ''}
                        print(newdat)
                        if newdat not in changes:
                            changes += [newdat]

                    if len(changes) > 0 and author:
                        entry[author] = changes
                        if date in all_changelog_entries:
                            all_changelog_entries[date].update(entry)
                        else:
                            all_changelog_entries[date] = entry

#fourth type of changelog
if args.type == 4 and os.path.isfile(args.targetFile):
    with open(args.targetFile, 'r') as f:
        soup = BeautifulSoup(f)
        for e in soup.find_all('h5'):
            datestring = e.string
            dssplit = datestring.split(',' )
            if len(dssplit) == 2:
                datestring = dssplit[0]
            elif len(dssplit) == 3:
                datestring = dssplit[0] + dssplit[1] + ' 2010'
            datestring = datestring.strip(' ,:)(').replace(',', '')
            datestring = re.sub(regex, '\g<date>', datestring)
            print(datestring)
            if validate(datestring, dateformat5):
                date = datetime.strptime(datestring, dateformat5).date()  # key
            else:
                date = datetime.strptime(datestring, dateformat6).date()
            author = '/tg/station ss13 team' #authors lost to time rip
            #get ul of changes
            changes = []
            entry = {}
            for itemT in e.next_sibling.next_sibling.children:
                if itemT.name != 'li': continue
                val = itemT.decode_contents(formatter="html")
                newdat = {'unknown' + '': val + ''}
                changes += [newdat]
            print(changes)
            if len(changes) > 0 and author:
                entry[author] = changes
                if date in all_changelog_entries:
                    all_changelog_entries[date].update(entry)
                else:
                    all_changelog_entries[date] = entry

#fifth type of changelog
if args.type == 5 and os.path.isfile(args.targetFile):
    with open(args.targetFile, 'r') as f:
        soup = BeautifulSoup(f)
        for e in soup.find_all('h5'):
            datestring = e.string
            datestring = datestring.strip(' ,:)(').replace(',', '')
            datestring = re.sub(regex, '\g<date>', datestring)
            date = datetime.strptime(datestring, dateformat6).date()
            author = '/tg/station ss13 team' #authors lost to time rip
            #get ul of changes
            changes = []
            entry = {}
            for itemT in e.next_sibling.next_sibling.children:
                if itemT.name != 'li': continue
                val = itemT.decode_contents(formatter="html")
                newdat = {'unknown' + '': val + ''}
                changes += [newdat]
            print(changes)
            if len(changes) > 0 and author:
                entry[author] = changes
                if date in all_changelog_entries:
                    all_changelog_entries[date].update(entry)
                else:
                    all_changelog_entries[date] = entry
#sixth type of changelog
if args.type == 6 and os.path.isfile(args.targetFile):
    with open(args.targetFile, 'r') as f:
        soup = BeautifulSoup(f)
        for e in soup.find_all('h5'):
            if e.b and e.b.font:
                datestring = e.b.font.string
            else:
                datestring = e.string
            datestring = datestring.strip(' ,:)(').replace(',', '')
            datestring = re.sub(regex, '\g<date>', datestring)
            date = datetime.strptime(datestring, dateformat6).date()
            author = '/tg/station ss13 team' #authors lost to time rip
            #get ul of changes
            changes = []
            entry = {}
            for itemT in e.next_sibling.next_sibling.children:
                if itemT.name != 'li': continue
                val = itemT.decode_contents(formatter="html")
                newdat = {'unknown' + '': val + ''}
                changes += [newdat]
            print(changes)
            if len(changes) > 0 and author:
                entry[author] = changes
                if date in all_changelog_entries:
                    all_changelog_entries[date].update(entry)
                else:
                    all_changelog_entries[date] = entry
                

with open(args.destFile, 'w') as f:
    yaml.dump(all_changelog_entries, f, default_flow_style=False)

