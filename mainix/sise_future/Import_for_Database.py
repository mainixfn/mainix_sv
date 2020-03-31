import pymysql
import requests
import datetime
from bs4 import BeautifulSoup
import urllib.request

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

    def stock_naver_sise(self,stock_name):
        url = "http://finance.naver.com/item/sise_day.nhn?code=215600"
        source = requests.get(url, headers=self.headers).text  # requests 모듈을 통해 텍스트로 끌어옴
        soup = BeautifulSoup(source, 'html.parser')


   #한국거래소 에서 실시간 시세 크롤링 / 20분 지연값 / 신호속도 빠름
    def stock_sise(self,stock_name):
        code = self.stock_code(stock_name)
        stock_api = "http://asp1.krx.co.kr/servlet/krx.asp.XMLSiseEng?code="+code
        request = urllib.request.urlopen(stock_api)
        xml = request.read()
        soup = BeautifulSoup(xml, "html.parser")
        result = soup.find("tbl_stockinfo")
        list = []
        sise = result["curjuka"]
        debi = result["debi"]
        if len(debi)>4:
            debi = debi[:-4]+debi[-3:]
        else:
            debi =debi
        prejuka = result["prevjuka"]
        if len(prejuka) > 4:
            prejuka = prejuka[:-4] + prejuka[-3:]
        elif len(prejuka) >7:
            prejuka =prejuka[:-7] +prejuka[-7:-4]+prejuka[-3:]
        else:
             prejuka =prejuka

        buho = result["dungrak"]
        #dungrak = int(debi)/int(prejuka)
        try:
            dungrak = round(((int(debi)/int(prejuka))*100),1)
            if buho == '2' or buho == '1':
                dungrak = dungrak
            elif buho == '5' or buho == '4':
                dungrak = -dungrak
            else :
                dungrak = 0
        except:
            dungrak = "None"

        list.append({"stock_name":stock_name,"sise": sise, "debi": debi, "dungrak": dungrak})

        # dungrak =result["DungRak"]

        return list


    # 네이버에서 실시간  시세크롤링 / 실시간 반영 / 신호속도 느림
    def stock_naver_sise(self,stock_name):
        list =[]
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
        start_price = price_table.find("span",{"class":"blind"}).text
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
        list.append({"stock_name": stock_name, "sise": sise, "dungrak": dungrak,"start_price":start_price})
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
        today = datetime.datetime.today()
        yester_day = today -datetime.timedelta(days=1)
        time =today.strftime("%H:%M:%S")
        today = today.strftime("%Y%m%d")
        yester_day = yester_day.strftime("%Y%m%d")

        today_list =[]

        try:
            try :
                call_sql = "select stock_name , count from blog_stock_"+today
                self.curs.execute(call_sql)
            except:
                call_sql ="select stock_name , count from blog_stock_"+yester_day
                self.curs.execute(call_sql)

            response = self.curs.fetchall()
            result =[]
            for j in range(len(response)):
                if int(response[j]["count"]) > 4 :
                    result.append(response[j])
                else:
                    pass

            for i in range(len(result)):
                n = result[i]["stock_name"]
                try:
                    data = self.stock_naver_sise(n)
                    p = data[0]["sise"]
                    r = data[0]["dungrak"]
                    c = result[i]["count"]
                    s = data[0]["start_price"]
                except:
                    p ="error"
                    r ="error"
                    c ="error"
                    s ="error"
                today_list.append({"name":n,"price":p,"rate":r,"start_price":s,"time":time})


        except:
            today_list.append({"name": "None", "price": "None", "rate": "None","start_price":"None", "time": time})
        self.curs.close()
        return today_list[:20]

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
    print(stock_future.Today_Stock())
    #print(stock_future.korea_index())