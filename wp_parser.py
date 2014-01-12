import argparse
import logging
import re
import sys
import urllib2
from HTMLParser import HTMLParser
from xml.parsers import expat


class WPHTMLParser(HTMLParser):
    """parse wordpress flavored html to regular (but not standalone) html
    and optionally retrieve related images.

    """

    NotParagraph = ('ul', 'ol', 'table', 'pre', 'blockquote', 'h1', 'h2', 'h3',
                    'h4', 'h5', 'h6')

    def __init__(self, retrieve_imgs=True):
        self._retrieve_imgs = retrieve_imgs
        self._reset()
        HTMLParser.__init__(self)

    def _reset(self):
        self._tagstack = []
        self._data = u''
        self._fragment = u''
        self._paragraph = True
        self._imgs = []

    def reset(self):
        self._reset()
        HTMLParser.reset(self)

    def _flush(self):
        if not self._fragment.strip('\t\r\n '):
            return
        data, self._fragment = self._fragment, u''
        if self._paragraph:
            if data.startswith('\n'):
                data = '\n<p>' + data[1:]
            else:
                data = '<p>' + data
            if data.endswith('\n'):
                data = data[:-1] + '</p>\n'
            else:
                data = data + '</p>'
            data = data.replace('\n\n', '</p>\n\n<p>')
        self._data += data

    def retrieve_file(self, url):
        qmark_pos = url.rfind('?')
        if qmark_pos != -1:
            url = url[:qmark_pos]
        filename = url.split('/')[-1]
        if filename == '':
            filename = 'image'
        logging.info('retrieving %s from "%s"', filename, url)
        img = {
            'filename': filename,
            'data': urllib2.urlopen(url).read(),
        }
        self._imgs.append(img)
        return filename

    def handle_starttag(self, tag, attrs):
        self._tagstack.append(tag)
        if tag in self.NotParagraph:
            self._flush()
            self._paragraph = False
        html = '<' + tag
        for attr in attrs:
            html += ' %s="%s"' % attr
        html += '>'
        self._fragment += html

    def handle_endtag(self, tag):
        self._fragment += '</%s>' % tag
        if tag != self._tagstack.pop():
            logging.error('possible malformed html: %s', self._tagstack)
            sys.exit()
        if tag in self.NotParagraph:
            self._flush()
        self._paragraph = True
        for t in self.NotParagraph:
            if t in self._tagstack:
                self._paragraph = False
                break

    def handle_startendtag(self, tag, attrs):
        html = '<' + tag
        for key, value in attrs:
            if self._retrieve_imgs and tag == 'img' and key == 'src':
                value = self.retrieve_file(value)
            html += ' %s="%s"' % (key, value)
        html += '/>'
        self._fragment += html

    def handle_data(self, data):
        self._fragment += data

    def handle_entityref(self, name):
        self._fragment += '&%s;' % name

    def handle_charref(self, name):
        self._fragment += '&#%s;' % name

    def parse(self, data):
        # unix format
        data = data.replace('\r\n', '\n')
        preprocess = [
            (re.compile(r'\n?\[sourcecode\]\n?'),
             r'\n<pre class="unspecified">\n'),
            (re.compile(r'\n?\[sourcecode language="(.+)"\]\n?'),
             r'\n<pre class="\1">\n'),
            (re.compile(r'\n?\[/sourcecode\]\n?'),
             r'\n</pre>\n'),
        ]
        for reobj, rep in preprocess:
            data = reobj.sub(rep, data)
        self.feed(data)
        self._flush()
        translated = self._data
        imgs = self._imgs
        self.reset()
        logging.debug('translated: %s', translated)
        return {
            'html': translated,
            'imgs': imgs,
        }


class WPXMLParser(object):

    def __init__(self, retrieve_imgs=True):
        self._categories = []
        self._tags = []
        self._items = []
        self._current = None
        self._name = None
        self._data = u''
        xmlparser = expat.ParserCreate()
        xmlparser.StartElementHandler = self._start_element_handler
        xmlparser.EndElementHandler = self._end_element_handler
        xmlparser.CharacterDataHandler = self._character_data_handler
        self._xmlparser = xmlparser
        self._htmlparser = WPHTMLParser(retrieve_imgs)

    def _to_html(self, name):
        """what's in _current[_name] now is supposed to be wordpress flavored
        html, which means it contains some wordpress specific [tag],
        and blank line means <p>.

        """
        parsed = self._htmlparser.parse(self._current[self._name])
        self._current[name] = parsed

    def _flush(self):
        if self._current is not None and self._name is not None:
            logging.debug('%s = "%s"', self._name, self._data)
            self._current[self._name] = self._data
        self._data = u''

    def _start_element_handler(self, name, attrs):
        self._flush()
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
        self._flush()
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
            self._items.append(self._current)
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
            self._to_html('content')
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

    def _character_data_handler(self, data):
        self._data += data

    def parse(self, fobj):
        self._xmlparser.ParseFile(fobj)
        return {
            'categories': self._categories,
            'tags': self._tags,
            'items': self._items,
        }


def main():
    argsparser = argparse.ArgumentParser(
        description='Parse WordPress XML')
    argsparser.add_argument(
        '--no-image', action='store_false', help='do not retrieve images')
    argsparser.add_argument('xml', type=unicode, metavar='wordpress.xml')
    args = argsparser.parse_args()
    with open(args.xml) as f:
        p = WPXMLParser(args.no_image)
        p.parse(f)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
