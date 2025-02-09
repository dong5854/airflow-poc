import json

import pendulum
import requests

from airflow.decorators import dag, task

@dag(
    schedule="@daily",
    start_date=pendulum.datetime(2025, 1, 1, tz="Asia/Seoul"),
    catchup=False,
)
def findpokemon():
    @task
    def get_pokemon_data(pokemon_name: str):
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 요청 실패 시 예외 발생
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API 요청 실패: {e}")
            return None  # 실패 시 None 반환

    @task
    def print_data(data):
        if data:
            print(json.dumps(data, indent=2))  # Airflow 로그에서 확인 가능
        else:
            print("포켓몬 데이터를 가져오지 못했습니다.")

    pokecard_data = get_pokemon_data("pikachu")
    pokecard_data >> print_data(pokecard_data)

findpokemon()