# PoE Build Notifier — Lista zmian / Patch Notes

**Aktualna wersja / Current version:** `v0.6.4c`

[🇵🇱 Lista zmian — strona](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [🇬🇧 Patch Notes — website](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html)

---

## 🇵🇱 Polski

### v0.6.4c — 13 listopada 2026
- Dodano przycisk **PoE Planner** w powiadomieniach o strategiach farmienia, gdy opis filmu YouTube zawiera link do `https://poeplanner.com` lub `https://www.poeplanner.com`.
- Rozszerzono weryfikację bezpiecznych odnośników i automatyczne odświeżanie przycisków o domenę PoE Planner; odrzucone są podszywające się domeny i niebezpieczne adresy.


### v0.6.4b — 13 listopada 2026
- `pScan` oraz `pFarmScan`: dodano opcjonalną liczbę nowych filmów do opublikowania, np. `pScan 1`, `pScan 2`, `pFarmScan 1` lub `pFarmScan 2`.
- Komendy bez liczby nadal wykonują pełny ręczny skan; podana liczba ogranicza liczbę zaakceptowanych filmów, a nie liczbę zapytań do YouTube API.
- Dodano walidację zakresu **1–25** i ograniczenie również dla filmów odkładanych w kolejce podczas ciszy nocnej.
- Podsumowanie ręcznego skanowania pokazuje także liczbę poradników dodanych do kolejki ciszy nocnej.


### v0.6.4 — 13 listopada 2026
- Dodano wyszukiwanie poradników o strategiach farmienia waluty w PoE 1 i PoE 2: `pFarmScan` oraz `pFarmSearch KATEGORIA`.
- Dodano `pFarmTopics` (lista kategorii), `pFarmRecent` (ostatnie strategie) oraz `pFarmAuto on/off/status` (dobrowolny monitoring).
- Rozpoznawanie kategorii m.in. Essence, Harvest, Expedition, Atlas, Delirium, Breach, Ritual, Legion, Blight, Heist, Sanctum, boss farming, crafting i trading.
- Strategie są filtrowane według wersji gry i daty publikacji, zapisywane osobno od buildów oraz uwzględniane w ciszy nocnej.
- Automatyczny monitoring jest domyślnie wyłączony; po włączeniu wykonuje maksymalnie jedno dodatkowe wyszukiwanie na interwał, dzieląc budżet YouTube API z buildami. Opcjonalny osobny kanał: `FARM_CHANNEL_ID`.


### v0.6.3 — 13 listopada 2026
- Dodano desktopowy launcher Windows z uruchamianiem bota bez ręcznych komend CMD, przyciskami start/stop i podglądem logów.
- Dodano sprawdzanie aktualizacji przy uruchomieniu, pobieranie wersji z konkretnego commita GitHuba, automatyczną instalację i restart launchera.
- Aktualizator tworzy kopie zastępowanych plików, przywraca je po błędzie i nie nadpisuje prywatnego `.env`, bazy SQLite ani konfiguracji użytkownika.
- Dodano skróty startowe `.bat` i `.vbs` oraz automatyczne tworzenie testowanej paczki ZIP.


### v0.6.2b — 13 listopada 2026
- **`pTranslateTitles`:** dodano wybór **MyMemory** (bez klucza API i rozliczeń) lub **Google Cloud Translation** (z własnym kluczem).
- Przełączanie silnika przez `pTranslateTitles mymemory`, `pTranslateTitles google` lub `pSettings`, z zapisaniem wyboru w SQLite.
- Lokalne wykrywanie języka źródłowego dla MyMemory, ograniczenie liczby zapytań i znaków oraz niezależne pamięci podręczne tłumaczeń.
- Dostosowano `pVersion` do rozpoznawania wersji z końcówką literową, np. `0.6.2b`.

### v0.6.2 — 13 listopada 2026
- **`pSetup`:** kreator wyboru gry, wersji, języka i interwału z potwierdzeniem zmian.
- **`pHelp`:** interaktywne menu kategorii komend Discorda.
- **`pQuietHours`:** przedział ciszy według czasu Warszawa, kolejka nowych poradników i podsumowanie po zakończeniu.
- **`pPause` / `pResume`:** czasowe lub bezterminowe zatrzymywanie automatycznych skanów.
- **`pSaved`:** zapisywanie filmów przyciskiem i prywatna lista zakładek użytkownika.
- **`pTrending`:** ranking ostatnich buildów według tempa przyrostu wyświetleń.
- **`pTranslateTitles`:** opcjonalne angielskie tłumaczenia tytułów przez Google Cloud Translation Basic v2, z zachowaniem oryginału, limitem wywołań i pamięcią podręczną.


### v0.6.1 — 13 listopada 2026
- **`pLanguage`:** wybór języka polskiego lub angielskiego w menu Discorda; również `pLanguage pl` i `pLanguage en`.
- Angielskie tłumaczenia odpowiedzi bota, alertów i elementów powiadomień.
- **`pSettings`:** interaktywny panel z listą ustawień, formularzami i przełącznikami.
- Edycja interwału skanowania, godziny podsumowania, wyników wyszukiwania, limitów zapytań, opóźnienia wiadomości, wieku filmów, odświeżania linków i sprawdzania wersji.
- Walidacja wartości i uprawnień; trwały zapis ustawień i języka w SQLite oraz zastosowanie zmian bez restartu.

### v0.6.0 — 13 listopada 2026
- **`pGame poe1` / `pGame poe2`:** wybór gry do automatycznych i ręcznych wyszukiwań.
- Osobna wersja i filtry dla każdej gry, zapisywane w SQLite.
- Wyszukiwanie PoE 2 domyślnie pod **1.0** z dedykowanymi frazami i odrzucaniem poradników do starszych wersji.
- Niezależna weryfikacja wieku publikacji filmu (maksymalnie 24 godziny).
- Rozpoznawanie linków Mobalytics dla PoE 2 (`/poe-2/`).

### v0.5.2 — 13 listopada 2026
- Nowy wygląd GitHub Pages w stylu dark fantasy.
- Animowane tło z cząsteczkami, efektem światła przy kursorze i obracającym się symbolem.
- Przełącznik jasnego/ciemnego motywu ☀️/🌙, układ mobilny i interaktywny podgląd komend.
- Ujednolicenie wyglądu polskich i angielskich podstron.

### v0.5.1 — 13 listopada 2026
- Inteligentniejsze planowanie lokalnego budżetu YouTube API i rotacja wyszukiwanych fraz.
- Czarna i biała lista kanałów: `pBlockChannel`, `pAllowChannel`, `pWhitelist`.
- Filtry buildów według skilla, klasy, ascendancy, trybu i etapu rozgrywki.
- Sprawdzanie linków PoB, Maxroll i Mobalytics.
- Uzupełnianie przycisków do buildów po edycji opisów filmów, przez aktualizację wiadomości Discord.
- Alerty o starcie i problemach z połączeniem oraz prywatne kopie zapasowe SQLite.
- **`pVersion`:** sprawdzanie nowej wersji na GitHubie i powiadomienia o aktualizacjach.

### v0.5.0 — 13 listopada 2026
- Uruchomienie dwujęzycznej witryny i dokumentacji.
- Dodanie publicznego `CHANGELOG.md` oraz stron Lista zmian / Patch Notes.

---

## 🇬🇧 English

### v0.6.4c — November 13, 2026
- Added a **PoE Planner** button to currency-farming notifications when a YouTube video description links to `https://poeplanner.com` or `https://www.poeplanner.com`.
- Extended safe-link validation and automatic button refresh to PoE Planner, rejecting lookalike domains and unsafe URLs.


### v0.6.4b — November 13, 2026
- `pScan` and `pFarmScan` now accept an optional cap on newly posted videos, such as `pScan 1`, `pScan 2`, `pFarmScan 1`, or `pFarmScan 2`.
- Commands without a number keep their full manual-scan behavior; the number limits eligible videos, not YouTube API search requests.
- Added **1–25** count validation; the cap also applies to videos queued during quiet hours.
- Manual scan summaries now also show how many videos were queued due to quiet hours.


### v0.6.4 — November 13, 2026
- Added separate currency-farming strategy searches for PoE 1 and PoE 2: `pFarmScan` and `pFarmSearch TOPIC`.
- Added `pFarmTopics` (categories), `pFarmRecent` (recent strategies), and opt-in `pFarmAuto on/off/status` monitoring.
- Recognizes Essence, Harvest, Expedition, Atlas, Delirium, Breach, Ritual, Legion, Blight, Heist, Sanctum, boss farming, crafting and trading.
- Strategies are filtered by game version and publish date, stored separately from build guides, and grouped during quiet hours.
- Automatic monitoring is off by default; when enabled it performs at most one additional query per scan interval within the shared YouTube API budget. Optional dedicated channel: `FARM_CHANNEL_ID`.


### v0.6.3 — November 13, 2026
- Added a Windows desktop launcher to start/stop the bot without typing CMD commands, including a log viewer.
- Added startup update checks, immutable GitHub commit downloads, automatic installation and launcher restart.
- The updater backs up replaced program files, rolls them back on failure, and leaves private `.env`, SQLite and user configuration untouched.
- Added `.bat` and `.vbs` launch shortcuts and an automated, tested ZIP packaging workflow.


### v0.6.2b — November 13, 2026
- **`pTranslateTitles`:** choose **MyMemory** (no API key or billing) or **Google Cloud Translation** (bring your own API key).
- Select the provider using `pTranslateTitles mymemory`, `pTranslateTitles google`, or `pSettings`, saved in SQLite.
- Local source-language detection for MyMemory, request/character caps and provider-specific translation caches.
- **`pVersion`** recognizes alphabetic version suffixes such as `0.6.2b`.

### v0.6.2 — November 13, 2026
- **`pSetup`:** interactive setup of game, patch, language and scan interval with confirmation.
- **`pHelp`:** interactive Discord command categories.
- **`pQuietHours`:** Warsaw-time quiet window, deferred build queue and a digest after quiet hours.
- **`pPause` / `pResume`:** temporary or indefinite pause for scheduled scanning.
- **`pSaved`:** bookmark buttons and private, user-owned saved video links.
- **`pTrending`:** recent build ranking by growth in YouTube views between observations.
- **`pTranslateTitles`:** optional English title translation via Google Cloud Translation Basic v2, with originals, caching and request caps.


### v0.6.1 — November 13, 2026
- **`pLanguage`:** Discord menu to switch between Polish and English; also `pLanguage pl` and `pLanguage en`.
- English translations for command responses, alerts and build notification labels.
- **`pSettings`:** interactive settings panel with dropdowns, forms and toggles.
- Editing scan intervals, digest time, results per query, search budget, posting delay, video age, link refresh and GitHub version checks.
- Input and permission validation, persistent language and settings in SQLite, and updates applied without restarting.

### v0.6.0 — November 13, 2026
- **`pGame poe1` / `pGame poe2`:** switch games for manual and scheduled searches.
- Separate per-game patch targets and build filters stored in SQLite.
- PoE 2 searches target **patch 1.0** by default with dedicated phrases and older-patch exclusions.
- Independent 24-hour video publication-age validation.
- Support for Mobalytics PoE 2 links (`/poe-2/`).

### v0.5.2 — November 13, 2026
- Redesigned GitHub Pages with a dark-fantasy aesthetic.
- Animated particles, cursor glow and rotating emblem.
- ☀️/🌙 light/dark theme switching, responsive layout and an interactive command preview.
- Consistent styling across the Polish and English pages.

### v0.5.1 — November 13, 2026
- Smarter local YouTube quota planning and query rotation.
- Creator blocklists and allowlists: `pBlockChannel`, `pAllowChannel`, `pWhitelist`.
- Advanced skill, class, ascendancy, game-mode and progression-stage filters.
- Validation for PoB, Maxroll and Mobalytics URLs.
- Editing previously posted Discord messages to add newly available build buttons.
- Startup and connection alerts, plus private SQLite backups.
- **`pVersion`:** GitHub version checks and release notifications.

### v0.5.0 — November 13, 2026
- Introduced the bilingual website and documentation.
- Added the repository `CHANGELOG.md` and bilingual Patch Notes pages.
