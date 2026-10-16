# Automatyzacja pozyskiwania: źródła w UE, workflow, narzędzia

Stan: 16.10.2026. Działający kod: `leads/radar.py` (opis w `leads/README.md`). Ten dokument to mapa całości: co da się zautomatyzować, co trzeba robić ręcznie i gdzie jest granica prawna.

## 1. Zasada

Automatyzujemy **zbieranie, filtrowanie, wzbogacanie i przygotowanie** rozmowy. **Nie automatyzujemy wysyłki.** Powody: (a) GitHub, Stack Overflow, Reddit i LinkedIn banują za masowe wiadomości; (b) B2B cold e-mail w UE jest legalny tylko w wąskich ramach (patrz §6); (c) reputacja autora biblioteki z 5 mln pobrań jest warta więcej niż każdy lejek. Jedna dopasowana wiadomość dziennie, wysłana ręcznie z gotowego szkicu, to cel.

## 2. Mapa źródeł (UE), uporządkowana według tego, czy ktoś już napisał "potrzebuję"

### 2.1 Popyt jawny: ktoś opublikował zapotrzebowanie z budżetem

| Źródło | Zasięg | Dostęp maszynowy | W radarze | Wartość |
|---|---|---|---|---|
| **TED** (ted.europa.eu) | wszystkie zamówienia publiczne UE powyżej progów (ok. 140 tys. EUR usługi) | Search API v3, anonimowo, bez limitu praktycznego | tak | średnia: duże postępowania, formalne, ale filtr po CPV + słowach technicznych daje kilka trafień tygodniowo; podwykonawstwo u integratora to realna ścieżka |
| **Krajowe platformy poniżej progu UE**: PL ezamowienia.gov.pl i platformazakupowa.pl; DE service.bund.de i evergabe; FR BOAMP; NL TenderNed; CZ NEN; SK UVO; AT data.gv.at; **OCDS** (Open Contracting) w wielu krajach | zamówienia krajowe | PL: eZamówienia ma API (BZP); platformazakupowa ma nowe "Ofertowa" z wyszukiwarką; OCDS to JSON | nie (następny krok: BZP API) | niska dla software'u na zamówienie: dominuje sprzęt i licencje |
| **Baza Konkurencyjności** (PL) | firmy z dotacjami UE, zakupy > 50 tys. zł | API za kontem (401 bez logowania), UI z alertami e-mail | ręcznie | **wysoka**: jedyne miejsce, gdzie MŚP z gwarantowanym budżetem ogłaszają potrzebę software'u |
| **Odpowiedniki Bazy w innych krajach**: DE "Vergabeportale" dla dotacji regionalnych, CZ "Profil zadavatele" | | rozproszone | nie | niska |
| **EU Funding & Tenders Portal** (ec.europa.eu/info/funding-tenders) | przetargi instytucji UE i konkursy grantowe (Horizon, Digital Europe) | SEDIA API, JSON | nie | partnerstwa w konsorcjach; długi cykl |
| **Useme, Oferia, Fixly** (PL), **Malt, Comet** (FR/DE/ES), **Freelancermap, GULP** (DE), **Twago** | zlecenia freelance | Useme HTML; Malt/Freelancermap HTML z limitami; GULP i Freelancermap mają RSS/alerty w UI | Useme tak | PL niskie stawki; DE (Freelancermap, GULP) to rynek kontraktów 80–120 EUR/h dla .NET, **warto dodać** |
| **Upwork, Toptal, Freelancer.com** | globalne | Upwork bez RSS od 2024, alerty w UI; Freelancer API z OAuth | nie | Upwork jako źródło gotówki z profilem "Avro/Kafka/.NET performance" |
| **Clutch, GoodFirms, Sortlist, DesignRush** | katalogi, inbound z RFP | profile + płatne leady | nie | dopiero z referencjami |

### 2.2 Popyt ukryty: ktoś ma problem, ale go nie ogłosił jako zlecenia

| Źródło | Co widać | Dostęp | W radarze |
|---|---|---|---|
| **GitHub issues** w repo konkurencji i narzędzi (apache/avro, confluent-kafka-dotnet, avro-source-generator, Parquet.Net, ParquetSharp, Apache.Arrow, EngineeredWood, GOEddie.Spark.Dotnet, Chr.Avro) | konkretne błędy, brak funkcji, pytania "jak" | REST search 10 req/min bez tokenu, 30 z tokenem; GraphQL z tokenem | tak |
| **GitHub dependents / code search** | kto używa naszej lub cudzej biblioteki; code search `"SolTechnology.Avro"` lub `Confluent.SchemaRegistry.Serdes.Avro` w `.csproj` | dependents HTML; code search wymaga tokenu | dependents tak; code search: dodać z tokenem |
| **Stack Overflow** | pytania bez odpowiedzi z tagami c#+avro/parquet/iceberg | API 2.3, 300 req/dzień bez klucza, 10 tys. z kluczem | tak |
| **Reddit** r/dotnet, r/csharp, r/dataengineering, r/apachekafka, r/ExperiencedDevs | "jak to zrobić w .NET?" | RSS blokowany z większości IP; OAuth app (darmowa) daje 100 req/min | best-effort; **następny krok: OAuth** |
| **Hacker News** | "Who is hiring", "Who wants to be hired", dyskusje | Algolia API | tak |
| **Discord/Slack**: C# Discord, .NET Evolution, Confluent Community Slack (#clients), Apache Iceberg Slack, Data Engineering Discord | pytania na żywo | bez API (regulaminy); ręcznie, 10 min dziennie | nie |
| **LinkedIn** | posty "szukamy", komentarze pod postami o Kafka/.NET, zmiany stanowisk | brak API; Sales Navigator (płatny) do list; scraping łamie regulamin | ręcznie: zapisane wyszukiwania |
| **NuGet** | pobrania naszej paczki per wersja (sygnał ogólny), brak danych o firmach | API statystyk | nie |
| **Ankiety w repo** | issue "Kto was używa?" w AvroConvert; GitHub Discussions | darmowe | zrobić raz: pinned issue |

### 2.3 Kupcy w ruchu: zmiany, które tworzą potrzebę

| Sygnał | Jak wykryć | Co oznacza |
|---|---|---|
| Firma publikuje ofertę pracy ".NET + Kafka/Avro/Databricks" | portale pracy (justjoin.it, nofluffjobs, pracuj.pl, StepStone, Indeed) mają JSON/RSS; justjoin.it ma publiczny JSON | zespół buduje coś z naszymi technologiami **teraz**; napisać do hiring managera, nie do HR |
| Dotacja przyznana (lista beneficjentów Dig.IT, FENG, KPO) | PDF/XLSX na stronach PARP/ARP/NCBR | za 3–9 miesięcy zapytanie ofertowe w Bazie Konkurencyjności; można być wcześniej |
| Konkurent zmienia licencję lub porzuca projekt | `scripts/nuget-radar.py` co kwartał, GitHub watch | użytkownicy szukają zamiennika |
| Nowy obowiązek regulacyjny z terminem | kalendarz w `VerticalExploration.md` §2 | okno 6–18 miesięcy |

## 3. Workflow docelowy

```
[zbieranie]  radar.py (TED, GitHub, SO, HN, Useme, Reddit) + alerty e-mail (Baza Konkurencyjności, Upwork, Freelancermap, LinkedIn)
     │
[filtr]      profile + próg + filtr .NET + noise regex          → ~30–60 kandydatów / tydzień
     │
[triage LLM] ocena 0–10, uzasadnienie, szkic w języku leada     → ~10 wartych uwagi / tydzień
     │
[wzbogacenie] ręcznie lub skryptem: kto to jest (strona, LinkedIn, wielkość firmy, kraj, czy > 100 osób = kupiec licencji)
     │
[kolejka]    digest/YYYY-MM-DD.md + status w sqlite (new → contacted → replied → won/ignored)
     │
[rozmowa]    ręcznie: komentarz pod issue / odpowiedź na SO / e-mail do zamawiającego / wiadomość na Useme
     │
[pętla]      co tydzień: skąd przyszły odpowiedzi → dostroić wagi, dodać/wyciąć źródła
```

Narzędzia, które warto dołożyć, w kolejności zwrotu:
1. **Reddit OAuth** (darmowa aplikacja "script"): odblokowuje najlepsze źródło pytań ".NET + dane". 1 godzina.
2. **GitHub token + code search**: `Confluent.SchemaRegistry.Serdes.Avro` w plikach `.csproj` organizacji → lista firm używających Avro w .NET; filtr po organizacjach (nie userach) → leady na AvroConvert. 2 godziny.
3. **justjoin.it / nofluffjobs JSON**: oferty ".NET" + (Kafka|Avro|Databricks|Snowflake|Iceberg) → firma + stack → napisać do tech leada. 2 godziny.
4. **Freelancermap / GULP** (DE) RSS lub HTML: kontrakty .NET w DACH. 2 godziny.
5. **eZamówienia BZP API** (PL poniżej progu UE): uzupełnienie TED. 3 godziny.
6. **Wzbogacanie**: dla organizacji z GitHub/TED pobrać stronę, LinkedIn (ręcznie), liczbę pracowników; proste heurystyki (domena firmowa vs gmail; liczba repo w org). Komercyjne: Apollo.io/Hunter.io (darmowe limity) tylko do e-maili firmowych, nie prywatnych.
7. **CRM**: na start sqlite + digest wystarczy. Gdy > 50 aktywnych leadów: Notion/Airtable/HubSpot Free. Nie wcześniej.
8. **Powiadomienie**: Action może wysłać digest na e-mail (SMTP) albo do Slacka/Discorda przez webhook; 30 minut, gdy będzie potrzebne.

## 4. Co rozmowa ma osiągnąć (żeby nie była sprzedażą)

Pierwsza wiadomość nie sprzedaje. Pyta o jedną konkretną rzecz z ich tekstu i oferuje coś od razu użytecznego (sprawdzę twój schemat, przepuszczę twój copybook, dam wczesną wersję). Cele rozmowy, w kolejności: (1) zrozumieć ich przypadek użycia i czym płacą dziś (czas, Spark, licencja Redgate); (2) dowiedzieć się, czy są > 100 osób (kupiec licencji) i kto decyduje o zakupie bibliotek; (3) dopiero potem produkt. Każda rozmowa trafia do notatki: firma, rola, problem, cytat, "zapłaciliby?".

## 5. Metryki (tygodniowo, w jednej linijce w README)

Zebrane → dopasowane → ocenione ≥ 7 → skontaktowane → odpowiedzi → rozmowy → płatne. Jeśli po 4 tygodniach stosunek odpowiedzi do skontaktowanych jest < 10%, wiadomości są złe albo źródło jest złe. Jeśli odpowiedzi są, ale nie ma rozmów, oferta w wiadomości jest za słaba.

## 6. Granice prawne i regulaminowe

- **Cold e-mail B2B w UE**: PECR/ePrivacy + RODO. W Polsce art. 10 ustawy o świadczeniu usług drogą elektroniczną i art. 172 Prawa telekomunikacyjnego (po zmianach z 2024/2025 w ustawie Prawo komunikacji elektronicznej): marketing bezpośredni na adres osoby fizycznej (także służbowy imienny) wymaga zgody; na adres ogólny firmy (biuro@, kontakt@) jest dopuszczalny w ramach uzasadnionego interesu z możliwością sprzeciwu. W Niemczech (UWG §7) jeszcze ostrzej: cold e-mail B2B bez zgody jest co do zasady zakazany. Praktyka: **odpowiadać tam, gdzie ktoś zadał pytanie publicznie** (issue, SO, Useme, TED to zaproszenie do oferty) jest poza tym reżimem; cold e-mail tylko na adresy ogólne albo do osób, które same opublikowały kontakt w celu kontaktu (np. zamawiający w TED).
- **GitHub**: komentarze pod issues są OK, jeśli dotyczą problemu; masowe "spróbuj mojej biblioteki" pod cudzymi issues to spam wg Acceptable Use. Zasada: jeden komentarz, konkret, bez linku, jeśli nie prosili.
- **Stack Overflow**: odpowiedź może wskazać własną bibliotekę, jeśli jest ujawnione autorstwo i odpowiedź rozwiązuje problem.
- **LinkedIn**: automatyzacja (boty, scraping) = blokada konta. Ręcznie.
- **Reddit**: self-promotion limit (~10% własnych treści), ujawniać autorstwo.
- **Scraping Useme/TED/HTML**: TED ma API i politykę ponownego użycia; Useme regulamin nie zabrania czytania, skrypt robi 5 żądań dziennie. Nie zapisywać danych osobowych poza tym, co jest w publicznym ogłoszeniu; `state/leads.sqlite` jest w prywatnym repo.

## 7. Czego nie robić

- Nie kupować list e-mail ani "lead gen as a service" dla tej skali.
- Nie automatyzować DM na LinkedIn/Reddit (narzędzia typu Expandi, Waalaxy kończą się banem).
- Nie wysyłać tego samego szkicu do dwóch osób; szkic jest punktem wyjścia.
- Nie mieszać tożsamości: w issues i na SO pisze Adrian jako autor AvroConvert, nie "SolTechnology".
