import requests
from bs4 import BeautifulSoup
import json

def make_htmls(cases):
    htmls = []
    for i in range(len(cases)):
        text = str(cases[i]['description'])
        title = '<b>'
        title += str(cases[i]['name'])
        title += '</b>\n\n'
        details = '<b>'
        details += str(cases[i]['details'])
        details += '</b>\n\n'
        time = '<b>'
        time += str(cases[i]['time'])
        time += '</b>\n'
        place = '<b>'
        place += str(cases[i]['place'])
        place += '</b>\n\n'
        new_text = ''
        new_text += title
        new_text += time
        new_text += place
        new_text += details
        flag = False
        for k in range(len(text)):
            if k <= len(text) - 2:
                if (text[k] == '<') and (text[k+1] == 'd'):
                    flag = True
                if text[k] == '>':
                    flag = False
            if not(flag):
                new_text += text[k]
        new_text = new_text.replace('>>', '')
        new_text = new_text.replace('</div>', '')
        new_text = new_text.replace('<br/>', '\n')
        new_text = new_text.replace('<u>', '')
        new_text = new_text.replace('</u>', '')
        htmls.append(new_text)
    return htmls

def get_coordinates(place):
    API_KEY = '' #ЗДЕСЬ НУЖЕН API КЛЮЧ ПОИСКА ЯНДЕКСА ПО ОРГАНИЗАЦИЯМ
    request = 'https://search-maps.yandex.ru/v1/?apikey={}&text={}&lang=ru'
    a = requests.get(request.format(API_KEY, place))
    json_data = json.loads(a.text)
    if json_data['properties']['ResponseMetaData']['SearchResponse']['found'] == 0:
        return []
    return json_data['features'][0]['geometry']['coordinates']

def main():
    a = requests.get('https://afisha.zona.media')
    b = BeautifulSoup(a.text,"html.parser")
    blocks = b.findAll('div', {'class':"t513__row t-row t-clear"})
    cases = []
    for i in blocks:
        time_place = i.find('div',{'class':'t513__time t-name t-name_md'}).findAll('span')
        time = time_place[0].text
        place = time_place[2].text
        case_details = i.find('div', {'class':'t513__rightcol t-col t-col_7 t-prefix_1'})
        name_of_case = case_details.find('div',{'class':'t513__persname t-descr t-descr_sm'}).find('span').text
        part_of_case = case_details.find('div',{'class':'t513__persname t-descr t-descr_sm'}).findAll('span',{'style':'font-weight: 300;'})[1].text
        if part_of_case.find('судья') != -1:
            index = part_of_case.find('судья')
            part_of_case = part_of_case[:index] + '\n' + part_of_case[index:]
        html_description = i.find('div',{'class':'t513__text t-text t-text_sm'})
        cases.append({'name':name_of_case, 'details':part_of_case, 'description':html_description, 'time':time, 'place':place}  )
    return cases
