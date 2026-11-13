# PoE Build Notifier — Changelog / Lista zmian

**Current version / Aktualna wersja:** `v0.6.1`  
**Versioning / Wersjonowanie:** `vMAJOR.MINOR.PATCH`; starting from `v0.5.0`, each subsequent project update increments the final number (`v0.6.2`, `v0.6.3`, etc.). Every update must have a new entry here and on both GitHub Pages changelog pages.

[🇵🇱 Lista zmian (GitHub Pages)](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [🇬🇧 Patch Notes (GitHub Pages)](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html)

---

## 🇵🇱 Polski

### v0.6.1 — 13 listopada 2026

**Nowości**
- Komenda **`pLanguage`** z interaktywnym menu wyboru polskiego lub angielskiego (także `pLanguage pl` i `pLanguage en`).
- Tłumaczenia odpowiedzi komend, komunikatów i pól powiadomień na język angielski; oryginalne tytuły YouTube pozostają bez zmian.
- Przebudowana **`pSettings`**: rozwijana lista ustawień, formularze Discorda i przełączanie opcji tak/nie.
- Edycja zakresów: skanowanie 1–24 h, godzina digestu, liczba wyników, odstęp wiadomości, budżet YouTube, filtry wieku ≤24 h, odświeżanie linków, kontrole linków i sprawdzanie wersji co 1–72 h.
- Zapis zmian w istniejącej tabeli SQLite `bot_settings`, walidacja danych, kontrola uprawnień i automatyczne zastosowanie zmian bez restartu.
- Zachowanie pełnej obsługi PoE 1 / PoE 2 1.0, poprzednich ustawień i wiadomości Discord.
- Nowe testy bezpieczeństwa i trwałości konfiguracji — **67 testów offline, 32 podtesty**.

### v0.6.0 — 13 listopada 2026

**Obsługa Path of Exile 2 — gotowość na wydanie 1.0**
- **`pGame poe1` / `pGame poe2`**: przełączanie wyszukiwanej gry bez restartowania bota.
- Dla PoE 2 domyślną wersją jest **1.0** (zapowiedziana premiera: 11 grudnia 2026 PST). PoE 1 pozostaje domyślnie na dotychczasowej lidze.
- Oddzielne ustawienia wersji obu gier w istniejącej bazie SQLite: `pLeague` działa dla aktualnej gry, a poprzednia wersja drugiej gry jest zapamiętana.
- Nowe frazy YouTube: `Path of Exile 2 1.0 build guide`, `PoE2 1.0 league starter build`, `PoE 2 1.0 leveling build`, `PoE2 1.0 bossing build` i inne.
- PoE 2 wymaga wyraźnego potwierdzenia **gry i wersji 1.0** w tytule albo na początku opisu oraz poradnikowej tematyki w tytule.
- Wykluczanie filmów oznaczonych starymi wersjami, np. **0.3 / 0.5 / 0.5.5**, i filmów o wiadomościach lub patch notes.
- Zachowany **limit 24 godzin od publikacji**, dodatkowe sprawdzanie daty lokalnie, budżet API i zabezpieczenie 429.
- Oddzielne filtry buildów i osobne zapamiętywanie dziennych podsumowań dla każdej gry.
- Obsługa linków Mobalytics **`/poe-2/`**.
- Zachowane wcześniejsze funkcje, kopie SQLite, przyciski, 7-dniowe czyszczenie lokalnych danych; **wiadomości Discord nie są usuwane automatycznie**.

**Uwaga:** ta wersja świadomie pomija nieoznaczone 1.0 poradniki, aby nie publikować starszych buildów. Nie była testowana z prywatnym tokenem Discord ani realnym kluczem YouTube.

### v0.5.2 — 13 listopada 2026

**Przeprojektowanie GitHub Pages — Dark Fantasy / Modern Gaming**
- Całkowicie odświeżona strona główna: duża sekcja powitalna, animowany symbol, karty funkcji i podgląd przykładowych wiadomości Discorda.
- **Animowane tło** z unoszącymi się cząsteczkami, delikatnie przemieszczającymi się gwiazdami i poświatą pod kursorem.
- **Przełącznik ☀️/🌙** do wyboru jasnego lub ciemnego motywu z zapamiętywaniem ustawienia w przeglądarce.
- Ujednolicony wygląd wszystkich stron: instalacja, komendy, prywatność, regulamin i Patch Notes w języku polskim i angielskim.
- Mobilne menu i ustawienia dostępności: automatyczne ograniczenie animacji przy `prefers-reduced-motion`, wstrzymanie ruchu kart przy ukrytej karcie przeglądarki.
- Wydanie oczyszczonego ZIP-a **PoE_Build_Notifier_v0.5.2.zip** z aktualnym numerem wersji. **Funkcje działającego bota pozostały bez zmian względem v0.5.1.**


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

### v0.6.1 — November 13, 2026

**New features**
- **`pLanguage`**: interactive Polish/English dropdown, plus direct `pLanguage pl` and `pLanguage en`.
- English-language command responses, status alerts, embed field labels and digests; original YouTube titles stay unchanged.
- Redesigned **`pSettings`**: interactive select, Discord modal input forms, and one-click on/off toggles.
- Safe settings for scan frequency (1–24 h), digest time, result count, posting delay, daily local YouTube budget, max video age (≤24 h), link verification/refresh, and version checks (1–72 h).
- SQLite `bot_settings` persistence, strict validation, administrative access checks, and immediate application without a restart.
- Full backwards compatibility with PoE 1 / PoE 2 1.0 modes, previous preferences, and existing Discord messages.
- **67 offline tests and 32 subtests** passing.

### v0.6.0 — November 13, 2026

**Path of Exile 2 support — targeting the 1.0 release**
- **`pGame poe1` / `pGame poe2`** switches the target game without a bot restart.
- PoE 2 targets **version 1.0** by default, ahead of its announced December 11, 2026 PST release. PoE 1 retains its previous league.
- Per-game versions stored separately in the existing SQLite database; `pLeague` applies to the selected game.
- Dedicated PoE 2 queries: `Path of Exile 2 1.0 build guide`, `PoE2 1.0 league starter build`, `PoE 2 1.0 leveling build` and more.
- PoE 2 videos must clearly identify both **PoE 2 and 1.0** near the start of the title/description and contain build/guide evidence in the title.
- Rejects older patch labels, including **0.3 / 0.5 / 0.5.5**, and generic patch-note/news material.
- Retains the independent **24-hour published-age window**, YouTube API quota protection and 429 pause.
- Separate advanced filters and daily digest bookkeeping for the active game.
- Mobalytics **`/poe-2/`** guide links are recognized.
- All previous features retained; local YouTube metadata is cleaned after 7 days and **Discord messages are not automatically deleted**.

**Note:** intentionally conservative 1.0 detection may skip unversioned but otherwise valid guides. Not tested with real Discord or YouTube credentials.

### v0.5.2 — November 13, 2026

**GitHub Pages redesign — Dark Fantasy / Modern Gaming**
- Rebuilt landing page with a prominent hero, animated emblem, feature cards, and simulated Discord messages.
- **Animated background** featuring gently drifting particles, moving stars, and a cursor-following glow.
- **☀️/🌙 theme toggle** with persistent light/dark preference in the browser.
- Consistent design across installation, commands, privacy, terms, and patch notes pages in both Polish and English.
- Responsive mobile navigation and accessibility: animations respect `prefers-reduced-motion` and pause when the tab is hidden.
- Published sanitized **PoE_Build_Notifier_v0.5.2.zip** with refreshed version metadata. **Bot runtime functionality is unchanged from v0.5.1.**


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
