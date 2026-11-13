# PoE Build Notifier v0.5.1 — 🇵🇱 Polski / 🇬🇧 English

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english) · [Lista zmian / Patch Notes](https://bollek231.github.io/poe-build-notifier-site/changelog.html)

## Polski

Niekomercyjny bot Discord wyszukujący **aktualne buildy Path of Exile 1** na YouTube. Wersja **v0.5.1** rozwija v0.5.0, zachowując dotychczasowe komendy i 24-godzinny limit wieku filmów.

### Instalacja / aktualizacja (Windows)

1. **Zatrzymaj lokalnego bota** (`Ctrl + C`) i zrób kopię folderu `D:\PoE-Bot`.
2. Rozpakuj ZIP v0.5.1. Do istniejącego folderu skopiuj **`main.py`, `storage.py`, `features.py`, `enhancements.py`, `services.py`, `backups.py`, `requirements.txt` i `VERSION`**.
3. **Nie nadpisuj** swoich plików `.env`, `search_config.json`, `poe330_seen.sqlite3` ani prywatnych kopii bazy.
4. W CMD wpisz:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

**Pierwsza instalacja** (jeśli nie masz `.venv`):

```bat
cd /d D:\PoE-Bot
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
python main.py
```

W `.env` wpisz **własne** `DISCORD_TOKEN`, `DISCORD_CHANNEL_ID` i `YOUTUBE_API_KEY`. W Discord Developer Portal włącz **Message Content Intent**. Nigdy nie publikuj pliku `.env` na GitHubie.

### Nowe funkcje v0.5.1

- **Inteligentna quota** — automatyczne wyszukiwania dzielą lokalną pozostałą pulę na kolejne skany do resetu w czasie PT. Rotacja fraz i rezerwa na `pSearch`. **To szacunek tego bota, nie oficjalny odczyt Google Cloud.**
- **Czarna i biała lista YouTube** — `pBlockChannel UC...`, `pAllowChannel UC...`, `pUnlistChannel UC...`, `pChannelRules`. `pWhitelist on` publikuje wyłącznie materiały kanałów z białej listy; `pWhitelist off` traktuje je priorytetowo, ale nie wyklucza pozostałych. ID kanału to ciąg `UC` i 22 znaki; nazwy `@handle` nie są obsługiwane.
- **Rozszerzone filtry** — `pFilters`, `pFilter skill Lightning Strike`, `pFilter ascendancy Deadeye`, `pFilter class Ranger`, `pFilter mode SSF`, `pFilter stage starter`; `pFilter mode all` usuwa jeden filtr, `pFilter clear` usuwa wszystkie. SSF/HC/SC wymagają wyraźnego oznaczenia w tytule lub początku opisu; bot nie zgaduje.
- **Bezpieczne przyciski** — bot sprawdza tylko dozwolone domeny HTTPS PoB / Maxroll / Mobalytics, bez przekierowań. Potwierdzony HTTP 404/410 usuwa wadliwy przycisk; chwilowy błąd, 403 lub timeout go nie usuwa.
- **Uzupełnianie linków** — co 6 godzin bot może pobrać aktualny opis filmu i **edytować tylko przyciski** istniejącego powiadomienia, bez kasowania ani ponownej publikacji. Działa **wyłącznie dla wiadomości wysłanych od v0.5.1** i monitorowanych maksymalnie 7 dni; ręcznie: `pRefreshLinks`.
- **Alerty** — wiadomości o uruchomieniu/restartach, odzyskaniu połączenia, błędach oraz dostępnych aktualizacjach; z ograniczeniem częstotliwości. Możesz wskazać prywatny kanał `ALERT_CHANNEL_ID`, domyślnie używany jest kanał buildów. Ustaw `ALERT_CHANNEL_ID=0`, aby wyłączyć wysyłanie alertów na Discord.
- **Kopie SQLite** — jedna spójna kopia dziennie w `BACKUP_DIR`, rotacja `BACKUP_KEEP_DAYS=7`. `pBackup` uruchamia ręcznie. Kopie zawierają historię, ID Discord oraz ustawienia; **nie zawierają pliku `.env`** i **nie mogą trafić do publicznego repozytorium**.
- **Sprawdzanie wersji** — `pVersion` porównuje lokalną wersję z publicznym plikiem `VERSION` na GitHubie. Bot może wysłać jednorazowe powiadomienie o nowym wydaniu. **Nigdy nie instaluje aktualizacji samodzielnie.**

### Dotychczasowe funkcje

- `pPrivacy`, `pAgree`, `pRevoke`, `pScan`, `pSearch`, `pLimit`, `pHealth`, `pSettings`, `pBuilds`, `pLeague`, `pDigest`.
- Skanowanie co **2 godziny**, filmy nie starsze niż **24 godziny**, **3 sekundy** przerwy między wiadomościami.
- Liga zmieniana przez `pLeague 3.31`; wykrywanie duplikatów; przyciski PoB, Maxroll, Mobalytics; podsumowanie o **20:00 PL**.
- Ochrona 429 i reset według czasu pacyficznego; lokalne metadane YouTube usuwane po **7 dniach**. **Wiadomości Discord nie są automatycznie usuwane.**

### Ustawienia opcjonalne `.env`

```env
# Lokalny dzienny budżet wyszukiwań: dostosuj do REALNEGO przydziału Google
DAILY_SEARCH_BUDGET=96
RESERVED_SEARCHES=24
ALERT_CHANNEL_ID=0
CHECK_EXTERNAL_LINKS=true
LINK_REFRESH_INTERVAL_HOURS=6
MAX_LINK_REFRESH_PER_RUN=10
BACKUP_DIR=backups
BACKUP_KEEP_DAYS=7
VERSION_CHECK_ENABLED=true
```

Przy `ALERT_CHANNEL_ID=0` alerty są tylko w logach. Jeśli chcesz dostawać je na Discord, wpisz **prawdziwy ID kanału administracyjnego**.

Na hostingu typu Railway używaj trwałego woluminu: np. `DB_PATH=/data/poe330_seen.sqlite3` i `BACKUP_DIR=/data/backups`. Inaczej kopie i ustawienia mogą zniknąć po ponownym wdrożeniu. Trzymaj kopie z dala od publicznego GitHuba i twórz również kopie poza serwerem w bezpiecznym miejscu.

**Przywracanie:** zatrzymaj bota, zrób kopię aktualnej bazy, skopiuj wybrany `poe-backup-YYYY-MM-DD.sqlite3` na ścieżkę `DB_PATH`, następnie uruchom `python main.py`.

**Testy offline:** `python -m unittest discover -s tests -v`.

---

## English

Non-commercial Discord bot that discovers fresh **Path of Exile 1 builds** using YouTube Data API v3. **v0.5.1** adds eight improvements while retaining the previous v0.5.0 functionality.

### Windows installation / update

1. Stop the running bot with `Ctrl + C` and back up `D:\PoE-Bot`.
2. Extract v0.5.1 ZIP. Copy **`main.py`, `storage.py`, `features.py`, `enhancements.py`, `services.py`, `backups.py`, `requirements.txt`, and `VERSION`** into the existing bot directory.
3. **Keep your original** `.env`, `search_config.json`, `poe330_seen.sqlite3`, and any private database backups.
4. Run:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

First installation:

```bat
cd /d D:\PoE-Bot
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
python main.py
```

Set your own `DISCORD_TOKEN`, `DISCORD_CHANNEL_ID`, and `YOUTUBE_API_KEY` in `.env`. Enable **Message Content Intent** in the Discord Developer Portal. Never commit private credentials to GitHub.

### New in v0.5.1

- **Smart search quota:** evenly distributes the locally estimated remaining budget across scheduled scans, rotates search phrases, and protects a reserve for manual commands. This is **not** an official Google Cloud quota reading.
- **Channel blocklist and allowlist:** `pBlockChannel UC...`, `pAllowChannel UC...`, `pUnlistChannel UC...`, `pChannelRules`. With `pWhitelist on`, only allowed channels can be posted; `pWhitelist off` prioritizes trusted channels while still accepting other non-blocked channels. Use YouTube's actual `UC` channel ID rather than `@handles`.
- **Advanced build filters:** `pFilters`, `pFilter skill Lightning Strike`, `pFilter ascendancy Deadeye`, `pFilter class Ranger`, `pFilter mode SSF`, `pFilter stage starter`; `pFilter clear` removes all filters. The bot requires explicit mode information instead of guessing SSF/HC/SC.
- **External guide URL checks:** strict HTTPS domain allowlist, no redirects, 404/410 rejection, tolerant of transient 403 and timeouts. Can be switched off with `CHECK_EXTERNAL_LINKS=false` while domain validation remains active.
- **Automatic button updates:** every 6 hours, recent video descriptions are rechecked and new guide buttons are added by **editing the existing Discord message**. Only messages published by v0.5.1 or newer are tracked, for up to 7 days. Manual command: `pRefreshLinks`.
- **Operational alerts:** startup, Discord reconnection, errors, and new-version notices are rate-limited. Set `ALERT_CHANNEL_ID` to an admin channel or `0` to disable Discord alerts; without a setting, the build channel is used.
- **SQLite backups:** one consistent daily snapshot, 7-file retention by default, and manual `pBackup`. Backups contain user/server identifiers and must stay **private**. `.env` is never backed up.
- **Version command:** `pVersion` checks the public GitHub `VERSION` file and optionally alerts you about new releases. It does **not** install any code automatically.

### Retained v0.5.0 features

Scheduled searches every 2 hours, videos less than 24 hours old, 3-second posting delay, PoE 1 and selected-league filtering, deduplication, PoB/Maxroll/Mobalytics buttons, 8:00 PM Warsaw-time daily digest, 429 quota pause, and the previous command set. Locally cached YouTube data is cleared after 7 days; **Discord messages are never deleted automatically**.

### Optional configuration

```env
DAILY_SEARCH_BUDGET=96
RESERVED_SEARCHES=24
ALERT_CHANNEL_ID=0
CHECK_EXTERNAL_LINKS=true
LINK_REFRESH_INTERVAL_HOURS=6
MAX_LINK_REFRESH_PER_RUN=10
BACKUP_DIR=backups
BACKUP_KEEP_DAYS=7
VERSION_CHECK_ENABLED=true
```

For Railway/VPS, store the live database and private backups on a **persistent volume**, e.g. `DB_PATH=/data/poe330_seen.sqlite3` and `BACKUP_DIR=/data/backups`. To restore a backup, stop the bot, back up your current DB, copy the selected snapshot to `DB_PATH`, then restart.

Offline tests: `python -m unittest discover -s tests -v`.

[🇵🇱 Lista zmian](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [🇬🇧 Patch Notes](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html) · [GitHub source](https://github.com/Bollek231/poe-build-notifier-site/tree/main/bot)
