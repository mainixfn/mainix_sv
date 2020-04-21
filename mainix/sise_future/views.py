from django.shortcuts import render
from django.http import HttpResponse
import sys
import os
import django
import datetime
path = os.getcwd() #현재 파일 위치 문자열로 반환
path = os.path.split(path) #상위폴더위치 찾기 위한 스플릿
sys.path.append(path[0])#상위폴더위치 sys.path에 등록
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainix.mainix.settings")
django.setup()
import threading
from . import Import_for_Database
#from .Import_for_Database import stock_future




# Create your views here.
def main(request):
    kst = datetime.timezone(datetime.timedelta(hours=9))
    today = datetime.datetime.now(kst)
    time = today.strftime("%H:%M:%S")[:2]
    time = int(time)
    stock_future =Import_for_Database.stock_future()
    america_index = stock_future.america_index()
    korea_index = stock_future.korea_index()
    today_stock = stock_future.Today_Stock()
    wti_index = stock_future.wti_future()
    usd_exchange = stock_future.usd_exchange()
    shinhan_wti_etn =stock_future.shinhan_wti()
    context = {'america_index' : america_index,'korea_index':korea_index,'t_stock':today_stock,
               "usd_exchange":usd_exchange,"wti":wti_index,"shinhan":shinhan_wti_etn,'time':time}
    return render(request,"stock_main.html",context)

