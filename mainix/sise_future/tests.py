from bs4 import BeautifulSoup
import urllib.request
import requests
import xml.etree.ElementTree as ET

def korea_index():
    list = []
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.146 Whale/2.6.90.18 Safari/537.36'
    headers = {'User-Agent': user_agent}
    url ="https://finance.naver.com/sise/"
    source = requests.get(url, headers=headers).text  # requests 모듈을 통해 텍스트로 끌어옴
    soup = BeautifulSoup(source, 'html.parser')
    kospi = soup.find("li",{"onmouseover":"moveIndex('tab_sel1')"})
    kospi_index = kospi.find("span",{"class":"num num2"}).text
    kospi_dungrak = kospi.find("span",{"class":"num_s num_s2"}).text[-9:-3]
    kosdaq = soup.find("li",{"onmouseover":"moveIndex('tab_sel2')"})
    kosdaq_index = kosdaq.find("span", {"class": "num"}).text
    kosdaq_dungrak =kosdaq.find("span",{"class":"num_s"}).text[-9:-3]
    list.append({"name":"kospi","index":kospi_index,"dungrak":kospi_dungrak})
    list.append({"name":"kosdaq","index":kosdaq_index,"dungrak":kosdaq_dungrak})

    return list
print(korea_index())



'''
url = "http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108"
request = urllib.request.urlopen(url)
xml = request.read()
soup = BeautifulSoup(xml, "html.parser")
print(soup.find("location"))
'''