# NFJ-LLM-JobFinder

> Scraper ofert pracy z [NoFluffJobs](https://nofluffjobs.com) oparty na **Playwright** z technikami anty-botowymi, przygotowany pod dalsze przetwarzanie przez LLM.

---

## Struktura projektu

```
NFJ-LLM-JobFinder/
├── .env                  # zmienne środowiskowe (z .env.example)
├── .env.example          # szablon konfiguracji
├── pyproject.toml        # zależności i konfiguracja (uv)
├── data/
│   └── jobs_links.json   # wynik scrapowania (tworzony automatycznie)
├── src/
│   └── nofluffjobs_llm_matcher/
│       ├── config.py         # wczytywanie konfiguracji z .env
│       ├── main.py           # punkt wejścia CLI
│       ├── scraper/
│       │   ├── browser.py    # Playwright + stealth + anty-bot
│       │   ├── pagination.py # obsługa "Pokaż kolejne oferty"
│       │   └── links.py      # zbieranie href z nfj-postings-list
│       └── storage/
│           └── writer.py     # zapis do JSON / CSV
└── tests/
    └── test_links.py         # testy jednostkowe parsowania linków
```

---

## Instalacja

```bash
# 1. Sklonuj repozytorium
git clone <repo-url>
cd NFJ-LLM-JobFinder

# 2. Zainstaluj zależności (uv)
uv sync

# 3. Zainstaluj przeglądarki Playwright
uv run playwright install chromium

# 4. Skopiuj i dostosuj konfigurację
copy .env.example .env
```

---

## Użycie

```bash
# Scrapuj oferty (headless, wynik w data/jobs_links.json)
uv run nfj-matcher scrape

# Widzialna przeglądarka (debugowanie)
uv run nfj-matcher scrape --no-headless

# Własna ścieżka wyjściowa
uv run nfj-matcher scrape --output data/moje_oferty.csv
```

Wynik (`data/jobs_links.json`):

```json
{
  "scraped_at": "2026-03-02T10:00:00+00:00",
  "count": 42,
  "links": [
    "https://nofluffjobs.com/pl/job/senior-ai-engineer-llms-python-addepto-remote-7",
    ...
  ]
}
```

---

## Konfiguracja (`.env`)

| Zmienna | Opis | Domyślna |
|---|---|---|
| `SCRAPER_BASE_URL` | Bazowy URL kategorii | `https://nofluffjobs.com/pl/artificial-intelligence` |
| `SCRAPER_CRITERIA` | Filtry NFJ (URL-encoded) | `requirement%3DPython%20salary%3Epln18000m` |
| `SCRAPER_HEADLESS` | Headless browser | `true` |
| `SCRAPER_DELAY_MIN` | Min. opóźnienie między akcjami (s) | `1.5` |
| `SCRAPER_DELAY_MAX` | Max. opóźnienie między akcjami (s) | `3.5` |
| `SCRAPER_OUTPUT_PATH` | Ścieżka pliku wyjściowego | `data/jobs_links.json` |

---

## Testy

```bash
uv run pytest
```

---

## Pipeline (dalsze etapy)

1. **Scraping linków** ← *ten moduł*
2. Pobieranie treści ofert (otwieranie zebranych linków)
3. Ocena dopasowania przez LLM (Qwen / lokalny model)

