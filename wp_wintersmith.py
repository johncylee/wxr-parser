import argparse
import logging
import subprocess
from cStringIO import StringIO
from wp_parser import WPXMLParser


def to_wintersmith_markdown(wp, path=None):
    """write wordpress contents to path.

    :param wp the result of WPXMLParser.parse
    :param path the directory to write to
    """
    for item in wp['items']:
        args = ('pandoc', '-f', 'html', '-t', 'markdown',
                '-o', '%s.md' % item['post_id'])
        popen = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = popen.communicate(item['content'].encode('utf8'))
        if stderr:
            logging.error(stderr)


def wp_to_wintersmith(filepath):
    with open(filepath) as f:
        wp = WPXMLParser().parse(f)
        to_wintersmith_markdown(wp)


def main():
    argsparser = argparse.ArgumentParser(
        description='Parse WordPress XML export to wintersmith')
    argsparser.add_argument('xml', type=unicode, metavar='wordpress.xml')
    xml = argsparser.parse_args().xml
    wp_to_wintersmith(xml)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
