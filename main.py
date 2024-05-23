import requests
from bs4 import BeautifulSoup
import csv


def clean_number(text):
    return int(text.replace('\xa0', '').replace(',', '').strip())


def scrape_streamer_details(streamer_url):
    response = requests.get(streamer_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    details = {}
    summary_table = soup.find('div', attrs={'data-name': 'overview_block__table'})
    if summary_table:
        for row in summary_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                detail_name = cells[0].text.strip()
                detail_value = cells[1].text.strip()
                details[detail_name] = detail_value

    return details


def scrape_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    streamers = soup.find_all('div', class_='streamers-list__item')
    page_data = []
    for streamer in streamers:
        name_element = streamer.find('a', class_='streamer-name')
        name = name_element.text.strip() if name_element else 'N/A'
        streamer_url = 'https://streamersbase.com' + name_element['href'] if name_element else ''
        description = streamer.find('div', class_='streamer-description')
        game = description.find_all('a')[-1].text if description else 'N/A'
        language_span = description.find('span') if description else None
        language = language_span.text if language_span else 'N/A'
        followers_views = streamer.find_all('div', class_='streamer-stats__item')
        followers = clean_number(followers_views[0].text.strip().split('Followers')[-1]) if len(followers_views) > 0 else 0
        views = clean_number(followers_views[1].text.strip().split('Views')[-1]) if len(followers_views) > 1 else 0

        details = scrape_streamer_details(streamer_url) if streamer_url else {}

        page_data.append([name, language, game, followers, views] + list(details.values()))
    return page_data


def save_data(all_data):
    with open('streamers_data.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Language', 'Game', 'Followers', 'Views', 'Last Data Update', 'Channel Language',
                         'Channel Creation Date', 'Channel Exists', 'Like Rating', 'Total User Votes',
                         'Views Per Follower'])
        writer.writerows(all_data)


all_data = []
page = 1
while True:
    print(f"Делаем страницу {page}")
    page_url = f"https://streamersbase.com/streamers-views?page={page}"
    page_data = scrape_page(page_url)
    if not page_data: 
        break
    all_data.extend(page_data)
    page += 1
    if page == 100:
        break

save_data(all_data)
print("Все тута 'streamers_data.csv'")
