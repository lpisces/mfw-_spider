#! /usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import time

#h = {"user_agent" : "TravelGuideMdd/7.6.2 (iPhone; iOS 10.0.1; Scale/2.00),Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Mobile/14A403 mfwappcode/cn.mafengwo.www mfwappver/7.6.2 mfwjssdk/0.1"}
h = {"user_agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"}
a = "PHPSESSID=bb0h86p1s50kip4q5mrenk8q35; mfw_uuid=57f8c4f1-d94f-6c55-b999-ad1802aef6a3; oad_n=a%3A3%3A%7Bs%3A3%3A%22oid%22%3Bi%3A2581%3Bs%3A2%3A%22dm%22%3Bs%3A16%3A%22mapi.mafengwo.cn%22%3Bs%3A2%3A%22ft%22%3Bs%3A19%3A%222016-10-08+18%3A05%3A37%22%3B%7D; __openudid=350765BA-CFE3-49BB-80DA-E85686D91743; __idfv=350765BA-CFE3-49BB-80DA-E85686D91743; __idfa=6AAACD72-C42B-45A6-A186-DB307000B9CD"

data = {
  "app_code": "cn.mafengwo.www",
  "app_ver": "7.6.2",
  "channel_id": "App Store",
  "column_num": "2",
  "device_token": "e9d9f1e0f4382d10771486526695bd5224903812c0da39cf2afd0693eccb3fa7",
  "device_type": "ios",
  "hardware_model": "iPhone8,1",
  "idfa": "6AAACD72-C42B-45A6-A186-DB307000B9CD",
  "idfv": "350765BA-CFE3-49BB-80DA-E85686D91743",
  "is_square": "0",
  "mfwsdk_ver": "20160401",
  "o_lat": "28.117029",
  "o_lng": "112.970454",
  "oauth_consumer_key": "4",
  "oauth_nonce": "148168a8-20d1-4a74-b616-d493cb192a6a",
  "oauth_signature": "o/1YmTPWmU0dhIADvmmx8k4nzKM=",
  "oauth_signature_method": "HMAC-SHA1",
  "oauth_timestamp": "1476005160",
  "oauth_token": "0_d5af5e71fbcea723b6af2ddae8ab084a",
  "oauth_version":  "1.0",
  "offset":  "0",
  "open_udid": "350765BA-CFE3-49BB-80DA-E85686D91743",
  "screen_height":   "667.000000",
  "screen_scale":    "2",
  "screen_width":    "375.000000",
  "sys_ver": "10.0.1",
  "time_offset": "480",
  "x_auth_mode": "client_auth"
}

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

def get_poi(pid = '12871'):
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

def get_poi_images(poi_id, page_num = 5):
  url = "http://www.mafengwo.cn/mdd/ajax_photolist.php?act=getPoiPhotoList&poiid=%s&page=%s"
  album = []
  for i in range(1, page_num + 1):
    try:
      u = url % (poi_id, i)
      r = requests.get(u, headers = h)
      soup = bs(r.text, 'html5lib')
      c = soup.select(".cover")
      for a in c:
        album.append("http://www.mafengwo.cn" + a["href"])
    except Exception as e:
      continue
  print album
  imgs = []
  for a in album:
    imgs += _get_album(a)
  return images

def _get_album(url):
  try:
    imgs = []
    r = requests.get(url, headers = h)
    soup = bs(r.text, 'html5lib')
    items = soup.select("li._j_noimg")
    for i in items:
      img = {}
      try:
        img["title"] = i["data-source_title"]
        print img["title"]
        img["intro"] = i["data-source_intro"]      
        img["ctime"] = i["data-imgptime"]
        img["bigimg"] = i["imgbig"]
        img["smallimg"] = i["imgsmall"]
      except:
        continue
      imgs.append(img)
  except Exception as e:
    print e
    return []
  return imgs

if __name__ == "__main__":
  print get_poi_images(1318)

