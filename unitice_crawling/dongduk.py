#!/usr/local/bin/python
#-*- coding: utf-8 -*-
#simple script for resizing images in all class directories
#also reformats everything from whatever to png

# db 한글 인코딩 현재 안되는 상태.. auzre 크레딧 없어서 설정 막혀버림 ㅜ
# 고민해봐야할 것: top (주요공지) 항상 위에 띄워줄지 ,,?
''' DB table [notice] 
    n_idx
    n_dept
    n_title
    n_link
    n_date
    n_views
    n_isTop 
'''
import config
import requests
from bs4 import BeautifulSoup
import re
import datetime
import mysql.connector
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

mydb = mysql.connector.connect(
    host = config.DATABASE_CONFIG['host'],
    port= config.DATABASE_CONFIG['port'],
    user = config.DATABASE_CONFIG['user'],
    password=config.DATABASE_CONFIG['password'],
    database=config.DATABASE_CONFIG['database']
)
mycursor =  mydb.cursor()   

baseUrl = 'https://www.dongduk.ac.kr'
url = baseUrl +  '/front/boardlist.do?bbsConfigFK=101&searchLowItem=ALL&searchField=ALL&searchValue=&currentPage=1'
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, 'html.parser')

# db 가장 최신 u_idx select 
max=0
try:
    getMaxSql = "SELECT max(n_idx) FROM notice"
    mycursor.execute(getMaxSql)
    max = mycursor.fetchone()[0]
except ValueError as e:
    print(e)
if(not max):
    max = 0
print(max)

all_noti=[]
list = soup.find("tbody").find_all("tr")

for list_tr in list:
    noti={}
    # 각 컬럼 td 순회 
    for td in ['.td-01','.td-02','.td-03','.td-05','.td-06']:
        for b in list_tr.select(td):
            noti[td] = b.text.strip().encode('utf-8')
            # print(noti)
            # 링크는 한번 더 들어가서 끌고나와줌
            if( td =='.td-03'):
                noti['url'] = baseUrl + b.a['href'].encode('utf-8')
    # Top notice 인 경우 체크 그러나 값이 없는데 pk라서 들어가질 않는다 -> 해결해야함 ㅠ
    if(not noti['.td-01']):
        noti['isTop'] = 1
        noti['.td-01'] = 0 
    else: 
        noti['isTop'] = 0
    # idx로 중복 데이터 처리 
    if( (int(noti.get('.td-01')) > max) or (noti.get('isTop') == 1)):
        print(noti)
        all_noti.append(noti)

print(all_noti)
for noti in all_noti:
    if(not noti):
        continue
    insertSql = "INSERT INTO notice(n_idx, n_dept, n_link, n_title, n_date, n_views, n_isTop) VALUES(%s,%s,%s,%s,%s,%s,%s)"
    # print(noti.get('.td-01'), noti.get('.td-02'), noti.get('url'),noti.get('.td-03'),noti.get('.td-05'),noti.get('.td-06') )
    mycursor.execute(insertSql, (noti.get('.td-01'), unicode(noti.get('.td-02').decode('utf-8')), unicode(noti.get('url').decode('utf-8')),unicode(noti.get('.td-03').decode('utf-8')),noti.get('.td-05'),noti.get('.td-06'), noti.get('isTop') ))
    mydb.commit()
mydb.close()