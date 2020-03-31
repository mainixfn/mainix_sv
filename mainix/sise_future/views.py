from django.shortcuts import render
from django.http import HttpResponse
import sys
import os
import django
path = os.getcwd() #현재 파일 위치 문자열로 반환
path = os.path.split(path) #상위폴더위치 찾기 위한 스플릿
sys.path.append(path[0])#상위폴더위치 sys.path에 등록
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mainix.mainix.settings")
django.setup()
import threading
from . import Import_for_Database




# Create your views here.
def main(request):
    stock_future =Import_for_Database.stock_future()
    #save_dt = stock_future.save_t_tock_date()
    america_index = stock_future.america_index()
    korea_index = stock_future.korea_index()
    today_stock = stock_future.Today_Stock()
    context = {'america_index' : america_index,'korea_index':korea_index,'t_stock':today_stock}
    return render(request,"stock_main.html",context)