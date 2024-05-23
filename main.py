import requests
from bs4 import BeautifulSoup
import csv


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
    if not streamers:
        return None
    page_data = []
    for streamer in streamers:
        name_element = streamer.find('a', class_='streamer-name')
        name = name_element.text.strip() if name_element else 'N/A'
        streamer_url = 'https://streamersbase.com' + name_element['href'] if name_element else ''
        game_element = streamer.find('a', href=True, string=True, title=True)
        game = game_element.text if game_element else 'N/A'
        details = scrape_streamer_details(streamer_url) if streamer_url else {}

        page_data.append([name, game] + list(details.values()))
    return page_data


headers = ['Name', 'Game', 'Last Data Update', 'Channel Language', 'Channel Creation Date', 'Channel Exists',
           'Like Rating', 'Total User Votes', 'Views Per Follower']
all_data = [headers]


page = 1
while True:
    print(f"Ебашим страницу {page}")
    page_url = f"https://streamersbase.com/streamers-views?page={page}"
    page_data = scrape_page(page_url)
    if page_data is None:  # Если данных нет, прекращаем обработку
        break
    all_data.extend(page_data)
    page += 1


with open('detailed_streamers_data.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(all_data)

print("Все в файлке 'detailed_streamers_data.csv'")
