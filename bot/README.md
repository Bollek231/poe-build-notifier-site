# PoE Build Notifier v0.6.2b — kod źródłowy / source code

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english) · [Strona / Website](https://bollek231.github.io/poe-build-notifier-site/) · [Lista zmian / Patch Notes](../CHANGELOG.md)

## Polski

Bot Discord do wyszukiwania nowych buildów **Path of Exile 1 i Path of Exile 2** na YouTube. Przykładowe pliki konfiguracyjne nie zawierają prawdziwych tokenów.

### Funkcje bota

- **`pSetup`:** konfiguracja gry, wersji, języka i interwału skanowania z menu Discorda. Zapis dopiero po zatwierdzeniu.
- **`pHelp`:** menu kategorii komend dostępne na kanale bota.
- **`pQuietHours 23:00 08:00`:** cisza nocna w strefie Warszawa; skanowanie trwa, a wykryte buildy trafiają do zbiorczego podsumowania po zakończeniu ciszy. `pQuietHours off` wyłącza funkcję.
- **`pPause 6h` / `pResume`:** pauza tylko dla automatycznego wyszukiwania (1–24 h lub `forever`). Ręczne `pScan` pozostaje dostępne.
- **`pSaved`:** przycisk zapisywania przy nowych buildach i prywatna lista zakładek wysyłana przez DM; `pSaved remove VIDEO_ID` i `pSaved clear` usuwają dane.
- **`pTrending`:** popularność ostatnich filmów według przyrostu wyświetleń między pomiarami. Pierwsze wywołanie ustala punkt odniesienia; ponowne odczyty mają 15-minutową pamięć podręczną.
- **`pTranslateTitles`:** opcjonalne tłumaczenie tytułów na angielski przez **MyMemory (bez klucza i rozliczeń)** albo **Google Cloud Translation**. Wybór: `pTranslateTitles mymemory`, `pTranslateTitles google` lub `pSettings`; oryginał pozostaje w wiadomości. Błędy tłumaczenia nie blokują publikacji.

**Tłumaczenia:** wpisz `pTranslateTitles mymemory`, aby włączyć bezpłatne MyMemory. Możesz opcjonalnie ustawić `MYMEMORY_CONTACT_EMAIL=...` w prywatnym `.env` dla wyższego limitu. Aby wybrać Google, dodaj `TRANSLATION_API_KEY=...` i wpisz `pTranslateTitles google`. Parametr `TRANSLATION_DAILY_LIMIT=30` ogranicza liczbę zapytań. Automatyczne wykrywanie języka jest lokalne, a w razie błędu bot zachowa oryginalny tytuł.

### Instalacja na Windows

1. Zainstaluj **Python 3.11 lub nowszy**. Pobierz [ZIP v0.6.2b](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.2b.zip) i wypakuj wszystkie pliki bota do folderu, np. `D:\PoE-Bot`.
2. Otwórz CMD:

```bat
cd /d D:\PoE-Bot
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

3. Uzupełnij w prywatnym `.env`: `DISCORD_TOKEN`, `YOUTUBE_API_KEY`, `DISCORD_CHANNEL_ID`. Włącz **Message Content Intent** w Discord Developer Portal.
4. Uruchom `python main.py`. Na Discordzie wpisz `pPrivacy`, `pAgree` i `pHealth`.

**Aktualizacja istniejącej instalacji:** zatrzymaj proces, wykonaj kopię folderu i bazy SQLite, a następnie podmień moduły Pythona z paczki. Zachowaj własny `.env`, `search_config.json`, bazę SQLite oraz folder `backups`. Uruchom `python -m pip install -r requirements.txt`, a potem `python main.py`.

### Sterowanie botem

| Komenda | Funkcja |
|---|---|
| `pGame poe1` / `pGame poe2` | Przełączanie Path of Exile 1 / Path of Exile 2 |
| `pLeague` / `pLeague 1.0` | Podgląd i zmiana wersji wybranej gry; PoE 2 domyślnie 1.0 |
| `pScan` / `pSearch Spark` | Skanowanie i wyszukiwanie nowych buildów |
| `pLanguage` | Menu wyboru języka: polski / angielski |
| `pSettings` | Menu bezpiecznej edycji ustawień |
| `pFilters` / `pFilter` | Filtry buildów |
| `pBlockChannel` / `pAllowChannel` | Zarządzanie listami kanałów |
| `pDigest` / `pBuilds` | Podsumowanie i lista buildów |
| `pLimit` / `pHealth` / `pVersion` | Limity, stan i aktualna wersja |
| `pBackup` / `pRefreshLinks` | Kopia bazy i odświeżanie odnośników |

### Ustawienia i bezpieczeństwo

`pSettings` pozwala edytować m.in. częstotliwość skanów (1–24 godziny), godzinę podsumowania, liczbę wyników, budżet wyszukiwania, odstęp wiadomości, maksymalny wiek filmu (do 24 godzin) i sprawdzanie aktualizacji GitHub. `pLanguage` otwiera rozwijaną listę **Polski / English**. Preferencje są zapisywane do SQLite, a więc nie giną po restarcie, jeżeli baza jest przechowywana trwale.

Panele administracyjne wymagają uprawnienia **Zarządzanie serwerem** oraz zaakceptowania zasad przez `pAgree`. Tokenów, kluczy API, ID kanałów ani ścieżki bazy nie można zmieniać przez Discorda.

Bot automatycznie skanuje YouTube (domyślnie co 2 godziny), przyjmuje tylko filmy opublikowane w ciągu ostatnich 24 godzin, a dla PoE 2 rozpoznaje poradniki oznaczone wersją **1.0**. Lokalna retencja metadanych YouTube wynosi domyślnie 7 dni. **Bot nie usuwa automatycznie wiadomości Discord.**

Na Railway/VPS ustaw trwały wolumin, np. `DB_PATH=/data/poe330_seen.sqlite3` i `BACKUP_DIR=/data/backups`. Nie udostępniaj swoich plików `.env`, bazy ani kopii zapasowych.

[Pełna instrukcja](INSTRUKCJA_INSTALACJI_v0.6.2b_PL_EN.md) · [Lista komend](https://bollek231.github.io/poe-build-notifier-site/komendy.html)

---

## English

A Discord bot for fresh **Path of Exile 1 and Path of Exile 2** YouTube build guides. The public sample configuration contains no real credentials.

### Bot features

- **`pSetup`:** choose game, patch, language and scan interval from a Discord menu; changes apply only after confirmation.
- **`pHelp`:** interactive command categories.
- **`pQuietHours 23:00 08:00`:** Warsaw-time quiet hours with continued scanning and a single digest after quiet hours; disable with `pQuietHours off`.
- **`pPause 6h` / `pResume`:** pause scheduled searches (1–24 hours or `forever`); manual `pScan` remains available.
- **`pSaved`:** Save button on new build posts; private bookmarks sent via DM. Remove them with `pSaved remove VIDEO_ID` or `pSaved clear`.
- **`pTrending`:** popularity based on sampled view growth of recently detected videos. The first reading establishes a baseline; results are cached for 15 minutes.
- **`pTranslateTitles`:** optional English title translation using **MyMemory (free, no key or billing)** or **Google Cloud Translation**. Select with `pTranslateTitles mymemory`, `pTranslateTitles google`, or `pSettings`. Original titles are shown and API failures do not block notifications.

**Translation setup:** use `pTranslateTitles mymemory` without an API key or billing. Optionally provide `MYMEMORY_CONTACT_EMAIL=...` to raise the free character quota. For Google, add your private `TRANSLATION_API_KEY=...` and select `pTranslateTitles google`. `TRANSLATION_DAILY_LIMIT=30` caps calls per 24 hours. Source language is detected locally when possible; failed translations fall back to original titles.

### Windows setup

1. Install **Python 3.11+**. [Download v0.6.2b](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.2b.zip) and extract the bot files to a directory such as `D:\PoE-Bot`.
2. Open Command Prompt:

```bat
cd /d D:\PoE-Bot
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

3. Add `DISCORD_TOKEN`, `YOUTUBE_API_KEY` and `DISCORD_CHANNEL_ID` to your private `.env`. Enable **Message Content Intent** in Discord Developer Portal.
4. Run `python main.py`, then use `pPrivacy`, `pAgree` and `pHealth` on Discord.

**Upgrading:** stop the bot, back up its folder and SQLite database, then replace the Python modules from the ZIP. Keep your private `.env`, `search_config.json`, SQLite database and `backups` directory. Run `python -m pip install -r requirements.txt`, then restart with `python main.py`.

### Commands

| Command | Purpose |
|---|---|
| `pGame poe1` / `pGame poe2` | Switch Path of Exile 1 / Path of Exile 2 |
| `pLeague` / `pLeague 1.0` | View or select the active game's patch; PoE 2 defaults to 1.0 |
| `pScan` / `pSearch Spark` | Scan or search build guides |
| `pLanguage` | Polish / English language dropdown |
| `pSettings` | Interactive, validated settings |
| `pFilters` / `pFilter` | Advanced build filters |
| `pBlockChannel` / `pAllowChannel` | Creator lists |
| `pDigest` / `pBuilds` | Digest and build list |
| `pLimit` / `pHealth` / `pVersion` | Quota, status and version |
| `pBackup` / `pRefreshLinks` | Database backup and link refresh |

### Configuration and safety

`pSettings` allows editing the scan schedule (1–24 hours), digest time, results per query, local YouTube search budget, message delay, maximum video age (up to 24 hours), and GitHub version checks. `pLanguage` selects **Polski / English**. These preferences are stored in SQLite and persist when the database is on permanent storage.

Administrative menus require **Manage Server** and prior `pAgree` consent. Discord tokens, API keys, channel IDs and database paths cannot be edited from Discord.

The default scan interval is 2 hours. Only videos published in the past 24 hours are eligible; PoE 2 guides must identify the target **1.0** version. Local YouTube metadata is cleaned up after 7 days by default. **Discord messages are not automatically deleted.**

On Railway/VPS use persistent storage, for example `DB_PATH=/data/poe330_seen.sqlite3` and `BACKUP_DIR=/data/backups`. Never publish your `.env`, database or private backups.

[Full setup guide](INSTRUKCJA_INSTALACJI_v0.6.2b_PL_EN.md) · [Commands](https://bollek231.github.io/poe-build-notifier-site/komendy-en.html)

---

Run offline tests with `python -m unittest discover -s tests -v`. Project source is unofficial and not affiliated with Grinding Gear Games, Discord, Google or YouTube.
