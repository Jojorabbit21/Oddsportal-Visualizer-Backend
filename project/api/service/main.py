import requests
import pandas as pd
import json
import re
import datetime
import time
from pprint import pprint
from bs4 import BeautifulSoup

from colorama import Fore, Back, Style #CLI Colors
import psutil #Memory Checker

from .utils import get_xhash, unhash, headers, betting_types, sports_id, bookmakers_id


def GetOddsData(match_url, betting_type):
    match_url = str(match_url).replace(" ", "")
  
    # match_url = input(Back.GREEN + Fore.WHITE + Style.BRIGHT + "Enter URL:" + Style.RESET_ALL + " ")
    print(Back.GREEN + Fore.WHITE + Style.BRIGHT + f"Enter URL: {match_url}" + Style.RESET_ALL + " ")
    
    try:
      match_id = match_url.split("/")[-2:-1][0].split("-")[-1:][0]
    except:
      raise ValueError(Back.RED + Fore.WHITE + Style.BRIGHT + "[!]Wrong URL! Please Try again." + Style.RESET_ALL)

    today = datetime.date.today().strftime("%Y%m%d")
    
    try:
      sport_input = match_url.split(".com/")[1].split("/")[0]
      print(Back.GREEN + Fore.WHITE + Style.BRIGHT + "Sports Type:" + Style.RESET_ALL + " " + sport_input)
    except:
      raise ValueError(Back.RED + Fore.WHITE + Style.BRIGHT + "[!]Wrong Sport Type! Please check your URL." + Style.RESET_ALL)
    betting_type = 'ha'

    # 추후에 input 으로 변경 -> 프론트단 POST 구현
    version_id = 1
    sport_id = sports_id[sport_input]
    betting_type = betting_types[betting_type]
    scope_id = 1
    target_bookie = bookmakers_id['Pinnacle']
    
    try:
      response = requests.get(match_url, headers=headers)
      html = response.text
      soup = BeautifulSoup(html, 'html.parser')
      
      # Home - Away -> ['Home', 'Away']
      match_title = soup.select_one("#col-content > h1").text.split(" - ")
      # t1663082100-4-1-1-1 -> t1663082100 -> 1663082100
      match_date = soup.select_one("#col-content > p.date.datet")['class'][-1:][0].split("-")[0].replace("t","")
      match_date = datetime.datetime.fromtimestamp(int(match_date))
      
      match_info = {
        "Home": match_title[0],
        "Away": match_title[1],
        "Date": match_date
      }
      
      if response.status_code == 200:
          html = response.text
          xhash = unhash(re.findall(r'xhash":"([^"]+)', html)[0])
          time_now = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=2)
          print(time_now)
          time_now_ms = round(time_now.timestamp() * 1000)
          print(time_now_ms)
          json_url = "http://fb.oddsportal.com/feed/match/" + "%d-%d-%s-%d-%d-%s.dat?_=%s" % \
                      (
                        version_id,
                        sport_id,
                        match_id,
                        betting_type,
                        scope_id,
                        xhash,
                        time_now_ms
                      )
          print(json_url)
          response = requests.get(json_url, headers=headers)
          odds_data = json.loads(re.findall(r"\.dat',\s({.*})", response.text)[0])
          with open('odds.json', 'w') as file:
            json.dump(odds_data, file, indent=4)
          # Current Odds
          history_cols = odds_data['d']['history']['back'].keys()
          history_dict = dict()
          for idx, cols in enumerate(history_cols):
              history_odds = odds_data['d']['history']['back'][f'{cols}'][f'{target_bookie}']
              data = dict()
              for idx_s, item in enumerate(reversed(history_odds)):
                  value, _, timestamp = item
                  row = dict()
                  row['timestamp'] = str(datetime.datetime.fromtimestamp(timestamp))
                  row['value'] = value
                  data[idx_s] = row
              history_dict[idx] = data
          # with open('history.json', 'w') as file:
          #   json.dump(history_dict, file, indent=4)
          return history_dict
    except:
      raise ValueError(Back.RED + Fore.WHITE + Style.BRIGHT + "[!]Wrong URL or Unknown Error occured! Please Try Again." + Style.RESET_ALL)
        
        
        
        
                   
# if __name__ == '__main__':
#   # Running time
#   start_time = time.time()
  
#   file = GetOddsData()
  
#   # Memory checking
#   p = psutil.Process()
#   rss = p.memory_info().rss / 2 ** 20 # Bytes to MB
#   print(f"memory usage: {rss: 10.5f} MB")

#   print(Back.WHITE + Fore.BLUE + Style.BRIGHT + "RUNNING TIME : " + Style.RESET_ALL + Back.GREEN + Fore.WHITE + Style.BRIGHT + f"{time.time() - start_time} sec" + Style.RESET_ALL)
