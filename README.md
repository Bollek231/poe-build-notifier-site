# PoE Build Notifier · v0.6.4

**Discord bot for Path of Exile 1 & Path of Exile 2 · 🇵🇱 Polski / 🇬🇧 English**

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english) · [🌐 Strona / Website](https://bollek231.github.io/poe-build-notifier-site/) · [📝 Patch Notes](CHANGELOG.md)

---

## Polski

### Strategie farmienia waluty (v0.6.4)

- `pFarmScan`: jednorazowy skan najnowszych strategii farmienia waluty (maks. 3 zapytania).
- `pFarmSearch essence`: wyszukiwanie określonej kategorii, np. `harvest`, `expedition`, `atlas`, `crafting` lub `trading`. Wszystkie kategorie: `pFarmTopics`.
- `pFarmRecent`: ostatnie znalezione strategie dla aktualnie wybranej gry i wersji.
- `pFarmAuto on` / `pFarmAuto off`: opcjonalne wyszukiwanie co interwał automatycznego skanu buildów (maksymalnie jedno dodatkowe wyszukiwanie, wspólny limit YouTube). Domyślnie wyłączone.
- Domyślnie wyniki trafiają na ten sam kanał Discord. Aby użyć osobnego kanału, ustaw prywatnie `FARM_CHANNEL_ID` w `.env` i zrestartuj bota. Filtry wersji gry i wieku filmów pozostają aktywne. Strategie z godzin ciszy trafiają do osobnego podsumowania.


PoE Build Notifier automatycznie wyszukuje **świeże poradniki buildów** na YouTube i publikuje je na wybranym kanale Discord. Obsługuje **Path of Exile 1** oraz **Path of Exile 2**. To niekomercyjny, nieoficjalny projekt społecznościowy.

### Funkcje bota

- **`pSetup`:** konfiguracja gry, wersji, języka i interwału skanowania z menu Discorda. Zapis dopiero po zatwierdzeniu.
- **`pHelp`:** menu kategorii komend dostępne na kanale bota.
- **`pQuietHours 23:00 08:00`:** cisza nocna w strefie Warszawa; skanowanie trwa, a wykryte buildy trafiają do zbiorczego podsumowania po zakończeniu ciszy. `pQuietHours off` wyłącza funkcję.
- **`pPause 6h` / `pResume`:** pauza tylko dla automatycznego wyszukiwania (1–24 h lub `forever`). Ręczne `pScan` pozostaje dostępne.
- **`pSaved`:** przycisk zapisywania przy nowych buildach i prywatna lista zakładek wysyłana przez DM; `pSaved remove VIDEO_ID` i `pSaved clear` usuwają dane.
- **`pTrending`:** popularność ostatnich filmów według przyrostu wyświetleń między pomiarami. Pierwsze wywołanie ustala punkt odniesienia; ponowne odczyty mają 15-minutową pamięć podręczną.
- **`pTranslateTitles`:** opcjonalne tłumaczenie tytułów na angielski przez **MyMemory (bez klucza i rozliczeń)** albo **Google Cloud Translation**. Wybór: `pTranslateTitles mymemory`, `pTranslateTitles google` lub `pSettings`; oryginał pozostaje w wiadomości. Błędy tłumaczenia nie blokują publikacji.

**Tłumaczenia:** wpisz `pTranslateTitles mymemory`, aby włączyć bezpłatne MyMemory. Możesz opcjonalnie ustawić `MYMEMORY_CONTACT_EMAIL=...` w prywatnym `.env` dla wyższego limitu. Aby wybrać Google, dodaj `TRANSLATION_API_KEY=...` i wpisz `pTranslateTitles google`. Parametr `TRANSLATION_DAILY_LIMIT=30` ogranicza liczbę zapytań. Automatyczne wykrywanie języka jest lokalne, a w razie błędu bot zachowa oryginalny tytuł.

### Możliwości

- **PoE 1 / PoE 2:** przełączanie komendą `pGame poe1` lub `pGame poe2`; dla PoE 2 domyślny cel to **1.0**.
- **Nowe buildy:** automatyczne skanowanie (domyślnie co 2 h), filmy opublikowane maksymalnie 24 h temu, wykrywanie duplikatów.
- **Filtry i kanały:** skill, klasa, ascendancy, tryb gry oraz czarna i biała lista twórców.
- **Przyciski do poradników:** Path of Building, Maxroll i Mobalytics, jeżeli twórca zamieścił odpowiednie linki.
- **Wygodne zarządzanie:** `pLanguage` do wyboru polskiego lub angielskiego oraz interaktywne `pSettings` do zmiany ustawień.
- **Dodatki:** codzienne podsumowania, ochrona limitu YouTube API, uzupełnianie linków, prywatne kopie SQLite, alerty i `pVersion`.

### Ważne komendy

| Komenda | Działanie |
|---|---|
| `pGame poe1` / `pGame poe2` | Wybór gry |
| `pLeague 1.0` | Ustawienie wersji dla wybranej gry (np. PoE 2) |
| `pScan` | Ręczne skanowanie YouTube |
| `pSearch Spark` | Wyszukiwanie buildów dla skilla |
| `pLanguage` | Menu wyboru języka |
| `pSettings` | Menu edycji ustawień |
| `pDigest` | Podsumowanie buildów |
| `pHealth` / `pLimit` / `pVersion` | Status, budżet API i wersja bota |

### Uruchamianie jednym kliknięciem (v0.6.4)

W folderze bota uruchom `Start_PoE_Bot.bat` (pierwszy raz tworzy `.venv` i instaluje zależności). Następnie używaj `Start_PoE_Bot.vbs` — otwiera graficzny launcher bez okna CMD. Launcher automatycznie sprawdza aktualizacje przed uruchomieniem bota, pozwala go zatrzymać i pokazuje logi. Przy aktualizacji kodu nie nadpisuje `.env`, `search_config.json`, bazy SQLite ani folderu `backups`.

### Instalacja na Windows — krok po kroku

**1. Pobierz pliki.** Zainstaluj [Python 3.11 lub nowszy](https://www.python.org/downloads/) i pobierz **[PoE Build Notifier v0.6.4 (ZIP)](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.4.zip)**. Wypakuj pliki tak, aby w folderze `D:\PoE-Bot` znajdowały się m.in. `main.py` i `requirements.txt`.

**2. Przygotuj środowisko Pythona.** Otwórz **Wiersz polecenia (CMD)** i wykonaj po kolei:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

**3. Utwórz bota na Discordzie.** Otwórz [Discord Developer Portal](https://discord.com/developers/applications), utwórz aplikację i dodaj bota. W zakładce **Bot** włącz **Message Content Intent**. Zaproś bota na serwer z uprawnieniami do przeglądania kanału, wysyłania wiadomości i osadzania linków. Skopiuj token i identyfikator kanału (w Discordzie włącz *Tryb dewelopera*).

**4. Przygotuj klucz YouTube.** W [Google Cloud Console](https://console.cloud.google.com/) włącz **YouTube Data API v3** dla swojego projektu, a następnie wygeneruj klucz API. Ogranicz jego użycie do tej usługi.

**5. Skonfiguruj prywatny plik `.env`.** W tym samym oknie CMD wpisz:

```bat
copy .env.example .env
notepad .env
```

W otwartym pliku zastąp przykładowe wartości własnymi danymi:

```dotenv
DISCORD_TOKEN=TU_WSTAW_TOKEN_DISCORDA
DISCORD_CHANNEL_ID=TU_WSTAW_NUMERYCZNE_ID_KANALU
YOUTUBE_API_KEY=TU_WSTAW_KLUCZ_GOOGLE
CHECK_INTERVAL_HOURS=2
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

**6. Uruchom i sprawdź bota.**

```bat
python main.py
```

Na skonfigurowanym kanale Discorda użyj `pPrivacy`, `pAgree` i `pHealth`. Wybrany język zmienisz przez `pLanguage`, ustawienia przez `pSettings`, a grę przez `pGame poe2` / `pGame poe1`.

**Aktualizacja istniejącego bota:** zatrzymaj go (`Ctrl + C`), wykonaj kopię folderu i pliku SQLite, a następnie podmień pliki Pythona, `VERSION` i `requirements.txt` z aktualnego ZIP-a. **Nie nadpisuj** własnego `.env`, `search_config.json`, bazy `.sqlite3` ani kopii zapasowych. Po aktualizacji uruchom ponownie `python -m pip install -r requirements.txt` i `python main.py`.

[Pełny poradnik instalacji (PL/EN)](bot/INSTRUKCJA_INSTALACJI_v0.6.4_PL_EN.md) · [Instalacja na GitHub Pages](https://bollek231.github.io/poe-build-notifier-site/instalacja.html) · [Kod źródłowy](bot/) · [Lista zmian](CHANGELOG.md)

### Dokumentacja

[Strona główna](https://bollek231.github.io/poe-build-notifier-site/index.html) · [Komendy](https://bollek231.github.io/poe-build-notifier-site/komendy.html) · [Prywatność](https://bollek231.github.io/poe-build-notifier-site/privacy.html) · [Regulamin](https://bollek231.github.io/poe-build-notifier-site/terms.html) · [Zgłoś problem](https://github.com/Bollek231/poe-build-notifier-site/issues)

---

## English

### Currency farming strategy discovery (v0.6.4)

- `pFarmScan`: run up to three queries for fresh currency farming guides.
- `pFarmSearch essence`: search a category such as `harvest`, `expedition`, `atlas`, `crafting` or `trading`; `pFarmTopics` lists all options.
- `pFarmRecent`: view recently discovered strategies for the active game and patch.
- `pFarmAuto on` / `pFarmAuto off`: opt in/out of up to one extra YouTube search each scheduled interval, using the shared API quota. Off by default.
- Optionally direct strategy posts to another channel by setting `FARM_CHANNEL_ID` in private `.env` and restarting. Patch/age filters and quiet-hours digests remain active.


PoE Build Notifier automatically discovers **fresh Path of Exile build guides** on YouTube and posts them to a configured Discord channel. It supports **Path of Exile 1** and **Path of Exile 2**. This is an unofficial, non-commercial community project.

### Bot features

- **`pSetup`:** choose game, patch, language and scan interval from a Discord menu; changes apply only after confirmation.
- **`pHelp`:** interactive command categories.
- **`pQuietHours 23:00 08:00`:** Warsaw-time quiet hours with continued scanning and a single digest after quiet hours; disable with `pQuietHours off`.
- **`pPause 6h` / `pResume`:** pause scheduled searches (1–24 hours or `forever`); manual `pScan` remains available.
- **`pSaved`:** Save button on new build posts; private bookmarks sent via DM. Remove them with `pSaved remove VIDEO_ID` or `pSaved clear`.
- **`pTrending`:** popularity based on sampled view growth of recently detected videos. The first reading establishes a baseline; results are cached for 15 minutes.
- **`pTranslateTitles`:** optional English title translation using **MyMemory (free, no key or billing)** or **Google Cloud Translation**. Select with `pTranslateTitles mymemory`, `pTranslateTitles google`, or `pSettings`. Original titles are shown and API failures do not block notifications.

**Translation setup:** use `pTranslateTitles mymemory` without an API key or billing. Optionally provide `MYMEMORY_CONTACT_EMAIL=...` to raise the free character quota. For Google, add your private `TRANSLATION_API_KEY=...` and select `pTranslateTitles google`. `TRANSLATION_DAILY_LIMIT=30` caps calls per 24 hours. Source language is detected locally when possible; failed translations fall back to original titles.

### Features

- **PoE 1 / PoE 2:** switch with `pGame poe1` or `pGame poe2`; PoE 2 defaults to **patch 1.0**.
- **Fresh guides:** automated scans (every 2 hours by default), a 24-hour publication-age limit and duplicate detection.
- **Custom filters:** skill, class, ascendancy, game mode, and creator allow/block lists.
- **Guide buttons:** Path of Building, Maxroll and Mobalytics when the video description includes relevant links.
- **Easy management:** `pLanguage` opens a Polish/English selector; `pSettings` offers interactive settings editing.
- **Extras:** daily digests, YouTube quota protection, link refresh, private SQLite backups, alerts and `pVersion`.

### Main commands

| Command | Purpose |
|---|---|
| `pGame poe1` / `pGame poe2` | Select the game |
| `pLeague 1.0` | Set the target patch for the selected game |
| `pScan` | Scan YouTube manually |
| `pSearch Spark` | Search for builds using a skill |
| `pLanguage` | Open the language selector |
| `pSettings` | Edit bot settings interactively |
| `pDigest` | Show the build digest |
| `pHealth` / `pLimit` / `pVersion` | Health, quota and release information |

### One-click Windows launcher (v0.6.4)

Run `Start_PoE_Bot.bat` once from the bot folder to create `.venv` and install dependencies. Then open `Start_PoE_Bot.vbs` for a no-console GUI. The launcher checks GitHub for updates at startup, starts/stops the bot and shows its logs. Private `.env`, `search_config.json`, SQLite and backups are not overwritten.

### Windows installation — step by step

**1. Download the bot.** Install [Python 3.11+](https://www.python.org/downloads/) and **[download PoE Build Notifier v0.6.4b (ZIP)](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.4.zip)**. Extract the bot files so that `D:\PoE-Bot` contains `main.py` and `requirements.txt`.

**2. Set up Python.** Open **Windows Command Prompt (CMD)** and run:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

**3. Set up Discord.** Create an application and bot in [Discord Developer Portal](https://discord.com/developers/applications). Enable **Message Content Intent** under Bot settings. Invite the bot to your server with permission to view and send messages and embed links. Copy its token and the destination channel ID (enable *Developer Mode* in Discord).

**4. Obtain a YouTube API key.** Enable **YouTube Data API v3** in [Google Cloud Console](https://console.cloud.google.com/) for your project and create an API key. Restrict the key to this API.

**5. Create your private `.env` file.** In CMD run:

```bat
copy .env.example .env
notepad .env
```

Replace the sample values:

```dotenv
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
DISCORD_CHANNEL_ID=YOUR_NUMERIC_CHANNEL_ID
YOUTUBE_API_KEY=YOUR_GOOGLE_API_KEY
CHECK_INTERVAL_HOURS=2
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

**6. Start and verify.**

```bat
python main.py
```

On the configured Discord channel run `pPrivacy`, `pAgree` and `pHealth`. Use `pLanguage` for Polish/English, `pSettings` for configurable options and `pGame poe1` / `pGame poe2` to select the game.

**Upgrading an existing bot:** stop it (`Ctrl + C`), back up the folder and SQLite database, then replace the Python modules, `VERSION`, and `requirements.txt` from the newest ZIP. **Keep** your private `.env`, custom `search_config.json`, `.sqlite3` database and backups. Run `python -m pip install -r requirements.txt`, then `python main.py`.

[Complete installation guide (PL/EN)](bot/INSTRUKCJA_INSTALACJI_v0.6.4_PL_EN.md) · [Installation on GitHub Pages](https://bollek231.github.io/poe-build-notifier-site/instalacja-en.html) · [Source code](bot/) · [Patch Notes](CHANGELOG.md)

### Documentation

[Home](https://bollek231.github.io/poe-build-notifier-site/index-en.html) · [Commands](https://bollek231.github.io/poe-build-notifier-site/komendy-en.html) · [Privacy](https://bollek231.github.io/poe-build-notifier-site/privacy-en.html) · [Terms](https://bollek231.github.io/poe-build-notifier-site/terms-en.html) · [Report an issue](https://github.com/Bollek231/poe-build-notifier-site/issues)

---

### Security / Bezpieczeństwo

The public repository and download archives **must not contain private `.env` files, credentials, SQLite data or backups**. GitHub Pages hosts documentation and downloads, **not a continuously running Discord bot**.

Do not share Discord tokens or YouTube API keys. The project is not affiliated with Grinding Gear Games, Discord, Google or YouTube.
