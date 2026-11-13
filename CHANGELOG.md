# PoE Build Notifier — Changelog / Lista zmian

**Current version / Aktualna wersja:** `v0.5.0`  
**Versioning / Wersjonowanie:** `vMAJOR.MINOR.PATCH`; starting from `v0.5.0`, each subsequent project update increments the final number (`v0.5.1`, `v0.5.2`, etc.). Every update must have a new entry here and on both GitHub Pages changelog pages.

[🇵🇱 Lista zmian (GitHub Pages)](https://bollek231.github.io/poe-build-notifier-site/changelog.html) · [🇬🇧 Patch Notes (GitHub Pages)](https://bollek231.github.io/poe-build-notifier-site/changelog-en.html)

---

## 🇵🇱 Polski

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
