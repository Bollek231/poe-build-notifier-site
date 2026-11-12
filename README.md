# PoE Build Notifier — Discord bot do Path of Exile 1

Niekomercyjny projekt bota Discord, który wyszukuje nowe buildy Path of Exile 1 przez YouTube Data API v3 i publikuje linki do oryginalnych filmów.

## Strona i dokumentacja

- 🌐 **[Strona główna](https://bollek231.github.io/poe-build-notifier-site/index.html)**
- 🛠️ **[Instalacja krok po kroku](https://bollek231.github.io/poe-build-notifier-site/instalacja.html)**
- 💬 **[Działanie i komendy](https://bollek231.github.io/poe-build-notifier-site/komendy.html)**
- 🔒 **[Polityka prywatności](https://bollek231.github.io/poe-build-notifier-site/privacy.html)**
- 📄 **[Warunki korzystania](https://bollek231.github.io/poe-build-notifier-site/terms.html)**

## Pobierz bota

- 📦 **[Pobierz paczkę ZIP z kodem](https://bollek231.github.io/poe-build-notifier-site/downloads/PoE_Build_Notifier_BEZ_DANYCH.zip)**
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
