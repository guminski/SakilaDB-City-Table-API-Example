# SakilaDB-City-Table-API-Example
## Zadanie pochodzi z zajęć [Python Level UP](https://github.com/daftcode/python_levelup_2018/tree/master/05_sqlalchemy)


### Polecenie:
1. Stwórz endpoint, który zwróci w JSON listę wszystkich nazw miast zawartych w tabeli city. Kolejność nazw miast powinna być alfabetyczna. Zapytanie na:
`GET /cities`
Zwróci:
`["A Corua (La Corua)", "Alessandria", ...]`

2. Dodaj do endpointu wyświetlającego listę nazw miast obsługę parametru country_name. Parametr ma powodować wybranie miast tylko z podanego kraju. Kolejność nazw miast powinna być alfabetyczna tak jak w pkt. 1.
`GET /cities?country_name=Poland`

Zwróci:
```
[
    "Bydgoszcz",
    "Czestochowa",
    "Jastrzebie-Zdrj",
    "Kalisz",
    "Lublin",
    "Plock",
    "Tychy",
    "Wroclaw"
]
```

3. Przygotuj endpoint do dodawania nowych miast. W JSONie przesyłanym POSTem powinna znajdować się informacja o nazwie miasta oraz id kraju do którego należy dodawane miasto. Po dodaniu miasta należy zwrócić stworzony obiekt z kodem 200. Endpoint powinien zawierać prostą walidację (tzn. odrzucać próbę stworzenia miasta dla nieistniejącego kraju itp.). W przypadku błędu należy zwrócić kod 400 oraz JSONa z kluczem "error", który będzie zawierał krótki opis błędu (treść błędu nie będzie sprawdzana).

```
POST /cities
{
    "country_id": 76,
    "city_name": "Warszawa"
}
```

Przykładowa odpowiedź:
```
{
    "country_id": 76,
    "city_name": "Warszawa",
    "city_id": 601
}
```

Przykładowa odpowiedź z błędem:
```
{
    "error": "Invalid country_id"
}
```
4. Dodaj do endpointu `GET /cities` możliwość dzielenia wyniku na strony. Endpoint powinien obsługiwać dodatkowe parametry w query stringu - `per_page`, czyli ile wyników ma się wyświetlać na jednej stronie i page, który mówi o tym, którą stronę chcemy aktualnie wyświetlić. Strony numerujemy od 1 w górę. Poprawne rozwiązanie powinno działać razem z filtrowaniem po nazwie kraju jeśli nazwa kraju będzie podana.
Wskazówka: `LIMIT`
Wskazówka: `OFFSET`

`GET /cities?per_page=10&page=2`
Zwróci:
```
[
    "Akron",
    "Alessandria",
    "Allappuzha (Alleppey)",
    "Allende",
    "Almirante Brown",
    "Alvorada",
    "Ambattur",
    "Amersfoort",
    "Amroha",
    "Angra dos Reis"
]
```
5. Rozwiązać zadanie ze ścieżką `/counter` z zajęć nr 1 wykorzystując Heroku PostgreSQL, SQLAlchemy i synchronizację na bazie.

Dokumentacja dla zapytania SELECT FOR UPDATE:

*    https://www.postgresql.org/docs/current/static/sql-select.html (sekcja: The Locking Clause)
*    http://docs.sqlalchemy.org/en/latest/orm/query.html#sqlalchemy.orm.query.Query.with_for_update

