# PoE Build Notifier — kod źródłowy

Publiczna wersja niekomercyjnego bota Discord wyszukującego poradniki Path of Exile 1 przez YouTube Data API v3.

**Ta wersja nie zawiera prawdziwych tokenów, kluczy API, prywatnych plików .env ani bazy SQLite.**

## Wymagania
- Python 3.11 lub nowszy, Windows / Linux
- Własna aplikacja/bot Discord (z włączonym Message Content Intent)
- Własny klucz YouTube Data API v3
- Dostęp do kanału Discord, na którym bot może czytać i wysyłać wiadomości oraz umieszczać linki i przyciski

## Instalacja Windows
1. Pobierz archiwum i rozpakuj do folderu np. `D:\PoE-Bot`.
2. Otwórz CMD w folderze, w którym jest `main.py` (nie w folderze nadrzędnym).
3. Wykonaj:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

4. W `.env` wpisz WŁASNE wartości `DISCORD_TOKEN`, `YOUTUBE_API_KEY` i `DISCORD_CHANNEL_ID`.
5. Uruchom `python main.py`.

**Uwaga:** Nie publikuj uzupełnionego `.env`, bazy `.sqlite3`, plików JSON zawierających prywatne klucze ani tokenów.

## Działanie
- Przeszukiwanie YouTube co 2 godziny, filmy nie starsze niż 24h, filtr ligi Path of Exile 1.
- Blokowanie duplikatów; 3 sekundy odstępu między powiadomieniami.
- Przyciski PoB, Maxroll i Mobalytics, gdy odpowiednie adresy są w opisie filmu.
- Ręczne skanowanie i wyszukiwanie; krótkie ostrzeżenia przy wyczerpanym limicie wyszukiwań (429).
- Dzienne podsumowanie buildów o 20:00 czasu polskiego, bez dodatkowych zapytań YouTube.
- Czyszczenie lokalnych metadanych YouTube po 7 dniach; **wiadomości Discord nie są automatycznie usuwane**.

## Komendy
`pPrivacy`, `pAgree`, `pRevoke`, `pSettings`, `pLeague`, `pLeague 3.31`, `pScan`, `pSearch Lightning Strike`, `pLimit`, `pHealth`, `pBuilds`, `pDigest`.

Komendy administracyjne wymagają uprawnienia **Zarządzanie serwerem** i akceptacji zasad przez `pAgree`.

## Testy
```bat
python -m unittest discover -s tests -v
```

## Dodatkowe informacje
- [Strona projektu](https://bollek231.github.io/poe-build-notifier-site/index.html)
- [Instrukcja instalacji](https://bollek231.github.io/poe-build-notifier-site/instalacja.html)
- [Komendy i działanie](https://bollek231.github.io/poe-build-notifier-site/komendy.html)
- [Polityka prywatności](https://bollek231.github.io/poe-build-notifier-site/privacy.html)
- [Warunki korzystania](https://bollek231.github.io/poe-build-notifier-site/terms.html)

**Zastrzeżenie:** Bot wymaga uruchomienia na własnym komputerze/serwerze; GitHub Pages hostuje wyłącznie stronę, nie działającego bota. Zgodność z zasadami YouTube Data API wymaga odrębnej weryfikacji, w tym sposobu przechowywania danych w wiadomościach Discord.
