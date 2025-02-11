import json

import pendulum
import requests

from airflow.decorators import dag, task

@dag(
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Seoul"),
    catchup=False,
    params={
        "pokemon_name": "pikachu"
    },
)
def findpokemon():
    @task
    def get_pokemon_data(**context):
        pokemon_name = context['params']['pokemon_name']
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return None

    @task
    def get_evolution_data(**context):
        pokemon_name = context['params']['pokemon_name']
        species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name}"
        try:
            species_response = requests.get(species_url)
            species_response.raise_for_status()
            species_data = species_response.json()
            
            evolution_url = species_data['evolution_chain']['url']
            evolution_response = requests.get(evolution_url)
            evolution_response.raise_for_status()
            return evolution_response.json()
        except requests.exceptions.RequestException as e:
            print(f"진화 정보 요청 실패: {e}")
            return None

    @task
    def print_data(data):
        if data:
            print(json.dumps(data, indent=2))
        else:
            print("포켓몬 데이터를 가져오지 못했습니다.")

    @task
    def print_evolution(evolution_data):
        if not evolution_data:
            print("진화 정보를 가져오지 못했습니다.")
            return
        
        chain = evolution_data['chain']
        evolution_line = []
        
        while chain:
            evolution_line.append(chain['species']['name'])
            chain = chain['evolves_to'][0] if chain['evolves_to'] else None
        
        print(f"진화: {' -> '.join(evolution_line)}")

    pokecard_data = get_pokemon_data()
    evolution_data = get_evolution_data()
    
    pokecard_data >> print_data(pokecard_data)
    evolution_data >> print_evolution(evolution_data)

findpokemon()