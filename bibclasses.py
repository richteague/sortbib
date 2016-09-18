import string
import numpy as np


class Bibliography:

    def __init__(self, filename='bibliography.bib'):

        # Upon intialisation, read in the file as a text file and parse into
        # a lsit of BibItems. Remove all the lines which are empty.

        self.bibfile = filename
        with open(filename) as f:
            self.bib = f.readlines()
            self.bib = [l for l in self.bib if l != '\n']
            self.bib = [l for l in self.bib if l.strip()[0] != '%']

        # Declare ordering of the months and an alphabet for citekey suffixes.

        self.months = {}
        self.monthnames = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                           'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        for m, month in enumerate(self.monthnames):
            self.months[month] = m
        self.alphabet = list(string.ascii_lowercase)

        # Parse into individual bibliography items. Each item becomes a
        # BibItem. Each BibItem gets assigned a citekey, check that there are
        # no duplicates. If so append the citekey with a, b, c etc. If the
        # citekey cannot be generated automatically, the user is asked to
        # enter one.

        self.parseBibItems()
        self.verifyMonthKeys()
        self.verifyCiteKeys()
        self.uniqueCiteKeys()
        self.updateCiteKeys()

        print 'All citekeys updated. Ready to write.'

        return

    def replaceCitations(self, filename, update=False):
        """Update the citekeys in filename. First replace into dummy variables,
        then from those into the new citekeys to prevent getting confused with
        old and new citekeys which may be the same.
        """
        with open(filename) as f:
            document = f.readlines()
        newck = np.array([bi.citekey for bi in self.bibitems])
        oldck = np.array([bi.oldcitekey for bi in self.bibitems])
        for i, ck in enumerate(oldck):
            document = [l.replace(ck, 'citekey%d' % i) for l in document]
        for i, ck in enumerate(newck):
            document = [l.replace('citekey%d' % i, ck) for l in document]

        # If update is True, overwrite the input file, otherwise write to a
        # second file with _updated in the name.

        if not update:
            for i in range(1, len(filename)):
                if filename[-i] == '.':
                    fileout = filename[:-i]
                    break
            fileout += '_updated.' + filename.split('.')[-1]
        else:
            fileout = filename
        with open(fileout, 'w') as fo:
            for line in document:
                fo.write(line)
        print 'Written to %s' % fileout
        return

    def parseBibItems(self):
        """Parse the different BibItems."""
        self.bibitems = []
        lb = 0
        rb = 0
        article = 0
        for l, line in enumerate(self.bib):
            lb += line.count(u'{')
            rb += line.count(u'}')
            if lb == rb:
                self.bibitems.append(BibItem(self.bib[article:l+1]))
                lb = 0
                rb = 0
                article = l + 1
        print 'Found %d bibliography items in %s.' % (len(self.bibitems),
                                                      self.bibfile)
        return

    def verifyCiteKeys(self):
        """Check that the citekeys follow the correct format style."""
        for bi in self.bibitems:

            # Split the citekeys into their three (two) components.
            error = 0
            split = bi.citekey.split('_')
            if len(split) == 2:
                name1, year = split
            elif len(split) == 3:
                name1, name2, year = split
            else:
                raise ValueError("")

            # Check that each component contains the allowed characeters.
            if not np.array([n in self.alphabet or n == '-'
                             for n in name1.lower()]).all():
                error += 1

            if len(split) == 3:
                if not np.array([n in self.alphabet or n == '-'
                                 for n in name2.lower()]).all():
                    error += 1

            if not(year[:-1].isdigit()
                   and (year[-1].isdigit() or year[-1] in self.alphabet)):
                error += 1

            # If any error found, ask for user input.
            if error > 0:
                print 'Unable to create citekey for:\n'
                for l in bi.text:
                    print l.replace('\n', '').replace('\t', '')
                print '\n'
                newkey = raw_input("New citekey: ")
                bi.citekey = newkey
        return

    def verifyMonthKeys(self):
        """Check for the months, if there are none, assume January."""
        for bi in self.bibitems:
            if 'month' not in bi.keys:
                bi.keys['month'] = 'jan'
            elif bi.keys['month'] not in self.monthnames:
                bi.keys['month'] = 'jan'
        return

    def uniqueCiteKeys(self):
        """Check there are no duplicate citekeys. If they are, append them a, b,
        c etc. depending on month published.
        """
        self.citekeys = [bibitem.citekey for bibitem in self.bibitems]
        if len(self.citekeys) != len(set(self.citekeys)):
            duplicate_citekeys = self.findDuplicates()
            for ck in duplicate_citekeys:

                # Return the BibItems which are duplicates.
                # From their month value assign a number and order them.
                # Once ordered, append the appropriate suffix.

                bibitems = [bi for bi in self.bibitems if bi.citekey == ck]
                sfx = np.array([self.months[bi.keys['month']]
                                for bi in self.bibitems if bi.citekey == ck])
                sfx = sfx.argsort()
                for b, bi in enumerate(bibitems):
                    bi.citekey += self.alphabet[sfx[b]]
        self.citekeys = [bibitem.citekey for bibitem in self.bibitems]
        return

    def findDuplicates(self):
        """Find the duplicate citekey values."""
        seen, dupl = set(), set()
        for citekey in self.citekeys:
            if citekey in seen:
                dupl.add(citekey)
            else:
                seen.add(citekey)
        return list(dupl)

    def updateCiteKeys(self):
        """Change the citekey with the shortened, unique values."""
        for bibitem in self.bibitems:
            bibitem.text[0] = bibitem.text[0].split(u'{')[0]
            bibitem.text[0] += '{' + bibitem.citekey + ',\n'
        return

    def writeBibliography(self, update=False):
        """Write in a new bibliography file with alphabetically ordered
        citekeys.
        """
        if not update:
            for i in range(1, len(self.bibfile)):
                if self.bibfile[-i] == '.':
                    fileout = self.bibfile[:-i]
                    break
            fileout += '_updated.bib'
        else:
            fileout = self.bibfile
        writeorder = sorted(self.citekeys)
        with open(fileout, 'w') as fo:
            for ck in writeorder:
                for bi in self.bibitems:
                    if bi.citekey == ck:
                        for line in bi.text:
                            fo.write(line)
                        fo.write('\n')
        print 'Written to %s' % fileout
        return


class BibItem:

    """A bibliography item. From the text will parse all the bibitem type, keywords and their aguments and citekey.
    From the author list a more readable citekey will be generated of the form: author_ea_year.

    BibItem.bitype : string, BibItem type, e.g. 'article'.
    BibItem.keywords : dictionary, returns the keyword values for a given keyword e.g. 'year'.
    BibItem.oldcitekey : string, original citekey used as the BibItem identifier.
    BibItem.citekey : string, citekey following the more readable author_ea_year format. May not be unique.

    """

    def __init__(self, text):
        self.text = text
        self.bitype = self.parseType()
        print self.bitype
        self.oldcitekey = self.parseOldCiteKey()
        self.keywords = self.getKeywords()
        self.citekey = self.writeCiteKey()
        return

    def parseType(self):
        """Parse the bibitem type."""
        bitype = self.text[0].split(u'{')[0][1:]
        return bitype.lower()

    def parseOldCiteKey(self):
        """Parse the old citekey to help replacement."""
        citekey = self.text[0].split(u'{')[-1]
        citekey = citekey.split(',')[0]
        return citekey

    def getKeywords(self):
        """Create a dictionary with all the keywords and their values."""
        keys = self.parseKeyWords()
        keywords = {}
        for key in keys:
            keywords[key] = self.parseKeyValue(key)
        return keywords

    def parseKeyValue(self, keyword):
        """Parse the information for the given keyword."""
        for l, line in enumerate(self.text):
            if keyword in line.lower():
                break
        s = self.stripBraces(self.getKeyWordValue(l))
        if keyword == 'author':
            return self.parseBraces(s)
        else:
            return s

    def parseKeyWords(self):
        """Return the different keyword used in the bibliography item."""
        return [l.split('=')[0].strip().lower() for l in self.text if '=' in l]

    def getKeyWordValue(self, i):
        """Return the value of the keyword starting on line i."""
        lb, rb = 0, 0
        for l, line in enumerate(self.text[i:]):
            lb += line.count(u'{')
            rb += line.count(u'}')
            if lb == rb:
                break
        s = ''.join([l for l in self.text[i:i+l+1]])
        return s.split('=')[-1]

    def stripBraces(self, s):
        """Remove the curly braces at the start and end of the string."""
        if (u'{' not in s and u'}' not in s):
            return self.stripNames(s)
        for i in range(len(s)):
            if s[i] == u'{':
                i += 1
                break
        for j in range(1, len(s)):
            if s[-j] == u'}':
                j *= -1
                break
        return s[i:j]

    def parseBraces(self, s):
        """Parse all the surnames in curly braces in a string of authors."""
        names = []
        lb, rb = 0, 0
        j = 0
        for i in range(len(s)):
            if s[i] == u'{':
                if lb == rb:
                    j = i + 1
                lb += 1
            elif s[i] == u'}':
                rb += 1
                if lb == rb:
                    names.append(self.stripNames(s[j:i]))
        return names

    def stripNames(self, s):
        """Remove spurious characters in a string but leave hyphens."""
        s = s.replace(u'\\', '')
        s = s.replace(u'"', '')
        s = s.replace(u'{', '')
        s = s.replace(u'}', '')
        s = s.replace(u'`', '')
        s = s.replace(u'\n', '')
        s = s.replace(u'\t', '')
        s = s.replace(u'=', '')
        s = s.replace(',', '')
        s = s.replace("'", "")
        s = s.replace(' ', '')
        return s.strip()

    def writeCiteKey(self):
        """Replace the citekey with a standard, more readable format:
        single author: author_year,
        two authors: author1_author_2_year,
        multiple authors: author1_ea_year.
        """
        if len(self.keywords['author']) == 1:
            citekey = '%s_%s' % (self.keywords['author'][0],
                                 self.keywords['year'])
        elif len(self.keywords['author']) == 2:
            citekey = '%s_%s_%s' % (self.keywords['author'][0],
                                    self.keywords['author'][1],
                                    self.keywords['year'])
        else:
            citekey = '%s_ea_%s' % (self.keywords['author'][0],
                                    self.keywords['year'])
        return citekey
