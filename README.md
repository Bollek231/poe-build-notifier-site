# PoE Build Notifier · v0.6.1

**Discord bot for Path of Exile 1 & Path of Exile 2 · 🇵🇱 Polski / 🇬🇧 English**

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english) · [🌐 Strona / Website](https://bollek231.github.io/poe-build-notifier-site/) · [📝 Patch Notes](CHANGELOG.md)

---

## Polski

PoE Build Notifier automatycznie wyszukuje **świeże poradniki buildów** na YouTube i publikuje je na wybranym kanale Discord. Obsługuje **Path of Exile 1** oraz **Path of Exile 2**. To niekomercyjny, nieoficjalny projekt społecznościowy.

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

### Pobieranie i instalacja

**[Pobierz PoE Build Notifier v0.6.1 (ZIP)](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip)** · [Instrukcja instalacji](https://bollek231.github.io/poe-build-notifier-site/instalacja.html) · [Kod bota](bot/) · [Lista zmian](CHANGELOG.md)

W skrócie: zainstaluj **Python 3.11+**, wypakuj ZIP, utwórz środowisko wirtualne i wykonaj `pip install -r requirements.txt`. Skopiuj `.env.example` do prywatnego `.env`, wpisz `DISCORD_TOKEN`, `YOUTUBE_API_KEY` i `DISCORD_CHANNEL_ID`, następnie uruchom `python main.py`.

Przy aktualizacji **zachowaj własny `.env`, `search_config.json` i bazę SQLite**. Przed podmianą plików utwórz kopię zapasową.

### Dokumentacja

[Strona główna](https://bollek231.github.io/poe-build-notifier-site/index.html) · [Komendy](https://bollek231.github.io/poe-build-notifier-site/komendy.html) · [Prywatność](https://bollek231.github.io/poe-build-notifier-site/privacy.html) · [Regulamin](https://bollek231.github.io/poe-build-notifier-site/terms.html) · [Zgłoś problem](https://github.com/Bollek231/poe-build-notifier-site/issues)

---

## English

PoE Build Notifier automatically discovers **fresh Path of Exile build guides** on YouTube and posts them to a configured Discord channel. It supports **Path of Exile 1** and **Path of Exile 2**. This is an unofficial, non-commercial community project.

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

### Download and setup

**[Download PoE Build Notifier v0.6.1 (ZIP)](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip)** · [Installation guide](https://bollek231.github.io/poe-build-notifier-site/instalacja-en.html) · [Bot source](bot/) · [Patch Notes](CHANGELOG.md)

Install **Python 3.11+**, extract the archive, create a virtual environment and run `pip install -r requirements.txt`. Copy `.env.example` to your private `.env`, add `DISCORD_TOKEN`, `YOUTUBE_API_KEY` and `DISCORD_CHANNEL_ID`, then run `python main.py`.

When upgrading, **keep your own `.env`, `search_config.json` and SQLite database**. Back them up before replacing source files.

### Documentation

[Home](https://bollek231.github.io/poe-build-notifier-site/index-en.html) · [Commands](https://bollek231.github.io/poe-build-notifier-site/komendy-en.html) · [Privacy](https://bollek231.github.io/poe-build-notifier-site/privacy-en.html) · [Terms](https://bollek231.github.io/poe-build-notifier-site/terms-en.html) · [Report an issue](https://github.com/Bollek231/poe-build-notifier-site/issues)

---

### Security / Bezpieczeństwo

The public repository and download archives **must not contain private `.env` files, credentials, SQLite data or backups**. GitHub Pages hosts documentation and downloads, **not a continuously running Discord bot**.

Do not share Discord tokens or YouTube API keys. The project is not affiliated with Grinding Gear Games, Discord, Google or YouTube.
