import requests
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

key = os.getenv("API _KEY")

def get_books(title):
    response = requests.get(
        "https://www.googleapis.com/books/v1/volumes",
        params={"q": title, "key": key}
    )
    return response.json()
