# PoE Build Notifier v0.6.2b — instalacja / installation

[🇵🇱 Polski](#polski) · [🇬🇧 English](#english)

## Polski

### 1. Pobierz i przygotuj Pythona

Zainstaluj **Python 3.11 lub nowszy** z [python.org](https://www.python.org/downloads/) i rozpakuj aktualny ZIP do np. `D:\PoE-Bot`. Upewnij się, że w folderze znajdują się `main.py`, `community.py`, `requirements.txt` oraz `.env.example`.

Otwórz **CMD** (Wiersz polecenia) i wpisz kolejno:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### 2. Utwórz bota Discord

W [Discord Developer Portal](https://discord.com/developers/applications) utwórz aplikację i bota. W zakładce **Bot** włącz **Message Content Intent**, następnie zaproś go na serwer z uprawnieniami do czytania, pisania i osadzania linków. Zapisz prywatnie **DISCORD_TOKEN**. Włącz w Discordzie Tryb dewelopera i skopiuj identyfikator docelowego kanału.

### 3. Przygotuj YouTube API

W [Google Cloud Console](https://console.cloud.google.com/) utwórz projekt, włącz **YouTube Data API v3** w Bibliotece interfejsów API, a w Dane logowania utwórz klucz API. Dla bezpieczeństwa ogranicz klucz do YouTube Data API v3.

### 4. Skonfiguruj `.env`

W CMD w folderze bota wykonaj:

```bat
copy .env.example .env
notepad .env
```

Wprowadź własne dane:

```dotenv
DISCORD_TOKEN=TWÓJ_TOKEN_BOTA
DISCORD_CHANNEL_ID=NUMERYCZNE_ID_KANAŁU
YOUTUBE_API_KEY=TWÓJ_KLUCZ_YOUTUBE
CHECK_INTERVAL_HOURS=2
MAX_VIDEO_AGE_HOURS=24
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

**Tłumaczenie tytułów na angielski (opcjonalne):** wybierz jeden z dwóch silników. Domyślnie tłumaczenie jest wyłączone i bot wyświetla oryginalny tytuł.

**MyMemory — darmowe, bez rozliczeń i bez klucza:**

```text
pTranslateTitles mymemory
pTranslateTitles status
```

Dla MyMemory **nie musisz** dodawać żadnego klucza ani karty. Usługa ogranicza anonimowe żądania do 5 000 znaków na dobę. Możesz opcjonalnie podać kontaktowy adres e-mail w swoim **prywatnym** `.env` (limit dostawcy 50 000 znaków na dobę):

```dotenv
TRANSLATION_PROVIDER=mymemory
MYMEMORY_CONTACT_EMAIL=twoj-adres@example.com
TRANSLATION_DAILY_LIMIT=30
```

Bot pilnuje własnego, niższego limitu bezpieczeństwa oraz nie wysyła treści opisów filmów. MyMemory wymaga znajomości języka źródłowego: biblioteka `langdetect` spróbuje wykryć go lokalnie; jeśli język jest nierozpoznany, bot pokaże oryginał.

**Google Cloud Translation Basic v2 — własny klucz API:**

Jeśli wolisz Google, włącz usługę Cloud Translation i rozliczenia w Google Cloud Console, utwórz klucz API oraz dopisz do prywatnego `.env`:

```dotenv
TRANSLATION_API_KEY=TWÓJ_KLUCZ_GOOGLE_TRANSLATION
TRANSLATION_PROVIDER=google
TRANSLATION_DAILY_LIMIT=30
```

Po uruchomieniu użyj `pTranslateTitles google`. Dostawcę możesz też wybrać w `pSettings` (pole **Silnik tłumaczeń**, wpisz `mymemory` albo `google`), a aktywować lub wyłączyć tłumaczenie przez `pTranslateTitles on/off`. Pamięć podręczna obu dostawców jest rozdzielona; oryginalny tytuł pozostaje dostępny.

### 5. Uruchom i skonfiguruj bota

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

Na swoim kanale Discorda kolejno wpisz `pPrivacy`, `pAgree`, `pHealth`, `pSetup`. Ustawienia można później zmienić przez `pSettings`. Nowe komendy: `pHelp`, `pQuietHours 23:00 08:00`, `pPause 6h`, `pResume`, `pSaved`, `pTrending`, `pTranslateTitles on/off`.

`pSaved` wysyła prywatną listę zakładek w DM; możesz usunąć je przez `pSaved clear`. `pTrending` wymaga dwóch pomiarów statystyk, więc pierwsze wywołanie ustala punkt odniesienia. Godziny ciszy są liczone według Warszawy.

### 6. Aktualizacja istniejącej instalacji

1. Zatrzymaj bota (`Ctrl + C`). Zrób kopię folderu i pliku SQLite `poe330_seen.sqlite3`.
2. Rozpakuj nowe ZIP do **oddzielnego** folderu. Skopiuj nowe pliki Pythona, w tym **`community.py` i `translation_providers.py`**, `requirements.txt` oraz `VERSION` do dotychczasowego folderu.
3. **Nie nadpisuj** własnego `.env`, `search_config.json`, bazy SQLite ani prywatnych kopii zapasowych.
4. W CMD wykonaj:

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

5. Na Discordzie sprawdź `pVersion`, `pHealth`, `pSetup` i `pHelp`.

### Typowe problemy

- **Bot nie reaguje:** sprawdź Message Content Intent, ID kanału i uprawnienia Zarządzanie serwerem.
- **Brak modułu Pythona:** aktywuj `.venv` i ponownie zainstaluj `requirements.txt`.
- **Brak wyników:** bot filtruje według gry, wersji i daty publikacji do 24 godzin.
- **Tłumaczenie nie działa:** sprawdź `pTranslateTitles status`. MyMemory wymaga rozpoznania języka, a Google poprawnego klucza i aktywnej usługi.
- **Brak prywatnej biblioteki:** włącz wiadomości prywatne od członków serwera Discorda.

---

## English

### 1. Install Python and extract the bot

Install **Python 3.11+** from [python.org](https://www.python.org/downloads/), and extract the ZIP into `D:\PoE-Bot` so that `main.py`, `community.py`, `requirements.txt` and `.env.example` are in that folder. In Windows CMD run:

```bat
cd /d D:\PoE-Bot
py --version
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### 2. Create a Discord bot and YouTube key

Create an application in [Discord Developer Portal](https://discord.com/developers/applications), enable **Message Content Intent**, invite the bot with read/send/embed permissions and copy its private token. Enable Developer Mode to copy your Discord channel ID.

In [Google Cloud Console](https://console.cloud.google.com/), enable **YouTube Data API v3** for your project and create an API key, restricting it to this service.

### 3. Configure `.env`

```bat
copy .env.example .env
notepad .env
```

Enter your own credentials:

```dotenv
DISCORD_TOKEN=YOUR_BOT_TOKEN
DISCORD_CHANNEL_ID=YOUR_NUMERIC_CHANNEL_ID
YOUTUBE_API_KEY=YOUR_YOUTUBE_KEY
CHECK_INTERVAL_HOURS=2
MAX_VIDEO_AGE_HOURS=24
TARGET_LEAGUE=3.30
POE2_TARGET_VERSION=1.0
```

**Optional English title translation:** select one provider. Translation is off by default, so the original title is published until you enable it.

**MyMemory — free, no API key or billing:**

```text
pTranslateTitles mymemory
pTranslateTitles status
```

Anonymous use is limited to 5,000 characters per day by MyMemory. An optional contact email can raise its allowance to 50,000 characters/day. Only add this in your **private** `.env`, never to GitHub:

```dotenv
TRANSLATION_PROVIDER=mymemory
MYMEMORY_CONTACT_EMAIL=your-address@example.com
TRANSLATION_DAILY_LIMIT=30
```

The bot enforces its own conservative limits. MyMemory requires a source language; `langdetect` attempts to identify it locally. If detection fails, the original title is sent.

**Google Cloud Translation Basic v2 — your own key:**

Enable Google Cloud Translation and billing, create an API key, then set:

```dotenv
TRANSLATION_API_KEY=YOUR_TRANSLATION_KEY
TRANSLATION_PROVIDER=google
TRANSLATION_DAILY_LIMIT=30
```

Use `pTranslateTitles google` after restarting. Select `mymemory` or `google` using `pSettings` (Translation provider), or use `pTranslateTitles on/off` to toggle translations. Provider caches are kept separately; the original title is always available.

### 4. Start and use the bot

```bat
cd /d D:\PoE-Bot
.venv\Scripts\activate
python main.py
```

On Discord use `pPrivacy`, `pAgree`, `pHealth`, then `pSetup`. Other commands include `pHelp`, `pQuietHours 23:00 08:00`, `pPause 6h`, `pResume`, `pSaved`, `pTrending`, and `pTranslateTitles on/off`. Saved bookmarks are sent by DM. A first `pTrending` run only records the baseline.

### 5. Upgrade safely

Stop the bot with **Ctrl + C** and back up the installation directory and SQLite database. Extract the new ZIP separately. Copy all new Python modules (including **`community.py` and `translation_providers.py`**), `requirements.txt` and `VERSION` into the existing folder. **Do not replace** your personal `.env`, custom `search_config.json`, SQLite database or backups. Activate `.venv`, rerun `python -m pip install -r requirements.txt` and start `python main.py`.

If the bot doesn't respond, check Message Content Intent and the configured channel. If Python modules are missing, reactivate `.venv` and reinstall requirements. If translations are unavailable, check `pTranslateTitles status`, MyMemory language detection or the Google Cloud API key and billing.
