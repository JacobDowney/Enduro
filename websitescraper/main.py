import requests
from bs4 import BeautifulSoup

# page = requests.get('https://www.strava.com/activities/5497959925/')
#
# soup = BeautifulSoup(page.text, 'html.parser')
#
# print(soup)

with requests.Session() as s:
    p = s.post('https://www.strava.com/activities/5497959925/', data = {
        'email': 'jacobdowney22@gmail.com',
        'password': 'larrydoggy'
    })
    print(p.text)

    # base_page = s.get('https://www.strava.com/activities/5497959925/')
    # soup = BeautifulSoup(base_page.content, 'html.parser')
    # print(soup)
