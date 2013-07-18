"""
This module provides classes for querying ACM website for authors and
papers information.
"""
import datetime
import optparse
import sys
import re
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

class Article():
    """
    A class representing articles listed on ACM.  The class
    provides basic dictionary-like behavior.
    """
    def __init__(self):
        self.attrs = {'title':         [None, 'Title',          0],
                      'url':           [None, 'URL',            1],
                      'num_citations': [0,    'Citations',      2],
                      'num_versions':  [0,    'Versions',       3],
                      'url_citations': [None, 'Citations list', 4],
                      'url_versions':  [None, 'Versions list',  5],
                      'year':          [None, 'Year',           6],
                      'authors':       [[],   'Authors',        7]}

    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key][0]
        return None

    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key][0] = item
        else:
            self.attrs[key] = [item, key, len(self.attrs)]

    def __delitem__(self, key):
        if key in self.attrs:
            del self.attrs[key]

    def as_txt(self):
        # Get items sorted in specified order:
        items = sorted(self.attrs.values(), key=lambda item: item[2])
        # Find largest label length:
        max_label_len = max([len(str(item[1])) for item in items])
        fmt = '%%%ds %%s' % max_label_len
        return '\n'.join([fmt % (item[1], item[0]) for item in items])

    def as_csv(self, header=False, sep='|'):
        # Get keys sorted in specified order:
        keys = [pair[0] for pair in \
                    sorted([(key, val[2]) for key, val in self.attrs.items()],
                           key=lambda pair: pair[1])]
        res = []
        if header:
            res.append(sep.join(keys))
        res.append(sep.join([unicode(self.attrs[key][0]) for key in keys]))
        return '\n'.join(res)

    def as_obj(self):
        # Get items sorted in specified order:
        items = sorted(self.attrs.values(), key=lambda item: item[2])
        out = {}
        for item in items:
            out[item[1]] = item[0]
        return out

class ACMParser():
    """
    ACMParser can parse HTML document strings obtained from ACM.
    """
    ACM_SITE = 'http://dl.acm.org'

    def __init__(self, site=None):
        self.soup = None
        self.article = None
        self.site = site or self.ACM_SITE
        self.year_re = re.compile(r'\b(?:20|19)\d{2}\b')

    def handle_article(self, art):
        """
        In this base class, the callback does nothing.
        """

    def parse(self, html):
        """
        This method initiates parsing of HTML content.
        """
        self.soup = BeautifulSoup(html)
        for div in self.soup.findAll(ACMParser._tag_checker):
            self._parse_article(div)

    def _parse_article(self, div):
        self.article = Article()

        for tag in div:
            if not hasattr(tag, 'name'):
                continue

            if tag.name == 'div' and tag.get('class') == 'gs_rt' and \
                    tag.h3 and tag.h3.a:
                self.article['title'] = ''.join(tag.h3.a.findAll(text=True))
                self.article['url'] = self._path2url(tag.h3.a['href'])

            if tag.name == 'font':
                for tag2 in tag:
                    if not hasattr(tag2, 'name'):
                        continue
                    if tag2.name == 'span' and tag2.get('class') == 'gs_fl':
                        self._parse_links(tag2)

        if self.article['title']:
            self.handle_article(self.article)

    def _parse_links(self, span):
        for tag in span:
            if not hasattr(tag, 'name'):
                continue
            if tag.name != 'a' or tag.get('href') == None:
                continue

            if tag.get('href').startswith('/scholar?cites'):
                if hasattr(tag, 'string') and tag.string.startswith('Cited by'):
                    self.article['num_citations'] = \
                        self._as_int(tag.string.split()[-1])
                self.article['url_citations'] = self._path2url(tag.get('href'))

            if tag.get('href').startswith('/scholar?cluster'):
                if hasattr(tag, 'string') and tag.string.startswith('All '):
                    self.article['num_versions'] = \
                        self._as_int(tag.string.split()[1])
                self.article['url_versions'] = self._path2url(tag.get('href'))

    @staticmethod
    def _tag_checker(tag):
        if tag.name == 'div' and tag.get('class') == 'gs_r':
            return True
        return False

    def _as_int(self, obj):
        try:
            return int(obj)
        except ValueError:
            return None

    def _path2url(self, path):
        if path.startswith('http://'):
            return path
        if not path.startswith('/'):
            path = '/' + path
        return self.site + path

class Author():
    """
    A class representing author.
    """
    def __init__(self):
        self.attrs = {'name':          [None, 'Name',          0],
                      'url':           [None, 'URL',           1],
                      'affiliation':   [None, 'Affiliation',   2]
        }

    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key][0]
        return None

    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key][0] = item
        else:
            self.attrs[key] = [item, key, len(self.attrs)]

    def __delitem__(self, key):
        if key in self.attrs:
            del self.attrs[key]

    def as_obj(self):
        # Get items sorted in specified order:
        items = sorted(self.attrs.values(), key=lambda item: item[2])
        out = {}
        for item in items:
            out[item[1]] = item[0]
        return out

    def as_txt(self):
        # Get items sorted in specified order:
        items = sorted(self.attrs.values(), key=lambda item: item[2])
        # Find largest label length:
        max_label_len = max([len(str(item[1])) for item in items])
        fmt = '%%%ds %%s' % max_label_len
        return '\n'.join([fmt % (item[1], item[0]) for item in items])

    def as_csv(self, header=False, sep='|'):
        # Get keys sorted in specified order:
        keys = [pair[0] for pair in \
                    sorted([(key, val[2]) for key, val in self.attrs.items()],
                           key=lambda pair: pair[1])]
        res = []
        if header:
            res.append(sep.join(keys))
        res.append(sep.join([unicode(self.attrs[key][0]) for key in keys]))
        return '\n'.join(res)

class ACMArticleParser(ACMParser):
    """ 
    Parser for citations page of ACM
    """
    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'

    def query(self, article_url):
        """
        This method queries an URL to get article information.
        """
        if not article_url.startswith("http://dl.acm.org/citation.cfm"):
            return None
        self.article_url = article_url
        req = urllib2.Request(url=self.article_url, headers={'User-Agent': self.UA})
        hdl = urllib2.urlopen(req)
        html = hdl.read()
        #print html
        self.parse(html)

    def parse(self, html):
        """
        This method initiates parsing of HTML content.
        """
        self.soup = BeautifulSoup(html)
        asses = self.soup.findAll(ACMArticleParser._tag_checker)
        self._parse_article(asses)

    @staticmethod
    def _tag_checker(tag):
        if tag.name == 'a' and tag.get('title') == 'Author Profile Page':
            return True
        return False

    def _parse_article(self, asses):
        self.article = Article()
        self.article['url'] = self.article_url
        
        self.article['authors'] = []
        for a in asses:
            self.article['authors'].append({'name': a.text, 'url': self._path2url(a['href'])})

class ACMAuthorParser(ACMParser):
    """ 
    Parser for authors page on ACM
    """
    UA = 'Mozilla/5.0 (X11; U; FreeBSD i386; en-US; rv:1.9.2.9) Gecko/20100913 Firefox/3.6.9'

    def query(self, author_url):
        """
        This method queries an URL to get author information.
        """
        if not author_url.startswith("http://dl.acm.org/author_page.cfm"):
            return None
        self.author_url = author_url
        req = urllib2.Request(url=self.author_url, headers={'User-Agent': self.UA})
        hdl = urllib2.urlopen(req)
        html = hdl.read()
        #print html
        self.parse(html)

    def parse(self, html):
        """
        This method initiates parsing of HTML content.
        """
        self.soup = BeautifulSoup(html)
        tds = self.soup.findAll(ACMAuthorParser._tag_checker)
        self._parse_author(tds)

    @staticmethod
    def _tag_checker(tag):
        if tag.name == 'td' and tag.get('class') == 'small-text':
            return True
        return False

    def _parse_author(self, tds):
        self.author = Author()
        self.author['url'] = self.author_url

        for td in tds:
            strongs = td.findAll('strong')
            for strong in strongs:
                if strong.text == 'Affiliation history':
                    div = td.find('div')
                    if div != None:
                        # First affiliation only
                        a = div.find("a")
                        if a != None:
                            self.author['affiliation'] = a.text

    
