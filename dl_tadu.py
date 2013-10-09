#!/usr/bin/env python3
# vim:fileencoding=utf-8

import sys
import urllib.request
import lxml.html
import re

def dl(url):
  html = urllib.request.urlopen(url).read().decode()
  print(html)
  html = lxml.html.fromstring(html)
  title = html.cssselect('head')[0][1].text
  patt = '(%\w+)+'
  content = html.cssselect('script')[7].text
  content = re.search(patt, content).group()
  print(content)
  content = content.replace('%','\\').encode()
  content = content.decode('unicode_escape')
  
  with open('a.txt', 'w') as f:
    f.write(title) 
    f.write(content)
if  __name__== '__main__':
  if len(sys.argv) == 2:
    url = sys.argv[1]
    dl(url)
  else:
    print("请给出 URL", file=sys.stderr)
    sys.exit(1)

