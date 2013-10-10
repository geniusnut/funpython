#!/usr/bin/env python3
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
    return ("http://www.tadu.com"+link)
  book['links'] = list(map(getlink, html.cssselect('a[href^="/book/366292"]')))
  print("共 %d 页" % len(book['links']))
  return book
def geturl(url):
  response = urllib.request.urlopen(url)
  return response.read().decode()

def getpage(url, f, count):
  html = geturl(url)
  html = lxml.html.fromstring(html)
  title = html.cssselect('h2')[0].text
  
  print('第 %d 页（%s）已下载' % (count, title))
  patt = '(%\w+)+'
  f.write(title + '\n\n')
  content = html.cssselect('script')[7].text
  content = re.search(patt, content).group()
  #print(content)
  content = content.replace('%3Cbr%2F%3E%3Cbr%2F%3E','\n')
  content = content.replace('%','\\').encode()
  content = content.decode('unicode_escape')
  f.write(content + '\n')
  
def dl(url):
  book = getBookInfo(geturl(url))
  fname = book['title']
  fname += '.txt' 
  with open(fname, 'w') as f: 
    for i, l in enumerate(book['links'][1::]):
      getpage(l, f, i+1)
  print('下载完成！') 
if  __name__== '__main__':
  if len(sys.argv) == 2:
    url = sys.argv[1]
    dl(url)
  else:
    print("请给出 URL", file=sys.stderr)
    sys.exit(1)

