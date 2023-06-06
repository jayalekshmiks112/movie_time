from .models import *
from django.utils import timezone
from datetime import timedelta
from requests import post,put,get

BASE_URL = "https://api.themoviedb.org/3/"
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1NTJkMTBhNmRhNGNjNzE0YzQ4MDNhZDJhNWM3NWVlNCIsInN1YiI6IjY0NmM1NGYwYzM1MTRjMmIwOWIzYjM0MCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.9Hhbcnj-hL6-BfxazsiKRFCuW_5Rn3tMmsgD_h8-pLY"

def execute_api_call(endpoint, params):
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer "+ACCESS_TOKEN
    }

    response = get(BASE_URL+endpoint, headers=headers, params=params)
    try :
        return response.json()
    except :
        return {'Error':'Some error with the request'}