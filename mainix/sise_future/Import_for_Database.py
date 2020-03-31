import pymysql
import requests
import datetime
from bs4 import BeautifulSoup
import schedule
import urllib.request
import threading

class stock_future():

    def __init__(self):
        self.conn = pymysql.connect(host='dydb.c2x6adsfvww3.ap-northeast-2.rds.amazonaws.com', user='qwasdf123',
                               password='rlarltjq1!', db='stock_db', charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
        self.curs = self.conn.cursor()

        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}


    def stock_code(self,stock_name):
        stock_code_sql = "select stock_code from stock_name where stock_name='"+stock_name+"'"
        self.curs.execute(stock_code_sql)
        result =self.curs.fetchall()[0]["stock_code"]
        return result


    # 네이버에서 실시간  시세크롤링 / 실시간 반영 / 신호속도 느림

    def Stock_name(self):
        self.curs.execute('select*from stock_name')
        re = self.curs.fetchall()
        name_list =[]
        for i in range(len(re)):
            n = re[i]['stock_name']
            name_list.append(n)
        return name_list


    def Thema_Stock(self,stock):
        sql ='select thema from stock_thema where stock_name=%s'
        self.curs.execute(sql,stock)
        re = self.curs.fetchall()
        return re

    def Today_Stock(self):
        naver_sise_call_sql= "select * from naver_sise"
        self.curs.execute(naver_sise_call_sql)
        re = self.curs.fetchall()
        self.curs.close()
        return re

    def korea_index(self):
        today = datetime.datetime.today()
        time = today.strftime("%H:%M:%S")
        list = []
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
        headers = {'User-Agent': user_agent}
        url = "https://finance.naver.com/sise/"
        source = requests.get(url, headers=headers).text  # requests 모듈을 통해 텍스트로 끌어옴
        soup = BeautifulSoup(source, 'html.parser')
        kospi = soup.find("li", {"onmouseover": "moveIndex('tab_sel1')"})
        kosdaq = soup.find("li", {"onmouseover": "moveIndex('tab_sel2')"})

        try:
            kospi_index = kospi.find("span", {"id": "KOSPI_now"}).text
            kospi_dungrak = kospi.find("span", {"class":"num_s"}).text[-9:-4]
            kosdaq_index = kosdaq.find("span", {"id": "KOSDAQ_now"}).text
            kosdaq_dungrak = kosdaq.find("span", {"class": "num_s"}).text[-9:-4]

        except:
            kospi_index = kospi.find("span", {"class": "num num2"}).text
            kospi_dungrak = kospi.find("span", {"class": "num_s num_s2"}).text[-9:-4]
            kosdaq_index = kosdaq.find("span", {"class": "num"}).text
            kosdaq_dungrak = kosdaq.find("span", {"class": "num_s"}).text[-9:-4]

        list.append({"market": "kospi", "indice": kospi_index, "rate": float(kospi_dungrak),"time":time})
        list.append({"market": "kosdaq", "indice": kosdaq_index, "rate": float(kosdaq_dungrak),"time":time})

        return list


    #다우,나스닥 선물 지수
    def america_index(self):
        url ="https://kr.investing.com/indices/indices-futures"
        source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
        soup = BeautifulSoup(source, 'html.parser')
        future = soup.select('#cross_rates_container > table > tbody > tr ')
        #a= soup.find('#cross_rates_container > table > tbody > tr > td')
        #print(a)

        future_current=[]
        for i in future:
            data =list(i)
            market =data[3].get_text()
            indice = data[7].get_text()
            rate = data[15].get_text()
            if rate[0] == "+":
                rate = rate[1:-1]
            else:
                rate = rate[:-1]
            time = data[17].get_text()
            time = data[17].get_text()
            future_current.append({'market':market ,"indice":indice,'rate' : float(rate), "time" : time})
        result = future_current[:3]

        return  result

if __name__=="__main__":
    start = datetime.datetime.now()
    stock_future = stock_future()
    print(stock_future.save_t_tock_date())
    #print(stock_future.korea_index())