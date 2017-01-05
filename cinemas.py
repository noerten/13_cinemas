import random

import requests
from bs4 import BeautifulSoup


AFISHA_CINEMA_SCHEDULE = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_SEARCH_URL = 'https://www.kinopoisk.ru/index.php'
MIN_NUMBER_OF_CINEMAS = 10
NUMBER_OF_FILMS_TO_SHOW = 10
KINOPOISK_TIMEOUT = 10
PROXY_LIST = "http://www.freeproxy-list.ru/api/proxy?token=demo"


def get_proxy_list():
    html = requests.get(PROXY_LIST).text
    return html.split('\n')


def fetch_afisha_page(url):
    return requests.get(url).text


def fetch_kinopoisk_film_page(film_title, proxy_list):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
               'AppleWebKit/537.36 (KHTML, like Gecko)'
               'Chrome/55.0.2883.87 Safari/537.36'}
    payload = {'first': 'yes',
               'kp_query': film_title}
    proxy = {"http": random.choice(proxy_list)}
    return requests.get(KINOPOISK_SEARCH_URL, params=payload,
                        timeout=KINOPOISK_TIMEOUT, proxies=proxy).text
    

def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    all_films = []
    for film_div in soup.find('div', id='schedule').find_all('div', class_=
                                                             'object',
                                                             recursive=False):
        film_cinema_number = len(film_div.table.find_all('tr'))
        if film_cinema_number < MIN_NUMBER_OF_CINEMAS:
            continue
        film_title = film_div.find('div', class_='m-disp-table').h3.string
        film_description = film_div.find('div', class_='m-disp-table').p.string
        film_link = film_div.find('div', class_='m-disp-table').a.get('href')
        film_cinema_number = len(film_div.table.find_all('tr'))
        film_info = [film_title, film_description, film_link,
                     film_cinema_number]
        all_films.append(film_info)
    return all_films


def parse_kinopoisk_page(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    film_rating = soup.find('span', class_='rating_ball').string
    film_number_of_votes = soup.find('span', class_='ratingCount').string
    return film_rating, film_number_of_votes


def output_film_to_console(film):
    one_film_string = ('{title}\n'
                       'rating: {rating}, number of votes: {number_of_votes}\n'
                       '{description}\n'
                       'number of cinemas: {number_of_cinemas}\n'
                       '{link}\n\n'.format(
                          title=film[2],
                          description=film[3],
                          link=film[4],
                          number_of_cinemas=film[5],
                          rating=film[0],
                          number_of_votes=film[1]
                          ))
    print(one_film_string)


if __name__ == '__main__':
    afisha_html = fetch_afisha_page(AFISHA_CINEMA_SCHEDULE)
    all_films = parse_afisha_list(afisha_html)
    proxy_list=get_proxy_list()
    for film in all_films:
        kinopoisk_film_html = fetch_kinopoisk_film_page(film[0], proxy_list)
        film_rating, film_number_of_votes = parse_kinopoisk_page(
            kinopoisk_film_html)
        film.insert(0, film_rating)
        film.insert(1, film_number_of_votes)
    for film in sorted(all_films, reverse=True)[0:NUMBER_OF_FILMS_TO_SHOW]:
        output_film_to_console(film)
