import argparse
import logging
from xml.parsers import expat


class WPXMLParser:

    def __init__(self):
        self._categories = []
        self._tags = []
        self._current = None
        self._name = None
        self._cdata = None
        parser = expat.ParserCreate()
        parser.StartElementHandler = self._start_element_handler
        parser.EndElementHandler = self._end_element_handler
        parser.CharacterDataHandler = self._character_data_handler
        parser.StartCdataSectionHandler = self._start_cdata_section_handler
        parser.EndCdataSectionHandler = self._end_cdata_section_handler
        self._parser = parser

    def _start_element_handler(self, name, attrs):
        if name == 'wp:category':
            self._current = {}
            self._categories.append(self._current)
        elif name == 'wp:tag':
            self._current = {}
            self._tags.append(self._current)
        elif name == 'wp:term_id':
            self._name = 'term_id'
        elif name == 'wp:category_nicename':
            self._name = 'category_nicename'
        elif name == 'wp:category_parent':
            self._name = 'category_parent'
        elif name == 'wp:cat_name':
            self._name = 'cat_name'
        elif name == 'wp:tag_slug':
            self._name = 'tag_slug'
        elif name == 'wp:tag_name':
            self._name = 'tag_name'
        elif name == 'item':
            self._current = {}
        elif name == 'title':
            self._name = 'title'
        elif name == 'link':
            self._name = 'link'
        elif name == 'pubDate':
            self._name = 'pubDate'
        elif name == 'dc:creator':
            self._name = 'creator'
        elif name == 'guid':
            self._name = 'guid'
        elif name == 'description':
            self._name = 'description'
        elif name == 'content:encoded':
            self._name = 'content_encoded'
        elif name == 'excerpt:encoded':
            self._name = 'excerpt_encoded'
        elif name == 'wp:post_id':
            self._name = 'post_id'
        elif name == 'wp:post_date':
            self._name = 'post_date'
        elif name == 'wp:post_date_gmt':
            self._name = 'post_date_gmt'
        elif name == 'wp:comment_status':
            self._name = 'comment_status'
        elif name == 'wp:ping_status':
            self._name = 'ping_status'
        elif name == 'wp:post_name':
            self._name = 'post_name'
        elif name == 'wp:status':
            self._name = 'status'
        elif name == 'wp:post_parent':
            self._name = 'post_parent'
        elif name == 'wp:menu_order':
            self._name = 'menu_order'
        elif name == 'wp:post_type':
            self._name = 'post_type'
        elif name == 'wp:post_password':
            self._name = 'post_password'
        elif name == 'wp:is_sticky':
            self._name = 'is_sticky'
        elif name == 'wp:attachment_url':
            self._name = 'attachment_url'
        elif name == 'category':
            if attrs['domain'] == 'category':
                self._name = 'category'
            elif attrs['domain'] == 'post_tag':
                self._name = 'tag'

    def _end_element_handler(self, name):
        if name == 'wp:category':
            self._current = None
        elif name == 'wp:tag':
            self._current = None
        elif name == 'wp:term_id':
            self._name = None
        elif name == 'wp:category_nicename':
            self._name = None
        elif name == 'wp:category_parent':
            self._name = None
        elif name == 'wp:cat_name':
            self._name = None
        elif name == 'wp:tag_slug':
            self._name = None
        elif name == 'wp:tag_name':
            self._name = None
        elif name == 'item':
            print self._current
            self._current = None
        elif name == 'title':
            self._name = None
        elif name == 'link':
            self._name = None
        elif name == 'pubDate':
            self._name = None
        elif name == 'dc:creator':
            self._name = None
        elif name == 'guid':
            self._name = None
        elif name == 'description':
            self._name = None
        elif name == 'content:encoded':
            self._name = None
        elif name == 'excerpt:encoded':
            self._name = None
        elif name == 'wp:post_id':
            self._name = None
        elif name == 'wp:post_date':
            self._name = None
        elif name == 'wp:post_date_gmt':
            self._name = None
        elif name == 'wp:comment_status':
            self._name = None
        elif name == 'wp:ping_status':
            self._name = None
        elif name == 'wp:post_name':
            self._name = None
        elif name == 'wp:status':
            self._name = None
        elif name == 'wp:post_parent':
            self._name = None
        elif name == 'wp:menu_order':
            self._name = None
        elif name == 'wp:post_type':
            self._name = None
        elif name == 'wp:post_password':
            self._name = None
        elif name == 'wp:is_sticky':
            self._name = None
        elif name == 'category':
            self._name = None
            return

    def _character_data_handler(self, data):
        if self._cdata is not None:
            self._cdata += data
            return
        if self._current is not None and self._name is not None:
            logging.debug('set %s = "%s"', self._name, data)
            self._current[self._name] = data

    def _start_cdata_section_handler(self):
        self._cdata = u''

    def _end_cdata_section_handler(self):
        if self._current is not None and self._name is not None:
            logging.debug('set %s = "%s"', self._name, self._cdata)
            self._current[self._name] = self._cdata
        self._cdata = None

    def parse(self, fobj):
        self._parser.ParseFile(fobj)


def main():
    argsparser = argparse.ArgumentParser(
        description='Parse WordPress XML export to markdown')
    argsparser.add_argument('xml', type=unicode, metavar='wordpress.xml')
    xml = argsparser.parse_args().xml
    with open(xml) as f:
        p = WPXMLParser()
        p.parse(f)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
