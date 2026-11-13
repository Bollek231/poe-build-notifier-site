# PoE Build Notifier — Lista zmian / Patch Notes

**Aktualna wersja / Current version:** `v0.6.2b`

[🇵🇱 Lista zmian — strona](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [🇬🇧 Patch Notes — website](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html)

---

## 🇵🇱 Polski

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
