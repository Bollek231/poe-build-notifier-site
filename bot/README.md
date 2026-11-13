# PoE Build Notifier v0.6.1 — 🇵🇱 Polski / 🇬🇧 English

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english) · [Lista zmian / Patch Notes](https://bollek231.github.io/poe-build-notifier-site/changelog.html)

## Polski

**Nowość v0.6.1: interaktywny język i ustawienia Discorda.** Funkcje PoE 1 / PoE 2 1.0 pozostają bez zmian. Wszystkie nowe preferencje zapisują się do lokalnej bazy SQLite.

### Język powiadomień (`pLanguage`)

- Wpisz **`pLanguage`**, a bot otworzy menu Discorda **Polski / English**.
- Możesz również użyć **`pLanguage pl`** lub **`pLanguage en`**.
- Wybrany język dotyczy odpowiedzi komend, nazw pól embedów, alertów i podsumowań. Oryginalne tytuły filmów YouTube i linki pozostają niezmienione.
- Wybór jest wspólny dla jednego serwera/kanału obsługiwanego przez tego bota i zachowywany po restarcie. Wcześniej opublikowane wiadomości nie są tłumaczone wstecz.

### Edytowalne ustawienia (`pSettings`)

- **`pSettings`** otwiera panel z listą aktualnych parametrów i menu rozwijanym.
- Wybór parametru liczbowego lub godziny otwiera **formularz Discord**. Opcje tak/nie przełączają się od razu.
- Dostępne są: interwał skanowania (1–24 h), godzina podsumowania (HH:MM, Warszawa), włączenie podsumowania, wyniki na frazę (1–50), odstęp powiadomień (1–30 s), lokalny budżet dzienny (1–10000), rezerwa na ręczne komendy, wiek publikacji filmu (1–24 h), częstotliwość odświeżania linków (1–24 h), liczba odświeżanych filmów (1–50), kontrola linków, sprawdzanie aktualizacji i interwał GitHub (1–72 h).
- Niedozwolone wartości nie są zapisywane. Rezerwa ręczna musi być mniejsza niż budżet dzienny. Maksymalny wiek filmu nadal **nie przekracza 24 godzin**.
- Zmiany działają bez restartu; są zapamiętywane w tabeli `bot_settings`. `.env` pozostaje źródłem wartości domyślnych.
- Panele może obsługiwać **wyłącznie administrator, który je otworzył**, na wybranym kanale Discorda po `pAgree`. Panel wygasa po 5 minutach.
- Tokeny, klucze API, ID kanałów i lokalizacja bazy **nie są edytowalne** przez Discorda.

### Bezpieczna aktualizacja z v0.6.0

1. Wyłącz bota (`Ctrl + C`); utwórz **kopię folderu** oraz pliku SQLite `poe330_seen.sqlite3`.
2. Rozpakuj ZIP v0.6.1. W istniejącym folderze wymień pliki Python, w tym **nowe `runtime_settings.py` i `localization.py`**, oraz `requirements.txt`.
3. **Nie nadpisuj** swojego `.env`, istniejącej bazy SQLite, prywatnych kopii zapasowych ani własnego `search_config.json`.
4. W aktywnym środowisku wykonaj `pip install -r requirements.txt`, a potem `python main.py`.
5. Na kanale Discorda sprawdź `pVersion`, `pLanguage`, `pSettings` i `pHealth`.

> Ważne dla hostingu: plik SQLite musi być na **trwałym woluminie** (np. `DB_PATH=/data/poe330_seen.sqlite3` na Railway). Inaczej zapisane preferencje mogą zniknąć po wdrożeniu. Bot nie zmienia starej historii, zgód ani konfiguracji PoE 1/PoE 2.


**W poprzedniej wersji v0.6.0: przełączanie Path of Exile 1 / Path of Exile 2 bez restartu.** PoE 2 domyślnie wyszukuje poradniki do **aktualizacji 1.0**, planowanej na 11 grudnia 2026 (PST). Zanim nadejdzie premiera, bot może wysłać nieliczne, świeże poradniki przygotowawcze do 1.0 — nie publikuje starszych filmów z 0.5 tylko dlatego, że zawierają słowo „build”.

### Najważniejsze komendy

| Komenda | Działanie |
|---|---|
| `pGame` | Wyświetla aktywną grę i wersję |
| `pGame poe2` | Przełącza na **Path of Exile 2, wersja 1.0** (domyślnie) |
| `pGame poe1` | Wraca do Path of Exile 1 i poprzednio ustawionej ligi |
| `pLeague` | Wyświetla wersję wybranej gry |
| `pLeague 1.0` | Ustawia wersję **1.0** podczas korzystania z PoE 2 |
| `pLeague 3.31` | Zmienia ligę podczas korzystania z PoE 1 |
| `pScan` | Skanuje YouTube dla **aktywnej gry** |
| `pSearch Spark` | Wyszukuje skill/build dla aktywnej gry i aktualnej wersji |

### Filtrowanie PoE 2 — bez nieaktualnych poradników

- Osobne zapytania dla PoE 2, np. `PoE2 1.0 league starter build`, `Path of Exile 2 1.0 endgame build`, `PoE 2 1.0 leveling build`.
- Wymagane rozpoznawalne oznaczenie **PoE 2**, **wersji 1.0** w tytule lub na początku opisu oraz oznaczenie buildu/poradnika w tytule.
- Odrzucane tytuły jasno wskazujące na starsze lub inne aktualizacje, np. **0.3**, **0.5**, **0.5.5**, a także zapowiedzi, reakcje i patch notes.
- Zawsze działa niezależny filtr **wieku publikacji do 24 godzin** (`publishedAfter` + lokalna weryfikacja daty). Samo „1.0” w tytule nie pozwala przesłać starego filmu.
- Osobne zapamiętywanie wersji gry oraz filtrów `pFilter` w SQLite. Historia i ustawienia PoE 1 nie znikają po przełączeniu.
- Linki z `mobalytics.gg/poe-2/...` są rozpoznawane jako przyciski **Mobalytics**.

**Uwaga:** to filtr zachowawczy. Poradnik bez wyraźnego oznaczenia 1.0 może zostać pominięty nawet jeśli jest aktualny. Po premierze można rozszerzyć słowa kluczowe w przyszłej aktualizacji.

### Instalacja / aktualizacja Windows

1. Zatrzymaj bota przez `Ctrl + C` i wykonaj kopię folderu `D:\PoE-Bot`.
2. Wypakuj `PoE_Build_Notifier_v0.6.0.zip`, skopiuj do istniejącego folderu **`main.py`, `storage.py`, `features.py`, `game_modes.py`, `enhancements.py`, `services.py`, `backups.py`, `requirements.txt`, `VERSION`**. Podmień pliki kodu.
3. **Nie nadpisuj** `.env`, `search_config.json`, `poe330_seen.sqlite3` ani folderu `backups`.
4. Otwórz CMD:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

5. Na Discordzie sprawdź `pHealth`, potem wpisz `pGame poe2`, `pLeague` i `pScan`. Jeśli nie zaakceptowałeś zasad, najpierw użyj `pPrivacy` i `pAgree`.

**Pierwsza instalacja:** utwórz `.venv` przez `py -m venv .venv`, zainstaluj zależności, skopiuj `.env.example` do `.env`, podaj własne `DISCORD_TOKEN`, `YOUTUBE_API_KEY` i `DISCORD_CHANNEL_ID`. Nigdy nie publikuj prawdziwego `.env`.

### Inne funkcje bez zmian

Skan co **2 godziny**, wiek filmów **24 h**, **3 s** między wiadomościami, przyciski PoB/Maxroll/Mobalytics, dzienne podsumowanie o **20:00 czasu polskiego**, limit 429 i lokalny licznik wyszukiwań, zaufane/zablokowane kanały, filtry, kopie bazy, alerty, `pVersion`, czyszczenie lokalnych danych YouTube po 7 dniach. **Bot nie usuwa automatycznie wiadomości z Discorda.**

### Opcjonalne ustawienia `.env`

```env
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
MAX_VIDEO_AGE_HOURS=24
CHECK_INTERVAL_HOURS=2
SEND_DELAY_SECONDS=3
YOUTUBE_CACHE_DAYS=7
```

`TARGET_LEAGUE` i `POE2_TARGET_VERSION` to ustawienia początkowe: zmiany przez `pLeague` są pamiętane w SQLite, także po restarcie. Stare `search_config.json` nadal działa bez zmian; nowa opcjonalna lista `poe2_search_queries` znajduje się w `search_config.example.json`.

**Bezpieczeństwo:** repozytorium nie zawiera tokenów, kluczy API, bazy danych ani prywatnych kopii zapasowych. Na Railway/VPS użyj trwałego woluminu, np. `DB_PATH=/data/poe330_seen.sqlite3` i `BACKUP_DIR=/data/backups`.

**Testy:** `python -m unittest discover -s tests -v`.

---

## English

**New in v0.6.1: interactive Discord language and settings controls.** All PoE 1 / PoE 2 1.0 features remain intact. Preferences persist in the existing local SQLite database.

### Bot language (`pLanguage`)

- Type **`pLanguage`** to open a Discord dropdown for **Polski / English**.
- Alternatively, use **`pLanguage pl`** or **`pLanguage en`**.
- This switches command responses, embed field labels, alerts and digests. Original YouTube video titles and URLs are never translated.
- One language is shared by the configured server/channel and saved across restarts. Previously posted Discord messages are not retroactively edited.

### Editable settings (`pSettings`)

- **`pSettings`** opens a Discord panel displaying current values and a dropdown of editable settings.
- Numeric fields and time use Discord **modal forms**; on/off options toggle immediately.
- Supported settings: scan interval (1–24 h), daily digest time (HH:MM Warsaw), digest on/off, results per query (1–50), notification delay (1–30 s), daily local budget (1–10000), reserve for manual searches, maximum video age (1–24 h), link refresh interval (1–24 h), posts per refresh (1–50), external-link verification on/off, version checks on/off, GitHub version-check interval (1–72 h).
- Invalid values are rejected. The manual reserve must stay below the daily budget. The **24-hour maximum age filter** remains enforced.
- Changes apply without restarting, are stored in `bot_settings`, and override the default settings loaded from `.env`.
- Only the **administrator who opened the menu** can use it, on the configured Discord channel and after `pAgree`. Interactive panels expire after five minutes.
- Tokens, API keys, channel IDs and database paths **cannot be changed** via Discord.

### Safe upgrade from v0.6.0

1. Stop the bot (`Ctrl + C`) and **back up the bot folder and SQLite database** (`poe330_seen.sqlite3`).
2. Extract v0.6.1 and replace the Python modules, including the **new `runtime_settings.py` and `localization.py`**, plus `requirements.txt`.
3. **Do not overwrite** your own `.env`, SQLite database, private backups, or custom `search_config.json`.
4. Activate your environment, run `pip install -r requirements.txt`, then `python main.py`.
5. Test `pVersion`, `pLanguage`, `pSettings`, and `pHealth` on Discord.

> Hosting: store the SQLite file on a **persistent volume** (for example `DB_PATH=/data/poe330_seen.sqlite3` on Railway) or settings may be lost on deployment. The migration preserves previous message history, privacy consent, and PoE 1 / PoE 2 preferences.


**Previously added in v0.6.0: switch between Path of Exile 1 and Path of Exile 2 without restarting.** PoE 2 searches for **version 1.0** by default, ahead of its announced December 11, 2026 PST full release. Before launch, it may find freshly published 1.0 build preparation guides; it does not publish old 0.5 videos simply because their titles contain “build”.

### Commands

| Command | What it does |
|---|---|
| `pGame` | Show the active game and target version |
| `pGame poe2` | Switch to **Path of Exile 2, version 1.0** by default |
| `pGame poe1` | Return to PoE 1 with its previous league version |
| `pLeague` | Show the active version |
| `pLeague 1.0` | Select **1.0** when PoE 2 is active |
| `pLeague 3.31` | Change the PoE 1 league when PoE 1 is active |
| `pScan` | Scan YouTube for builds for the **selected game** |
| `pSearch Spark` | Search builds for the selected game and patch |

### Strict 1.0 filtering for PoE 2

- Dedicated search phrases such as `PoE2 1.0 league starter build`, `Path of Exile 2 1.0 endgame build`, `PoE 2 1.0 leveling build`.
- Requires identifiable **PoE 2**, **patch 1.0** near the beginning of the content, and a build/guide signal in the video title.
- Rejects titles explicitly marked for older patches **0.3**, **0.5**, **0.5.5**, as well as news, reactions, tier lists, and trailers.
- Applies YouTube's `publishedAfter` plus an independent **24-hour publication-age check**; a 1.0 label alone never overrides video age.
- Stores each game's version and advanced filters independently in SQLite.
- Recognizes Mobalytics PoE 2 URLs such as `mobalytics.gg/poe-2/builds/...`.

The filter intentionally prioritizes accuracy over recall. A legitimate fresh video without an explicit 1.0 marker may be skipped.

### Upgrade (Windows)

1. Stop the bot and back up `D:\PoE-Bot`.
2. Extract `PoE_Build_Notifier_v0.6.0.zip` and replace **`main.py`, `storage.py`, `features.py`, `game_modes.py`, `enhancements.py`, `services.py`, `backups.py`, `requirements.txt`, `VERSION`**.
3. **Keep your own** `.env`, `search_config.json`, `poe330_seen.sqlite3`, and private backups.
4. Run:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

5. On Discord, use `pHealth`, `pGame poe2`, `pLeague`, then `pScan`. The bot requires `pPrivacy` and `pAgree` before administrative commands unless already accepted.

For first-time installation, create a virtual environment (`py -m venv .venv`), install dependencies, copy `.env.example` to `.env`, and supply your own Discord token, YouTube API key, and channel ID.

### Existing features retained

2-hour automatic scans, 24-hour video age window, 3-second message delay, PoB/Maxroll/Mobalytics buttons, 8 PM Warsaw-time digest, 429 quota protection, channel allow/block rules, filters, private SQLite backups, alerts, `pVersion`, and 7-day cleanup of local YouTube metadata. **Discord messages are not automatically deleted.**

### Optional `.env` settings

```env
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
MAX_VIDEO_AGE_HOURS=24
CHECK_INTERVAL_HOURS=2
SEND_DELAY_SECONDS=3
YOUTUBE_CACHE_DAYS=7
```

`pLeague` persists the per-game version to SQLite; the environment variables are initial defaults. Existing `search_config.json` files remain compatible, with an optional `poe2_search_queries` list for customization.

For Railway/VPS, use persistent storage for `DB_PATH` and `BACKUP_DIR`. Never commit secrets, the database, or backups to a public repository.

Offline tests: `python -m unittest discover -s tests -v`.

[🇵🇱 Changelog](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [🇬🇧 Patch Notes](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html) · [GitHub source](https://github.com/Bollek231/poe-build-notifier-site/tree/main/bot)
