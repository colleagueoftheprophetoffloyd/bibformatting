#----------------------------------------------------------------------
# Copyright (c) 2017 Raytheon BBN Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
#----------------------------------------------------------------------
#
import sys
import codecs
import string
import re
import copy
from HTMLParser import HTMLParser
from unidecode import unidecode
import locale

hp = HTMLParser()

#
# Takes a name in HTML escaped format and convert it to a list of
# lowercase ascii fields.
#
def toFields(name):
    # Strip out HTML escapes and unicode
    nameAscii = unidecode(hp.unescape(name))

    # Convert all separators to '#' and lower case everything
    separators = ' ,;.'
    delimiters = '####'
    nameLower = nameAscii.lower()
    nameStd = nameLower.translate(string.maketrans(separators, delimiters))
    nameStd2 = re.sub(r'##+', r'#', nameStd)
    return nameStd2.split('#')

#
# Compare two names for similarity.
# They're similar if the first name in the list (hopefully a surname) matches identically
# AND
# All other names that appear in both lists match on a prefix basis.
# The intent here is to catch initials and ommitted names.
# So: ['Jones', 'Robert', 'A'] will match
#     ['Jones', 'R', 'A'] and ['Jones', 'Rob']
# but not ['Jones', 'Bob'].
#
def isSimilar(name1, name2):
    fields1 = toFields(name1)
    fields2 = toFields(name2)
    
    # Surname (first field) must match
    if (fields1[0] != fields2[0]):
        return False

    # Now, figure out which list has fewer names/initials
    if len(fields1) < len(fields2):
        shorter = fields1
        longer = fields2
    else:
        shorter = fields2
        longer = fields1

    # Then, each other name must be similar (substring)
    # until we run out of names in one list.
    # For example "Jones, Mary B" should match "Jones, M B"
    # or "Jones, M"
    for i in range(len(shorter)):
        if (not shorter[i].startswith(longer[i]) and
            not longer[i].startswith(shorter[i])):
            return False

    # If we get to the end of the shorter list without a mismatch,
    # then the names match
    return True

#
# Class for holding multiple names for one author.
# The 'longest' name we've seen is the primary name.
#
# There are some unfortunate order dependencies in name matching
# that current algorithm is too primitive to handle.
#
class AuthorEntry:
    def __init__(self, name):
        self.primaryName = name
        self.allNames = [name];

    def addName(self, name):
        if len(name) > len(self.primaryName):
            self.primaryName = name
        if not name in self.allNames:
            self.allNames.append(name)

    def __unicode__(self):
        otherNames = copy.copy(self.allNames)
        otherNames.remove(self.primaryName)
        if otherNames == []:
            return self.primaryName
        else:
            return self.primaryName + ' (' + ', '.join(otherNames) + ')'

    def nameMatches(self, name):
        for eachName in self.allNames:
            if isSimilar(name, eachName):
                return True
        return False;

# Class for all the authors we know about.
class AuthorList:
    
    def __init__(self):
        self.authorEntries = []
    
    def add(self, newAuthorName):
        for author in self.authorEntries:
            if author.nameMatches(newAuthorName):
                author.addName(newAuthorName)
                return
        newAuthorEntry = AuthorEntry(newAuthorName)
        self.authorEntries.append(newAuthorEntry)
    
    def __unicode__(self):
        entryStrings = [unicode(entry) for entry in self.authorEntries]
        return '\n'.join(sorted(entryStrings, key=lambda s: s.lower()))
        #return '\n'.join(sorted(entryStrings, cmp=locale.strcoll))


# Read in all authors' names (expected to come in HTML-escaped format),
# and produce a sorted list with duplicates removed.
if __name__ == '__main__':
    authors = AuthorList()
    UTF8Reader = codecs.getreader('utf8')
    sys.stdin = UTF8Reader(sys.stdin)
    for line in sys.stdin.readlines():
        authors.add(hp.unescape(line.strip()))
    uniList = unicode(authors)
    print uniList.encode('ascii', 'xmlcharrefreplace')
