# WXR Parser

A simple WXR parser written in Python to parse the XML export from
WordPress and store the information it in in Python's basic data
structures, i.e. dictionaries and lists. It also goes with a backend
to export it in Markdown syntax suitable for
[Wintersmith](http://wintersmith.io). In its current form, it can
simplify the migration from WordPress to Wintersmith, but it's easy to
be extended to export more formats.

It's created because the author failed to find a simple one to use.

## Usage

`python wxr_parser.py -h` and `python wxr_backend.py -h` to check
usage info. Get a WXR document, try them on it and observe the logs to
understand how it works.

## Note

`wxr_parser` can optionally download the image files used by WordPress
articles. This is for convenience but should only be used with
caution.

## ToDo

1.  unsupported wordpress tags:

	1. [gallery]
	2. [slideshare]
	3. [youtube]
	4. more...

2. disqus support
