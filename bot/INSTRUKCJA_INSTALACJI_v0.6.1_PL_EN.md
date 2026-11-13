# PoE Build Notifier v0.6.1 — instalacja / installation

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


---

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

