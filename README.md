# PoE Build Notifier v0.5.0 — PL 🇵🇱 / EN 🇬🇧

**Wybierz język / Choose language:** [🇵🇱 Polski](#polski) · [🇬🇧 English](#english)

## Polski

**Aktualna wersja: v0.5.0. Następna aktualizacja: v0.5.1.**


Niekomercyjny projekt bota Discord, który wyszukuje nowe buildy Path of Exile 1 przez YouTube Data API v3 i publikuje linki do oryginalnych filmów.

## Strona i dokumentacja

- 🌐 **[Strona główna](https://bollek231.github.io/poe-build-notifier-site/index.html)**
- 🛠️ **[Instalacja krok po kroku](https://bollek231.github.io/poe-build-notifier-site/instalacja.html)**
- 💬 **[Działanie i komendy](https://bollek231.github.io/poe-build-notifier-site/komendy.html)**
- 🔒 **[Polityka prywatności](https://bollek231.github.io/poe-build-notifier-site/privacy.html)**
- 📄 **[Warunki korzystania](https://bollek231.github.io/poe-build-notifier-site/terms.html)**
- 📝 **[Lista zmian / Patch Notes](https://bollek231.github.io/poe-build-notifier-site/changelog.html)**

## Pobierz PoE Build Notifier v0.5.0

- 📦 **[Pobierz paczkę ZIP z kodem](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.5.0.zip)**
- 🐍 **[Przejrzyj kod źródłowy na GitHubie](https://github.com/Bollek231/poe-build-notifier-site/tree/main/bot)**
- 📚 **[README kodu bota](bot/README.md)**

Archiwum zawiera pliki `main.py`, `storage.py`, `features.py`, zależności, przykładową konfigurację i testy. **Nie zawiera prywatnych tokenów, kluczy API, plików .env ani bazy SQLite.**

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

**Current version: v0.5.0. Next update: v0.5.1.**


A non-commercial Discord bot that discovers fresh Path of Exile 1 builds using YouTube Data API v3 and posts links to the original videos.

### Website and documentation

- 🌐 **[Home](https://bollek231.github.io/poe-build-notifier-site/index-en.html)**
- 🛠️ **[Step-by-step installation](https://bollek231.github.io/poe-build-notifier-site/instalacja-en.html)**
- 💬 **[Features and commands](https://bollek231.github.io/poe-build-notifier-site/komendy-en.html)**
- 🔒 **[Privacy Policy](https://bollek231.github.io/poe-build-notifier-site/privacy-en.html)**
- 📄 **[Terms of Use](https://bollek231.github.io/poe-build-notifier-site/terms-en.html)**
- 📝 **[Patch Notes / Changelog](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html)**

### Download PoE Build Notifier v0.5.0

- 📦 **[Download the source ZIP](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_v0.5.0.zip)**
- 🐍 **[Browse the source on GitHub](https://github.com/Bollek231/poe-build-notifier-site/tree/main/bot)**
- 📚 **[Bot source README (PL/EN)](bot/README.md)**

The archive contains `main.py`, `storage.py`, `features.py`, dependencies, sample configuration, and tests. **It does not contain real tokens, API keys, private .env files, or SQLite databases.**

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

