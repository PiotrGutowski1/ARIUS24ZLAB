import requests
import json

BASE_URL = "http://127.0.0.1:5000"  # Adres lokalnego serwera Flask
HEADERS = {"Authorization": "Piotr Gutowski"}


def test_teacher_list():
    print("### TEST /teacher-list ###")
    # Funkcja nie przyjmuje danych wejściowych wiec nie rozpatruję przypadku negatywnego
    response = requests.get(f"{BASE_URL}/teacher-list", headers=HEADERS)
    print("Wynik:", response.status_code, response.json())

def test_teacher_details():
    print("\n### TEST /teacher-details ###")
    # Przypadek pozytywny - poprawne id
    response = requests.get(f"{BASE_URL}/teacher-details/1", headers=HEADERS)
    print("Pozytywny wynik:", response.status_code, response.json())
    
    # Przypadek negatywny - nieistniejący student
    response = requests.get(f"{BASE_URL}/teacher-details/999", headers=HEADERS)
    print("Negatywny wynik:", response.status_code, response.json())

def test_book_lesson():
    print("\n### TEST /book-lesson ###")
    # Przypadek pozytywny
    payload = {
        "id": 1,
        "id_studenta": 1,
        "id_nauczyciela": 1,
        "data_lekcji": "2024-12-18 10:00", 
    }
    response = requests.post(f"{BASE_URL}/book-lesson", headers=HEADERS, json=payload)
    print("Pozytywny wynik:", response.status_code, response.json())

    # Przypadek negatywny - zajęty termin
    response = requests.post(f"{BASE_URL}/book-lesson", headers=HEADERS, json=payload)
    print("Negatywny wynik:", response.status_code, response.json())

def test_add_teacher():
    print("\n### TEST /add-teacher ###")
    # Przypadek pozytywny
    payload = {
        "imie": "Adam",
        "nazwisko": "Nowakowski",
        "prowadzone_przedmioty": "matematyka, fizyka",
        "opis": "Nauczyciel z wieloletnim doświadczeniem.",
        "ocena_nauczyciela": 4.9,
        "numer_telefonu": "123456788",
        "stawka": 100,
        "waluta": "PLN",
        "email": "a.nowakowski@example.com",
        "id": 3 # Pole id oznacza id kalendarza
    }
    response = requests.post(f"{BASE_URL}/add-teacher", headers=HEADERS, json=payload)
    print("Pozytywny wynik:", response.status_code, response.json())

    # Przypadek negatywny - brak wymaganych danych
    payload.pop("imie")  
    response = requests.post(f"{BASE_URL}/add-teacher", headers=HEADERS, json=payload)
    print("Negatywny wynik:", response.status_code, response.json())


def test_get_lessons():
    print("\n### TEST /get-lessons ###")

    # Przypadek pozytywny
    params = {
        "id_studenta": 1,
        "data_początkowa": "2024-12-10 08:00",
        "data_końcowa": "2024-12-18 18:00"
    }
    response = requests.get(f"{BASE_URL}/get-lessons", headers=HEADERS, params=params)
    print("Pozytywny wynik:", response.status_code, response.text)

    # Przypadek negatywny - nieistniejący student
    params["id_studenta"] = 999
    response = requests.get(f"{BASE_URL}/get-lessons", headers=HEADERS, params=params)
    print("Negatywny wynik:", response.status_code)
    if response.text:
        print("Treść błędu", response.text)
    else:
        print("Prawidłowa pusta odpowiedź.")




if __name__ == "__main__":
    # Testowanie endpointów
    test_teacher_list()
    test_teacher_details()
    test_book_lesson()
    test_add_teacher()
    test_get_lessons()
