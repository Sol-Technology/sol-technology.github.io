# SolTechnology – roadmapa produktów

Stan: 16.10.2026. Źródła i dowody: `docs/ProductExploration.md`. Licencja bez zmian dla wszystkiego poniżej: PolyForm NC + Small Business za darmo, komercyjna przez Paddle, bez klucza (decyzja z 08.10.2026). Jedna licencja dla całej rodziny; wyjątek tylko dla kodu wnoszonego do cudzych projektów.

Ograniczenie: **jedna osoba, po godzinach, obok etatu.** Dlatego kolejność jest twarda i produkty są trzy, nie siedem.

## Produkty

| | Produkt | Jedno zdanie | Stan | Kupiec |
|---|---|---|---|---|
| 1 | **AvroConvert** | Avro ↔ obiekty C# bez codegen | istnieje, 4.0 w budowie | zespoły Kafki i danych w .NET |
| 2 | **SolTechnology.Lake** (nazwa robocza) | czytasz i piszesz dane w data lake'u z C# bez Sparka: katalogi Parquet/Avro, tabele **Iceberg**, potem Delta | nowy, główny zakład po 4.0 | zespoły .NET w firmach, które mają Databricks / Snowflake / Fabric / Trino / S3 |
| 3 | **CopybookConvert** | pliki z mainframe'a (COBOL copybook, EBCDIC, COMP-3) → obiekty C# / Avro | nowy, warunkowy | banki, ubezpieczyciele, integratorzy |
| 4 | **DataMask** (nazwa robocza) | spójny podzbiór produkcyjnej bazy SQL Server / PostgreSQL z zanonimizowanym PII pod środowiska testowe; CLI + biblioteka | nowy, warunkowy, pierwszy spoza parserów | compliance i DevOps w firmach z danymi osobowymi na produkcji |

Wszystko inne z researchu to albo funkcja jednego z tych czterech, albo darmowy magnes (sekcja niżej), albo odrzucone (sekcja na końcu).

## Jak łapać popyt (metoda, nie jednorazowy research)

Trzy wzorce, w których firmy .NET płacą za bibliotekę, a nie biorą darmowego forka:

- **A. Oficjalny stos za darmo + złe API → płatny wrapper.** OPC UA: darmowy stack OPC Foundation (6,4M pobrań) i obok cztery płatne SDK (Traeger, Softing, OPC Labs, Unified Automation), każdy sprzedaje "simple .NET API". To relacja AvroConvert vs Apache.Avro; model utrzymuje kilka firm naraz. Szukać kolejnego takiego stosu (Arrow już jest w planie).
- **B. Ryzyko, którego nie da się zrobić "prawie dobrze".** EPPlus, QuestPDF, iText, Redgate: błąd kosztuje, więc płacą. Trzeba trafić przed terminem regulacji albo w domenę, w której nikt nie chce brać odpowiedzialności (e-faktury przegrały na zatłoczeniu, nie na popycie).
- **C. Ekosystem wyjechał do Pythona/JVM, kupiec został w .NET.** Lakehouse, mainframe, Spark. Tu jest Lake i Copybook.

Narzędzie: `scripts/nuget-radar.py` (top N pakietów NuGet: ostatnie stabilne wydanie, liczba właścicieli, deprecjacja, licencja). Puszczać co kwartał. Przebieg 16.10.2026: 202 z 620 popularnych pakietów bez wydania od roku, ale żaden nie jest okazją komercyjną: są skończone, zastąpione przez BCL albo sforkowane w tygodnie (SpecFlow → Reqnroll). Radar służy do pilnowania własnych zależności i słabnącej konkurencji, nie do wymyślania produktów.

Czego nie robić: ogólnych bibliotek (mapper, asercje, CSV, HTTP client). Każda luka tam jest zatykana forkiem w dwa tygodnie, a cena spada do 14,95 USD (FluentAssertions).

---

## 1. AvroConvert

### 4.0 (teraz)
Licencja, typowany rdzeń, zgodność ze spec 1.12, otwarte issues. Szczegóły: `V4ReleasePlan.md`. Nic innego nie startuje przed 4.0.0.

### Funkcje w 4.x
- **Zgodność schematów offline** (BACKWARD/FORWARD/FULL, diff, fingerprinty). Darmowa, zamyka issue #73, materiał na README: "test zgodności w xUnit bez rejestru". Port `SchemaCompatibility` z Avro Java.

### Addon: Avro.Kafka 2.0 (warunkowy)
Serde POCO ↔ Confluent / Azure / Apicurio Schema Registry bez codegen. `Confluent.SchemaRegistry.Serdes.Avro` ma 84K pobrań dziennie i wymaga `avrogen`. Pakiet 3.0.0 istnieje, jest cienki.
Bramka (1 dzień, zaraz po 4.0): benchmark i porównanie funkcji z **Chr.Avro** (MIT, robi to samo). Wygrana → 2.0. Przegrana → pakiet w maintenance, temat zamknięty.

---

## 2. SolTechnology.Lake

Jedna biblioteka, wydawana etapami. Każdy etap działa sam i jest osobno reklamowalny, ale to jeden pakiet, jedna licencja, jeden nagłówek marketingowy: **"Iceberg dla .NET"**.

### Etap 1: katalog plików jako tabela
`Lake.Open("s3://bucket/events/")` → partycje hive z nazw katalogów, pomijanie plików po statystykach, scalanie schematów, `IAsyncEnumerable<T>`. Odpowiednik `pyarrow.dataset` (pyarrow: 333M pobrań/30 dni). W .NET Parquet.Net czyta jeden plik, warstwy katalogu nie ma. Większość firm ma lake bez formatu tabel, więc to od razu użyteczne.

### Etap 2: Arrow ↔ POCO jako publiczne API
Wewnętrzna warstwa dekodowania (`RecordBatch` → `T` i z powrotem), wystawiona publicznie, bo `Apache.Arrow.Adbc` ma 1,5M pobrań (sterowniki Databricks, Spark/Hive, Snowflake, BigQuery, Flight SQL) i wszystkie zwracają Arrow bez warstwy obiektowej. Energinet opublikował własny pakiet do czytania Databricks SQL do typów C# (198K pobrań), bo nie było czym. Ten sam kod obsłuży wyniki Spark Connect.

### Etap 3: Iceberg odczyt → Etap 4: Iceberg zapis
Zero oficjalnej implementacji w .NET (Java, Python, Rust, Go, C++ są). Snowflake, BigQuery, Databricks, OneLake, Redpanda, S3 Tables przeszły na Iceberg. Manifesty to pliki Avro, czyli parser z AvroConvert. Spec v2 stabilna od 2021, REST Catalog ma OpenAPI. Konkurencja: `EngineeredWood.Iceberg` 0.3.0, metadata-only, 373 pobrania.

**Spike (2 tygodnie) przed etapem 3, co musi wyjść:**
1. REST Catalog (Lakekeeper/Polaris w kontenerze): `loadTable`, OAuth2 client credentials, credential vending dla S3.
2. `metadata.json` v2 → snapshot → manifest list (Avro) → manifesty → data files z partycjami i statystykami.
3. Odczyt Parquet z projekcją i pushdownem po statystykach z manifestu.
4. **Delete files.** Tabela po `MERGE`/`DELETE` ze Sparka ma positional/equality deletes. Odczyt, który je ignoruje, zwraca po cichu złe dane. Albo je stosujemy, albo odmawiamy odczytu z jasnym błędem.
5. Czy Parquet.Net **zapisuje `field_id`** w schemacie Parquet (Iceberg tego wymaga) i wystawia statystyki row group po zapisie. Jeśli nie: ParquetSharp albo własny writer. Decyzja o zależności na lata.
6. Partition transforms: identity, bucket (Murmur3 wg spec, test zgodności z Javą), truncate, year/month/day/hour.

**Go/no-go po spike'u:** 5 rozmów z zespołami .NET na Databricks/Snowflake/Fabric/Trino. Mniej niż 2 "tak, zapłacimy" → Iceberg spada do obserwacji, Lake zostaje przy etapach 1–2 jako mniejszy produkt. Stack Overflow (1 pytanie `c#`+`apache-iceberg`) nie rozstrzyga; rozmowy tak.

### Etap 5: Delta Lake (opcjonalny)
Ta sama warstwa, drugi format. Świat Databricks/Fabric to dużo .NET-u. Protokół zmienia się częściej niż Iceberg, mniej synergii z Avro, a `delta-kernel-rs` ma FFI, więc ktoś może zbindować szybciej, niż my napiszemy. Dopiero po etapie 4.

### Ryzyka
- **Apache założy `iceberg-dotnet`.** Dziś brak śladu. Jeśli tak, nasza wartość przesuwa się na POCO, wydajność i wsparcie, czyli relacja AvroConvert vs Apache.Avro. Znany model.
- **EngineeredWood (Hagenlocher, Arrow PMC, Microsoft) trafi pod Fabric.** Konkurencja z darmowym i oficjalnym. Mitigacja: być pierwszym z kompletnym odczytem i zapisem; sprawdzać repo co kwartał.
- **Parquet.Net: jeden maintainer, polityka "no LLM".** Kodu z agentów tam nie upstreamujemy. Plan B: fork albo ParquetSharp.
- **Rynek może być mały.** Sygnał z SO dla lakehouse w .NET jest fatalny (załącznik). Dlatego go/no-go, nie wiara.

---

## 3. CopybookConvert

COBOL copybook + plik EBCDIC → model C# generowany z copybooka, deserializacja, strumieniowanie, most do Avro/Kafki. Jedyna naprawdę pusta nisza z całego researchu: na NuGet 2 martwe pakiety (2018, 2021). `cobol`+`c#` na SO: 31 pytań, czyli ludzie to robią. Wzorce w Javie: JRecord, Cobrix. Komercyjnie płaci się SnapLogic/Precisely.

Warunki wejścia, w tej kolejności:
1. **Umowa o pracę** – sprawdzić konflikt przed pierwszą linijką (domena blisko płatności).
2. Dane testowe: start z repo Cobrix (Apache 2.0, copybooki + pliki EBCDIC w testach), potem 2–3 firmy z prawdziwymi copybookami (dialekty IBM/Micro Focus, REDEFINES, OCCURS DEPENDING ON).
3. Niezależne od Lake; można robić równolegle, jeśli czas pozwoli, ale nie przed 4.0.

---

## 4. DataMask

Problem: zespoły kopiują produkcję do dev/test, bo syntetyczne dane nie odtwarzają błędów. GDPR i DORA tego zabraniają. Rozwiązania: ręczne skrypty (większość), Redgate Test Data Manager / Tonic.ai (tysiące USD rocznie), w Go darmowe Greenmask (tylko Postgres) i Neosync (open core). **Na NuGet zero pakietów** pod "masking / anonymization / subsetting". Sklepy SQL Server to sklepy .NET, a SQL Server ma najsłabsze pokrycie w narzędziach z Go.

Produkt: CLI + biblioteka. (1) Subsetting: wybierz 1% klientów, zabierz wszystko, co do nich należy przez klucze obce, z cyklami i tabelami słownikowymi. (2) Maskowanie: deterministyczne (ten sam PESEL → ten sam fałszywy PESEL w każdej tabeli), z zachowaniem formatu, sum kontrolnych i integralności. (3) Wyjście: do drugiej bazy, do plików (bcp/COPY), docelowo do Parquet przez Lake.

Dlaczego pasuje: wzorzec B (ryzyko), kupiec z budżetem (compliance), marka "szybkie .NET dla systemów z dużą ilością danych", zero konfliktu z pracą. Trudność wysoka: graf FK, identity, computed columns, temporal tables, Always Encrypted, wydajność na terabajtach. Tego nie napisze się z AI w weekend.

Warunki wejścia:
1. 5 rozmów z zespołami, które dziś robią kopie produkcji ręcznie albo płacą Redgate. Pytanie: "jak dziś robicie dane testowe i ile to kosztuje?" Mniej niż 2 "zapłacimy" → odkładamy.
2. Nie przed 4.0 i nie równolegle z etapem 3 Lake. Realnie: 2028 albo zamiast Copybooka, jeśli Copybook nie przejdzie walidacji.

---

## Darmowe magnesy

Małe pakiety, które przyciągają dokładnie tych, którzy kupują produkty płatne. Każdy do 2 tygodni pracy, MIT (wyjątek od jednej licencji, bo to nie produkty).

| Pakiet | Dla kogo | Skąd się bierze |
|---|---|---|
| Biblioteka licencjonowania (deklaracja licencji w kodzie, podpisane klucze offline, webhook Paddle/Polar/Stripe, grace, zero telemetrii) | autorzy bibliotek .NET idący na komercję | wydzielona z AvroConvert 4.0, bo i tak powstaje |
| NuGet License Radar (CLI: które zależności przeszły na płatne licencje: AutoMapper 15+, MediatR 13+, MassTransit 9+, FluentAssertions 8+, EPPlus 5+, ImageSharp 3+, Hangfire Pro, Duende, SpecFlow EOL) | prawnicy i compliance w firmach > 100 osób | baza zmian licencyjnych z researchu; ruch z działów, które potem kupują |
| Paddle SDK dla .NET | autorzy produktów na Paddle (brak oficjalnego SDK .NET, do potwierdzenia) | powstaje przy integracji sklepu AvroConvert |

## Obserwować, nie budować

| Temat | Dlaczego nie teraz |
|---|---|
| Spark Connect dla .NET | Microsoft zarchiwizował .NET for Apache Spark (2024); `GOEddie.Spark.Dotnet` 26,6K, aktywny, jeden autor; nie konkurować, raczej wnieść tam Arrow→POCO z Lake |
| Databricks SDK / SQL dla .NET | ADBC + `Microsoft.Azure.Databricks.Client` (2,4M) pokrywają większość; Databricks może wydać w każdej chwili |
| Unified storage (fsspec dla .NET) | FluentStorage/Zio; warstwa pod Lake, nie produkt |
| CDC (Debezium bez JVM) | Postgres się commodityzuje (Wallaby, Excalibur, Npgsql.Replication); trudna część to SQL Server i gwarancje dostarczenia = produkt operacyjny; ewentualnie darmowy sink Avro do Wallaby jako reklama Avro.Kafka |
| DataFrame / Polars dla .NET | Microsoft.Data.Analysis w preview od 2019; lata pracy albo bindingi Rust na 6 platform |
| ORC | martwe w .NET, popyt maleje; reader w Lake na życzenie klienta |
| EDI X12/EDIFACT | luka na uczciwą licencję po EdiFabric istnieje, ale setki transaction setów i zero wspólnego z marką |

## Odrzucone

| Temat | Dlaczego |
|---|---|
| E-faktury UE (KSeF FA(3), EN 16931, UBL/Peppol, XRechnung, Factur-X) | najbardziej zatłoczona nisza na NuGet: ZUGFeRD-csharp 1,5M z komercyjnym następcą, `International.EInvoicing` (pełny zestaw), Soneta.KSeF 137K, kilkanaście nowych pakietów w 60 dni; terminy KSeF minęły; inny kupiec |
| CSV | CsvHelper ma złe API, ale Sep/Sylvan są darmowe i szybsze; nikt nie zapłaci |
| Parquet jako produkt | Parquet.Net 181K/dzień, MIT, dobre; zależność Lake, nie konkurent |
| ISO 20022 / SWIFT | konflikt z pracą w Mastercard |
| Transpiler SQL (sqlglot) | MIT do sportowania, migracje jednorazowe, AI to robi |
| HL7 v2, PDF/UA, RDLC/SSRS, Peppol AS4, docling, DMN | darmowe i utrzymywane alternatywy, SaaS, albo lata certyfikacji; brak związku z marką |
| Klony MediatR/MassTransit, workflow, PDF, Protobuf/MessagePack/gRPC | .NET ma tu dobre lub darmowe rozwiązania |
| CRDT/Automerge, H3, CEL, jq, YAML, Excel | brak luki albo brak kupca B2B |
| Apache Tika, Camel, Lucene, Flink dla .NET | realne luki, ale za duże na jedną osobę albo firmy biorą SaaS/Elastic |
| networkx, rapidfuzz, docx, OCR, ffmpeg | .NET poniżej bazy na SO, ale darmowe biblioteki wystarczają |
| OPC UA client z ludzkim API | wzorzec A działa, ale już jest 4 płatnych graczy |
| Generowanie Word/PDF z szablonów | Templater, Docmosis, Syncfusion z 15-letnią przewagą |
| Podpis PDF (PAdES) bez iText/Aspose | wzorzec B, luka prawdopodobna, ale nic wspólnego z marką; do sprawdzenia, jeśli kiedyś zabraknie tematów |

## Załącznik: sygnał ze Stack Overflow

Stosunek pytań `c#` do `python`/`java` dla tematu; baza dla wszystkich pytań 0,74–0,85. parquet 0,13, avro 0,09, kafka 0,06, snowflake 0,07, databricks 0,006, spark 0,005, delta-lake 0,004, iceberg 0,003, microsoft-fabric 0,12 (3 pytania). Przy Avro i Kafce pobrania na NuGet są mimo to masowe (Confluent.Kafka 1,2M/dzień), więc ludzie z .NET w tych tematach instalują, a nie pytają. SO nie odróżnia "nikt tego nie robi w .NET" od "robią, ale pytają LLM-a". Stąd rozmowy jako kryterium, nie SO.
