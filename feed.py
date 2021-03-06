#!/usr/bin/env python3
"""
Usage:
  feed.py [-p=<port>]
  feed.py -h

Options:
  -p=<port>  port [default: 80]
  -h --help  show this
"""

import datetime
import time
from time import mktime
from urllib.parse import urljoin

from docopt import docopt
from flask import Flask
from flask import request
from flask import render_template
from werkzeug.contrib.atom import AtomFeed
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/feed')
def feed():
    feed = AtomFeed('China National Museum\'s notices feed',
            feed_url=request.url,
            url=request.url_root,
            author={'name': 'typd', 'email': 'othertang@gmail.com'})
    list = get_notice_list()
    for title, link, content, updated in list:
        feed.add(title, content, url=link, updated=updated)
    return feed.get_response()

def get_notice_list():
    url = 'http://www.chnmuseum.cn/Default.aspx?TabId=71&MoreModuleID=649&MoreTabID=124'
    base = 'http://www.chnmuseum.cn/'
    agent = {'User-Agent':'Mozilla/5.0'}
    html = None
    try:
        html = requests.get(url, headers=agent, timeout=5).text
    except:
        print('fail to access {}'.format(url))
        return []
    soup = BeautifulSoup(html)
    table = soup.find(id='ess_ctr439_ListC_Info_LstC_Info')
    rows = table.find_all('table')
    items = []
    for row in rows:
        a = row.a
        title = a.get_text()
        text = row.get_text()
        date = time.strptime(row.find(class_='title1 ').get_text(), '%Y-%m-%d')
        items.append((title, urljoin(base, a.get('href')), text, datetime.datetime.fromtimestamp(mktime(date))))
    items.sort(key=lambda tup: tup[3])
    items.reverse()
    return items

def get_middle(str, start, end):
    start_index = str.find(start)
    end_index = str[start_index + len(start):].find(end)
    return str[start_index + len(start):start_index + len(start) + end_index]

if __name__ == '__main__':
    args = docopt(__doc__)
    app.debug = True
    app.run(host='0.0.0.0', port=int(args['-p'] or 80))
