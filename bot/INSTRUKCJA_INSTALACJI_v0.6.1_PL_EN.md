# PoE Build Notifier v0.6.1 — Instalacja / Installation

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english) · [Strona główna / Homepage](https://bollek231.github.io/poe-build-notifier-site/)

## Polski

### Pierwsza instalacja na Windows

1. Zainstaluj **Python 3.11+** i pobierz [aktualną paczkę ZIP](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip).
2. Wypakuj pliki bota do `D:\PoE-Bot`.
3. Otwórz CMD i wykonaj:

```bat
cd /d D:\PoE-Bot
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

4. W `.env` wpisz własne `DISCORD_TOKEN`, `YOUTUBE_API_KEY` i `DISCORD_CHANNEL_ID`. Włącz **Message Content Intent** w ustawieniach aplikacji Discord.
5. Uruchom `python main.py`, a potem na Discordzie `pPrivacy`, `pAgree`, `pHealth`.

### Aktualizacja istniejącego bota

1. Zatrzymaj proces (`Ctrl+C`), zrób kopię folderu i pliku `poe330_seen.sqlite3`.
2. Skopiuj z ZIP-a aktualne moduły Python, szczególnie `game_modes.py`, `localization.py`, `runtime_settings.py`, plik `VERSION` i `requirements.txt`.
3. **Zachowaj** własny `.env`, bazę SQLite, `search_config.json` i folder prywatnych kopii zapasowych.
4. Uruchom `python -m pip install -r requirements.txt` oraz `python main.py`.
5. Na Discordzie przetestuj `pVersion`, `pGame`, `pLanguage` i `pSettings`.

### Język i ustawienia

`pLanguage` wyświetla menu **Polski / English**; dostępne są również `pLanguage pl` i `pLanguage en`.

`pSettings` pozwala zmienić: interwał skanowania (1–24 h), godzinę i włączenie podsumowania, wyniki na frazę (1–50), odstęp wiadomości (1–30 s), lokalny budżet wyszukiwań (1–10000), rezerwę ręczną, wiek filmów (do 24 h), odświeżanie i weryfikację linków oraz sprawdzanie aktualizacji (1–72 h). Wartości są walidowane i przechowywane w SQLite. Menu edycji wymaga uprawnienia **Zarządzanie serwerem** i `pAgree`.

**Hosting 24/7:** na Railway lub VPS przechowuj bazę na trwałym woluminie, np. `DB_PATH=/data/poe330_seen.sqlite3`, a kopie w `BACKUP_DIR=/data/backups`. Nie publikuj prywatnych plików ani kluczy API.

---

## English

### First-time Windows setup

1. Install **Python 3.11+** and [download the ZIP](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip).
2. Extract the bot files to `D:\PoE-Bot`.
3. Open Command Prompt:

```bat
cd /d D:\PoE-Bot
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

4. Add `DISCORD_TOKEN`, `YOUTUBE_API_KEY` and `DISCORD_CHANNEL_ID` to your private `.env`, and enable Discord **Message Content Intent**.
5. Run `python main.py` and use `pPrivacy`, `pAgree`, `pHealth` on Discord.

### Upgrading the bot

1. Stop the bot (`Ctrl+C`) and back up its folder and `poe330_seen.sqlite3` database.
2. Copy the current Python modules from the archive, including `game_modes.py`, `localization.py`, `runtime_settings.py`, plus `VERSION` and `requirements.txt`.
3. **Do not overwrite** your own `.env`, SQLite database, `search_config.json` or private backups.
4. Run `python -m pip install -r requirements.txt` and `python main.py`.
5. Test `pVersion`, `pGame`, `pLanguage` and `pSettings`.

### Language and settings

`pLanguage` opens a **Polski / English** dropdown, or use `pLanguage pl` / `pLanguage en`.

`pSettings` lets admins edit scan intervals (1–24 h), digest time and enablement, results per query (1–50), posting delay (1–30 s), local search budget (1–10000), manual reserve, video age (up to 24 h), link checks and refresh, and version checks (1–72 h). Changes are validated and stored in SQLite. Editing requires **Manage Server** and `pAgree`.

**24/7 hosting:** store SQLite on a persistent volume, e.g. `DB_PATH=/data/poe330_seen.sqlite3`, and backups at `BACKUP_DIR=/data/backups`. Do not publish your credentials or private data.
