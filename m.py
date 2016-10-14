#! /usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import os
import json
import logging

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(filename='mfw.log', filemode='a', level=logging.DEBUG, format='[%(asctime)s]\t%(message)s', datefmt="%Y/%m/%d %H:%M:%S")
logging.getLogger("requests").setLevel(logging.WARNING)

h = {"Accept-Encoding": "gzip, deflate, sdch", "user_agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}
a = "mfw_uuid=57c53eda-942b-0361-4849-98a78362c803; __mfwurd=a%3A3%3A%7Bs%3A6%3A%22f_time%22%3Bi%3A1472544475%3Bs%3A9%3A%22f_rdomain%22%3Bs%3A0%3A%22%22%3Bs%3A6%3A%22f_host%22%3Bs%3A3%3A%22www%22%3B%7D; __mfwuuid=57c53eda-942b-0361-4849-98a78362c803; _r=google; _rp=a%3A2%3A%7Bs%3A1%3A%22p%22%3Bs%3A15%3A%22www.google.com%2F%22%3Bs%3A1%3A%22t%22%3Bi%3A1472545422%3B%7D; oad_n=a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A1029%3Bs%3A2%3A%22dm%22%3Bs%3A15%3A%22www.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222016-10-08+17%3A52%3A09%22%3B%7D; PHPSESSID=pi9isl7ue6h991l669f17ki885; __mfwlv=1476067280; __mfwvn=6; __mfwlt=1476067280; CNZZDATA30065558=cnzz_eid%3D1345273616-1472543737-%26ntime%3D1476065044; uva=a%3A5%3A%7Bs%3A2%3A%22lt%22%3Bi%3A1476067280%3Bs%3A10%3A%22last_refer%22%3Bs%3A6%3A%22direct%22%3Bs%3A5%3A%22rhost%22%3Bs%3A0%3A%22%22%3Bs%3A4%3A%22step%22%3Bi%3A73%3Bs%3A13%3A%22host_pre_time%22%3Bs%3A10%3A%222016-08-30%22%3B%7D"
c = dict([tuple(i.split("=")) for i in a.replace(" ", "").split(";")])

def get_city():
  url = "http://www.mafengwo.cn/mdd/"
  try:
    r = requests.get(url, headers = h)
    soup = bs(r.text, 'html5lib')
    a1 = soup.select(".hot-list")[0].select("a")
    a2 = soup.select(".bd-china")[0].select("a")
    a = a1 + a2
    c = []
    for i in a:
      if len(i.text) != 0:
        c.append((i.text, i["href"].split("/")[-1].replace(".html", "")))
    return c
  except:
    return None

def get_poi(pid = 0):
  logging.info("Get poi in city %s" % (pid, ))
  url = "http://www.mafengwo.cn/jd/%s/gonglve.html" % (pid, )
  try:
    r = requests.get(url, headers = h)
    soup = bs(r.text, 'html5lib')
    a = soup.select(".list")[0].select("a")
    c = []
    for i in a:
      if len(i.text) != 0:
        c.append((i.text.strip(), i["href"].split("/")[-1].replace(".html", "")))
    return c
  except Exception as e:
    print e
    return None

def get_poi_images(poi_id, page_num = 1):
  url = "http://www.mafengwo.cn/mdd/ajax_photolist.php?act=getPoiPhotoList&poiid=%s&page=%s"
  album = []
  for i in range(1, page_num + 1):
    logging.info("Get images from poi %s, page %s" % (poi_id, i))
    try:
      u = url % (poi_id, i)
      r = requests.get(u, headers = h)
      soup = bs(r.text, 'html5lib')
      c = soup.select(".cover")
      for a in c:
        album.append("http://www.mafengwo.cn" + a["href"])
	break
    except Exception as e:
      continue
  imgs = []
  pool = ThreadPool(2)
  r = pool.map(_get_album, album)
  pool.close() 
  pool.join()
  for img in r:
    imgs += img
  logging.info("Got %s images" % (len(imgs), ))
  return imgs

def get_poi_intro(poi_id):
  url = "http://www.mafengwo.cn/poi/%s.html" % (poi_id, )
  poi = {}
  try:
    r = requests.get(url, headers = h, cookies = c)
    soup = bs(r.text, 'html5lib')
    poi["name"] = soup.select("h1")[0].text
    intro = soup.select("dl.intro")[0]
    poi['intro'] = intro.select('dt span')[0].text
    attr = []
    for i in intro.select("dd"):
      key = i.select("span.label")[0].text
      value = i.select("span")[-1].text
      attr.append((key, value))
    poi['attr'] = attr
    tips = []
    for j in soup.select("div.poigonglve dl"):
      key = j.select("dt")[0].text
      value = j.select("dd")[0].text
      tips.append((key.strip(), value.strip()))
    poi["tips"] = tips
    return poi
  except Exception as e:
    print e
  return None
    

def _get_album(url):
  try:
    imgs = []
    r = requests.get(url, headers = h, cookies = c)
    soup = bs(r.text, 'html5lib')
    items = soup.select("li._j_noimg")
    for i in items:
      img = {}
      try:
        img["title"] = i["data-source_title"].encode("iso-8859-1")
        img["intro"] = i["data-source_intro"].encode("iso-8859-1")     
        img["ctime"] = i["data-imgptime"].encode("iso-8859-1")
        img["bigimg"] = i["data-imgbig"]
        img["smallimg"] = i["data-imgsmall"]
        img['source_id'] = i["data-source_id"]
        img['source_uid'] = i["data-source_uid"]
        imgs.append(img)
      except Exception as e:
        print e
        continue
  except Exception as e:
    print e
    return []
  return imgs

def go(out = './data', cache = True):
  if not os.path.isdir(out):
    os.mkdir(out)
  city_file = "%s/%s" % (out, "city.json")
  if not os.path.isfile(city_file) or cache == False:
    action = 'Write'
    city = list(set(get_city()))
    with open(city_file, "w") as f:
      f.write(json.dumps(city))
  else:
    action = 'Read'
    with open(city_file, 'r') as f:
      city = json.loads(f.read())
  logging.info("%s %s" % (action, city_file))
  logging.info("Get %s cities" % (len(city), ))
  
  cids = []
  for c in city:
    cids.append(c[1])
    city_dir = "%s/%s"% (out, c[1])
    if not os.path.isdir(city_dir):
      logging.info("Create dir for %s" % (c[0], ))
      os.mkdir(city_dir)

  poi_file = "%s/%s" % (out, "poi.json")
  if not os.path.isfile(poi_file) or cache == False:
    action = "Write"
    pool = ThreadPool(2)
    r = pool.map(get_poi, cids)
    pool.close() 
    pool.join()
    logging.info("Write %s" % (poi_file))
    with open(poi_file, "w") as f:
      f.write(json.dumps(r))
  else:
    action = "Read"
    logging.info("Read %s" % (poi_file))
    with open(poi_file, "r") as f:
      r = json.loads(f.read())

  for i in range(len(cids)):
    for poi in r[i]:
      poi_name = poi[0]
      poi_id = poi[1]
      poi_dir = "%s/%s/%s"% (out, cids[i], poi_id)
      if not os.path.isdir(poi_dir):
        logging.info("Create dir for poi %s %s" % (poi_name, poi_dir))
        os.mkdir(poi_dir)
      intro_file = poi_dir + "/intro.json"
      if not os.path.isfile(intro_file) or 0 == os.path.getsize(intro_file):
        intro = get_poi_intro(poi_id)
        with open(intro_file, "w") as f:
          logging.info("Write intro for poi %s %s" % (poi_name, poi_dir))
          f.write(json.dumps(intro))
      else:
        logging.info("Skip intro for poi %s %s" % (poi_name, poi_dir))

      images_file  = poi_dir + "/images.json"
      if not os.path.isfile(images_file) or 0 == os.path.getsize(images_file):
        images = get_poi_images(poi_id)
        with open(images_file, "w") as f:
          logging.info("Write iamges for poi %s %s" % (poi_name, poi_dir))
          f.write(json.dumps(images))
      else:
        logging.info("Skip images for poi %s %s" % (poi_name, poi_dir))
      
if __name__ == "__main__":
  go()

