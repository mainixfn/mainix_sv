from bs4 import BeautifulSoup
import requests
import pymysql
import datetime
import schedule

conn = pymysql.connect(host='dydb.c2x6adsfvww3.ap-northeast-2.rds.amazonaws.com', user='qwasdf123',
                               password='rlarltjq1!', db='stock_db', charset='utf8',
                               cursorclass=pymysql.cursors.DictCursor)
curs = conn.cursor()

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
headers = {'User-Agent': user_agent}

def stock_code( stock_name):
    stock_code_sql = "select stock_code from stock_name where stock_name='" + stock_name + "'"
    curs.execute(stock_code_sql)
    result = curs.fetchall()[0]["stock_code"]
    return result

def stock_naver_sise(stock_name):
    list = []
    code = stock_code(stock_name)
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

    return start_price

def save_t_tock_date():
    #sql 쿼리문
    insert_sql = "insert into naver_sise(stock_name, sise, dungrak, start_price,time) values(%s,%s,%s,%s,%s)"
    delet_sql = "delete from naver_sise;"

    #시간변수
    today = datetime.datetime.today()
    yester_day = today -datetime.timedelta(days=1)
    time =today.strftime("%H:%M:%S")
    today = today.strftime("%Y%m%d")
    yester_day = yester_day.strftime("%Y%m%d")

    today_list =[]
    curs.execute(delet_sql)
    #db에서 t_stock call
    try:
        try :
            call_sql = "select stock_name , count from blog_stock_"+today
            curs.execute(call_sql)
        except:
            call_sql ="select stock_name , count from blog_stock_"+yester_day
            curs.execute(call_sql)

        response = curs.fetchall()
        result =[]
        for j in range(len(response)):
            if int(response[j]["count"]) > 4 :
                result.append(response[j])
            else:
                pass

        for i in range(len(result)):
            n = result[i]["stock_name"]
            try:
                data = stock_naver_sise(n)
                p = data[0]["sise"]
                r = float(data[0]["dungrak"])
                c = result[i]["count"]
                s = data[0]["start_price"]
            except:
                p ="error"
                r = 0
                c ="error"
                s ="error"
            curs.execute(insert_sql, (n, p, r, s,time))
    except:
        curs.execute(insert_sql, ("None", "None",0, "None","None"))
    conn.commit()

    return


def job():
    print("I'm working...")




if __name__=="__main__":

    print(stock_naver_sise("힘스"))

    #네이버시세를 주기적으로 저장
    '''
    schedule.every(10).seconds.do(save_t_tock_date)
    while True:
        schedule.run_pending()
    '''

