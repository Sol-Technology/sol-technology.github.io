# Lead radar

Codzienny zbieracz sygnałów popytu dla produktów SolTechnology. Czyta publiczne źródła, punktuje według profili z `profiles.json`, pamięta co już widział (`state/leads.sqlite`) i pisze digest do `digest/YYYY-MM-DD.md` z gotowym szkicem pierwszej wiadomości.

**Niczego nie wysyła.** Szkice są do ręcznego dopasowania i wklejenia. To jest celowe: automatyczna wysyłka na GitHub/LinkedIn/e-mail kończy się banem albo opinią spamera, a jedna dobra wiadomość dziennie jest warta więcej niż sto szablonowych.

## Uruchomienie

```bash
python3 leads/radar.py                       # ostatnie 7 dni, wszystkie profile
python3 leads/radar.py --days 2 --llm        # z oceną i szkicem od LLM (ANTHROPIC_API_KEY lub OPENAI_API_KEY)
python3 leads/radar.py --profiles lake,avroconvert --sources ted,github_issues
python3 leads/radar.py --all                 # pokaż też już widziane
```

Tylko biblioteka standardowa Pythona. `GITHUB_TOKEN` opcjonalny (bez niego 10 zapytań/min, skrypt czeka).

**LLM bez osobnego klucza**: `--llm` używa GitHub Models (`openai/gpt-4o-mini`), autoryzowanych tokenem GitHub. W Actions działa z wbudowanym `GITHUB_TOKEN` (workflow ma `models: read`). Lokalnie: PAT z uprawnieniem `models:read` w `GITHUB_MODELS_TOKEN` (fine-grained token → Account permissions → Models: Read-only), albo `gh auth login` i `GITHUB_MODELS_TOKEN=$(gh auth token)`. Darmowy limit to kilkadziesiąt–kilkaset zapytań dziennie zależnie od modelu; subskrypcja Copilota podnosi limity. Jeśli ustawisz `ANTHROPIC_API_KEY` lub `OPENAI_API_KEY`, mają pierwszeństwo. Tokena Copilota z VS Code nie da się użyć poza IDE i nie wolno (regulamin).

Workflow `.github/workflows/lead-radar.yml` odpala się codziennie 05:15 UTC, commituje digest i stan z `[skip ci]`, więc nie uruchamia deployu strony. Sekrety opcjonalne: `ANTHROPIC_API_KEY` albo `OPENAI_API_KEY`; bez nich LLM idzie przez GitHub Models.

## Źródła

| Źródło | Co | Dostęp | Uwagi |
|---|---|---|---|
| `ted` | Zamówienia publiczne w całej UE (TED), CPV 72* i 48* (usługi IT, oprogramowanie) | Search API v3, anonimowo, POST JSON | ~1000 ogłoszeń tygodniowo; tytuły wielojęzyczne, więc punktują słowa techniczne (Kafka, Iceberg, data platform, hurtownia danych) |
| `github_issues` | Nowe issues z zapytań typu "avro c#", "iceberg .net", "copybook c#" | REST search, 10 req/min bez tokenu | dużo szumu z cudzych projektów; dla profili bibliotecznych wymagany ślad .NET w treści albo nazwie repo |
| `github_dependents` | Repozytoria publiczne zależne od AvroConvert | HTML (pierwsza strona) | lista organizacji = leady na licencję komercyjną 4.0; zmienia się rzadko |
| `stackexchange` | Nowe pytania SO z tagami c#+avro/kafka/parquet/iceberg/cobol/… | API 2.3, 300 req/dzień bez klucza | ruch na SO jest mały, ale pytanie = ktoś ma problem dziś |
| `hn` | Hacker News (Algolia) | API, bez limitu praktycznego | "Who is hiring" i wzmianki o .NET + dane |
| `useme` | Polskie zlecenia dla MŚP | HTML listingu kategorii, 5 stron, co 2 s | niskie stawki, ale najszczerszy obraz, czego szukają małe firmy |
| `nofluffjobs` | Oferty pracy "(Kafka\|Databricks\|Snowflake\|Parquet\|Iceberg\|Spark\|Mainframe\|ETL) AND (.NET\|C#)" | publiczne API wyszukiwarki (POST JSON), PL/EU | firma rekrutująca = buduje z naszym stackiem teraz; pisać do tech leada, nie aplikować. Ostatnie 14 dni: 7 firm, m.in. Beesafe (ubezpieczyciel), Upvanta (bankowość) |
| `reddit` | r/dotnet, r/csharp, r/dataengineering, r/apachekafka, r/humanresources | RSS old.reddit | Reddit blokuje większość IP bez OAuth; z tej sieci zwraca 0 lub 429. Działa czasem z GitHub Actions. Zostawione jako best-effort |

Nie zintegrowane, do zrobienia ręcznie lub z kluczem:
- **Baza Konkurencyjności** (zapytania ofertowe firm z dotacjami UE, budżety 50 tys.–kilka mln zł): API wymaga konta (`/api/announcements` → 401). Założyć konto i ustawić alerty w UI; to najlepsze polskie źródło zleceń z gwarantowanym budżetem.
- **Upwork**: RSS wyłączony w 2024, API tylko dla partnerów. Alerty w UI.
- **Freelancer.com**: ma API z OAuth, niska jakość zleceń. Pominięte.
- **LinkedIn**: brak API, scraping łamie regulamin. Ręcznie: zapisane wyszukiwania postów ("schema registry .NET", "Iceberg C#", "jawność wynagrodzeń").
- **NuGet "used by"**: brak publicznego API dla zależnych pakietów.

## Profile

`profiles.json`: słowa kluczowe z wagami, `require_any` (bez któregoś z tych słów lead odpada), `negative`, `min_score`, `dotnet_required` (domyślnie true dla źródeł społecznościowych), szkice `opener_pl` / `opener_en` / `opener_dependents` z polami `{topic}`, `{title}`, `{org}`.

Punktacja: suma wag × liczba wystąpień (max 3), trafienia w tytule liczone podwójnie. Lead trafia do profilu z najwyższym wynikiem powyżej progu. Z `--llm` najlepsze 40 leadów dostaje ocenę 0–10, uzasadnienie i spersonalizowany szkic w języku leada.

## Rytuał (15 minut dziennie)

1. Otwórz dzisiejszy digest. Sekcje są posortowane po ocenie LLM, potem po punktach.
2. Z każdej sekcji weź maksymalnie 1–2 leady, przeczytaj źródło w całości.
3. Dopasuj szkic (konkret z ich tekstu, jedno pytanie na końcu), wyślij ręcznie tam, gdzie lead żyje (komentarz pod issue, odpowiedź na SO, e-mail do zamawiającego z TED, wiadomość na Useme).
4. Zanotuj w `state/leads.sqlite` (`status`: `contacted`, `replied`, `won`, `ignored`) albo w arkuszu; `sqlite3 leads/state/leads.sqlite "update leads set status='contacted' where key='ted:701793-2026'"`.
5. Raz w tygodniu: które źródło dało odpowiedź? Dostrój wagi i `negative` w profilach.

## Co się już nauczyliśmy z pierwszego przebiegu (16.10.2026)

- TED: 1057 ogłoszeń IT w 7 dni, z czego ~10 ma słowa z naszych profili. Reszta to sprzęt, licencje i utrzymanie. Sygnał rzadki, ale z budżetem i terminem.
- GitHub issues bez filtra .NET to 90% szumu (issues cudzych projektów w Rust/Go/C++). Z filtrem zostaje kilka dziennie.
- `sadicangel/avro-source-generator` (0.7.0) to nowy konkurent w niszy Avro bez `avrogen`: source generator nad Apache.Avro. Obserwować; jego issues to nasi potencjalni użytkownicy.
- Useme ma dziś "Senior .NET Developer – KSeF / moduł faktur OMS" i "programista ASP.NET Core do rozwoju platformy": realne, płatne, .NET.
- Dependents AvroConvert: 18 publicznych repo, w tym Optimove (SaaS marketing, > 100 osób), superstreamlabs/memphis.net, naveego. To gotowa lista do rozmowy o 4.0 i licencji.
