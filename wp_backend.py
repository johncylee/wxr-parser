import argparse
import logging
import re
import sys
import os
import os.path
from subprocess import Popen, PIPE

from wp_parser import WPXMLParser


def to_wintersmith(xml, path):
    """write wordpress contents to path in wintersmith format."""
    wp = wp_to_markdown(xml)
    for item in wp['items']:
        if item['post_type'] != 'post':
            continue
        markdown = item['markdown']
        if markdown.strip(' \t\r\n') == '' :
            continue
        if markdown.find('<span class="more"></span>') == -1:
            markdown = markdown.replace(
                '\n\n', '\n\n<span class="more"></span>\n\n', 1)
        # workaround if we really can't find a place to put `more'
        if markdown.find('<span class="more"></span>') == -1:
            markdown = '...\n\n<span class="more"></span>\n\n' + markdown
        tags = []
        if 'categories' in item:
            tags.extend(item['categories'])
        if 'tags' in item:
            tags.extend(item['tags'])
        tags = ', '.join(tags)
        if tags == '':
            markdown = ('---\ntitle: "%s"\nauthor: "%s"\ndate: %s\n' \
                        + 'template: article.jade\n---\n\n') \
                % (item['title'], item['creator'], item['post_date_gmt']) \
                + markdown
        else:
            markdown = ('---\ntitle: "%s"\nauthor: "%s"\ndate: %s\n' \
                        + 'tags: %s\n' \
                        + 'template: article.jade\n---\n\n') \
                % (item['title'], item['creator'], item['post_date_gmt'],
                   tags) + markdown
        target = os.path.join(path, '%04d' % int(item['post_id']))
        if not os.path.exists(target):
            os.mkdir(target)
        for img in item['content'].get('imgs', []):
            with open(target + '/%s' % img['filename'], 'wb') as f:
                f.write(img['data'])
        target += '/index.md'
        with open(target, 'w') as f:
            f.write(markdown.encode('utf8'))


def wp_to_markdown(xml):
    with open(xml) as xml:
        wp = WPXMLParser().parse(xml)
    postprocess = [
        (re.compile(r'~{3,} \{\.unspecified\}\n'),
         r'```\n'),
        (re.compile(r'~{3,} \{\.(.+)\}\n'),
         r'```\1\n'),
        (re.compile(r'~{3,}\n'),
         r'```\n'),
    ]
    for item in wp['items']:
        text = item['content']['html']
        args = (
            'pandoc', '-f', 'html', '-t',
            'markdown_github-pipe_tables-markdown_in_html_blocks' \
            + '-all_symbols_escapable', '-R',
        )
        popen = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        text, stderr = popen.communicate(text.encode('utf8'))
        if stderr:
            logging.error(stderr)
            sys.exit()
        text = text.decode('utf8')
        for reobj, rep in postprocess:
            text = reobj.sub(rep, text)
        item['markdown'] = text
    return wp


def main():
    argsparser = argparse.ArgumentParser(
        description='Parse WordPress XML export to wintersmith')
    argsparser.add_argument(
        '-b', '--basedir', nargs='?', default='.',
        type=unicode,
        help='base directory to export to. default is current dir.',
    )
    argsparser.add_argument('xml', type=unicode, metavar='wordpress.xml')
    args = argsparser.parse_args()
    to_wintersmith(args.xml, args.basedir)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
