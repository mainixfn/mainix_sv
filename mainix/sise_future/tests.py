import pymysql
from bs4 import BeautifulSoup
from functools import partial
import time
import requests
import datetime
from selenium import webdriver

import concurrent.futures

stock_db_conn = pymysql.connect(host='dydb.c2x6adsfvww3.ap-northeast-2.rds.amazonaws.com', user='qwasdf123',
                                password='rlarltjq1!', db='stock_db', charset='utf8',
                                cursorclass=pymysql.cursors.DictCursor)
stock_db_curs = stock_db_conn.cursor()

user_agent ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
path = "C:\\Users\\Doyoeng_Desktop\\Desktop\\django_coding\\Stock_BigData\\chromedriver"
headers = {'User-Agent' : user_agent }


def Stock_name():
    stock_db_curs.execute('select*from stock_name')
    re = stock_db_curs.fetchall()
    name_list = []
    for i in range(len(re)):
        n = re[i]['stock_name']
        name_list.append(n)
    return name_list

def Thema_Stock(stock):
    sql ='select thema from stock_thema where stock_name=%s'
    stock_db_curs.execute(sql,stock)
    re = stock_db_curs.fetchall()
    return re

def stock_naver_sise(stock_name):
        list = []
        try:
            code = stock_code(stock_name)
        except:
            code =stock_name
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
        headers = {'User-Agent': user_agent}
        url = "http://finance.naver.com/item/sise.nhn?code=" + code
        source = requests.get(url, headers=headers).text  # requests 모듈을 통해 텍스트로 끌어옴
        soup = BeautifulSoup(source, 'html.parser')
        no_today = soup.find("p", {"class": "no_today"})
        no_exday = soup.find("p", {"class": "no_exday"})
        sise = no_today.find("span", {"class": "blind"}).text
        price_table = soup.find("table")
        start_price = price_table.find_all("td", {"class": "first"})[1]
        try:
            start_price = start_price.find("span", {"class": "blind"}).text
        except:
            start_price = start_price.find("span", {"class": "no0"}).text
        try:
            dungrak = no_exday.find_all("em", {"class": "no_up"})[1]
            buho = dungrak.text[1]

        except:
            try:
                dungrak = no_exday.find_all("em", {"class": "no_down"})[1]
                buho = dungrak.text[1]

            except:
                dungrak = no_exday.find_all("em", {"class": "X"})[1]
                buho = ""
        dungrak = buho + dungrak.find("span", {"class": "blind"}).text
        dungrak = float(dungrak)

        list.append({"stock_name": stock_name, "sise": sise, "dungrak": dungrak, "start_price": start_price})

        return list

def Naver_Blog_url_word(days,keyword,page_num):
    days = days
    keyword = keyword
    cafe_today = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    cafe_days_ago = (datetime.datetime.today() - datetime.timedelta(days)).strftime("%Y%m%d%H%M%S")

    url_list1 = []
    blog_text =[]

    url_naver_blog = "https://search.naver.com/search.naver?" \
                     "date_from=" + cafe_today + \
                     "&date_option=2" \
                     "&date_to=" + cafe_days_ago + \
                     "&dup_remove=1&nso=p%3A1d&post_blogurl=&post_blogurl_without=&query=" + keyword + \
                     "&sm=tab_pge&srchby=all&st=sim" \
                     "&where=post&start="+page_num

    source = requests.get(url_naver_blog, headers=headers).text  # requests 모듈을 통해 텍스트로 끌어옴
    soup = BeautifulSoup(source, 'html.parser')
    for text in soup.select("span.inline > a.url"):
        crowl = text.get_text()
        blog_url = "http://m."+crowl
        url_list1.append(blog_url)
    url_set = set(url_list1)
    url_list2 = list(url_set)

    for url in url_list2:
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('window-size=1920x1080')
            options.add_argument("disable-gpu")
            driver = webdriver.Chrome(path,chrome_options=options)
            driver.get(url)
            cont = driver.find_element_by_xpath('//*[@id="viewTypeSelector"]').text
        except:
            cont='error'


        blog_text.append(cont)

       #driver.close()
        time.sleep(2)
    return blog_text


def Blog_find_word(keyword, page_num):

    word_list = Naver_Blog_url_word(1, keyword, page_num)
    sentence_anal = {}
    stock_list = []
    stock_name_list = Stock_name()
    for sentence in word_list:
        for stock_name in stock_name_list:
            if sentence.find(stock_name) > 0 and sentence.count(stock_name) > 1:
                cou = sentence.count(stock_name)
                sentence_anal[stock_name] = cou
    sentence_anal = sorted(sentence_anal.items(), key=lambda t: t[1], reverse=True)
    for i in range(len(sentence_anal)):
        stock_name = sentence_anal[i][0]
        cnt = sentence_anal[i][1]
        try:
            try:
                thema = Thema_Stock(stock_name + " ")[0]['thema']
            except:
                thema = Thema_Stock(stock_name)[0]['thema']
        except:
            thema = "None"
        stock_list.append({'stock_name': stock_name, "thema": thema, "count": cnt})

    return stock_list


def blog_multi_and_dbSave(keyword):
    today = datetime.datetime.today()
    ago_day = today - datetime.timedelta(days=2)
    today = today.strftime("%Y%m%d")
    ago_day = ago_day.strftime("%Y%m%d")
    page_num_list = []
    fun = partial(Blog_find_word, keyword)
    stock_list = []
    for i in range(10):
        if i == 0:
            page_num = str(1)
        else:
            page_num = str(i) + str(1)
        page_num_list.append(page_num)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        for st in executor.map(fun, page_num_list):
            stock_list.append(st)

    creat_sql = "create table blog_stock_" + today + "(id INT NOT NULL AUTO_INCREMENT," \
                                                     "stock_name varchar(50), thema varchar(50),count varchar(10),PRIMARY KEY (id))"
    delete_sql = "drop table blog_stock_" + ago_day + ";"
    insert_sql = "insert into blog_stock_" + today + "(stock_name, thema, count) values(%s,%s,%s)"

    try:
        stock_db_curs.execute(creat_sql)
    except:
        stock_db_curs.execute("SET SQL_SAFE_UPDATES = 0;")
        stock_db_curs.execute("delete from blog_stock_" + today)

    for i in range(len(stock_list)):
        for j in range(len(stock_list[i])):
            c = stock_list[i][j]["count"]
            if int(c) > 4:
                n = stock_list[i][j]["stock_name"]
                t = stock_list[i][j]["thema"]
                stock_db_curs.execute(insert_sql, (n, t, c))
                stock_db_conn.commit()
            else:
                pass
    try:
        stock_db_curs.execute(delete_sql)
    except:
        pass
    stock_db_conn.close()
    return keyword + " Blog Bigdata Analysis for Stock Save Complete"

if __name__=="__main__":
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
    headers = {'User-Agent': user_agent}
    url = "https://emp.koscom.co.kr/home/info/issue/"
    source = requests.get(url, headers=headers).text  # requests 모듈을 통해 텍스트로 끌어옴
    soup = BeautifulSoup(source, 'html.parser')
    kospi = soup.find("div", {"data-v-32e0b8e9 class": "table-box"})
    kosdaq = soup.find("li", {"onmouseover": "moveIndex('tab_sel2')"})
    print(soup)
