# PoE Build Notifier v0.6.2 — instalacja / installation

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english)

## Polski

### 1. Pobierz i przygotuj Pythona

Zainstaluj **Python 3.11 lub nowszy** z [python.org](https://www.python.org/downloads/) i rozpakuj aktualny ZIP do np. `D:\PoE-Bot`. Upewnij się, że w folderze znajdują się `main.py`, `community.py`, `requirements.txt` oraz `.env.example`.

Otwórz **CMD** (Wiersz polecenia) i wpisz kolejno:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### 2. Utwórz bota Discord

W [Discord Developer Portal](https://discord.com/developers/applications) utwórz aplikację i bota. W zakładce **Bot** włącz **Message Content Intent**, następnie zaproś go na serwer z uprawnieniami do czytania, pisania i osadzania linków. Zapisz prywatnie **DISCORD_TOKEN**. Włącz w Discordzie Tryb dewelopera i skopiuj identyfikator docelowego kanału.

### 3. Przygotuj YouTube API

W [Google Cloud Console](https://console.cloud.google.com/) utwórz projekt, włącz **YouTube Data API v3** w Bibliotece interfejsów API, a w Dane logowania utwórz klucz API. Dla bezpieczeństwa ogranicz klucz do YouTube Data API v3.

### 4. Skonfiguruj `.env`

W CMD w folderze bota wykonaj:

```bat
copy .env.example .env
notepad .env
```

Wprowadź własne dane:

```dotenv
DISCORD_TOKEN=TWÓJ_TOKEN_BOTA
DISCORD_CHANNEL_ID=NUMERYCZNE_ID_KANAŁU
YOUTUBE_API_KEY=TWÓJ_KLUCZ_YOUTUBE
CHECK_INTERVAL_HOURS=2
MAX_VIDEO_AGE_HOURS=24
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

**Tłumaczenie tytułów (opcjonalne):** jeśli chcesz użyć `pTranslateTitles on`, włącz płatną usługę **Google Cloud Translation Basic v2** w swoim projekcie Google Cloud, skonfiguruj osobny klucz i dopisz do prywatnego `.env`:

```dotenv
TRANSLATION_API_KEY=TWÓJ_KLUCZ_GOOGLE_TRANSLATION
TRANSLATION_DAILY_LIMIT=30
```

Bez tego klucza bot będzie działał normalnie, tylko nie będzie tłumaczył tytułów. Tłumaczenie jest domyślnie wyłączone. Nie udostępniaj nikomu `.env` ani tokenów.

### 5. Uruchom i skonfiguruj bota

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

Na swoim kanale Discorda kolejno wpisz `pPrivacy`, `pAgree`, `pHealth`, `pSetup`. Ustawienia można później zmienić przez `pSettings`. Nowe komendy: `pHelp`, `pQuietHours 23:00 08:00`, `pPause 6h`, `pResume`, `pSaved`, `pTrending`, `pTranslateTitles on/off`.

`pSaved` wysyła prywatną listę zakładek w DM; możesz usunąć je przez `pSaved clear`. `pTrending` wymaga dwóch pomiarów statystyk, więc pierwsze wywołanie ustala punkt odniesienia. Godziny ciszy są liczone według Warszawy.

### 6. Aktualizacja istniejącej instalacji

1. Zatrzymaj bota (`Ctrl + C`). Zrób kopię folderu i pliku SQLite `poe330_seen.sqlite3`.
2. Rozpakuj nowe ZIP do **oddzielnego** folderu. Skopiuj nowe pliki Pythona, w tym **`community.py`**, `requirements.txt` oraz `VERSION` do dotychczasowego folderu.
3. **Nie nadpisuj** własnego `.env`, `search_config.json`, bazy SQLite ani prywatnych kopii zapasowych.
4. W CMD wykonaj:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

5. Na Discordzie sprawdź `pVersion`, `pHealth`, `pSetup` i `pHelp`.

### Typowe problemy

- **Bot nie reaguje:** sprawdź Message Content Intent, ID kanału i uprawnienia Zarządzanie serwerem.
- **Brak modułu Pythona:** aktywuj `.venv` i ponownie zainstaluj `requirements.txt`.
- **Brak wyników:** bot filtruje według gry, wersji i daty publikacji do 24 godzin.
- **Tłumaczenie nie działa:** sprawdź aktywną usługę Cloud Translation v2, poprawny klucz, rozliczenia i `pTranslateTitles status`.
- **Brak prywatnej biblioteki:** włącz wiadomości prywatne od członków serwera Discorda.

---

## English

### 1. Install Python and extract the bot

Install **Python 3.11+** from [python.org](https://www.python.org/downloads/), and extract the ZIP into `D:\PoE-Bot` so that `main.py`, `community.py`, `requirements.txt` and `.env.example` are in that folder. In Windows CMD run:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### 2. Create a Discord bot and YouTube key

Create an application in [Discord Developer Portal](https://discord.com/developers/applications), enable **Message Content Intent**, invite the bot with read/send/embed permissions and copy its private token. Enable Developer Mode to copy your Discord channel ID.

In [Google Cloud Console](https://console.cloud.google.com/), enable **YouTube Data API v3** for your project and create an API key, restricting it to this service.

### 3. Configure `.env`

```bat
copy .env.example .env
notepad .env
```

Enter your own credentials:

```dotenv
DISCORD_TOKEN=YOUR_BOT_TOKEN
DISCORD_CHANNEL_ID=YOUR_NUMERIC_CHANNEL_ID
YOUTUBE_API_KEY=YOUR_YOUTUBE_KEY
CHECK_INTERVAL_HOURS=2
MAX_VIDEO_AGE_HOURS=24
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

**Optional English translations:** enable **Google Cloud Translation Basic v2** (with billing), create a separate API key and add:

```dotenv
TRANSLATION_API_KEY=YOUR_TRANSLATION_KEY
TRANSLATION_DAILY_LIMIT=30
```

Translation is disabled by default and requires `pTranslateTitles on`. The bot works normally without a translation key; the original title is published if translation is unavailable.

### 4. Start and use the bot

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

On Discord use `pPrivacy`, `pAgree`, `pHealth`, then `pSetup`. Other commands include `pHelp`, `pQuietHours 23:00 08:00`, `pPause 6h`, `pResume`, `pSaved`, `pTrending`, and `pTranslateTitles on/off`. Saved bookmarks are sent by DM. A first `pTrending` run only records the baseline.

### 5. Upgrade safely

Stop the bot with **Ctrl + C** and back up the installation directory and SQLite database. Extract the new ZIP separately. Copy all new Python modules (including **`community.py`**), `requirements.txt` and `VERSION` into the existing folder. **Do not replace** your personal `.env`, custom `search_config.json`, SQLite database or backups. Activate `.venv`, rerun `python -m pip install -r requirements.txt` and start `python main.py`.

If the bot doesn't respond, check Message Content Intent and the configured channel. If Python modules are missing, reactivate `.venv` and reinstall requirements. If English translations are unavailable, check Cloud Translation v2, its API key, billing and `pTranslateTitles status`.
