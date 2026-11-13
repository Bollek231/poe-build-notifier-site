# PoE Build Notifier v0.6.1 — instrukcja instalacji / installation guide

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english) · [Strona instalacji / Setup website](https://bollek231.github.io/poe-build-notifier-site/instalacja.html) · [Lista zmian / Patch Notes](../CHANGELOG.md)

---

## Polski

Ta instrukcja prowadzi przez **pierwszą instalację na Windows** i bezpieczną aktualizację już działającego bota. Nie musisz znać Pythona. PoE Build Notifier obsługuje **Path of Exile 1** i **Path of Exile 2** oraz publikuje na Discordzie linki do nowych poradników z YouTube.

### Krok 1. Zainstaluj Pythona i pobierz pliki

Pobierz **Python 3.11 lub nowszy** ze strony [python.org/downloads](https://www.python.org/downloads/). Jeżeli instalator oferuje opcję dodania Pythona do PATH, możesz ją włączyć.

Pobierz [**PoE Build Notifier v0.6.1 (ZIP)**](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip). Rozpakuj zawartość do folderu, np. `D:\PoE-Bot`. Bezpośrednio w tym folderze powinny być widoczne m.in. `main.py`, `requirements.txt`, `.env.example`, `game_modes.py`, `localization.py` i `runtime_settings.py`. Jeżeli po rozpakowaniu widzisz dodatkowy katalog z plikami bota, wejdź do niego lub przenieś pliki do `D:\PoE-Bot`.

### Krok 2. Utwórz środowisko Pythona

W menu Start wyszukaj **Wiersz polecenia** (CMD). Wpisuj poniższe polecenia po kolei:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Polecenie `py --version` powinno wyświetlić zainstalowaną wersję Pythona. `.venv` tworzy osobne środowisko dla bota; aktywacja sprawia, że kolejne komendy `python` korzystają z właściwych bibliotek. Jeżeli system nie rozpoznaje `py`, sprawdź instalację Pythona i uruchom nowe okno CMD.

### Krok 3. Utwórz aplikację Discord

1. Otwórz [Discord Developer Portal](https://discord.com/developers/applications) i wybierz **New Application**.
2. Utwórz bota w zakładce **Bot** i włącz **Message Content Intent** w części *Privileged Gateway Intents*.
3. Skopiuj **token bota** — będzie potrzebny w pliku `.env`. Nikomu go nie wysyłaj.
4. W sekcji **OAuth2 / URL Generator** wybierz zakres `bot` i uprawnienia **View Channels**, **Send Messages**, **Embed Links** oraz **Read Message History**. Wygenerowanym linkiem zaproś bota na swój serwer.
5. W Discordzie włącz **Ustawienia użytkownika → Zaawansowane → Tryb dewelopera**. Kliknij prawym przyciskiem docelowy kanał tekstowy i wybierz **Kopiuj ID kanału**.

Do korzystania z administracyjnych komend bota **Twoje konto** powinno mieć na serwerze uprawnienie **Zarządzanie serwerem**. Nie musisz nadawać botowi uprawnień administratora.

### Krok 4. Włącz YouTube Data API v3

Otwórz [Google Cloud Console](https://console.cloud.google.com/), utwórz lub wybierz projekt, a następnie:

1. Wejdź w **Interfejsy API i usługi → Biblioteka**.
2. Wyszukaj **YouTube Data API v3** i kliknij **Włącz**.
3. W zakładce **Dane logowania** utwórz **klucz API**.
4. W ustawieniach klucza ogranicz go do **YouTube Data API v3**. Nie dodawaj go do publicznych plików GitHub.

Uwaga: codzienny limit Google i lokalny limit bota to oddzielne wartości. `pLimit` prezentuje lokalny licznik szacunkowy, a nie oficjalny stan puli Google.

### Krok 5. Skonfiguruj prywatny plik `.env`

W otwartym CMD (wewnątrz folderu bota) wpisz:

```bat
copy .env.example .env
notepad .env
```

Uzupełnij własne dane. Poniżej są **wyłącznie przykładowe nazwy pól**, nie prawdziwe tokeny:

```dotenv
DISCORD_TOKEN=TU_WSTAW_TOKEN_BOTA
DISCORD_CHANNEL_ID=TU_WSTAW_NUMERYCZNE_ID_KANALU
YOUTUBE_API_KEY=TU_WSTAW_KLUCZ_YOUTUBE
CHECK_INTERVAL_HOURS=2
SEND_DELAY_SECONDS=3
MAX_VIDEO_AGE_HOURS=24
YOUTUBE_CACHE_DAYS=7
DAILY_DIGEST_ENABLED=true
DAILY_DIGEST_TIME=20:00
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

**Ważne:** `DISCORD_CHANNEL_ID` musi być liczbą skopiowaną z Discorda. Nie dodawaj cudzysłowów ani spacji do tokenów. Zapisz plik w Notatniku. Opcjonalne parametry są opisane w `.env.example`; wiele z nich ustawisz później przez `pSettings`.

### Krok 6. Uruchom i sprawdź działanie

W CMD z aktywnym `.venv` uruchom:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

Na wybranym kanale Discorda wpisz kolejno:

```text
pPrivacy
pAgree
pHealth
pVersion
pLanguage
pSettings
```

Po zaakceptowaniu zasad `pAgree` administrator będzie mógł korzystać z komend. `pLanguage` otwiera wybór **Polski / English**, a `pSettings` pozwala zmieniać interwały i inne ustawienia bez ręcznej edycji `.env`. Aby przełączyć na buildy **PoE 2 1.0**, wpisz:

```text
pGame poe2
pScan
```

Powrót do PoE 1: `pGame poe1`. Bot akceptuje tylko świeże filmy (domyślnie z ostatnich 24 godzin). **CMD musi pozostać uruchomione**, chyba że hostujesz bota na serwerze działającym całodobowo.

### Bezpieczna aktualizacja już zainstalowanego bota

1. Zatrzymaj bota w CMD przez **Ctrl + C**.
2. Wykonaj kopię folderu bota i pliku `poe330_seen.sqlite3` (lub bazy wskazanej przez `DB_PATH`). Jeśli używasz trwałego woluminu na hostingu, zrób kopię również tam.
3. Wypakuj nowy ZIP do **osobnego folderu**. Skopiuj do dotychczasowego folderu **pliki `.py`**, `requirements.txt` i `VERSION` (w tym nowe moduły, np. `game_modes.py`, `localization.py`, `runtime_settings.py`).
4. **Nie nadpisuj** swojego `.env`, `search_config.json`, pliku SQLite ani prywatnych kopii z folderu `backups`.
5. W CMD wykonaj:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

6. Sprawdź na Discordzie `pHealth`, `pVersion`, `pGame`, `pLanguage` i `pSettings`.

### Typowe problemy

| Problem | Co sprawdzić |
|---|---|
| `py` nie działa | Czy Python jest zainstalowany i widoczny w CMD; otwórz nowe CMD |
| `ModuleNotFoundError` | Aktywuj `.venv`, ponów `python -m pip install -r requirements.txt` |
| Bot nie odpowiada | Sprawdź `DISCORD_CHANNEL_ID`, **Message Content Intent**, zgodę `pAgree` i uprawnienie Zarządzanie serwerem |
| Brak filmów | Wiek publikacji ≤ 24 h, właściwa gra/wersja w `pGame` i `pLeague`, ustawione filtry |
| YouTube zwraca 429 | Pula API mogła się wyczerpać; sprawdź `pLimit` i limity Google |
| Nie działa strefa czasowa | `python -m pip install tzdata` |
| Ustawienia znikają po wdrożeniu | Umieść SQLite na trwałym dysku, np. `DB_PATH=/data/poe330_seen.sqlite3` |

Plik `.env`, baza SQLite i prywatne kopie zapasowe **nigdy nie powinny trafić do publicznego repozytorium**. GitHub Pages służy do publikowania strony i archiwów — nie uruchamia procesu Discord bota.

---

## English

This guide covers the **first-time Windows installation** and safe upgrades. No Python programming experience is needed. PoE Build Notifier supports **Path of Exile 1** and **Path of Exile 2**.

### Step 1. Install Python and download the bot

Install **Python 3.11 or later** from [python.org/downloads](https://www.python.org/downloads/). Download the [**v0.6.1 ZIP**](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip) and extract it into a folder such as `D:\PoE-Bot`. Ensure `main.py`, `requirements.txt`, `.env.example`, `game_modes.py`, `localization.py` and `runtime_settings.py` are in that folder.

### Step 2. Set up the Python environment

Open **Windows Command Prompt (CMD)** and run these commands in order:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The `.venv` directory stores dependencies separately from other programs. If `py` is not recognized, check your Python installation and reopen CMD.

### Step 3. Create a Discord bot

1. In [Discord Developer Portal](https://discord.com/developers/applications), create an application and add a bot.
2. Under **Bot**, enable **Message Content Intent**.
3. Copy the bot token and keep it private.
4. In **OAuth2 / URL Generator**, select the `bot` scope and **View Channels**, **Send Messages**, **Embed Links** and **Read Message History** permissions. Invite the bot to your server.
5. Enable **User Settings → Advanced → Developer Mode** in Discord, right-click your destination text channel and choose **Copy Channel ID**.

**Your own Discord account** needs **Manage Server** for the bot's administrative commands. Do not give the bot Administrator permission unnecessarily.

### Step 4. Get a YouTube Data API v3 key

In [Google Cloud Console](https://console.cloud.google.com/), select or create a project. Open **APIs & Services → Library**, enable **YouTube Data API v3**, then open **Credentials** and create an API key. Restrict the key to YouTube Data API v3.

Google's official quota is separate from the bot's local estimate shown by `pLimit`.

### Step 5. Configure your private `.env`

Run in CMD:

```bat
copy .env.example .env
notepad .env
```

Replace the sample fields with your own values:

```dotenv
DISCORD_TOKEN=YOUR_BOT_TOKEN
DISCORD_CHANNEL_ID=YOUR_NUMERIC_CHANNEL_ID
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
CHECK_INTERVAL_HOURS=2
SEND_DELAY_SECONDS=3
MAX_VIDEO_AGE_HOURS=24
YOUTUBE_CACHE_DAYS=7
DAILY_DIGEST_ENABLED=true
DAILY_DIGEST_TIME=20:00
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

The channel ID must be a numeric Discord ID. Do not add quotation marks around tokens. Save the file. Other optional defaults are shown in `.env.example` and many can later be changed with `pSettings`.

### Step 6. Start and verify

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

Use these commands in your configured Discord channel:

```text
pPrivacy
pAgree
pHealth
pVersion
pLanguage
pSettings
```

Use `pLanguage` to choose Polish/English, `pSettings` to edit validated settings, and `pGame poe2` followed by `pScan` to search fresh **PoE 2 1.0** build guides. Return with `pGame poe1`. Only videos published within the last 24 hours are eligible by default.

The CMD process must keep running, unless you deploy the bot to an always-on host.

### Upgrade an existing installation safely

1. Stop the bot using **Ctrl + C**.
2. Back up the bot folder and SQLite database (`poe330_seen.sqlite3` or the path specified by `DB_PATH`).
3. Extract the new ZIP separately, then copy the current **Python modules (`.py`)**, `requirements.txt` and `VERSION` into your existing bot folder. Include all new modules, particularly `game_modes.py`, `localization.py` and `runtime_settings.py`.
4. **Do not overwrite** your personal `.env`, `search_config.json`, SQLite database or private backup files.
5. Reinstall the dependencies and start the bot:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

6. Test `pHealth`, `pVersion`, `pGame`, `pLanguage` and `pSettings`.

### Troubleshooting

| Symptom | Solution |
|---|---|
| `py` not found | Check Python installation, reopen CMD |
| `ModuleNotFoundError` | Activate `.venv` and install requirements again |
| Bot doesn't reply | Check `DISCORD_CHANNEL_ID`, **Message Content Intent**, `pAgree`, and **Manage Server** |
| No new guides | Check the 24-hour publication limit, `pGame`, `pLeague` and filters |
| YouTube HTTP 429 | Check `pLimit` and the Google quota |
| Time zone missing | `python -m pip install tzdata` |
| Settings lost after deployment | Keep SQLite on persistent storage, e.g. `DB_PATH=/data/poe330_seen.sqlite3` |

Never publish your `.env`, SQLite database, or backups. GitHub Pages serves documentation and downloads only; it does not run the Discord bot.

---

[Source code / Kod źródłowy](README.md) · [Commands / Komendy](https://bollek231.github.io/poe-build-notifier-site/komendy.html) · [Report an issue / Zgłoś problem](https://github.com/Bollek231/poe-build-notifier-site/issues)
