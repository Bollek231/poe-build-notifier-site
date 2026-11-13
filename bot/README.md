# PoE Build Notifier v0.5.0 — source code / kod źródłowy

**Wybierz język / Choose language:** [🇵🇱 Polski](#polski) · [🇬🇧 English](#english)

## Polski

**Wersja: v0.5.0 · Kolejna aktualizacja: v0.5.1.**


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
- [Lista zmian](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [CHANGELOG.md](../CHANGELOG.md)

**Zastrzeżenie:** Bot wymaga uruchomienia na własnym komputerze/serwerze; GitHub Pages hostuje wyłącznie stronę, nie działającego bota. Zgodność z zasadami YouTube Data API wymaga odrębnej weryfikacji, w tym sposobu przechowywania danych w wiadomościach Discord.

---

## English

**Version: v0.5.0 · Next update: v0.5.1.**


Public source-code release of a non-commercial Discord bot that finds Path of Exile 1 build guides through YouTube Data API v3.

**No real Discord tokens, API keys, private .env files, or SQLite databases are included.**

### Requirements

- Python 3.11 or later, Windows or Linux
- Your own Discord bot (enable Message Content Intent)
- Your own YouTube Data API v3 key
- A Discord channel where the bot can read/send messages and post links and buttons

### Windows installation

1. Download and extract the ZIP into a directory such as `D:\PoE-Bot`.
2. Open CMD in the directory containing `main.py` (not its parent folder).
3. Run:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

4. Set **your own** `DISCORD_TOKEN`, `YOUTUBE_API_KEY`, and `DISCORD_CHANNEL_ID` in `.env`.
5. Start with `python main.py`.

**Warning:** do not commit a filled-in `.env`, SQLite databases, private service-account JSON files, or tokens.

### Features

- Scheduled YouTube searches every 2 hours; videos must be no older than 24 hours and match the current Path of Exile 1 league.
- Duplicate filtering and a 3-second gap between posted notifications.
- PoB, Maxroll, and Mobalytics buttons when applicable links are found in a video description.
- Manual scanning and searching, with short messages and automatic backoff on HTTP 429 quota exhaustion.
- Daily build digest at 8:00 PM Warsaw time without extra YouTube search requests.
- Locally cached YouTube metadata is cleared after 7 days; **Discord messages are not deleted automatically**.

### Commands

`pPrivacy`, `pAgree`, `pRevoke`, `pSettings`, `pLeague`, `pLeague 3.31`, `pScan`, `pSearch Lightning Strike`, `pLimit`, `pHealth`, `pBuilds`, and `pDigest`.

Administrative commands require the **Manage Server** permission and acceptance of the terms using `pAgree`.

### Tests

```bat
python -m unittest discover -s tests -v
```

### More information

- [Project website](https://bollek231.github.io/poe-build-notifier-site/index-en.html)
- [Installation guide](https://bollek231.github.io/poe-build-notifier-site/instalacja-en.html)
- [Features and commands](https://bollek231.github.io/poe-build-notifier-site/komendy-en.html)
- [Privacy Policy](https://bollek231.github.io/poe-build-notifier-site/privacy-en.html)
- [Terms of Use](https://bollek231.github.io/poe-build-notifier-site/terms-en.html)
- [Patch Notes](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html) · [CHANGELOG.md](../CHANGELOG.md)

**Disclaimer:** This bot must run on your own machine or server. GitHub Pages hosts the documentation only. Compliance with YouTube API Services policies requires an independent review, including the handling of data retained in Discord messages.

