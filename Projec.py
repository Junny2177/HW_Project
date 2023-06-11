#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import requests
import numpy
import random
import string 
import json
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import streamlit as st
import time
import sympy


# In[2]:


def ignore_details (words):
    string_return = str(words)
    table = str.maketrans("", "", string.punctuation)
    string_return = string_return.translate(table)
    string_return = string_return.lower()
    return (string_return)
    
            


# In[ ]:


def basic_game_info (name, key):
 # Введите ваш ключ API Steam
 steam_key = key

 # Введите название игры
 game_name = ignore_details(name)

 # Получите список всех игр и их идентификаторов
 all_games_url = f"http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key={steam_key}&format=json"
 all_games_response = requests.get(all_games_url)
 all_games_data = all_games_response.json()

 # Найдите игру с нужным названием и извлеките ее идентификатор
 game_id = None
 for game in all_games_data["applist"]["apps"]:
    listname = ignore_details(game['name'])
    if listname == game_name:
        game_id = game["appid"]
        break

 # Если игра не найдена, выведите сообщение об ошибке
 if game_id is None:
    game_info_new = {'Name' : 'Игра не найдена в Steam', 'Release date' : None, 'Price' : None, 'Developer' : None, 'Description' : None, 'Amount of reviews': None}
    df_game = pd.DataFrame(game_info_new, index=["1"])
 else:
    # Получите информацию об игре по ее идентификатору
    game_info_url = f"http://store.steampowered.com/api/appdetails?appids={game_id}"
    game_info_response = requests.get(game_info_url)
    game_info_data = game_info_response.json()


    # Если информация об игре доступна, выведите ее
    if game_info_data[str(game_id)]["success"]:
        game_info = game_info_data[str(game_id)]["data"]
        descript = str(game_info['detailed_description'])
        descript = re.sub(r"\<.*?\>", ' ', descript)
        if 'price_overview' in game_info:
            if game_info['release_date']['coming_soon']:
                game_info_new = {'Name' : game['name'], 'Release date' : game_info['release_date']['date'], 'Required age': game_info['required_age'], 'Price' : game_info['price_overview']['final_formatted'], 'Developer' : game_info['developers'][0], 'Description' : descript, 'Amount of reviews': None, 'P.S': 'Infomations about the game is available'}
            else:
                game_info_new = {'Name' : game['name'], 'Release date' : game_info['release_date']['date'], 'Required age': game_info['required_age'], 'Price' : game_info['price_overview']['final_formatted'], 'Developer' : game_info['developers'][0], 'Description' : descript, 'Amount of reviews': game_info['recommendations']['total'],'P.S': 'Infomation about the game is available'}
                df_game = pd.DataFrame(game_info_new, index=["1"])
        else: 
            if game_info['release_date']['coming_soon']:
                game_info_new = {'Name' : game['name'], 'Release date' : game_info['release_date']['date'], 'Required age': game_info['required_age'], 'Price' : 'Free', 'Developer' : game_info['developers'][0], 'Description' : descript, 'Amount of reviews': None, 'P.S': 'Infomations about the game is available'}
            else:
                game_info_new = {'Name' : game['name'], 'Release date' : game_info['release_date']['date'], 'Required age': game_info['required_age'], 'Price' : 'Free', 'Developer' : game_info['developers'][0], 'Description' : descript, 'Amount of reviews': game_info['recommendations']['total'],'P.S': 'Infomation about the game is available'}
                df_game = pd.DataFrame(game_info_new, index=["1"])
    else:
        # Если информация об игре недоступна, выведите сообщение об ошибке
        game_info_new = {'Name' : game['name'], 'Release date' : None, 'Price' : None, 'Developer' : None, 'Description' : None, 'Amount of reviews': None, 'P.S': 'Infomation about the game is not available'}
        df_game = pd.DataFrame(game_info_new, index=["1"])
 return (df_game)


# In[ ]:


API_key, name = st.text_input('API key для Steam: '), st.text_input('Название игры: ')
name = name.split(',')
df_games = basic_game_info(name[0], API_key)
if len(name) > 1:
    for i in range(len(name)-1):
        df_game_i = basic_game_info(name[i+1], API_key)
        df_games = pd.concat([df_games, df_game_i])
st.write(df_games)


# In[3]:


#Получение конкретного адреса книги по названию
def name_to_link_lab (name, author, number):
    product_name = str(name)
    Author = str(author)
    product_name_2 = product_name + ' ' + Author
    product_name_to_check = ignore_details(product_name)
    
    url_1 = f"https://www.labirint.ru/search/{product_name}/?stype=0"
    url_2 = f"https://www.labirint.ru/search/{product_name_2}/?stype=0"
    
    response_1 = requests.get(url_1)
    response_2 = requests.get(url_2)
    
    list_of_books = []
    
    if response_2.status_code == 200:
        books = BeautifulSoup(response_2.text, "html.parser")
        products = books.find_all("div", class_="product")
        for product in products:
            if len(list_of_books) < number:
                title = product['data-name']
                if ignore_details(title) == product_name_to_check:
                    classes = product.find('a', class_="product-title-link" )
                    link = 'https://www.labirint.ru' + classes['href']
                    list_of_books.append([title, link])
    else: 
        list_of_books.append('Такой книжки не найдено,')
        list_of_books.append('попробуйте другое название')
    
    if response_1.status_code == 200:
        books = BeautifulSoup(response_1.text, "html.parser")
        products = books.find_all("div", class_="product")
        for product in products:
            if len(list_of_books) < number:
                title = product['data-name']
                if  product_name_to_check in ignore_details(title):
                    classes = product.find('a', class_="product-title-link")
                    link = 'https://www.labirint.ru' + classes['href']
                    list_of_books.append([title, link])
    else: 
        list_of_books.append('Такой книжки не найдено,')
        list_of_books.append('попробуйте другое название')
    if len(list_of_books) ==0:
        list_of_books.append('Такой книжки не найдено,')
        list_of_books.append('попробуйте другое название')
    
    list_of_books_upd = []
    for i in list_of_books:
        if i not in list_of_books_upd:
            list_of_books_upd.append(i)
    if len(list_of_books_upd) > 2 :
        if 'Такой книжки не найдено,' in list_of_books_upd:
            list_of_books_upd.remove('Такой книжки не найдено,')
        if 'попробуйте другое название' in list_of_books_upd:
            list_of_books_upd.remove('попробуйте другое название')
             
    return (list_of_books_upd)


# In[4]:


def link_to_info_lab (name, url):
    data = {'Название': name, 'Наличие':'','Цена без скидки':'', 'Цена со скидкой': '','Издатель': '','Автор': '','Рейтинг': '','Кол-во страниц': '','Ссылка': url ,'Описание':'' }
    # Делаем запрос к сайту и получаем ответ
    response = requests.get(str(url))

    # Проверяем статус ответа
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для разбора HTML-кода
        product = BeautifulSoup(response.text, "html.parser")
        availability = product.find('div', class_="prodtitle-availibility rang-available")
        if availability == None:
            availability = 'Нет информации'
        else: 
            availability = availability.text
        data.update({"Наличие":availability})
        if availability == 'На складе':
            price = product.find(id="product-info")
            dis_price = price['data-discount-price']
            price = price['data-price']
            data.update({"Цена без скидки": price})
            data.update({"Цена со скидкой": dis_price})
        else: data.update({"Цена без скидки": 'Товар отсутствует'})
        publisher = product.find("a", attrs={"data-event-label": "publisher"}).text #издатель
        data.update({"Издатель": publisher})
        author = product.find("div", class_="authors")
        if author == None:
            author = 'Нет информации'
        else: 
            author = author.text  
            delete = r"\Авт.*?\:"
            author = re.sub(delete, "", author)
        data.update({"Автор": author})
        rating = product.find("div", id="rate").text.strip() # оценка книги
        data.update({"Рейтинг": rating})
        pages = product.find('div', class_='pages2')
        if pages == None:
            pages = 'Нет информации'
        else: 
            pages = pages.text
            delete = r"\—.*?\ей"
            pages = re.sub(delete, "", pages) 
            delete = r"\—.*?\я"
            pages = re.sub(delete, "", pages) 
            delete = r"\Стра.*?\ниц:"
            pages = re.sub(delete, "", pages)
        data.update({"Кол-во страниц": pages})
        description = product.find(id="product-about") 
        description = description.find('noindex')
        if description == None:
            description = 'Нет информации'
        else: 
            description = description.text# описание книги
        data.update({"Описание": description})
        data = pd.DataFrame(data, index = ['1'])
    else:
        # Выводим сообщение об ошибке, если статус ответа не 200
        data = 'Ошибка запроса'
    
    return (data)


# In[39]:


def book_search_lab (name, author, number):
    book_lab = name_to_link_lab(name, author, number) 
    if 'Такой книжки не найдено,' in book_lab:
        string_to_print = ''
        for i in book_lab:
            string_to_print = string_to_print + i + ' '
        return (string_to_print)
    else:
        df = link_to_info_lab(book_lab[0][0], book_lab[0][1])
        if len(book_lab) > 1:
            for j in range(len(book_lab)-1):
                df_j = link_to_info_lab(book_lab[j+1][0], book_lab[j+1][1])
                df = pd.concat([df, df_j])
            df.reset_index(drop=True, inplace= True)
    return (df)


# In[40]:


def name_to_link_chg (name, author, number):
    product_name = name
    Author =  author
    product_name_2 = product_name + ' ' + Author
    product_name_to_check = ignore_details(product_name)
    
    url_1 = f"https://www.chitai-gorod.ru/search?phrase={product_name}"
    url_2 = f"https://www.chitai-gorod.ru/search?phrase={product_name_2}"

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get(url_2)

    list_of_books = []

    href = driver.find_elements(By.CLASS_NAME, "product-card__picture.product-card__row")
    books = driver.find_elements(By.CLASS_NAME, "product-title__head")
    book_href = href[0].get_attribute('href')

    if len (books) > 0:
        for i in range (len(books)):
            if len(list_of_books) < number:
                if ignore_details(product_name) == ignore_details(books[i].text):
                    book_href = href[i].get_attribute('href')
                    list_of_books.append([books[i].text, book_href])
    else: 
        list_of_books.append('Такой книжки не найдено,')
        list_of_books.append('попробуйте другое название')
    


    driver.get(url_1)

    href = driver.find_elements(By.CLASS_NAME, "product-card__picture.product-card__row")
    books = driver.find_elements(By.CLASS_NAME, "product-title__head")

 
    if len(books) > 0:
        for i in range (len(books)):
            if len(list_of_books) < number:
                if ignore_details(product_name) in ignore_details(books[i].text):
                    book_href = href[i].get_attribute('href')
                    list_of_books.append([books[i].text, book_href])

    else: 
        list_of_books.append('Такой книжки не найдено,')
        list_of_books.append('попробуйте другое название')

    if len(list_of_books) == 0:
        list_of_books.append('Такой книжки не найдено,')
        list_of_books.append('попробуйте другое название')
    
    list_of_books_upd = []
    for i in list_of_books:
        if i not in list_of_books_upd:
            list_of_books_upd.append(i)
    if len(list_of_books_upd) > 2 :
        if 'Такой книжки не найдено,' in list_of_books_upd:
            list_of_books_upd.remove('Такой книжки не найдено,')
        if 'попробуйте другое название' in list_of_books_upd:
            list_of_books_upd.remove('попробуйте другое название')

    

    return (list_of_books_upd)



# In[41]:


def link_to_info_chg (name, url):
    data = {'Название': name, 'Наличие':'','Цена без скидки':'21313', 'Цена со скидкой': '','Издатель': '','Автор': '','Рейтинг': '','Кол-во страниц': '','Ссылка': url,'Описание':'' }
    
    response = requests.get(str(url))
    
    if response.status_code == 200 and (url !='попробуйте другое название'):
        product = BeautifulSoup(response.text, "html.parser")
        availability = product.find('link', {'itemprop':"availability"})
        availability = availability['href']
        if availability == 'InStock':
            availability = 'В наличие'
        else: 
            availability = "Нет в наличие"
        data.update({"Наличие":availability})
        if availability == 'В наличие':
            if product.find('span', class_="product-detail-offer-header__old-price"):
                price = product.find('span', class_="product-detail-offer-header__old-price").text.strip()
                price = price.strip(' ₽')
                data.update({"Цена без скидки": price})
                dis_price = product.find('span', {'itemprop': 'price'}).text.strip()
                dis_price = dis_price.strip(' ₽')
                data.update({"Цена со скидкой": dis_price})
            else:
                price = product.find('span', {'itemprop': 'price'}).text.strip()
                price = price.strip(' ₽')
                data.update({"Цена без скидки": price})
                data.update({"Цена со скидкой": 'Скидки нет'})
        else: 
            data.update({"Цена без скидки": 'Товар отсутствует'})
            data.update({"Цена со скидкой": 'Товар отсутствует'})
        publisher = product.find("a", {"itemprop": "publisher"}).text.strip() #издатель
        data.update({"Издатель": publisher})
        author = product.find("a", {'itemprop':"author"})
        if author == None:
            author = 'Нет информации'
        else: 
            author = author.text.strip()
        data.update({"Автор": author})
        rating = product.find("span", {'itemprop':"ratingValue"}).text.strip() # оценка книги
        data.update({"Рейтинг":2*float( rating)})
        pages = product.find('span', {'itemprop': 'numberOfPages'}).text.strip()
        data.update({"Кол-во страниц": pages})
        description = product.find('div',{'itemprop':"description"})
        if description == None:
            description = 'Нет информации'
        else: 
            description = description.text.strip()# описание книги
        data.update({"Описание": description})
        data = pd.DataFrame(data, index = ['1'])
    else:
        data = 'Ошибка запроса'
    return (data)


# In[42]:


def book_search_chg (name, author, number):
    book_chg = name_to_link_chg(name, author, number) 
    if 'Такой книжи не найдено,' in book_chg:
        string_to_print = ''
        for i in book_chg:
            string_to_print = string_to_print + i + ' '
        return (string_to_print)
    else:
        df = link_to_info_chg(book_chg[0][0], book_chg[0][1])
        if len(book_chg) > 1:
            for j in range(len(book_chg)-1):
                df_j = link_to_info_chg(book_chg[j+1][0], book_chg[j+1][1])
                df = pd.concat([df, df_j])
            df.reset_index(drop=True, inplace= True)
    return (df)


# In[9]:


name, author, number = st.text_input('Название книги: '), st.text_input('Автор: '), st.text_input('Количество результатов: ')
if number.isnumeric():
    number = int(number)
    results_1 = book_search_lab(name, author, number)
    results_2 = book_search_chg(name, author, number)
    if (type (results_1) == str) and (type(results_2) == str):
        print (results_1)
        st.write(results_1)
    elif (type (results_1) != str) and (type(results_2) == str):
        print(results_1)
        st.write(results_1)
        print (f'Ошибка при поиске в читай-городе {results_2}')
        st.write(f'Ошибка при поиске в читай-городе {results_2}')
    elif (type (results_2) != str) and (type(results_1) == str):
        print(results_2)
        st.write(results_2)
        print (f'Ошибка при поиске в лабиринте {results_1}')
        st.write(f'Ошибка при поиске в лабиринте {results_1}')
    else:
        results = pd.concat([results_1, results_2])
        results.reset_index(drop = True, inplace = True)
        st.write(results)
else: 
    st.write('Вы ввели не число в строке кол-во результатов, введите заново')


# In[265]:


def pub_to_price_lab (pub, n):
    if type(n) == str:
        if n.isnumeric():
           n = int(n)
        else:
           return ('Вы ввели не число в кол-ве книг')
    name = str(pub)
    pub_name_to_check = ignore_details(name)
    
    url = f"https://www.labirint.ru/search/{pub_name_to_check}/?stype=2"
    
    response = requests.get(url)
    
    list_of_books = []
    
    books = BeautifulSoup(response.text, "html.parser")
    products = books.find_all("a", class_="rubric-list-item")
    for product in products:
        pub_name = product.find('span', class_='rubric-item-name').text.strip()
        if ignore_details(pub_name) == pub_name_to_check:
            pub = product['href'].strip('/').split('/')
            break
    pub = '/' + pub[0] + '/' + 'books' + '/' + pub[1] + '/' 
    pub = f'https://www.labirint.ru{pub}'
    url = f'{pub}?available=1&preorder=1'
    response = requests.get(url)
    if response.status_code == 200:
        books = BeautifulSoup(response.text, "html.parser")
        page_number = books.find_all('a', class_='pagination-number__text')
        if len(page_number) == 0:
            for i in range(n):
                list_of_books.append('0')
            labirint = pd.DataFrame(list_of_books, columns = [f'{pub_name}'])
            labirint.reset_index(drop = True, inplace = True)
            return (labirint)
        page_number = int(page_number[len(page_number)-1]['href'].split('=')[3])
        for i in range(max(page_number-1, 1)):
            if len(list_of_books) < n:
                url = f'{pub}?available=1&preorder=1&page={i+1}'
                response = requests.get(url)
                if response.status_code == 200:
                    books = BeautifulSoup(response.text, "html.parser")
                    products = books.find_all("span", class_="price-val")
                    for product in products:
                        if len(list_of_books) < n:
                            price = product.text.strip().strip(' ₽')
                            price_new =''
                            for i in price.split():
                                price_new = price_new +i
                            if price_new.isnumeric():
                                price = int(price_new)
                                list_of_books.append(price)
                else:
                    return ('Ошибка')
    if len(list_of_books) == 0:
        for i in range(n):
            list_of_books.append('0')
        labirint = pd.DataFrame(list_of_books, columns = [f'{pub_name}'])
        labirint.reset_index(drop = True, inplace = True)
        return (labirint)
    else: 
        if len(list_of_books) < n:
            for i in range (n - len(list_of_books)):
                list_of_books.append('0')
        labirint = pd.DataFrame(list_of_books, columns = [f'{pub_name}'])
        labirint.reset_index(drop = True, inplace = True)
        return (labirint)      
    


# In[266]:


def pub_to_price_chg (publisher, n):
    if type(n) == str:
        if n.isnumeric():
           n = int(n)
        else:
           return ('Вы ввели не число в кол-ве книг')
    name = str(publisher)
    pub_name_to_check = ignore_details(name)
    
    url = f"https://www.chitai-gorod.ru/search/publisher?phrase={pub_name_to_check}"
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get(url)
    list_of_books = []

    pubs_list = driver.find_elements(By.TAG_NAME, "article")
    for pub_list in pubs_list:
        pub_name = pub_list.text.split('\n')[0].strip()
        pub = ''
        if ignore_details(pub_name) == pub_name_to_check:
            pub = pub_list.find_elements(By.TAG_NAME, 'a')
            pub = pub[0].get_attribute("href")
        if pub != '':
            break
    if pub == '':
        if len(list_of_books) < n:
            for i in range (n - len(list_of_books)):
                list_of_books.append('0')
        chg = pd.DataFrame(list_of_books, columns = [f'{pub_name}'])
        chg.reset_index(drop = True, inplace = True)
        return (chg) 
    url = pub+"?available=1"
    driver.get(url)
    page = driver.find_elements(By.CLASS_NAME, 'pagination__text')
    if len(page) > 1:
        page = int(page[len(page)-1].text)
    else:
        page = 1
    for i in range(max(page-1, 1)):
        if len(list_of_books) < n:
            url = pub+"?available=1" + f'&page={i+1}'
            driver.get(url)
            books_list =  driver.find_elements(By.TAG_NAME, 'article')
            for book in books_list:
                if len(list_of_books) < n:
                    list_of_books.append(book.get_attribute('data-chg-product-price'))   
                else:
                    break
        else:
            break
    if len(list_of_books) < n:
        for i in range (n - len(list_of_books)):
            list_of_books.append('0')
    chg = pd.DataFrame(list_of_books, columns = [f'{pub_name}'])
    chg.reset_index(drop = True, inplace = True)
    return (chg)      


# In[6]:


number_of_pubs = 3
number = 500
name_1 = st.text_input('Издательство 1: ')
name_2 = st.text_input('Издательство 2: ')
name_3 = st.text_input('Издательство 3: ')
list_of_pubs = [name_1]
list_of_pubs.append(name_2)
list_of_pubs.append(name_3)
df_lab = pub_to_price_lab(list_of_pubs[0], number)
for i in range(2):
    df_i = pub_to_price_lab(list_of_pubs[i+1], number)
    if type (df_i) == str:
        st.write(df_i)
    else:
         df_lab = df_lab.join(df_i, rsuffix='_right') 
st.write(df_lab)
df_chg = pub_to_price_chg(list_of_pubs[0], number)
for i in range(len(list_of_pubs)-1):
    df_i = pub_to_price_chg(list_of_pubs[i+1], number)
    if type (df_i) == str:
        st.write(df_i)
    else:
        df_chg = df_chg.join(df_i, rsuffix='_right') 
st.write(df_chg)


# In[5]:


columns = df_chg.columns.tolist()
for i in columns:
    plt.plot(df_chg.index,df_chg[i].expanding().mean ())
    plt.plot(df_chg.index,df_lab[i].expanding().mean ())
    plt.title(i)
    plt.xlabel('Книги')
    plt.ylabel('Цена')
    plt.legend(['Читай-город','Лабиринт'])
    st.pyplot()


# In[ ]:




