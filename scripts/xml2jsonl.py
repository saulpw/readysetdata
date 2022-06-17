#!/usr/bin/env python3

import sys
import collections
import json
import xml.sax


def simplify(d):
    if not isinstance(d, dict):
        return d

    if len(d) == 1 and '#text' in d:
        return d['#text']

    return {k:simplify(v) for k, v in d.items() if v}


class Handler(xml.sax.handler.ContentHandler):
    def __init__(self, fp, tags):
        self.stack = []
        self.fp = fp
        self.tags = tags

    def startElement(self, tag, attrs):
        if tag in self.tags or self.stack:
            self.stack.append([tag, dict(attrs), []])

        if self.stack[1:]:
            self.stack[-2][1][tag] = self.stack[-1][1]


    def endElement(self, tag):
        if not self.stack:
            return

        _, contents, texts = self.stack.pop()

        s = ''.join(texts).strip()
        if s:
            contents['#text'] = s

        if tag in self.tags:
            print(json.dumps(simplify(contents)), file=self.fp)


    def characters(self, content):
        if self.stack:
            self.stack[-1][2].append(content)


def main():
    rdr = xml.sax.make_parser()
    rdr.setContentHandler(Handler(sys.stdout, sys.argv[1:]))
    rdr.parse(sys.stdin)


main()
