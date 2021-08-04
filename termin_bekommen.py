import sys
import beepy
import datetime as dt
import os
import time
from random import randint
import http.client
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

"""
This Script uses an API endpoint to determine if a vaccination is available.
This Script assumes:
1. You already got your registration code
2. You used your registration code for the appropriate vaccination center while tracking your network. 
   You then caught your authentication credentials (check readme)
"""

#Config
########
registration_code_sindelfinden = "" # insert registration code
authorization_sindelfinden = "Basic " # insert authentication credential
########

payload={}
headers = \
{
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'Accept': 'application/json, text/plain, */*',
    'Cache-Control': 'no-cache',
    'Authorization': "",
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Content-Type': 'application/json',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': "",
    'Accept-Language': 'de-DE,de;q=0.9',
}

# list with dicts.
# each dict contains the info to get an appointment at one vaccination center
# you have to reference the correct data for each vaccination center.
info_list= \
[
    {
        "Stadt": "Sindelfinden",
        "url": "229-iz.impfterminservice.de",
        "plz" : "71065",
        'Authorization': f'{authorization_sindelfinden}',
        'Referer': f'https://229-iz.impfterminservice.de/impftermine/suche/{registration_code_sindelfinden}/71065',
    },

     # {
     #     "Stadt": "Heidelberg",
     #     "url": "001-iz.impfterminservice.de",
     #     "plz" : "69124",
     #     'Authorization': f'Basic {}',
     #     'Referer': f'https://001-iz.impfterminservice.de/impftermine/suche/{}/69124',
     # },
]


def call_request_dict():
    """
    Check API if a vaccination appintment is available in the requested center for your registration code.
    If an appointmenr is available there will be an audio notification.

    :return: boolean or string
    booloean: False if appointment was not found
    string: If appointmenr was found, the string will contain the url to the vaccination center with
    the registration-code included in the URL.
    """
    for dic in info_list:
        headers["Authorization"] = dic["Authorization"]
        headers["Referer"] = dic["Referer"]
        print(f"{dt.datetime.now()} requesting : {dic['Referer']}")

        conn = http.client.HTTPSConnection(dic["url"])
        payload = ''
        conn.request("GET", f"/rest/suche/impfterminsuche?plz={dic['plz']}", payload, headers)
        response = conn.getresponse()
        response_byte = response.read()
        response_str = response_byte.decode("utf-8")

        #print(response.json())
        if response.getcode() != 200:
            print(response.status_code)
            continue

        response_dict = json.loads(response_str)

        if ( (len(response_dict["termine"]) > 0) or (len(response_dict["termineTSS"]) > 0) or \
        (len(response_dict["praxen"].keys()) > 0) ):

            print(dic["Stadt"], response_dict)
            beepy.beep(sound=4)

            return dic["Referer"]
    return False


def create_browser_site(url):
    """
    Creates a chrome instance if an appointment was found.

    :param url: string
    url to the vaccination center. URL will include registration code

    :return: selenium.webdriver
    instance of webdriver. This is required to keep Chrome open, after this script leaved this function.
    """

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(driver_path, options=chrome_options)

    valid_str = "termine suchen"
    str_found = False
    while str_found == False:
        driver.get(url)
        body = driver.find_elements_by_tag_name("body")[0]
        time.sleep(2)
        str_found = valid_str in body.text.lower()
        if str_found == True:
            print("blub")
            break
    return driver

if __name__ == "__main__":
    # you need to have chrome installed. Chromedriver must be in the same directory as this script
    if os.name == "nt":
        driver_path = ".\chromedriver.exe"
    driver = webdriver.Chrome("./chromedriver")

    result = False
    while result == False:
        result = call_request_dict()
        if result != False:
            create_browser_site(result)
            quit()
            sys.exit()
            break
        time.sleep(randint(8, 13))



