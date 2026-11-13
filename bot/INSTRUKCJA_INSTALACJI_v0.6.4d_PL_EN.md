# PoE Build Notifier v0.6.4d — instalacja / installation

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

**Tłumaczenie tytułów na angielski (opcjonalne):** wybierz jeden z dwóch silników. Domyślnie tłumaczenie jest wyłączone i bot wyświetla oryginalny tytuł.

**MyMemory — darmowe, bez rozliczeń i bez klucza:**

```text
pTranslateTitles mymemory
pTranslateTitles status
```

Dla MyMemory **nie musisz** dodawać żadnego klucza ani karty. Usługa ogranicza anonimowe żądania do 5 000 znaków na dobę. Możesz opcjonalnie podać kontaktowy adres e-mail w swoim **prywatnym** `.env` (limit dostawcy 50 000 znaków na dobę):

```dotenv
TRANSLATION_PROVIDER=mymemory
MYMEMORY_CONTACT_EMAIL=twoj-adres@example.com
TRANSLATION_DAILY_LIMIT=30
```

Bot pilnuje własnego, niższego limitu bezpieczeństwa oraz nie wysyła treści opisów filmów. MyMemory wymaga znajomości języka źródłowego: biblioteka `langdetect` spróbuje wykryć go lokalnie; jeśli język jest nierozpoznany, bot pokaże oryginał.

**Google Cloud Translation Basic v2 — własny klucz API:**

Jeśli wolisz Google, włącz usługę Cloud Translation i rozliczenia w Google Cloud Console, utwórz klucz API oraz dopisz do prywatnego `.env`:

```dotenv
TRANSLATION_API_KEY=TWÓJ_KLUCZ_GOOGLE_TRANSLATION
TRANSLATION_PROVIDER=google
TRANSLATION_DAILY_LIMIT=30
```

Po uruchomieniu użyj `pTranslateTitles google`. Dostawcę możesz też wybrać w `pSettings` (pole **Silnik tłumaczeń**, wpisz `mymemory` albo `google`), a aktywować lub wyłączyć tłumaczenie przez `pTranslateTitles on/off`. Pamięć podręczna obu dostawców jest rozdzielona; oryginalny tytuł pozostaje dostępny.

### 5. Uruchom i skonfiguruj bota

**Wygodniejszy sposób (Windows):** najpierw uruchom `Start_PoE_Bot.bat`, który utworzy środowisko i zainstaluje zależności. Następne uruchomienia wykonuj dwuklikiem na `Start_PoE_Bot.vbs`. Launcher automatycznie sprawdzi najnowszą wersję na GitHubie, pobierze aktualizację i uruchomi bota. Możesz go zatrzymać oraz czytać logi. Aktualizator nie nadpisuje prywatnej konfiguracji ani danych SQLite.



```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

Na swoim kanale Discorda kolejno wpisz `pPrivacy`, `pAgree`, `pHealth`, `pSetup`. Ustawienia można później zmienić przez `pSettings`. Nowe komendy: `pHelp`, `pQuietHours 23:00 08:00`, `pPause 6h`, `pResume`, `pSaved`, `pTrending`, `pTranslateTitles on/off`.

`pSaved` wysyła prywatną listę zakładek w DM; możesz usunąć je przez `pSaved clear`. `pTrending` wymaga dwóch pomiarów statystyk, więc pierwsze wywołanie ustala punkt odniesienia. Godziny ciszy są liczone według Warszawy.

### 6. Aktualizacja istniejącej instalacji

1. Zatrzymaj bota (`Ctrl + C`). Zrób kopię folderu i pliku SQLite `poe330_seen.sqlite3`.
2. Rozpakuj nowe ZIP do **oddzielnego** folderu. Skopiuj nowe pliki Pythona, w tym **`community.py` i `translation_providers.py`**, `requirements.txt` oraz `VERSION` do dotychczasowego folderu.
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
- **Tłumaczenie nie działa:** sprawdź `pTranslateTitles status`. MyMemory wymaga rozpoznania języka, a Google poprawnego klucza i aktywnej usługi.
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

**Optional English title translation:** select one provider. Translation is off by default, so the original title is published until you enable it.

**MyMemory — free, no API key or billing:**

```text
pTranslateTitles mymemory
pTranslateTitles status
```

Anonymous use is limited to 5,000 characters per day by MyMemory. An optional contact email can raise its allowance to 50,000 characters/day. Only add this in your **private** `.env`, never to GitHub:

```dotenv
TRANSLATION_PROVIDER=mymemory
MYMEMORY_CONTACT_EMAIL=your-address@example.com
TRANSLATION_DAILY_LIMIT=30
```

The bot enforces its own conservative limits. MyMemory requires a source language; `langdetect` attempts to identify it locally. If detection fails, the original title is sent.

**Google Cloud Translation Basic v2 — your own key:**

Enable Google Cloud Translation and billing, create an API key, then set:

```dotenv
TRANSLATION_API_KEY=YOUR_TRANSLATION_KEY
TRANSLATION_PROVIDER=google
TRANSLATION_DAILY_LIMIT=30
```

Use `pTranslateTitles google` after restarting. Select `mymemory` or `google` using `pSettings` (Translation provider), or use `pTranslateTitles on/off` to toggle translations. Provider caches are kept separately; the original title is always available.

### 4. Start and use the bot

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

On Discord use `pPrivacy`, `pAgree`, `pHealth`, then `pSetup`. Other commands include `pHelp`, `pQuietHours 23:00 08:00`, `pPause 6h`, `pResume`, `pSaved`, `pTrending`, and `pTranslateTitles on/off`. Saved bookmarks are sent by DM. A first `pTrending` run only records the baseline.

### 5. Upgrade safely

Stop the bot with **Ctrl + C** and back up the installation directory and SQLite database. Extract the new ZIP separately. Copy all new Python modules (including **`community.py` and `translation_providers.py`**), `requirements.txt` and `VERSION` into the existing folder. **Do not replace** your personal `.env`, custom `search_config.json`, SQLite database or backups. Activate `.venv`, rerun `python -m pip install -r requirements.txt` and start `python main.py`.

If the bot doesn't respond, check Message Content Intent and the configured channel. If Python modules are missing, reactivate `.venv` and reinstall requirements. If translations are unavailable, check `pTranslateTitles status`, MyMemory language detection or the Google Cloud API key and billing.


## One-click launcher / Uruchamianie jednym kliknięciem (v0.6.4b)

On Windows run `Start_PoE_Bot.bat` once to initialize dependencies, then double-click `Start_PoE_Bot.vbs` for a window without a command prompt. The launcher checks for updates on GitHub before starting the bot, provides start/stop controls and displays logs. User configuration and SQLite data remain unchanged during updates.


## Strategie farmienia / Currency farming (v0.6.4b)

**PL:** Po aktualizacji wpisz na Discordzie `pFarmTopics`, aby zobaczyć wszystkie obsługiwane kategorie. `pFarmSearch essence` uruchamia jedno wyszukiwanie filmów dla aktualnej wersji gry, a `pFarmScan` przeszukuje kilka kategorii (maksymalnie trzy zapytania). `pFarmRecent` pokazuje ostatnie wyniki. `pFarmAuto on` włącza automatyczny monitoring; `pFarmAuto off` wyłącza go. Funkcja jest domyślnie wyłączona i korzysta z tego samego budżetu YouTube API co buildy. Jeśli chcesz osobny kanał Discord dla poradników o farmieniu, dopisz `FARM_CHANNEL_ID=NUMERYCZNE_ID_KANAŁU` do prywatnego `.env` i zrestartuj bota. Nie nadpisuj swojego `.env` przy aktualizacji.

**EN:** Use `pFarmTopics` to see available categories. `pFarmSearch essence` makes one query for the currently selected game/patch, and `pFarmScan` searches up to three categories. `pFarmRecent` lists recent results. Enable automatic discovery using `pFarmAuto on`, or disable it with `pFarmAuto off`. Auto mode is disabled by default and shares the existing YouTube budget. To send strategies to a separate Discord channel, set `FARM_CHANNEL_ID=NUMERIC_CHANNEL_ID` in your private `.env` and restart. Keep your existing `.env` during upgrades.


## Ręczne wyszukiwanie z limitem / Limited manual scans (v0.6.4b)

**PL:** `pScan` wyszukuje buildy jak dotychczas, a `pFarmScan` strategie farmienia. Możesz ograniczyć liczbę opublikowanych nowych filmów przez `pScan 1`, `pScan 2`, `pFarmScan 1` albo `pFarmScan 2`. Dozwolone są liczby całkowite **1–25**. Limit obejmuje także nowe filmy zebrane do podsumowania w godzinach ciszy. Liczba nie ogranicza liczby zapytań YouTube API, a liczba faktycznie znalezionych filmów może być mniejsza.

**EN:** `pScan` keeps its full build search and `pFarmScan` the full farming search. Use `pScan 1`, `pScan 2`, `pFarmScan 1` or `pFarmScan 2` to cap new matching videos (integer **1–25**). The cap also applies during quiet hours. It does not limit the number of YouTube API queries, and fewer results may be posted when insufficient fresh guides qualify.


## PoE Planner w strategiach farmienia / PoE Planner in farming posts (v0.6.4c)

**PL:** Kiedy poradnik o farmieniu znaleziony przez `pFarmScan` lub `pFarmSearch` zawiera w opisie bezpieczny link do `https://poeplanner.com` albo `https://www.poeplanner.com`, bot dołącza przycisk **PoE Planner** do wiadomości Discord. Link jest sprawdzany tak jak odnośniki PoB, Maxroll i Mobalytics. Przy późniejszym uzupełnieniu opisu filmu `pRefreshLinks` również może dołączyć przycisk do opublikowanej już wiadomości.

**EN:** If a guide discovered by `pFarmScan` or `pFarmSearch` includes a safe `https://poeplanner.com` or `https://www.poeplanner.com` URL in its YouTube description, the Discord notification displays a **PoE Planner** button. The link is validated like PoB, Maxroll and Mobalytics links. `pRefreshLinks` can also add it later when the creator updates the video description.

## Wygląd powiadomień / Notification appearance (v0.6.4d)

**PL:** Od wersji v0.6.4d nowe powiadomienia buildów mają fioletową kolorystykę, a strategie farmienia złotą. W Discordzie wpisz `pEmbedStyle expanded` (pełny układ, ustawienie domyślne), `pEmbedStyle compact` (krótszy układ) lub `pEmbedStyle status` (odczyt). Bot zapamiętuje wybór w Twojej obecnej bazie SQLite. Nowe wiadomości mają klikalny tytuł i przycisk **YouTube**, zamiast surowego linku nad embedem. Dostępne odnośniki do PoB, Maxroll, Mobalytics i PoE Planner są nadal dodawane jako osobne przyciski. Nowy styl nie przerabia ani nie usuwa wcześniej wysłanych wiadomości Discorda. Kolor obramowania pochodzi z wbudowanego `discord.Embed`; Discord nie obsługuje CSS ani ozdobnych ramek z koncepcji graficznej.

**EN:** From v0.6.4d onward, new build messages use purple and currency-farming notifications use gold. Run `pEmbedStyle expanded` (detailed default), `pEmbedStyle compact` (shorter) or `pEmbedStyle status`. The preference is stored in the existing SQLite database. Notifications have a clickable title and a **YouTube** button instead of the duplicate raw URL. Available PoB, Maxroll, Mobalytics and PoE Planner links remain as buttons. Existing Discord messages are not edited or removed. The accent comes from native Discord embeds; Discord does not support custom CSS or the mockup's decorative image borders.
