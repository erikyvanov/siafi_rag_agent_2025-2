import requests
import os
import json
from bs4 import BeautifulSoup

from src.entities.pokemon_place import PokemonPlace


def get_image_src(place_soup: BeautifulSoup) -> str:
    figure_tag = place_soup.find('figure', class_='pi-item pi-image')
    if not figure_tag:
        return ''

    image_tag = figure_tag.find('img')

    image_src = image_tag.get('src')
    image_src = image_src.split('/revision/')[0]

    return image_src


def get_region(place_soup: BeautifulSoup) -> str:
    location_section = place_soup.find(
        'section', class_='pi-item pi-group pi-border-color')
    if not location_section:
        return 'Unknown'

    location_div = location_section.find(
        'div', class_='pi-item pi-data pi-item-spacing pi-border-color')
    if not location_div:
        return 'Unknown'

    location_name_div = location_div.find(
        'div', class_='pi-data-value pi-font')
    if not location_name_div:
        return 'Unknown'

    region_a_tag = location_name_div.find('a')
    if not region_a_tag:
        return 'Unknown'

    region = region_a_tag.get('title').lower().replace(
        ' ', '').replace('\n', '')

    return region


def get_generation(region: str) -> int:
    if region == 'kanto':
        return 1
    elif region == 'johto':
        return 2
    elif region == 'hoenn':
        return 3
    elif region == 'sinnoh':
        return 4
    elif region == 'teselia':
        return 5
    elif region == 'kalos':
        return 6
    elif region == 'alola':
        return 7
    elif region == 'galar':
        return 8

    return -1


def parse_descriptions(description: str) -> str:
    return description.replace('\t', '').replace('\n', '')


def is_valid_description(description: str) -> bool:
    if len(description) < 35:
        return False

    if description and description[0].isdigit():
        return False

    invalid_phrases = [
        'Ilustración',
        'https://',
        'En el videojuego',
        'LEE MÁS',
        'Mapa del',
        'Política de privacidad',
        'Al desafiarte',
        'conseguir los siguientes',
        'Al perder',
        'Tras perder',
        '↑',
        '¡Revisa cómo colaborar!',
        'Lista de episodios',
        'TCG Cartas de Pokémon'
    ]

    for invalid_phrase in invalid_phrases:
        if invalid_phrase in description:
            return False

    return True


def get_description(place_soup: BeautifulSoup) -> str:
    ps = place_soup.find_all('p')
    lis = place_soup.find_all('li')

    descriptions = ps + lis
    descriptions = [parse_descriptions(
        description.get_text()) for description in descriptions]

    final_descriptions = []

    for description in descriptions:
        if is_valid_description(description):
            final_descriptions.append(description)

    return '\n'.join(final_descriptions)


def get_place_info(place_name: str, place_url: str) -> PokemonPlace | None:
    pokemon_place_response = requests.get(place_url)
    if pokemon_place_response.status_code != 200:
        return None

    place_soup = BeautifulSoup(pokemon_place_response.text, 'html.parser')

    image_src = get_image_src(place_soup)
    region = get_region(place_soup)
    generation = get_generation(region)
    description = get_description(place_soup)

    pokemon_place = PokemonPlace(
        name=place_name,
        description=description,
        region=region,
        generation=generation,
        image_src=image_src,
        url=place_url,
    )

    return pokemon_place


def save_to_json(place: PokemonPlace, path: str):
    pokemon_place_dict = pokemon_place.to_dict()
    output_path = f'{path}/{place.name}.json'

    with open(output_path, 'w') as file:
        json.dump(pokemon_place_dict, file, indent=4)
        print(f'{place.name} saved.')


pokemon_fandom_url = 'https://pokemon.fandom.com'
places_page_url = f'{pokemon_fandom_url}/es/wiki/Lista_de_ciudades_y_pueblos_por_región'

page_response = requests.get(places_page_url)
if page_response.status_code != 200:
    raise Exception(f'Error: {page_response.status_code}')

places_soup = BeautifulSoup(page_response.text, 'html.parser')

tables_soup = places_soup.find_all('table', class_='wiki sortable')

save_path = './database/places'
if not os.path.exists(save_path):
    os.mkdir(save_path)

for region_table in tables_soup:
    trs_places_row = region_table.find_all('tr')
    trs_places_row = [tr for tr in trs_places_row if tr.get(
        'class') != 'encabezado']

    for place_row in trs_places_row:
        if not place_row:
            continue

        place_a_tag = place_row.find('a')
        if not place_a_tag:
            continue

        place_name = place_a_tag.get('title').replace(
            '\n', '').replace(' ', '_').lower()

        place_url = place_a_tag.get('href')
        place_url = f'{pokemon_fandom_url}{place_url}'.replace('\n', '')

        pokemon_place = get_place_info(place_name, place_url)

        save_to_json(pokemon_place, save_path)
