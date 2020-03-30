import pymysql
import requests
import datetime
from bs4 import BeautifulSoup
#from Import_for_Database import stock_code

user_agent ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
headers = {'User-Agent' : user_agent }



user_agent ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
headers = {'User-Agent' : user_agent }



#종목 가격/ 등락 데이터
def stock_data(stock_name):
    stock_base_url = "https://finance.naver.com/item/main.nhn?code="
    stock_list =[]
    code = stock_code(stock_name)
    url = stock_base_url + code
    source = requests.get(url,headers=headers).text
    soup = BeautifulSoup(source, 'html.parser')
    price = soup.select("div.today > p.no_today > em > span.blind")
    rate = soup.select("div.today > p.no_exday > em > span.blind")
    rate = rate[1].text
    price = price[0].get_text()
    flutuation = soup.select("div.today > p.no_exday > em > span ")[0].text
    if flutuation == "상승":
        rate ="+"+rate
    elif flutuation == "하락":
        rate = "-"+rate
    else:
        rate = rate

    stock_list.append({"price":price,"rate":rate})
    return stock_list


#다우,나스닥,코스피 선물 지수
def future_current():
    url ="https://kr.investing.com/indices/indices-futures"
    source = requests.get(url, headers=headers).text  # requests 모듈을 통해 텍스트로 끌어옴
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
        time = data[17].get_text()
        future_current.append({'market':market ,"indice":indice,'rate' : rate, "time" : time})
    result = future_current[:3]
    result.append(future_current[-4])
    return  result
if __name__=="__main__":
    print(stock_data("케이엠"))