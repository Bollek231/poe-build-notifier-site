# PoE Build Notifier v0.6.1 — PL 🇵🇱 / EN 🇬🇧

**Wybierz język / Choose language:** [🇵🇱 Polski](#polski) · [🇬🇧 English](#english)

## Polski

**Nowość w v0.6.0:** przeprojektowana, animowana strona GitHub Pages z efektem poświaty pod kursorem, ruchomymi cząsteczkami, przełącznikiem motywu ☀️/🌙, nowym podglądem Discorda i spójną stylistyką dokumentacji. Funkcje bota pozostały bez zmian względem v0.5.1.


**Aktualna wersja: v0.6.1. Następna aktualizacja: v0.6.2.**


Niekomercyjny projekt bota Discord, który wyszukuje nowe buildy Path of Exile 1 przez YouTube Data API v3 i publikuje linki do oryginalnych filmów.

## Nowość v0.6.1 — wybór języka i interaktywne ustawienia

- **`pLanguage`**: menu Discorda z wyborem **Polski / English**; dostępne także `pLanguage pl` i `pLanguage en`. Wybór jest zapisywany w SQLite i obowiązuje po restarcie.
- **`pSettings`**: menu oraz formularze do zmiany interwału skanowania (1–24 h), godziny podsumowania, liczby wyników, odstępu powiadomień, lokalnego budżetu YouTube, wieku filmu (maksymalnie 24 h), weryfikacji i odświeżania linków, powiadomień o aktualizacji i czasu sprawdzania GitHuba.
- Edycja dostępna tylko dla administratora na skonfigurowanym kanale po `pAgree`; wszystkie wartości są weryfikowane przed zapisaniem. Tokenów i identyfikatorów kanałów nie można zmieniać z Discorda.
- Ustawienia są trwałe, działają bez restartu, nie zmieniają historii wysłanych filmów ani konfiguracji PoE 1 / PoE 2.
- [Instrukcja instalacji v0.6.1](bot/INSTRUKCJA_INSTALACJI_v0.6.1_PL_EN.md) · [Kod źródłowy](bot/) · [Lista zmian](CHANGELOG.md)

## Strona i dokumentacja

- 🌐 **[Strona główna](https://bollek231.github.io/poe-build-notifier-site/index.html)**
- 🛠️ **[Instalacja krok po kroku](https://bollek231.github.io/poe-build-notifier-site/instalacja.html)**
- 💬 **[Działanie i komendy](https://bollek231.github.io/poe-build-notifier-site/komendy.html)**
- 🔒 **[Polityka prywatności](https://bollek231.github.io/poe-build-notifier-site/privacy.html)**
- 📄 **[Warunki korzystania](https://bollek231.github.io/poe-build-notifier-site/terms.html)**
- 📝 **[Lista zmian / Patch Notes](https://bollek231.github.io/poe-build-notifier-site/changelog.html)**

### Nowość v0.6.0 — PoE 1 / PoE 2

Bot obsługuje teraz **Path of Exile 1** i **Path of Exile 2**. PoE 2 domyślnie filtruje **wersję 1.0** (premiera planowana na 11 grudnia 2026 PST), bez pobierania starych filmów o 0.3/0.5.

| Komenda | Działanie |
|---|---|
| \`pGame\` | Pokazuje aktualną grę i wersję |
| \`pGame poe2\` | Przełącza na **PoE 2 1.0** |
| \`pGame poe1\` | Wraca do **PoE 1** i zapamiętanej ligi |
| \`pLeague 1.0\` | Ustawia wersję PoE 2 na **1.0** |
| \`pScan\` | Skanuje YouTube dla wybranej gry |
| \`pSearch Spark\` | Wyszukiwanie skilla w wybranej grze |

Weryfikacja PoE 2 wymaga oznaczenia PoE 2 i 1.0 w tytule lub początku opisu oraz wskazania, że film jest poradnikiem/buildem. Niezależnie obowiązuje **24-godzinny limit wieku publikacji**. Wersje i dodatkowe filtry dla obu gier są zapisywane oddzielnie. Obsługiwane są również linki \`mobalytics.gg/poe-2/\`.

Przy aktualizacji **skopiuj też nowy plik \`game_modes.py\`**, ale zachowaj dotychczasowy \`.env\`, \`search_config.json\` i \`poe330_seen.sqlite3\`. PoE 2 nie wymaga nowych kluczy API.

## Pobierz PoE Build Notifier v0.6.1

- 📦 **[Pobierz paczkę ZIP z kodem](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip)**
- 🐍 **[Przejrzyj kod źródłowy na GitHubie](https://github.com/Bollek231/poe-build-notifier-site/tree/main/bot)**
- 📚 **[README kodu bota](bot/README.md)**

Archiwum zawiera pliki `main.py`, `storage.py`, `features.py`, `enhancements.py`, `services.py`, `backups.py`, zależności, przykładową konfigurację i testy. **Nie zawiera prywatnych tokenów, kluczy API, plików .env ani bazy SQLite.**

### Nowe w v0.5.1

- Inteligentny budżet wyszukiwań, rotacja fraz i rezerwa na ręczne komendy.
- Czarne/białe listy twórców: `pBlockChannel`, `pAllowChannel`, `pWhitelist on/off`, `pChannelRules`, `pUnlistChannel`.
- Rozszerzone filtry: `pFilters`, `pFilter skill Lightning Strike`, `pFilter mode SSF`, `pFilter class Ranger`, `pFilter stage starter`.
- Walidacja linków PoB/Maxroll/Mobalytics oraz uzupełnianie przycisków w nowych wiadomościach przez `pRefreshLinks`.
- Alerty o starcie, odzyskaniu połączenia i problemach; prywatne kopie SQLite z komendą `pBackup`.
- `pVersion` i powiadomienia o nowej wersji na GitHubie (bez automatycznej instalacji).

## Najważniejsze funkcje

- Automatyczne wyszukiwanie co 2 godziny i filtrowanie filmów nie starszych niż 24 godziny.
- Wybieralna liga (np. `pLeague 3.31`), blokowanie części duplikatów i krótki komunikat o limicie 429.
- Przyciski Discord do PoB, Maxroll i Mobalytics, gdy w opisie filmu są odpowiednie adresy.
- Codzienne podsumowanie o 20:00 czasu polskiego oraz `pDigest` do podsumowania na żądanie.
- Lokalny licznik API, `pScan`, `pSearch`, `pLimit`, `pHealth`, `pBuilds`, `pSettings`.
- Lokalna retencja metadanych YouTube przez 7 dni. Wiadomości Discord nie są automatycznie usuwane.

## Szybka instalacja (Windows)

1. Pobierz ZIP i wypakuj, np. do `D:\\PoE-Bot`.
2. Otwórz CMD i wykonaj:

```bat
cd /d D:\\PoE-Bot
py -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

3. W `.env` uzupełnij **własny** `DISCORD_TOKEN`, `YOUTUBE_API_KEY` oraz `DISCORD_CHANNEL_ID`.
4. W Discord Developer Portal włącz `Message Content Intent` dla swojego bota.
5. Uruchom `python main.py` i na Discordzie użyj `pPrivacy`, `pAgree`, `pHealth`.

**GitHub Pages udostępnia stronę i pliki, ale nie hostuje uruchomionego bota.** Bot wymaga własnego komputera lub serwera.

## Bezpieczeństwo i odpowiedzialność

Nie udostępniaj `.env`, prawdziwego tokenu Discord, klucza YouTube API ani plików JSON z prywatnymi kluczami Google. Repozytorium zawiera wyłącznie oczyszczone pliki źródłowe i demonstracyjne wartości konfiguracyjne.

Projekt nie jest związany z Google, YouTube, Discord ani Grinding Gear Games. Nie stanowi potwierdzenia zgodności z YouTube API Services Policies. Zwłaszcza metadane pozostające w wiadomościach Discord wymagają odrębnej oceny.

[Kontakt i zgłaszanie problemów](https://github.com/Bollek231/poe-build-notifier-site/issues)

---

## English

**New in v0.6.0:** redesigned, animated GitHub Pages website with a cursor spotlight, drifting particles, ☀️/🌙 theme toggle, new Discord command preview, and consistent documentation styling. Bot runtime features are unchanged from v0.5.1.


**Current version: v0.6.1. Next update: v0.6.2.**


A non-commercial Discord bot that discovers fresh Path of Exile 1 builds using YouTube Data API v3 and posts links to the original videos.

### New in v0.6.1 — language selection and interactive settings

- **`pLanguage`**: Discord selection menu for **Polski / English**; alternatively use `pLanguage pl` or `pLanguage en`. The preference persists in SQLite across restarts.
- **`pSettings`**: interactive dropdown and modals to edit scan interval (1–24 h), digest schedule, result count, message delay, local YouTube budget, maximum video age (24 h), link validation/refresh, version alerts and GitHub version-check interval.
- Only the original administrator may edit from the configured channel after `pAgree`. Inputs are validated; tokens and channel IDs cannot be changed from Discord.
- Changes apply without restarting and preserve existing messages and PoE 1 / PoE 2 game settings.
- [Installation guide v0.6.1](bot/INSTRUKCJA_INSTALACJI_v0.6.1_PL_EN.md) · [Source code](bot/) · [Changelog](CHANGELOG.md)

## Website and documentation

- 🌐 **[Home](https://bollek231.github.io/poe-build-notifier-site/index-en.html)**
- 🛠️ **[Step-by-step installation](https://bollek231.github.io/poe-build-notifier-site/instalacja-en.html)**
- 💬 **[Features and commands](https://bollek231.github.io/poe-build-notifier-site/komendy-en.html)**
- 🔒 **[Privacy Policy](https://bollek231.github.io/poe-build-notifier-site/privacy-en.html)**
- 📄 **[Terms of Use](https://bollek231.github.io/poe-build-notifier-site/terms-en.html)**
- 📝 **[Patch Notes / Changelog](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html)**

### New in v0.6.0 — PoE 1 / PoE 2

The bot now supports **Path of Exile 1** and **Path of Exile 2**. PoE 2 defaults to **patch 1.0**, ahead of the announced December 11, 2026 PST release. Old 0.3/0.5 build videos are rejected.

| Command | Purpose |
|---|---|
| \`pGame\` | Show the active game and patch |
| \`pGame poe2\` | Switch to **PoE 2 1.0** |
| \`pGame poe1\` | Return to **PoE 1** and its saved league |
| \`pLeague 1.0\` | Select **PoE 2 version 1.0** |
| \`pScan\` | Scan YouTube for the selected game |
| \`pSearch Spark\` | Search builds for the selected game |

PoE 2 filtering requires explicit game and 1.0 evidence near the start of the video metadata, plus a build/guide title. The independent **24-hour publication-age limit** remains enforced. Each game has its own saved patch and filters. PoE 2 Mobalytics links (\`/poe-2/\`) are supported.

During upgrades, **copy the new \`game_modes.py\` file** alongside the existing source modules. Preserve your own \`.env\`, \`search_config.json\`, and \`poe330_seen.sqlite3\`. No new API keys are required.

### Download PoE Build Notifier v0.6.1

- 📦 **[Download the source ZIP](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.6.1.zip)**
- 🐍 **[Browse the source on GitHub](https://github.com/Bollek231/poe-build-notifier-site/tree/main/bot)**
- 📚 **[Bot source README (PL/EN)](bot/README.md)**

The archive contains `main.py`, `storage.py`, `features.py`, `enhancements.py`, `services.py`, `backups.py`, dependencies, sample configuration, and tests. **It does not contain real tokens, API keys, private .env files, or SQLite databases.**

### What's new in v0.5.1

- Smarter local YouTube search budgeting, query rotation and a reserve for manual commands.
- Creator blocklist/allowlist: `pBlockChannel`, `pAllowChannel`, `pWhitelist on/off`, `pChannelRules`, `pUnlistChannel`.
- Advanced build filters: `pFilters`, `pFilter skill Lightning Strike`, `pFilter mode SSF`, `pFilter class Ranger`, `pFilter stage starter`.
- Restricted PoB/Maxroll/Mobalytics URL checks and button completion for newly posted Discord messages via `pRefreshLinks`.
- Startup, reconnection and error alerts; private SQLite backups with `pBackup`.
- `pVersion` and new-release notifications (no automatic installations).

### Key features

- Automated searches every 2 hours; only videos published within the last 24 hours.
- Switchable target league (for example, `pLeague 3.31`), partial duplicate detection, and concise HTTP 429 quota warnings.
- Discord buttons for Path of Building, Maxroll, and Mobalytics when matching URLs are present in video descriptions.
- Daily digest at 8:00 PM Warsaw time, with `pDigest` for an on-demand summary.
- Local quota tracker and commands including `pScan`, `pSearch`, `pLimit`, `pHealth`, `pBuilds`, and `pSettings`.
- Locally cached YouTube metadata is deleted after 7 days. **Discord messages are not automatically removed.**

### Quick installation (Windows)

1. Download the ZIP and extract it, for example into `D:\PoE-Bot`.
2. Open Command Prompt and run:

```bat
cd /d D:\PoE-Bot
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
notepad .env
```

3. Add **your own** `DISCORD_TOKEN`, `YOUTUBE_API_KEY`, and `DISCORD_CHANNEL_ID` to `.env`.
4. Enable `Message Content Intent` for your Discord bot in the Discord Developer Portal.
5. Run `python main.py`. On Discord, start with `pPrivacy`, `pAgree`, and `pHealth`.

**GitHub Pages only hosts the website and files, not a running bot.** Run the bot on your own PC or server.

### Security and limitations

Do not publish `.env`, your Discord bot token, YouTube API key, or Google JSON private keys. This repository contains sanitized source code and example configuration only.

This project is not affiliated with Google, YouTube, Discord, or Grinding Gear Games. Its publication does not mean that YouTube has approved its compliance. In particular, keeping metadata in Discord messages for an extended period requires a separate review.

[Questions and issue reports](https://github.com/Bollek231/poe-build-notifier-site/issues)

