# Eksploracja: kolejne biblioteki SolTechnology

Stan: research 16.10.2026. Liczby z nuget.org z tego dnia. Nic nie jest zdecydowane.

## 1. Czego szukamy

Model AvroConvert, czyli: format/protokół, który w Javie/Pythonie/Rust ma dojrzałe wsparcie, a w .NET albo nic nie ma, albo oficjalna biblioteka wymaga codegen / ręcznego budowania schematów. Kupujący: firma > 100 osób, data engineering, płaci przez Paddle za roczną licencję. To od razu wycina rzeczy ładne, ale bez budżetu (CRDT, hobbystyczne parsery, narzędzia CLI).

Dwa pytania przy każdym kandydacie:
1. Czy ktoś w korporacji ma problem, który blokuje mu projekt (a nie tylko "API brzydkie")?
2. Czy da się to zrobić w pojedynkę w kilka miesięcy, korzystając z tego, co już jest w AvroConvert (parser Avro, kontrakt POCO ↔ schemat, kodeki, benchmarki)?

## 2. Punkt odniesienia (nuget.org, 16.10.2026)

| Pakiet | Total | /dzień | Licencja | Uwagi |
|---|---|---|---|---|
| AvroConvert | 5,3M | 4,4K | CC BY-NC-SA → PolyForm | nasz punkt startu |
| Apache.Avro | 71,3M | 26,3K | Apache-2.0 | wymaga codegen `ISpecificRecord` lub `GenericRecord` |
| Confluent.SchemaRegistry.Serdes.Avro | 39,5M | 84,0K | Apache-2.0 | zbudowane na Apache.Avro, ten sam problem codegen |
| Confluent.Kafka | 280,5M | 1,2M | Apache-2.0 | README wprost: "quality and maturity of the non-Java [Avro] implementations lags that of Java" |
| Parquet.Net | 33,3M | 181K | MIT | jeden maintainer (aloneguid), dojrzałe, ma `ParquetSerializer` dla POCO |
| Apache.Arrow | 47,9M | 41,6K | Apache-2.0 | API builderów, zero warstwy POCO |
| Microsoft.Data.Analysis | 11,6M | 11,0K | MIT | wersja 0.23.x, od lat preview |
| CsvHelper | 713,7M | 399K | MS-PL/Apache | ostatnie wydanie 02.06.2025, `ClassMap` + `CultureInfo` w każdym wywołaniu |
| YamlDotNet | 591,7M | 666K | MIT | w porządku, brak luki |
| ClosedXML | 235,0M | 171K | MIT | w porządku, brak luki |
| EPPlus | 214,0M | 2,5M | PolyForm NC + komercyjna | dowód, że nasz model licencyjny działa w .NET |
| MassTransit 9 | 254,7M | 5,0M | komercyjna (Massient) | fala komercjalizacji OSS w .NET 2025–26 |
| Polars.NET (community) | 7K | – | – | wrapper na Rust, 0.7.0 |
| pocketken.H3 | 811K | – | – | port H3, działa, brak luki |
| Cel / Cel.NET | 734K / 98K | – | – | CEL już zajęte (Cel.NET pisze rayokota z Confluent) |
| EngineeredWood.* (Iceberg, Delta, Lance, ORC, Vortex…) | 0,3–1,8K każdy | – | – | 0.3.0 "preliminary", autor: Curt Hagenlocher (maintainer Apache.Arrow C#) |
| ApacheOrcDotNet | 3,6K | 1 | – | martwe od 2020 |

Formaty tabel: Iceberg ma oficjalne implementacje Java, Python, Rust, Go, C++. .NET: nic oficjalnego. Delta Lake: delta-rs (Rust/Python), delta-kernel; w .NET tylko preliminary EngineeredWood i DeltaIO aloneguida (repo pod starym adresem nie istnieje, status do sprawdzenia).

## 3. Kandydaci

### A. Mocne dopasowanie

#### A1. Schema Registry serde dla POCO (rozbudowa `SolTechnology.Avro.Kafka`)

Problem: 84K pobrań dziennie `Confluent.SchemaRegistry.Serdes.Avro`, a każdy z tych użytkowników musi albo generować klasy `avrogen`, albo klepać `GenericRecord`. My mamy już kontrakt POCO ↔ schemat. Pakiet `SolTechnology.Avro.Kafka` 3.0.0 istnieje, ale jest cienki.

Zakres 2.0:
- serializer/deserializer zgodny z Confluent wire format (magic byte + schema id), rejestracja schematu z POCO, cache po fingerprincie
- Azure Schema Registry (Event Hubs) i Apicurio – inny wire format, te same POCO
- single-object encoding (już planowane w 4.0 jako S12) dla Kafki bez rejestru
- ewolucja schematu z reader schema = typ C#, bez codegen
- zgodność z `Confluent.Kafka` (`ISerializer<T>`/`IAsyncSerializer<T>`) i z KafkaFlow/MassTransit riders

Koszt: niski, to głównie szkło nad rdzeniem 4.0. Konkurencja: **Chr.Avro** (C.H. Robinson) robi dokładnie POCO ↔ Confluent bez codegen, MIT. Trzeba porównać wydajność i funkcje zanim się w to wejdzie; jeśli Chr.Avro jest dobre, sprzedaż będzie trudna.

#### A2. Apache Iceberg dla .NET

Największa luka na liście. Oficjalne implementacje: Java, Python, Rust, Go, C++. W .NET: `EngineeredWood.Iceberg` 0.3.0, metadata-only, 373 pobrania. Tymczasem na Iceberg przeszli: Snowflake, BigQuery, Databricks (UniForm), Redpanda, Microsoft OneLake, AWS (S3 Tables, Firehose). Zespół .NET w banku czy ubezpieczycielu, który chce dopisać do tabeli Iceberg z serwisu C#, dziś odpala Sparka albo PyIceberg przez subprocess.

Dlaczego pasuje do nas: manifesty i manifest listy Iceberga to **pliki Avro**. Metadata JSON + Avro manifesty + Parquet dane. Mamy pierwszy element, drugi daje Parquet.Net (MIT, można zależeć) albo własny writer później.

MVP (czytanie + append):
1. REST Catalog client (spec OpenAPI; testy na Polaris / Lakekeeper / Nessie)
2. parsowanie `metadata.json` v1/v2, snapshoty, manifest list (Avro) → lista plików z partycjami i statystykami
3. scan planning z predicate pushdown na statystykach, zwrot `IAsyncEnumerable<T>` przez Parquet.Net
4. append: zapis Parquet, nowy manifest (Avro), nowy snapshot, commit przez REST z optimistic concurrency
5. mapowanie POCO ↔ schemat Iceberg, ewolucja schematu

Poza MVP: delete files (positional/equality), v3, partition transforms poza identity/bucket/truncate/time, Glue/Hive catalog, widoki.

Koszt: wysoki, pół roku na MVP. Ryzyka: spec duży i żywy; Apache może kiedyś założyć `iceberg-dotnet` (dziś nie ma śladu); Hagenlocher może dociągnąć EngineeredWood (ale to projekt poboczny, 0.3.0, API "may change"). Plus: Microsoft nie ma własnego SDK Iceberg dla .NET mimo OneLake – to dziwne i warte sprawdzenia, czy coś szykują.

Nazwa robocza: `SolTechnology.Iceberg`. "IcebergConvert" brzmi źle, bo to nie konwersja.

#### A3. Arrow bez bólu ("ArrowConvert")

`Apache.Arrow` ma 41,6K/dzień i API z 2017: `StringArray.Builder`, ręczne `Schema.Builder`, zero mapowania na klasy. Brakuje warstwy: `IEnumerable<T>` → `RecordBatch`, `RecordBatch` → `IEnumerable<T>`, IPC stream/file, Flight, ADBC, konwersje Arrow ↔ Avro ↔ Parquet.

Samo w sobie trudne do sprzedania (ludzie, którzy używają Arrow w .NET, zwykle umieją go używać). Ale to warstwa pod A2 i pod każdą integrację z DuckDB/Polars/ADBC. Robić jako część A2, nie jako osobny produkt.

### B. Możliwe, ale z zastrzeżeniami

#### B1. Delta Lake w czystym .NET

Ten sam argument co Iceberg, mniejsza luka pokrycia (delta-rs ma bindingi, EngineeredWood ma `DeltaLake.Table` z deletion vectors). Kupujący to świat Databricks/Fabric, czyli dużo .NET-u. Transaction log to JSON + Parquet checkpointy, bez Avro, więc mniej synergii. Sensowne jako drugi format po Iceberg, na wspólnej warstwie Arrow/Parquet.

#### B2. CSV

CsvHelper: 399K/dzień, 16 miesięcy bez wydania, API wymaga `CsvConfiguration(CultureInfo.InvariantCulture)` i `ClassMap` do czegokolwiek nietrywialnego. Luka istnieje, ale darmowe alternatywy (Sep, Sylvan.Data.Csv) są szybsze i dobre. Nikt nie zapłaci za CSV. Jedyny sens: jako jeden z formatów w pakiecie "DataConvert" (Avro/Parquet/CSV/JSON/Arrow, jedno API, jedna licencja).

#### B3. DataFrame / Polars

Popyt realny (Microsoft.Data.Analysis stoi w preview od 2019, 11K/dzień). Ale to albo wrapper na Rust (utrzymanie bindingów na 6 platform, Polars Inc. może wydać oficjalne), albo własny silnik (lata pracy). Nie dla jednej osoby.

#### B4. ORC

Zero żywych bibliotek w .NET. Popyt jednak maleje (Hive/Trino w legacy), Parquet wygrał. Dorzucić do Iceberg jako reader, jeśli klient zapłaci.

### C. Odrzucone

- **CRDT / Automerge**: ciekawe, brak kupującego B2B w naszym segmencie.
- **H3, CEL, jq, YAML, Excel**: istniejące biblioteki są wystarczające; EPPlus już zarabia na Excelu, ClosedXML jest MIT.
- **Service bus po MassTransit**: luka po komercjalizacji MassTransit jest realna, ale wypełniają ją Wolverine i Rebus, a to nie nasza domena.
- **Protobuf, MessagePack, gRPC**: .NET ma tu najlepsze implementacje na rynku.

## 4. Kontekst rynkowy

W 2025–26 na model płatny przeszły: EPPlus (PolyForm NC, identycznie jak nasz plan), MassTransit 9, FluentAssertions 8, AutoMapper i MediatR, wcześniej ImageSharp. Działy zakupów w .NET-owych firmach już wiedzą, jak kupować licencje na biblioteki. Z drugiej strony każda taka zmiana wywołała fork albo migrację (Wolverine, Mapperly, Shouldly). Lekcja: licencja darmowa musi być naprawdę darmowa dla małych (PolyForm Small Business to załatwia), a produkt musi robić coś, czego fork nie zrobi w weekend. Iceberg spełnia drugi warunek, serde do Schema Registry raczej nie.

## 5. Rekomendacja

1. Dokończyć AvroConvert 4.0 (licencja, wydajność, zgodność ze spec). Bez tego nic dalej nie ma sensu.
2. Równolegle, tanio: porównać `SolTechnology.Avro.Kafka` z Chr.Avro. Jeśli jesteśmy szybsi i prostsi, wydać 2.0 jako pierwszy produkt satelitarny pod tą samą licencją. Jeśli nie, zostawić.
3. Główny zakład na 2027: **Iceberg dla .NET**. Przed decyzją spike 2 tygodnie: odczyt tabeli z Lakekeeper/Polaris przez REST, parsowanie manifestów naszym parserem Avro, zwrot wierszy przez Parquet.Net. Jeśli po dwóch tygodniach działa odczyt z partycjami, iść dalej.
4. Arrow i Delta jako rozszerzenia tej samej warstwy, nie osobne produkty.

## 6. Do zweryfikowania przed decyzją

- Chr.Avro: funkcje, wydajność, aktywność repo.
- Plany Microsoftu wokół OneLake/Fabric SDK dla Iceberg w .NET (brak publicznego SDK dziś).
- Roadmap EngineeredWood (Hagenlocher) i czy Apache planuje `iceberg-dotnet` (lista dyskusyjna dev@iceberg).
- Status DeltaIO (aloneguid) – repo przeniesione lub porzucone.
- Czy Parquet.Net jako zależność jest OK w produkcie komercyjnym (MIT – tak, ale jeden maintainer; alternatywa: własny writer w dalszej fazie).

## 7. Review drugiej analizy ("SolTechnology — nisze .NET pod Paddle", 15.10.2026)

Druga analiza (Claude, plik `SolTechnology-nisze-NET.md`) rekomenduje jako nr 1 zestaw do e-faktur UE, potem walidator PDF/UA i konwerter RDLC, a osobno wymienia pomysły pod markę AvroConvert. Sprawdziłem jej kluczowe twierdzenia na NuGet 16.10.2026. Ocena punkt po punkcie.

### 7.1 Co się nie zgadza z danymi

**E-faktury: nisza nie jest pusta, jest zalana.** Analiza pisze "ZUGFeRD-csharp robiony hobbystycznie przez jedną osobę" i "SDK KSeF od MF to tylko transport API". Stan faktyczny:

| Pakiet | Pobrania | Uwagi |
|---|---|---|
| ZUGFeRD-csharp | 1,53M | 18.0.1 sprzed 7 dni; **koniec wsparcia 30.11.2026, od 1.12.2026 deprecated**. Następca komercyjny wygląda na `FactoorSharp.FacturX` 20.0.0 (stwo-industries = s2industries, ten sam autor) |
| International.EInvoicing (EpicDiceStudio) | ~10–13K na pakiet | pełny zestaw: model EN 16931, UBL, CII, Factur-X, Peppol BIS, XRechnung/Leitweg-ID, czytelne diagnostyki. Dokładnie to, co analiza proponuje zbudować |
| Soneta.KSeF.Client | 137K | enova365, FA(3) od producenta ERP |
| MarcinBorecki.KsefKit | ~1K | "fluent invoice build/send, UPO, XAdES, retry" |
| ITBees.Ksef, OfficeIMO.Invoicing.KSeF (Evotec), TBJ, PikSystems, KSEFAPI | po kilkaset–3K | klienci + budowanie FA(3) |
| Balsoft.Hive.EInvoice, Klarfakt, XSchematron, InvoiceLint, Antiphon.*, OfficeIMO.Invoicing.Validation | 0–500 | wszystkie z ostatnich 1–2 miesięcy, w tym natywne silniki Schematron bez Saxona |

Czyli: w ciągu ostatnich 60 dni pojawiło się kilkanaście pakietów robiących to samo, w tym dwa kompletne (International.EInvoicing, Balsoft.Hive). Terminy KSeF (luty/kwiecień 2026) już minęły, więc software house'y już coś kupiły albo napisały. Jedyny prawdziwy sygnał to deprecjacja ZUGFeRD-csharp w grudniu, ale jego 1,5M użytkowników ma gotowego komercyjnego następcę od tego samego autora. Analiza sama ustawia kryterium 4 ("przewaga nad darmowym OSS i nad AI") i sama zauważa, że "NuGet zalewają biblioteki pisane z AI". E-faktury są tego najlepszym przykładem, a mimo to lądują na pierwszym miejscu. Do tego inny kupiec, zero wspólnej dystrybucji z AvroConvert (analiza to przyznaje w sekcji o marce). **Odrzucić.**

**CDC dla .NET: Postgres już się commodityzuje.** Analiza zna tylko PgOutput2Json. Na NuGet jest `Wallaby` (Hawxy, 11K, 1.3.0 sprzed 9 dni, sinki do Meilisearch/Elastic/OpenSearch), `Excalibur.Cdc.Postgres`, `DebeTail`, `WalFlow`, `DbSignal`, a sam Npgsql ma od 2021 API logical replication (`Npgsql.Replication`), więc strona Postgresa to kilkaset linii. Trudna część to SQL Server (polling tabel `cdc.*`, LSN, brak push) i gwarancje dostarczenia, czyli odpowiedzialność za utratę zdarzeń w cudzej produkcji. Synergia z Avro.Kafka realna, ale to produkt operacyjny (snapshoty, backfill, failover), nie biblioteka formatu. **Obserwować, nie budować.** Ewentualnie: sink Avro/Schema Registry do Wallaby jako darmowy plugin reklamujący Avro.Kafka.

**Delta/Iceberg "do obserwacji, protokół szybko się zmienia".** Dla Delty zgoda (protokół Databricks, deletion vectors, column mapping, częste zmiany). Dla Iceberga nie: spec v2 jest stabilna od 2021, v3 ratyfikowana w 2025, REST Catalog ma standard OpenAPI, a liczba implementacji (5 języków) pokazuje, że da się ją napisać. Analiza wrzuca oba do jednego worka i przez to zaniża Iceberga. Podtrzymuję §3 A2.

### 7.2 Co jest trafne

**Narzędzia ewolucji schematów (BACKWARD/FORWARD/FULL offline, diff).** Dobry pomysł, zła skala. To funkcja AvroConvert 4.x (issue #73 `CompareSchema`, fingerprinty S13), nie produkt. Reguły zgodności Confluenta są udokumentowane, Apache Avro Java ma `SchemaCompatibility` do przeportowania w tydzień. Zrobić jako darmową funkcję i materiał na README: "test zgodności w xUnit bez rejestru". Sprzedaje wersję płatną pośrednio.

**CopybookConvert (COBOL copybook, EBCDIC, COMP-3, REDEFINES, OCCURS → C#/Avro).** Jedyna prawdziwie pusta nisza w obu analizach: na NuGet są 2 martwe pakiety (2018, 2021). Wzorce w Javie (JRecord, Cobrix) istnieją, komercyjnie płaci się SnapLogic/Precisely. Pasuje do marki (binarny format → POCO, generowanie modelu, strumieniowanie) i do kupca z budżetem. Zastrzeżenia: (1) rozmiar rynku .NET + mainframe jest nieznany, większość takich integracji żyje w Javie; (2) bez prawdziwych copybooków i danych EBCDIC nie da się tego dobrze przetestować, a nikt ich nie udostępni; (3) sama analiza zauważa konflikt z pracą w Mastercard. **Kandydat nr 2 po Icebergu, pod warunkiem znalezienia 2–3 firm, które pokażą copybooki.**

**Odrzucenie klonów MediatR/MassTransit, workflow, generowania PDF, Parquet.** Zgoda w całości, te same wnioski co w §3 C.

**Sekcja o rynku (EPPlus, QuestPDF, MediatR, FluentAssertions).** Dobra i zgodna z `LicensingMigrationPlan.md`. Jedna rozbieżność: analiza proponuje "klucz podpisany kryptograficznie, sprawdzany offline", a decyzja z 08.10.2026 to brak klucza i walidacji (model QuestPDF). Zostawić decyzję z 08.10.

**Przestroga FluentAssertions (130 → 14,95 USD).** Ważna. Mówi, że za wygodniejsze API bez twardej funkcji trudno brać pieniądze. Dotyczy to też ArrowConvert (§3 A3) i serde do Schema Registry (§3 A1): oba są "wygodą", nie "ryzykiem". Iceberg i Copybook są po stronie ryzyka.

### 7.3 Pozostałe pomysły z tamtej listy

| Pomysł | Ocena | Dlaczego |
|---|---|---|
| EDI X12/EDIFACT | nie | EdiFabric ma znienawidzone licencjonowanie, więc luka na "uczciwą" licencję istnieje, ale to setki transaction setów, jest darmowe `indice.Edi`, i zero wspólnego z marką |
| ISO 20022 / SWIFT | nie | konflikt z Mastercard, analiza sama to mówi |
| Transpiler SQL (sqlglot) | nie | sqlglot jest MIT, ktoś go sportuje; migracje to zadanie jednorazowe, AI je robi; `SqlParserCS` (709K) pokrywa parsowanie |
| HL7 v2 | nie | nHapi 22M, darmowe, utrzymywane |
| Walidator PDF/UA, PDF/A | nie | veraPDF w kontenerze; kupiec niszowy; nic wspólnego z danymi |
| RDLC/SSRS | nie | rynek zajęty, analiza sama to przyznaje |
| Peppol AS4 | nie | certyfikacja OpenPeppol, WS-Security, lata pracy |
| Docling dla .NET, DMN | nie | modele ML / SaaS, nie biblioteka |

### 7.4 Wniosek z obu analiz

Obie zgadzają się co do modelu (darmowo dla małych, płatnie per podmiot, bez DRM) i co do odrzuceń. Różnią się w jednym: tamta ucieka od marki do regulacji (e-faktury), ta zostaje przy danych. Dane z NuGet rozstrzygają na korzyść zostania przy danych: e-faktury to w tej chwili najbardziej zatłoczona nisza na całym NuGet, a jedyna pusta nisza z tamtej listy (copybook) jest akurat formatem danych.

Lista po połączeniu:
1. AvroConvert 4.0 + zgodność schematów jako darmowa funkcja.
2. Spike Iceberg (2 tygodnie, §5 pkt 3).
3. Rozmowy o copybookach z 2–3 firmami (bank, ubezpieczyciel, integrator) zanim powstanie linijka kodu.
4. Avro.Kafka 2.0 tylko jeśli wygra porównanie z Chr.Avro.

## 8. Dalszy research: top pakiety innych ekosystemów i Stack Overflow (16.10.2026)

### 8.1 Stack Overflow: ile pytań zadają ludzie z .NET w porównaniu z Pythonem/Javą

Metoda: Stack Exchange API, liczba pytań z tagiem X **i** `c#`, podzielona przez liczbę z tagiem X i `python` (lub `java`). Punkt odniesienia: wszystkie pytania `c#` / `python` = 1,62M / 2,20M = **0,74**; `c#` / `java` = **0,85**. Jeśli dla tematu stosunek jest dużo niższy, .NET jest tam niedoreprezentowany (brak narzędzi albo brak popytu, SO tego nie rozróżnia).

| Temat | c# | python / java | stosunek | odczyt |
|---|---|---|---|---|
| docx | 387 | 750 (py) | 0,52 | lekko poniżej bazy; OpenXML SDK ma złe API, ale jest DocX/Syncfusion |
| ffmpeg | 762 | 2 215 (py) | 0,34 | poniżej bazy, ale FFMpegCore/Xabe.FFmpeg istnieją |
| ocr | 465 | 1 839 (py) | 0,25 | poniżej bazy; Tesseract wrappery istnieją |
| parquet | 36 | 271 (java) | 0,13 | 6× poniżej bazy |
| avro | 86 | 980 (java) | 0,09 | 10× poniżej bazy, a mimo to AvroConvert ma 4,4K/dzień |
| snowflake | 55 | 834 (py) | 0,07 | |
| apache-kafka | 342 | 6 092 (java) | 0,06 | 15× poniżej bazy, a Confluent.Kafka ma 1,2M/dzień |
| web-scraping | 777 | 29 901 (py) | 0,03 | Python wygrał, brak kupca |
| duckdb | 2 | 153 (py) | 0,01 | |
| databricks | 11 | 1 853 (py) | 0,006 | |
| apache-spark | 51 | 10 652 (py) | 0,005 | |
| delta-lake | 5 | 1 418 (wszystkie) | 0,004 | |
| apache-iceberg | 1 | 312 (wszystkie) | 0,003 | |
| microsoft-fabric | 3 | 25 (py) | 0,12 | platforma Microsoftu, a .NET prawie nieobecny |
| cobol / ebcdic | 31 / 20 | – | – | niezerowe; ludzie w C# czytają EBCDIC |

Wnioski:
- SO jest słabym sygnałem (ruch na SO spadł o >70% od 2023, pytania o nowe tematy idą do LLM-ów), ale kierunek jest spójny: im bliżej "lakehouse", tym bardziej .NET znika. Dla Avro i Kafki stosunek pytań jest 10–15× poniżej bazy, a jednak pobrania na NuGet są masowe. To znaczy, że ludzie z .NET w tych tematach **nie pytają, tylko instalują**. Nie da się na tej podstawie odróżnić "nikt tego nie robi w .NET" od "robią, ale nie ma gdzie pytać".
- Iceberg z 1 pytaniem w `c#` to albo pusty rynek, albo rynek, który jeszcze nie wie, że może. Spike (§5 pkt 3) i rozmowy z 3–5 zespołami .NET na Databricks/Snowflake/Fabric rozstrzygną to lepiej niż SO.
- `cobol`+`c#` = 31 pytań to dla tak niszowego tematu sporo. Potwierdza, że copybook w .NET istnieje jako problem.

### 8.2 Top PyPI (30 dni, 01.10.2026) a odpowiedniki w .NET

Przejrzałem ~400 najczęściej pobieranych pakietów PyPI pod kątem "dojrzałe w Pythonie, słabe lub brak w .NET". Większość jest pokryta (requests/httpx → HttpClient, pydantic → DataAnnotations/FluentValidation, tenacity → Polly, rich/typer → Spectre.Console, jsonschema → JsonSchema.Net, faker → Bogus, paramiko → SSH.NET, playwright, openpyxl → ClosedXML, structlog → Serilog, croniter → Cronos, mcp → oficjalny SDK, langchain/litellm → Semantic Kernel / Microsoft.Extensions.AI, tiktoken → Microsoft.ML.Tokenizers). Luki:

| Pakiet PyPI | Pobrania/30 dni | Co robi | Stan w .NET | Ocena |
|---|---|---|---|---|
| pyarrow + `pyarrow.dataset` | 333M | odczyt katalogu Parquet/Avro/CSV z partycjonowaniem hive na S3/GCS/ADLS, predicate pushdown, projekcja | Parquet.Net czyta pojedynczy plik; brak warstwy "dataset" (lista plików, partycje z nazw katalogów, pushdown po statystykach, scalanie schematów) | **wejście do Iceberga**: to samo API dla "surowego" lake'u i dla tabel Iceberg; ten sam kupiec, mniejsza bariera |
| fsspec + s3fs + adlfs + gcsfs | 563M + 303M | jeden interfejs plikowy nad S3/Azure/GCS/HDFS/local, glob, strumienie, cache | FluentStorage (następca Storage.Net aloneguida), Zio; żaden nie jest standardem, Azure/AWS SDK są osobne | warstwa pod dataset/Iceberg, nie produkt |
| awswrangler | 85M | pandas ↔ S3/Athena/Glue/Redshift w jednej linii | brak | potwierdza popyt na "dataset" w chmurze; sam w sobie za szeroki |
| narwhals / pandas / polars | 116M / 547M | DataFrame | Microsoft.Data.Analysis 0.23 preview | jak w §3 B3: nie na jedną osobę |
| snowflake-connector-python | 103M | natywny klient Snowflake z Arrow | Snowflake.Data (oficjalny, słaby), `Apache.Arrow.Adbc.Drivers.Interop.Snowflake` 6,8K | ADBC pokrywa, brak warstwy POCO |
| databricks-sdk | 82M | REST SDK Databricks | `Microsoft.Azure.Databricks.Client` 2,4M (tylko Azure, zarządzanie), brak oficjalnego SDK Databricks dla .NET | poza marką, Databricks może wydać w każdej chwili |
| sqlglot | 72M | parser/transpiler SQL | SqlParserCS 709K (tylko parsowanie) | odrzucone w §7.3 |
| networkx | 199M | grafy | QuikGraph (stare) | brak kupca B2B |
| rapidfuzz | 120M | fuzzy matching | FuzzySharp | mała luka |
| huggingface-hub, datasets, safetensors, tokenizers | 231M / 71M / 73M / 166M | ekosystem HF | TorchSharp częściowo | poza domeną |
| cbor2, msgpack, zstandard, lz4, brotli, flatbuffers, protobuf | 71M–619M | formaty | wszystkie mają dobre implementacje w .NET | brak luki |

### 8.3 Odkrycie: ADBC w .NET ma 1,5M pobrań i nikt nie mapuje wyników na obiekty

`Apache.Arrow.Adbc` 1,49M pobrań, `Apache.Arrow.Adbc.Client` 1,07M, sterowniki: Databricks 114K, Spark/Hive (Thrift) 119K, BigQuery 9K, Snowflake 6,8K, Flight SQL 21K. Wszystkie zwracają `Apache.Arrow.RecordBatch`. Nie ma w .NET nic, co zamienia strumień RecordBatch na `IAsyncEnumerable<T>` z POCO i z powrotem. Dodatkowy dowód: duński operator sieci Energinet opublikował własny `Energinet.DataHub.Core.Databricks.SqlStatementExecution` (198K pobrań, 17.0.1 sprzed 3 dni), bo nie było czym czytać wyników Databricks SQL do typów C#.

To zmienia ocenę "ArrowConvert" z §3 A3: to nie "wygoda" dla użytkowników Arrow, tylko brakujące ogniwo dla każdego, kto przez ADBC gada z Databricks, Snowflake, BigQuery, Dremio, DuckDB (Flight SQL). Ten sam kod obsłuży wyniki skanowania Iceberga. Przenieść z C do B jako `SolTechnology.Arrow` lub jako moduł Iceberga.

### 8.4 Spark Connect dla .NET

Microsoft zarchiwizował `.NET for Apache Spark` w 2024. Spark Connect (gRPC + Arrow) ma oficjalnych klientów Python/Scala/Go/Rust/Swift, w .NET: `GOEddie.Spark.Dotnet` 26,6K pobrań, 4.0.0-build.41 sprzed 14 dni, jeden autor (Ed Elliott), oraz martwy `Apache.Spark.Connect` 0.1.2-alpha z 2024. Kupiec: zespoły .NET na Databricks (Databricks Connect = Spark Connect) i Fabric. Pokrywa się z Iceberg/Arrow w warstwie dekodowania wyników. Nie budować równolegle; obserwować GOEddie, ewentualnie wnieść warstwę Arrow→POCO tam zamiast konkurować.

### 8.5 Spoza danych: co z top Maven/npm nie ma dobrego odpowiednika w .NET

Z pamięci (Maven Central i npm nie dały się odpytać z tego środowiska), tylko rzeczy z realną luką:

| Java / npm | .NET | Uwagi |
|---|---|---|
| Apache Tika (detekcja typu + ekstrakcja tekstu z ~1000 formatów) | brak (TikaOnDotNet przez IKVM, martwe) | kupiec: e-discovery, RAG on-prem, DLP; duży zakres, poza marką |
| Apache Camel (300+ konektorów integracyjnych) | NServiceBus/MassTransit/Rebus to szyny, nie konektory | za duże na jedną osobę |
| Apache Lucene | Lucene.NET 4.8 beta od 2017 | firmy biorą Elastic/Meilisearch, nie bibliotekę |
| Flink / Kafka Streams | Streamiz (community, przyzwoite) | stream processing w .NET to nisza niszy |
| jOOQ (typowany SQL) | linq2db, SqlKata | wystarczające |
| Drools / Camunda | NRules, Elsa | wystarczające lub SaaS |
| yjs / automerge | brak dojrzałego | odrzucone w §3 C |
| sharp (obrazy) | ImageSharp (komercyjny od 2024), SkiaSharp | pokryte |

Wniosek z całej sekcji: poza danymi (lakehouse, Arrow, mainframe) nie ma w .NET dziury, za którą firma zapłaci, a której nie zatka darmowa biblioteka albo port przez AI w weekend. Każda luka z tabel 8.2 i 8.5, która ma kupca z budżetem, leży w tym samym miejscu co Iceberg: .NET w świecie, który przeszedł na Pythona i JVM. Ścieżka wejścia wygląda tak: dataset nad surowym Parquet/Avro na S3/ADLS → Arrow↔POCO (ADBC, Spark Connect) → Iceberg → Delta. Każdy krok jest osobno użyteczny i każdy używa poprzedniego.

## 9. Jak łapać popyt poza parserami: metoda i wyniki (16.10.2026)

### 9.1 Radar NuGet: popularne, porzucone, jednoosobowe

Skrypt `scripts/nuget-radar.py` ściąga top N pakietów po pobraniach, odfiltrowuje Microsoft/System/runtime i dla każdego sprawdza datę ostatniego stabilnego wydania, liczbę właścicieli, deprecjację i licencję. Przebieg 16.10.2026, top 1500: po filtrze 620 pakietów, **202 bez stabilnego wydania od ponad roku**, w tym:

| Pakiet | Pobrania | Ostatnie stabilne | Uwagi |
|---|---|---|---|
| CsvHelper | 700M | 06.2025 | 1 właściciel |
| Portable.BouncyCastle | 521M | 10.2021 | zastąpione przez BouncyCastle.Cryptography |
| DnsClient | 498M | 07.2024 | 1 właściciel |
| prometheus-net | 334M | 01.2024 | 1 właściciel; OpenTelemetry przejmuje |
| AutoFixture | 331M | 11.2023 | |
| CommandLineParser | 261M | 05.2022 | System.CommandLine |
| Flurl / Flurl.Http | 179M / 129M | 12.2023 / 01.2024 | 1 właściciel |
| SpecFlow | 120M | 05.2022 | deprecated; fork Reqnroll w tygodnie |
| Shouldly | 129M | 01.2025 | |
| MathNet.Numerics | 78M | 04.2022 | |
| Docker.DotNet | 80M | 05.2023 | |
| Dapper.Contrib | 68M | 11.2020 | |
| FastMember | 66M | 05.2019 | 1 właściciel; AvroConvert ma własny fork |

Co z tego wynika: **staleness w top 1500 to prawie nigdy okazja komercyjna.** Pakiety są albo skończone (NCrontab, morelinq, Nito.*), albo zastąpione przez coś z BCL (CommandLineParser, Portable.BouncyCastle), albo w chwili śmierci dostają darmowy fork w kilka tygodni (SpecFlow → Reqnroll, FluentAssertions → AwesomeAssertions, Moq → NSubstitute). Jedyny wzorzec, w którym porzucenie tworzy płatny rynek, to gdy biblioteka była już płatna albo gdy domena jest za trudna na fork weekendowy. W top 1500 takiego przypadku nie ma. Radar warto puszczać co kwartał, ale jako system wczesnego ostrzegania o zależnościach i o tym, gdzie konkurencja słabnie, nie jako generator pomysłów.

### 9.2 Trzy wzorce, które naprawdę sprzedają biblioteki w .NET

Patrząc na to, kto w .NET bierze pieniądze za bibliotekę (nie za SaaS, nie za komponenty UI):

**A. Oficjalny stos za darmo + złe API → płatny wrapper.** OPC UA: OPC Foundation daje darmowy, potworny stack (6,4M pobrań), a obok żyją cztery płatne SDK: Traeger Opc.UaFx (496K + 975K), Softing (362K), OPC Labs QuickOPC (812K), Unified Automation. Każdy sprzedaje to samo: "simple & familiar .NET API" nad stosem Fundacji. To dokładnie relacja AvroConvert vs Apache.Avro i dowód, że ten model utrzymuje kilka firm naraz. Nie wchodzić w OPC UA (piąty gracz), ale szukać kolejnego takiego stosu. Kandydaci do sprawdzenia: Apache.Arrow (już w planie), OPCFoundation-podobne stacki w telekomunikacji (Diameter/SS7 – niszowe), HL7 FHIR (Firely już to robi), ISO 8583 (konflikt).

**B. Ryzyko regulacyjne, którego nie da się zrobić "prawie dobrze".** EPPlus, QuestPDF (PDF/A, PDF/UA), iText, PDF Tools: płacą, bo błąd kosztuje. Tu leżała e-fakturowa teza drugiej analizy i poległa na zatłoczeniu, nie na braku popytu. Lekcja: ryzyko regulacyjne sprzedaje, ale trzeba trafić w okno **przed** terminem albo w domenę, w której nikt nie chce brać odpowiedzialności.

**C. Ekosystem wyjechał gdzie indziej, a kupiec został w .NET.** Lakehouse (Iceberg/Delta/Arrow), mainframe (copybook), Spark Connect. Tu jest cała roadmapa.

### 9.3 Kandydaci spoza parserów, sprawdzeni

| Pomysł | Wzorzec | Stan w .NET | Kupiec | Ocena |
|---|---|---|---|---|
| **Maskowanie i subsetting baz pod środowiska testowe** (SQL Server, PostgreSQL): spójny podzbiór produkcji po kluczach obcych, deterministyczna anonimizacja PII z zachowaniem formatu i integralności, CLI + biblioteka | B | **zero** pakietów na NuGet dla "masking/anonymization/subsetting". Poza .NET: Greenmask (Go, tylko Postgres), Neosync (Go, open core), Jailer (Java, subsetting); komercyjnie Redgate Test Data Manager i Tonic.ai (tysiące USD/rok). Sklepy SQL Server to sklepy .NET | compliance (GDPR, DORA), DevOps w firmach z prod PII; płacą za brak wycieku do dev | **mocny, pierwszy kandydat spoza danych w ruchu**; trudność wysoka (graf FK, cykle, identity, temporal tables, Always Encrypted, wydajność na TB); produkt-narzędzie, nie tylko biblioteka |
| Biblioteka licencjonowania dla autorów bibliotek .NET (podpisane klucze offline, webhook Paddle/Polar/Stripe, grace, zero telemetrii) | A | 7 małych pakietów (Aegis 31K, reszta < 3K), każdy ISV pisze własne 200 linii, my też | autorzy bibliotek idący na komercję (rosnąca grupa po 2025) | mały rynek; zrobić jako **darmowy pakiet** wydzielony z AvroConvert 4.0, bo i tak powstanie; marketing wśród autorów |
| "NuGet License Radar": CLI sprawdzające drzewo zależności pod kątem pakietów, które przeszły na płatne licencje (AutoMapper 15+, MediatR 13+, MassTransit 9+, FluentAssertions 8+, EPPlus 5+, ImageSharp 3+, Hangfire Pro, Duende, SpecFlow EOL) | B | nuget-license (free, tylko SPDX), Snyk/FOSSA ($$, nie znają niuansów .NET) | prawnicy i compliance w firmach > 100 osób | **darmowy magnes**, nie produkt: baza zmian licencyjnych to mała fosa, ale ruch na soltechnology.dev z działów compliance, które potem kupują |
| OPC UA client z ludzkim API | A | 4 płatne SDK już to robią | przemysł | nie, piąty gracz |
| Generowanie dokumentów Word/PDF z szablonów + dane | B | Templater, Docmosis, Syncfusion (płatne); MiniWord, OpenXML (darmowe, prymitywne) | każdy ERP/back-office | popyt stały, ale rynek obsadzony przez graczy z 15-letnią przewagą |
| Podpis PDF (PAdES, LTV, timestamp) bez iText/Aspose | B | do zweryfikowania: PDFsharp 6 nie ma PAdES, PdfPig nie pisze; iText AGPL/komercyjny | regulowane firmy, e-podpis | **do sprawdzenia**, pasuje do wzorca B, nie pasuje do marki |
| Oficjalny SDK Paddle dla .NET | – | brak oficjalnego (Paddle ma Node/PHP/Python/Go/Java); nie udało się zweryfikować strony SDK | autorzy produktów na Paddle | darmowy, 2 tygodnie pracy, dobry PR wśród dokładnie tej grupy, która kupuje bibliotekę licencjonowania |

### 9.4 Co dopisać do roadmapy

1. **Metoda** (radar kwartalny + trzy wzorce) jako stała sekcja.
2. **Maskowanie/subsetting baz** jako czwarty produkt warunkowy, obok Copybooka. Inny kupiec niż Lake, ale ten sam dział zakupów (compliance ma budżet) i ta sama marka "szybkie .NET dla systemów z dużą ilością danych". Warunek: 5 rozmów z zespołami, które dziś robią kopie produkcji do dev ręcznie albo płacą Redgate.
3. **Darmowe magnesy** (licencjonowanie, License Radar, Paddle SDK) jako osobna lista; każdy z nich przyciąga dokładnie tę grupę, która kupuje produkty płatne.
