#!/usr/bin/env python3
  iook['author'] = 
# vim:fileencoding=utf-8

import sys
import urllib.request
import lxml.html
import re

def getBookInfo(str):
  html = lxml.html.fromstring(str)
  book = {}
  book['title'] = html.cssselect('a[href^="/book/366292/"]')[0].get('alt')
  book['author'] = html.cssselect('a[href^="/book/author/"]')[0].get('alt')

  print("书名:", book['title'])
  print("作者:", book['author'])
  def getlink(a):
    link = a.get('href')
    return ("")
  book['links'] = list(map(getlink, html.cssselect('a[href^="/book/366292"]')))
def geturl(url):
  response = urllib.request.urlopen(url)
  return response.read().decode()

def getpage(url, f, count):
  html = geturl()
  html = lxml.html.fromstring(html)
  title = html.cssselect('head')[0][1].text
  patt = '(%\w+)+'
  content = html.cssselect('script')[7].text
  content = re.search(patt, content).group()
  #print(content)
  content = content.replace('%','\\').encode()
  content = content.decode('unicode_escape')
  
def dl(url):
  book = getBookInfo(geturl(url))
  fname = book['title']
  
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

