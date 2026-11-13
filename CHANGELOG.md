# PoE Build Notifier — Changelog / Lista zmian

**Current version / Aktualna wersja:** `v0.5.1`  
**Versioning / Wersjonowanie:** `vMAJOR.MINOR.PATCH`; starting from `v0.5.0`, each subsequent project update increments the final number (`v0.5.2`, `v0.5.3`, etc.). Every update must have a new entry here and on both GitHub Pages changelog pages.

[🇵🇱 Lista zmian (GitHub Pages)](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [🇬🇧 Patch Notes (GitHub Pages)](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html)

---

## 🇵🇱 Polski

### v0.5.1 — 13 listopada 2026

**Nowe funkcje:**
- Inteligentne planowanie zużycia lokalnej puli YouTube Search API, rotacja fraz i rezerwa na ręczne wyszukiwania (bez udawania oficjalnego licznika Google).
- Czarna i biała lista kanałów: `pBlockChannel`, `pAllowChannel`, `pUnlistChannel`, `pChannelRules`, `pWhitelist on/off`.
- Rozszerzone filtry buildów: skill, ascendancy, klasa, tryb SSF/HC/SC i etap (starter/endgame/leveling).
- Walidacja linków HTTPS PoB/Maxroll/Mobalytics, bez śledzenia przekierowań; odrzucanie HTTP 404/410, tolerowanie przejściowych problemów 403/timeout.
- Automatyczne uzupełnianie przycisków po zmianie opisu YouTube poprzez **edycję** istniejących wiadomości. Dotyczy tylko wiadomości wysłanych od v0.5.1 i rejestrowanych maksymalnie 7 dni.
- Ograniczane częstotliwością alerty o uruchomieniu, odzyskaniu połączenia, błędach i aktualizacjach; opcjonalny kanał administracyjny.
- Codzienne prywatne kopie bazy SQLite z rotacją (domyślnie 7 plików), komenda `pBackup`. Tokenów z `.env` nie kopiuje.
- Komenda `pVersion` i okresowe sprawdzanie publicznego pliku `VERSION` na GitHubie, bez automatycznego instalowania aktualizacji.

**Zachowane funkcje:** pScan, pSearch, pLimit, pHealth, pLeague, pDigest, podsumowanie 20:00, wiek filmów 24 h, skan co 2 h, odstęp 3 s, wykrywanie duplikatów, przyciski buildów, wstrzymywanie wyszukiwań po 429, czyszczenie lokalnych metadanych po 7 dniach oraz **brak automatycznego usuwania wiadomości Discord**.

**Bezpieczeństwo i wydanie:** dodano migrację SQLite bez usuwania starych danych, testy offline, instrukcję PL/EN i oczyszczoną paczkę `PoE_Build_Notifier_v0.5.1.zip`. Uwaga: kopie zapasowe zawierają lokalną bazę i powinny pozostawać prywatne.

### v0.5.0 — 13 listopada 2026

**Nowości i zmiany w tej aktualizacji dokumentacji**
- Wprowadzenie numerowania wersji projektu od **PoE Build Notifier v0.5.0**.
- Dodanie dwujęzycznej zakładki **Lista zmian / Patch Notes** na GitHub Pages wraz z przełączaniem 🇵🇱 / 🇬🇧.
- Dodanie tego pliku `CHANGELOG.md` w repozytorium, który będzie aktualizowany przy kolejnych wydaniach.
- Ujednolicenie numeru wersji w witrynie i dokumentacji na GitHubie.

**Funkcje obecne w wersji bazowej v0.5.0 (dodane wcześniej)**
- Wyszukiwanie filmów Path of Exile 1 co 2 godziny, filtrowanie materiałów do 24 godzin i wybranej ligi.
- Komenda `pLeague` do zmiany ligi, ręczne skanowanie `pScan` i wyszukiwanie `pSearch`.
- Przyciski PoB, Maxroll i Mobalytics, gdy odpowiedni odnośnik znajduje się w opisie filmu.
- Dzienne podsumowanie buildów o 20:00 czasu polskiego oraz `pDigest`.
- Blokowanie kolejnych wyszukiwań po osiągnięciu limitu YouTube API i zwięzły komunikat o resecie.
- Weryfikacja duplikatów, 3-sekundowy odstęp między wiadomościami.
- Usuwanie lokalnych metadanych YouTube po 7 dniach, bez automatycznego usuwania wiadomości Discord.
- Publiczny kod źródłowy bez prywatnych tokenów, instrukcja instalacji i dwujęzyczna strona WWW.

> Ta wersja rozpoczyna historię numerowanych zmian. Wcześniejsze aktualizacje nie mają retrospektywnie przypisanych numerów.

---

## 🇬🇧 English

### v0.5.1 — November 13, 2026

**New features:**
- Smart, local YouTube Search API budget allocation across scheduled scans, rotating query phrases and reserving calls for manual searches. Not an official Google quota reading.
- YouTube channel blocklist and allowlist: `pBlockChannel`, `pAllowChannel`, `pUnlistChannel`, `pChannelRules`, and `pWhitelist on/off`.
- Advanced build filters for skill, ascendancy, base class, SSF/HC/SC mode, and starter/endgame/leveling stage.
- Restricted HTTPS verification of PoB/Maxroll/Mobalytics links; no redirect following, reject confirmed 404/410, tolerate temporary 403/timeouts.
- Automatic button completion when YouTube creators update video descriptions, using **Discord message edits**, never deleting or reposting messages. Tracks only posts created by v0.5.1 and keeps tracking metadata up to 7 days.
- Rate-limited startup, reconnection, error, and update alerts, with an optional separate admin channel.
- Daily private SQLite snapshots with rotation (7 by default) and the `pBackup` command. Never backs up `.env`.
- `pVersion` and periodic checks of the public GitHub `VERSION` file, without installing updates automatically.

**Retained features:** pScan, pSearch, pLimit, pHealth, pLeague, pDigest, 8 PM Warsaw daily summary, 24-hour video age limit, searches every 2 hours, 3-second post delays, duplicate filtering, guide buttons, 429 search pause, 7-day local YouTube cache cleanup, and **no automatic deletion of Discord posts**.

**Security and distribution:** additive SQLite migration, offline tests, PL/EN installation instructions and sanitized `PoE_Build_Notifier_v0.5.1.zip`. Private backups contain local database records and must never be published.

### v0.5.0 — November 13, 2026

**New in this documentation update**
- Introduced project versioning, starting with **PoE Build Notifier v0.5.0**.
- Added bilingual **Changelog / Patch Notes** pages to GitHub Pages, with 🇵🇱 / 🇬🇧 switching.
- Created this repository-level `CHANGELOG.md` to record all future updates.
- Made the version number consistent across the website and GitHub documentation.

**Features already present in the v0.5.0 baseline (implemented earlier)**
- Automated Path of Exile 1 build discovery every 2 hours, 24-hour publication-age filtering, target league filtering.
- `pLeague` command to switch leagues, manual `pScan` and `pSearch`.
- PoB, Maxroll, and Mobalytics buttons for URLs found in video descriptions.
- Daily digest at 8:00 PM Warsaw time and an on-demand `pDigest` command.
- YouTube API quota pause and concise reset-time notification.
- Duplicate filtering and a 3-second delay between posted notifications.
- Seven-day cleanup of locally cached YouTube metadata, with no automatic deletion of Discord messages.
- Public sanitized source code, installation guide, and bilingual website.

> This is the beginning of numbered release history. Earlier changes have not been retroactively assigned versions.
