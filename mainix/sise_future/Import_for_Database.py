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
    def stock_naver_sise(self,stock_name):
        list = []
        code = self.stock_code(stock_name)
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
        # 시간변수
        kst = datetime.timezone(datetime.timedelta(hours=9))
        today = datetime.datetime.now(kst)
        weekday = today.weekday()
        yester_day = today - datetime.timedelta(days=1)
        time = today.strftime("%H:%M:%S")
        today = today.strftime("%Y%m%d")
        yester_day = yester_day.strftime("%Y%m%d")

        today_list = []
        # db에서 t_stock call

        try:
            call_sql = "select stock_name , count from blog_stock_" + today
            self.curs.execute(call_sql)
        except:
            call_sql = "select stock_name , count from blog_stock_" + yester_day
            self.curs.execute(call_sql)

        response = self.curs.fetchall()
        response = sorted(response, key=lambda t:(int(t["count"])), reverse=True)[:15]
        result = []
        for j in range(len(response)):
            if int(response[j]["count"]) > 4:
                result.append(response[j])
            else:
                pass

        for i in range(len(result)):
            n = result[i]["stock_name"]
            if weekday > 4 :
                try:
                    data = self.stock_naver_sise(n)
                    p = data[0]["sise"]
                    r = float(data[0]["dungrak"])
                    c = result[i]["count"]
                    s = data[0]["start_price"]
                    code = self.stock_code(n)
                except:
                    p = "error"
                    r = 0
                    c = "error"
                    s = "error"
                today_list.append({"stock_name":n, "sise":p, "dungrak":0, "start_price":'-',"code":code,"time":"주 말"})

            elif weekday < 5 and int(time[:2]) > 8 and int(time[:2]) < 16:
                try:
                    data = self.stock_naver_sise(n)
                    p = data[0]["sise"]
                    r = float(data[0]["dungrak"])
                    c = result[i]["count"]
                    s = data[0]["start_price"]
                    code = self.stock_code(n)
                except:
                    p = "error"
                    r = 0
                    c = "error"
                    s = "error"
                today_list.append({"stock_name":n, "sise":p, "dungrak":r, "start_price":s,"code":code,"time":time})
            else:
                try:
                    data = self.stock_naver_sise(n)
                    p = data[0]["sise"]
                    r = float(data[0]["dungrak"])
                    c = result[i]["count"]
                    s = data[0]["start_price"]
                    code = self.stock_code(n)
                except:
                    p = "error"
                    r = 0
                    c = "error"
                    s = "error"
                today_list.append({"stock_name":n, "sise":p, "dungrak":0, "start_price":'-',"code":code,"time":"장마감"})

        return today_list

    def korea_index(self):
        kst = datetime.timezone(datetime.timedelta(hours=9))
        today = datetime.datetime.now(kst)
        weekday = today.weekday()
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

        if weekday > 4:
            list.append({"market": "코스피", "indice": kospi_index, "rate": float(kospi_dungrak), "time": "장마감"})
            list.append({"market": "코스닥", "indice": kosdaq_index, "rate": float(kosdaq_dungrak), "time": "장마감"})

        elif int(time[:2]) > 8 and int(time[:2]) < 17:
            list.append({"market": "코스피", "indice": kospi_index, "rate": float(kospi_dungrak),"time":time})
            list.append({"market": "코스닥", "indice": kosdaq_index, "rate": float(kosdaq_dungrak),"time":time})
        else:
            list.append({"market": "코스피", "indice": kospi_index, "rate": float(kospi_dungrak), "time": "장마감"})
            list.append({"market": "코스닥", "indice": kosdaq_index, "rate": float(kosdaq_dungrak), "time": "장마감"})

        return list

    #다우,나스닥 선물 지수
    def america_index(self):
        america = datetime.timezone(datetime.timedelta(hours=-4))
        today = datetime.datetime.now(america)
        weekday = today.weekday()
        time = today.strftime("%H:%M:%S")
        future_current = []

        if weekday == 5 : # 뉴욕시간 기준 토요일 장마감
            url = "https://kr.investing.com/indices/indices-futures"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            future = soup.select('#cross_rates_container > table > tbody > tr ')[:3]
            # a= soup.find('#cross_rates_container > table > tbody > tr > td')
            # print(a)

            for i in future:
                data = list(i)
                market = data[3].get_text()
                index = data[7].get_text()
                rate = data[15].get_text()
                if rate[0] == "+":
                    rate = rate[1:-1]
                else:
                    rate = rate[:-1]
                future_current.append({'market': market, "indice": index, 'rate': 0, "time": "장마감"})

        elif weekday == 6 and int(time[:2]) < 17 : # 뉴욕시간 기준 일요일 17시 이전 장마감
            url = "https://kr.investing.com/indices/indices-futures"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            future = soup.select('#cross_rates_container > table > tbody > tr ')[:3]
            # a= soup.find('#cross_rates_container > table > tbody > tr > td')
            # print(a)

            for i in future:
                data = list(i)
                market = data[3].get_text()
                index = data[7].get_text()
                rate = data[15].get_text()
                if rate[0] == "+":
                    rate = rate[1:-1]
                else:
                    rate = rate[:-1]
                future_current.append({'market': market, "indice": index, 'rate': 0, "time": "장마감"})

        # 뉴욕시간 기준 일요일 17시 ~ 금요일 24시 까지 장운용
        elif int(time[:2])>8 and int(time[:2])<16 :
            url ="https://kr.investing.com/indices/major-indices"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            future = soup.select('table > tbody > tr ')[3:6]
            for i in future:
                data = list(i)
                market = data[3].text
                index = data[5].text
                rate = data[13].text
                if rate[0] == "+":
                    rate = rate[1:-1]
                else:
                    rate = rate[:-1]
                future_current.append({'market': market, "indice": index, 'rate': float(rate), "time": time})

        else:
            url ="https://kr.investing.com/indices/indices-futures"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            future = soup.select('#cross_rates_container > table > tbody > tr ')[:3]
            #a= soup.find('#cross_rates_container > table > tbody > tr > td')
            #print(a)


            for i in future:
                data =list(i)
                market =data[3].get_text()
                index = data[7].get_text()
                rate = data[15].get_text()
                if rate[0] == "+":
                    rate = rate[1:-1]
                else:
                    rate = rate[:-1]
                future_current.append({'market': market, "indice": index, 'rate': float(rate), "time": time})
        result = future_current
        return result

    def wti_future(self):
        kst = datetime.timezone(datetime.timedelta(hours=9))
        today = datetime.datetime.now(kst)
        weekday = today.weekday()
        time = today.strftime("%H:%M:%S")
        wti_future = []

        if weekday > 4 :
            url = "https://kr.investing.com/commodities/real-time-futures"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            wti = soup.select('#cross_rates_container > table > tbody > tr ')[6]
            future_li = []
            wti = list(wti)
            market = wti[3].get_text()
            index = wti[7].get_text()
            rate = wti[15].get_text()
            if rate[0] == "+":
                rate = rate[1:-1]
            else:
                rate = rate[:-1]
            wti_future.append({'market': market, "indice": index, 'rate': 'None', "time": "장마감"})
        else:
            url = "https://kr.investing.com/commodities/real-time-futures"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            wti = soup.select('#cross_rates_container > table > tbody > tr ')[6]
            future_li = []
            wti = list(wti)
            market = wti[3].get_text()
            index = wti[7].get_text()
            rate = wti[15].get_text()
            if rate[0] == "+":
                rate = rate[1:-1]
            else:
                rate = rate[:-1]
            wti_future.append({'market': market, "indice": index, 'rate': float(rate) , "time": time})

            return wti_future

    def usd_exchange(self):
        kst = datetime.timezone(datetime.timedelta(hours=9))
        today = datetime.datetime.now(kst)
        weekday = today.weekday()
        time = today.strftime("%H:%M:%S")
        usd_exchange = []

        if weekday > 4:
            url = "https://kr.investing.com/currencies/usd-krw"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            dollar = soup.find("div", {"class": "top bold inlineblock"})
            dollar = dollar.select("span")
            market = "USD 환율"
            exchange = dollar[0].get_text()
            rate = dollar[3].get_text()
            if rate[0] == "+":
                rate = rate[1:-1]
            else:
                rate = rate[:-1]
            usd_exchange.append({'market': market, "indice": exchange, 'rate': 'None', "time": "장마감"})
        else:
            url = "https://kr.investing.com/currencies/usd-krw"
            source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
            soup = BeautifulSoup(source, 'html.parser')
            dollar = soup.find("div", {"class": "top bold inlineblock"})
            dollar = dollar.select("span")
            market = "USD 환율"
            exchange = dollar[0].get_text()
            rate = dollar[3].get_text()
            if rate[0] == "+":
                rate = rate[1:-1]
            else:
                rate = rate[:-1]
            usd_exchange.append({'market': market, "indice": exchange, 'rate':float(rate), "time": time})
        return usd_exchange




if __name__=="__main__":
    start = datetime.datetime.now()
    stock_future = stock_future()
    print(stock_future.Today_Stock())
    #print(stock_future.korea_index())






'''
#Tday 가격함수를 db에 저장한후 콜 클래스
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
'''