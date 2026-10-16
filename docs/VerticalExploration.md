# Eksploracja: aplikacje branżowe i obowiązkowe, poza bibliotekami

Stan: 16.10.2026. Osobny tor od `ROADMAP.md` (biblioteki). Terminy oznaczone ✓ zweryfikowane na gov.pl 16.10.2026; pozostałe z pamięci, **do potwierdzenia przed jakąkolwiek decyzją**.

## 1. Na czym polega różnica

Biblioteka: kupuje programista, instaluje sam, nie dzwoni. Aplikacja dla kantoru czy dentysty: kupuje właściciel firmy, trzeba ją hostować, utrzymywać, odbierać telefony, podpisać umowę powierzenia danych, często pojechać na wdrożenie. Rynek software'u dla polskich MŚP jest zatłoczony (Comarch, Symfonia, enova, wFirma, iFirma, Proassist, Prodentis, setki mniejszych) i wygrywa się tam sprzedażą i wsparciem, nie kodem. Dla jednej osoby po godzinach to inna liga.

Jest jeden wyjątek: **małe firmy kupują software prawie wyłącznie wtedy, gdy zmusza je nowy obowiązek z terminem.** KSeF, e-Doręczenia, system kaucyjny, JPK. Wtedy przez 6–18 miesięcy jest okno, w którym kupują wszystko, co działa, bo nie mają wyboru. Po oknie rynek się zamyka i zostają ci, którzy weszli pierwsi.

Dlatego metoda dla tego toru to nie "jaka branża", tylko **"jaki obowiązek, kiedy, dla ilu podmiotów, czy da się self-serve"**.

### Filtry, bez których nie wchodzimy

1. **Self-serve.** Klient rejestruje się, płaci kartą, używa. Zero wdrożeń, zero integracji na zamówienie. Inaczej to nie produkt, tylko usługa.
2. **Bez danych wrażliwych u nas**, jeśli się da. Medyczne (dentysta) = umowy powierzenia, audyty, odpowiedzialność. Przetwarzanie w przeglądarce (WASM) albo on-premise zamiast chmury tam, gdzie to możliwe.
3. **Bez konfliktu z etatem.** Płatności, FX (kantor), karty: sprawdzić umowę przed czymkolwiek.
4. **Okno popytu ≥ 6 miesięcy przed terminem**, bo tyle trwa zrobienie i zauważenie produktu.
5. **Populacja × skłonność do płacenia.** 1,3 mln rolników × 0 zł = 0. 8 tys. firm > 150 pracowników × 2 tys. zł = rynek.

## 2. Kalendarz obowiązków 2026–2028 (okna popytu)

| Termin | Obowiązek | Kogo dotyczy (PL) | Co trzeba zrobić w sofcie | Kto już to robi | Okno |
|---|---|---|---|---|---|
| ✓ od 01.10.2026 | **e-Doręczenia** dla firm z CEIDG zarejestrowanych przed 2025 (wcześniej: KRS od 04.2025, zawody zaufania od 01.2025) | ~2,5 mln JDG; pośrednio ~50 tys. biur rachunkowych, które obsługują ich korespondencję | skrzynka, integracja API (Poczta Polska / KDU), archiwizacja, obsługa wielu klientów z jednego panelu | moduły w Comarch/Symfonia/enova; interfejs Poczty Polskiej jest zły; standalone dla biur rachunkowych: do sprawdzenia | **otwarte teraz**, 12–18 mies. |
| ✓ od 10.2025 | **System kaucyjny** | sklepy > 200 m² obowiązkowo, mniejsze dobrowolnie; producenci napojów | rozliczenia z operatorami, ewidencja zwrotów, POS | dostawcy POS i operatorzy (kilku) | zamyka się; zostaje nisza małych sklepów bez POS |
| 02.2026 / 04.2026 (minęło) | KSeF FA(3) | wszyscy podatnicy VAT | – | zatłoczone (patrz `ProductExploration.md` §7) | zamknięte |
| 07.06.2026 (transpozycja, PL spóźniona) → pierwsze raporty 06.2027 | **Jawność wynagrodzeń** (dyrektywa 2023/970): raport luki płacowej, "praca tej samej wartości", prawo pracownika do informacji | > 150 pracowników od 2027 (ok. 8–10 tys. firm w PL, ~100 tys. w UE), > 100 od 2031 | wczytaj listę płac → analiza luki po kategoriach stanowisk → raport zgodny z wzorem; wycena stanowisk | SaaS zagraniczne (Syndio, Figures, PayAnalytics, beqom), moduły w HR-ach, Excel; polskich self-serve mało | **otwiera się w 2026**, szczyt 2027 |
| 02.08.2026 (część może przesunąć "Digital Omnibus") | **AI Act**: obowiązki dla systemów wysokiego ryzyka, rejestr, logowanie, nadzór | wdrażający AI w HR, kredytach, edukacji, infrastrukturze | inwentarz systemów AI, ocena ryzyka, dokumentacja | Big4, SaaS GRC (OneTrust, Vanta), dziesiątki startupów | zatłoczone, kupiec duży |
| 01.01.2026 start okresu definitywnego, pierwsza deklaracja 30.09.2027 | **CBAM**: importerzy stali, aluminium, cementu, nawozów, wodoru, energii; próg 50 t/rok wyłącza ~90% importerów | kilka tysięcy firm w PL powyżej progu | zbieranie danych emisyjnych od dostawców, obliczenia wg metodologii KE, deklaracja, zakup certyfikatów | agencje celne, Big4, SaaS (CBAM-tools, Greenly), moduły SAP | 2026–2027, kupiec średni, temat techniczny |
| 30.12.2026 duże i średnie, 30.06.2027 mikro i małe (po przesunięciu z 2024; w 2025 KE proponowała dalsze uproszczenia, **sprawdzić stan**) | **EUDR** (rozporządzenie 2023/1115): oświadczenie należytej staranności w TRACES z geolokalizacją działek dla drewna, mebli, papieru, kawy, kakao, soi, kauczuku, bydła | **Polska = największy eksporter mebli w UE**: ~25 tys. firm meblarskich i drzewnych, do tego palarnie kawy, producenci czekolady, importerzy opon, pasz | zbieranie poligonów od dostawców, walidacja GeoJSON, ocena ryzyka kraju, generowanie DDS, przekazywanie numerów DDS w dół łańcucha | osapiens, Preferred by Nature, TradeAware, Sourcemap, SAP; dla polskich MŚP meblarskich: izby branżowe i Excel | **2026–2027**, ryzyko kolejnego przesunięcia |
| 18.02.2027 | **Paszport baterii** (2023/1542) dla baterii EV i przemysłowych > 2 kWh; pierwszy obowiązkowy Digital Product Passport | producenci i importerzy baterii, w PL kilkadziesiąt firm (LG, Northvolt-podobne, integratorzy magazynów energii) | DPP: dane, QR, API, hosting przez cykl życia | konsorcja (Battery Pass), SaaS (Circularise, Spherity) | niszowe, ale pierwsze DPP; tekstylia i elektronika później (2027–2030) |
| 2026 (ustawa o KSC w toku) | **NIS2 / KSC**: podmioty kluczowe i ważne, rejestr, incydenty w 24 h, audyty | kilkanaście tysięcy podmiotów w PL | GRC, rejestr aktywów, zgłaszanie do CSIRT | zatłoczone (GRC SaaS, integratorzy) | kupiec duży, sprzedaż konsultingowa |
| od 01.01.2026 (rozp. 2023/564) | **Elektroniczna ewidencja zabiegów ochrony roślin** | ~1,3 mln gospodarstw, realnie ~200 tys. towarowych | prosta ewidencja z kodami środków, eksport dla PIORiN | darmowe aplikacje ARiMR/MRiRW, 365FarmNet, Agrivi, polskie apki | skłonność do płacenia bliska zeru |
| 2026 pilotaż → rozszerzanie | **Centralna e-Rejestracja** (P1): kardiologia, mammografia, cytologia, potem więcej | placówki NFZ | integracja HIS/gabinetowego z P1 | robią dostawcy systemów gabinetowych; darmowa aplikacja gabinet.gov.pl dla małych | nie dla nowego gracza |
| 07.2027 | **eFTI** (elektroniczne informacje o transporcie towarów), e-CMR | przewoźnicy, spedycje | platformy eFTI certyfikowane | duzi gracze TMS | poza zasięgiem |
| 30.06.2026 (koniec okresu przejściowego w PL, **sprawdzić**) | **MiCA / polska ustawa o kryptoaktywach**: licencja CASP, travel rule, monitoring | kantory krypto, bitomaty, giełdy (kilkaset podmiotów) | KYC/AML, travel rule, raportowanie | Sumsub, Notabene, Chainalysis | **konflikt z etatem**, nie |
| 2030 | ViDA: raportowanie cyfrowe VAT w UE | wszyscy | – | za wcześnie | – |

Branże z pytania, bez nowego obowiązku-katalizatora:
- **Kantory stacjonarne** (~4,5 tys. w PL): obowiązki AML/GIIF i raporty NBP od lat, software istnieje (kilku lokalnych dostawców), rynek malejący, do tego FX = ryzyko konfliktu z etatem. Nie.
- **Dentyści** (~40 tys. praktyk): EDM, e-recepta, e-skierowanie już wdrożone; 10+ dostawców (Prodentis, Estomed, Dentico, Proassist, iGabinet, Medfile, Docplanner). Dane medyczne. Nie.
- **ZUS/KRUS**: ZUS ma PUE/eZUS i API dla płatników, obsługują to systemy kadrowo-płacowe (Płatnik za darmo). KRUS nie wystawia API dla firm trzecich. Nie ma tu produktu dla nowego gracza.

## 3. Kandydaci, którzy przeszli filtry

### 3.1 Raport luki płacowej (jawność wynagrodzeń) – najlepszy w tym torze

- **Produkt:** aplikacja web, do której HR wrzuca eksport z listy płac (CSV/XLSX), przypisuje pracowników do kategorii "pracy tej samej wartości" (kreator wyceny stanowisk wg kryteriów dyrektywy: umiejętności, wysiłek, odpowiedzialność, warunki), dostaje raport luki płacowej w formacie wymaganym przez ustawę, analizę "co jeśli" i listę pracowników, którym trzeba odpowiedzieć na wniosek o informację.
- **Dlaczego self-serve działa:** dane nie muszą opuszczać przeglądarki. Przetwarzanie lokalnie (WASM/JS), eksport PDF, zero PII na serwerze. To od razu zamyka temat umów powierzenia i jest argumentem sprzedażowym wobec SaaS-ów, które chcą całej listy płac w swojej chmurze.
- **Kupiec:** HR i compliance w firmach > 150 pracowników. W Polsce 8–10 tys., w UE ~100 tys. Budżet jest (kara + ryzyko pozwów o dyskryminację płacową z odwróconym ciężarem dowodu).
- **Okno:** ustawa w Polsce spóźniona (termin transpozycji 07.06.2026), pierwsze raporty za 2026 do czerwca 2027. Produkt gotowy na początek 2027 trafia w szczyt.
- **Konkurencja:** zagraniczne SaaS od 5–20 tys. EUR/rok (celują w korporacje), moduły w dużych HR-ach (dla ich klientów), Excel. Luka: firmy 150–1000 osób bez SAP SuccessFactors, z Optimą/enovą/Symfonią, które chcą zapłacić 2–5 tys. zł i mieć spokój.
- **Ryzyka:** polska ustawa może przesunąć terminy; PIP może opublikować darmowy arkusz; metodyka "tej samej wartości" jest sporna prawnie, więc produkt musi mieć partnera-prawnika do treści. Model na jeden kraj trzeba zrobić pierwszy, ale dyrektywa jest wspólna, więc skalowanie na DE/CZ/SK to lokalizacja, nie nowy produkt.
- **Walidacja (30 dni):** landing page + lista oczekujących; 10 rozmów z HR-ami firm 150–500 osób ("jak policzycie lukę za 2026?"); sprawdzić projekt ustawy w RCL i wzór raportu.

### 3.2 e-Doręczenia dla biur rachunkowych i kancelarii

- **Produkt:** jeden panel do skrzynek e-Doręczeń wielu klientów (biuro rachunkowe prowadzi 100–300 firm, od 01.10.2026 każda ma skrzynkę), automatyczny odbiór, archiwizacja z dowodami doręczenia, alerty terminów, eksport do systemu księgowego.
- **Dlaczego teraz:** ✓ obowiązek dla 2,5 mln JDG wszedł 01.10.2026; biura rachunkowe są wąskim gardłem i mają budżet (płacą per klient).
- **Do sprawdzenia przed czymkolwiek:** (1) czy API Poczty Polskiej / KDU jest dostępne dla integratorów na warunkach self-serve, czy wymaga umowy i certyfikacji; (2) czy pełnomocnictwo do skrzynki klienta da się nadać masowo; (3) co już wypuścili Comarch, Symfonia, wFirma, iFirma, Saldeo, i czy jest standalone dla biur z różnymi systemami. Jeśli API jest otwarte i standalone nie ma, okno jest realne na 12 miesięcy.
- **Ryzyko:** biura rachunkowe kupują od dostawcy swojego systemu księgowego; standalone sprzedaje się tylko do tych, którzy mają kilka systemów naraz.

### 3.3 EUDR dla polskich MŚP meblarskich i drzewnych

- **Produkt:** zbieranie od dostawców geolokalizacji działek (formularz dla dostawcy, walidacja GeoJSON/poligonów, limity rozmiaru TRACES), ocena ryzyka wg kraju i benchmarkingu KE, generowanie i składanie DDS przez API TRACES, przekazywanie numerów referencyjnych klientom w dół łańcucha, archiwum 5 lat.
- **Dlaczego Polska:** największy eksporter mebli w UE, ~25 tys. firm drzewnych i meblarskich, większość mała, dostawcy drewna lokalni (Lasy Państwowe wystawiają dane), a odbiorcy (IKEA, sieci DIY w DE) będą żądać DDS. Pattern B z lokalną przewagą.
- **Ryzyka:** EUDR przesunięto raz (2024), w 2025 KE proponowała uproszczenia i kolejne zmiany; jeśli przesuną znowu, okno ucieka. Konkurencja korporacyjna (osapiens) nie zejdzie do firmy z 30 pracownikami, ale izby branżowe mogą dać darmowe narzędzie.
- **Walidacja:** stan prawny na dziś (data stosowania dla MŚP), rozmowy z 5 firmami meblarskimi 20–200 osób i jedną palarnią kawy.

### 3.4 CBAM dla importerów stali i aluminium (rezerwowy)

Kupiec realny (importerzy powyżej 50 t/rok), temat obliczeniowy (pasuje do umiejętności), ale sprzedaż idzie przez agencje celne i doradców, a nie self-serve. Obserwować; wejść tylko jako narzędzie dla agencji celnych, jeśli któraś poprosi.

## 4. Odrzucone w tym torze

| Temat | Dlaczego |
|---|---|
| Kantory, krypto-kantory (MiCA) | konflikt z etatem; rynek mały lub obsadzony |
| Dentyści, gabinety, Centralna e-Rejestracja | dane medyczne, 10+ dostawców, integracje P1 robią oni |
| ZUS/KRUS | brak produktu: ZUS obsługują systemy płacowe i darmowy Płatnik, KRUS nie ma API |
| KSeF, system kaucyjny | okno zamknięte |
| AI Act, NIS2/KSC, DORA | GRC = sprzedaż konsultingowa do dużych, zatłoczone |
| Ewidencja zabiegów, aplikacje dla rolników | skłonność do płacenia bliska zeru, darmowe narzędzia państwowe |
| Paszport baterii / DPP | za wcześnie i za mało podmiotów w PL; wrócić przy tekstyliach (2027+) |
| eFTI, e-CMR | certyfikowane platformy, duzi gracze |
| Sygnaliści, dostępność (EAA), PPK | okna zamknięte, SaaS-y już są |

## 5. Jak to łapać na bieżąco (metoda)

1. **Kalendarz obowiązków**: raz na kwartał przejrzeć (a) wykaz prac legislacyjnych RCL i Dziennik Ustaw, (b) EUR-Lex: akty z datą stosowania w ciągu 24 miesięcy, (c) komunikaty MF, MC, MKiŚ, MRPiPS. Dla każdego: data, populacja, czy jest darmowe narzędzie państwowe, czy obowiązek da się spełnić bez software'u.
2. **Popyt wyszukiwany**: frazy typu "program do X", "jak złożyć X", "X api" w Google Trends / Senuto / Ahrefs; wzrost na 6 miesięcy przed terminem to sygnał, brak wzrostu to brak rynku.
3. **Populacja**: GUS/CEIDG po PKD, liczby z izb branżowych; pomnożyć przez realistyczną cenę roczną i udział 1–3%. Jeśli wychodzi mniej niż 300 tys. zł rocznie przy 2% rynku, nie warto.
4. **Konkurencja**: Google w trzech językach, Capterra/GetApp, moduły u dużych dostawców ERP; jeśli duży ERP ma to w cenie, rynek jest tylko wśród jego nie-klientów.
5. **10 rozmów** z potencjalnymi kupcami zanim powstanie linijka kodu; **landing page z listą oczekujących** mierzona z ruchu na frazy z pkt 2.
6. **Pierwszy płatny pilot** (nawet symboliczny) przed pełnym MVP.

## 6. Werdykt dla tego toru

Tor branżowy to inne przedsięwzięcie niż SolTechnology: inny kupiec, inna sprzedaż, wsparcie, hosting, inna marka. Jeśli wchodzić, to w jeden temat, self-serve, bez danych u siebie, w oknie regulacyjnym. Z całego kalendarza taki jest jeden: **raport luki płacowej**, z e-Doręczeniami dla biur rachunkowych jako drugim, zależnym od dostępności API. EUDR jako opcja, jeśli KE przestanie przesuwać termin.

Nie łączyć tego z roadmapą bibliotek ani czasowo (dopiero po 4.0), ani marketingowo (osobna domena i nazwa).

## 7. Gdzie fizycznie łapać zlecenia i klientów (stan 16.10.2026)

Dwa różne cele: (a) **zlecenia**, czyli ktoś już napisał "potrzebuję X" i ma budżet; (b) **klienci na własny produkt**, czyli miejsca, gdzie siedzą ludzie z problemem, zanim ogłoszą zapotrzebowanie. Pierwsze daje gotówkę i wiedzę o domenie, drugie daje produkt.

### 7.1 Portale ze zleceniami: co tam naprawdę jest

| Portal | Co tam jest (sprawdzone) | Budżety | Jak używać |
|---|---|---|---|
| **Baza Konkurencyjności** (bazakonkurencyjnosci.funduszeeuropejskie.gov.pl) | Każda firma, która dostała dotację UE (FENG, Dig.IT, KPO, programy regionalne) i kupuje za > 50 tys. zł netto, **musi** opublikować tu zapytanie ofertowe. To jedyne publiczne miejsce, gdzie widać popyt MŚP na software **z zagwarantowanym budżetem**: "system do zarządzania produkcją", "aplikacja B2B", "integracja ERP", "platforma e-learningowa". Strona ładuje się przez JS, nie ma RSS. | 50 tys. – kilka mln zł, zwykle 100–500 tys. | Założyć konto, ustawić powiadomienia na kategorie "Usługi IT" / "Dostawy > oprogramowanie" i słowa kluczowe; sprawdzać 2× w tygodniu. Oferty wymagają formalnej odpowiedzi (terminy 7–14 dni). Uwaga: część zapytań jest pisana pod z góry wybranego wykonawcę. |
| **Useme** (useme.com/pl/jobs) | Prawdziwe potrzeby małych firm: dziś na pierwszej stronie "oprogramowanie dla stadniny" (pensjonat dla koni, dziś zeszyty i Excel), "dedykowany CRM dla firmy usługowej", "aplikacja dla pośredników z własnym serwerem", "programista ASP.NET Core do rozwoju platformy", "naprawa wysyłki korekt do KSeF w enova365". | 2–30 tys. zł, rzadko więcej | Nie jako źródło przychodu (stawki niskie), ale jako **darmowe badanie rynku**: codziennie 20–40 nowych zleceń pokazuje, czego małe firmy szukają i jakimi słowami. Zlecenie typu "stadnina" to gotowy wywiad z klientem. Useme rozlicza bez działalności, co przy etacie jest wygodne. |
| **Oferia.pl, Fixly, OLX Usługi** | drobnica: strony WWW, sklepy, naprawy | < 10 tys. zł | pominąć |
| **Upwork / Freelancer / Toptal** | globalne; .NET + data engineering + Kafka/Avro ma tam realny popyt (stawki 60–120 USD/h za seniora) | godzinowe | Jeśli celem jest gotówka na finansowanie produktu: Upwork z profilem "Avro/Kafka/.NET performance" daje leady od firm, które używają AvroConvert. Jeśli celem jest produkt: słabe, bo zlecenia są projektowe. |
| **platformazakupowa.pl, ezamowienia.gov.pl, TED** | zamówienia publiczne; dziś pod "oprogramowanie" 23 postępowania i prawie wszystkie to sprzęt + licencje Microsoft/ESET, albo utrzymanie AMMS w szpitalu | duże, ale dla dostawców sprzętu i integratorów | pominąć, chyba że jako podwykonawca integratora |
| **Clutch, GoodFirms, Sortlist** | katalogi software house'ów, leady inbound z zagranicy | średnie i duże, ale konkurencja 500 firm | dopiero z marką i referencjami |

Wniosek: **jedyny portal, który łączy MŚP, budżet i software na zamówienie, to Baza Konkurencyjności.** Useme to termometr popytu. Reszta to albo sprzęt, albo drobnica.

### 7.2 Dotacje, które tworzą kupców

Firma z dotacją ma pieniądze "znaczone" na software i termin, w którym musi je wydać. Programy aktywne lub ogłaszane w 2026 (sprawdzić aktualne nabory na funduszeeuropejskie.gov.pl i parp.gov.pl):
- **Dig.IT** (ARP, FENG): granty na transformację cyfrową MŚP przemysłowych, do 1,2 mln zł; beneficjenci kupują systemy MES, integracje, analitykę danych. Lista beneficjentów jest publiczna; każdy z nich będzie publikował zapytania w Bazie Konkurencyjności.
- **Ścieżka SMART** (PARP/NCBR): moduł cyfryzacja.
- **KPO: Cyberbezpieczne Wodociągi, HoReCa, cyfryzacja MŚP** (zależnie od naboru).
- **Regionalne programy FE 2021–2027**: "cyfryzacja MŚP" w większości województw.
- **BUR (Baza Usług Rozwojowych)**: szkolenia i doradztwo dofinansowane do 80%; jeśli produkt ma komponent szkoleniowy (np. "jak policzyć lukę płacową"), da się go sprzedać przez BUR firmom, które same nie zapłaciłyby pełnej ceny.

### 7.3 Gdzie siedzą klienci na dwa główne tematy

**Luka płacowa (HR w firmach 150–1000 osób):**
- Grupy FB: "Kadry i płace", "HR-owcy", "HR Business Partner Polska", "Specjaliści ds. wynagrodzeń" – po kilkanaście–kilkadziesiąt tysięcy członków, codziennie pytania o nowe przepisy.
- LinkedIn: hasztag #jawnośćwynagrodzeń, webinary kancelarii (PwC Legal, Raczkowski, Lubasz, DZP, Sedlak & Sedlak) – kancelarie **szukają narzędzi**, które mogą pokazać klientom; partnerstwo "kancelaria daje treść, my dajemy kalkulator" to najszybsza droga do pierwszych 10 klientów.
- Konferencje: HR Tech Summit, Wynagrodzenia (Sedlak), Kongres Kadry.
- Sedlak & Sedlak, Hays, Antal publikują raporty płacowe – ich czytelnicy to kupcy.
- Systemy HR, które nie mają modułu: Optima, enova, Symfonia, Sage, TETA – ich partnerzy wdrożeniowi (setki małych firm) chętnie dosprzedadzą gotowe narzędzie.

**e-Doręczenia (biura rachunkowe):**
- Grupy FB: "Biura Rachunkowe" (ok. 40 tys.), "Księgowi", "Samodzielni Księgowi" – od 1.10.2026 lawina pytań o skrzynki klientów.
- SKwP (Stowarzyszenie Księgowych w Polsce), oddziały regionalne: szkolenia, newslettery.
- Fora: forum.infor.pl, gofin.pl.
- Konferencje: Kongres Biur Rachunkowych, Forum Księgowych.
- Partnerzy: Saldeo, wFirma dla biur, iFirma, Comarch Optima partnerzy – sprawdzić, czy mają już panel multi-skrzynkowy; jeśli nie, oni są kanałem.

**EUDR (meblarze, drzewiarze):**
- OIGPM (Ogólnopolska Izba Gospodarcza Producentów Mebli), Polska Izba Gospodarcza Przemysłu Drzewnego – oba organizują webinary EUDR i szukają narzędzi dla członków.
- Targi: DREMA i Meble Polska (Poznań), Furnica.
- Klienci końcowi wymuszający DDS: działy zakupów IKEA, JYSK, OBI, Leroy Merlin – ich dostawcy to lista potencjalnych klientów.

### 7.4 Jak złapać pierwszy temat: plan na 30 dni, zero kodu

1. **Dzień 1–3.** Konto w Bazie Konkurencyjności z alertami (kategorie IT + słowa: "system", "aplikacja", "integracja", "platforma", "dane"). Konto na Useme, codzienny przegląd kategorii Programowanie i IT. Zapisać się do 3 grup FB (HR, biura rachunkowe, meblarze) i czytać, nie pisać.
2. **Dzień 1–7.** Landing page pod jeden temat (luka płacowa): nagłówek "Policz lukę płacową za 2026 w 15 minut, dane nie opuszczają Twojej przeglądarki", formularz na e-mail, FAQ o ustawie. Osobna domena, nie soltechnology.dev. Google Ads na 10 fraz ("raport luki płacowej", "jawność wynagrodzeń narzędzie", "kalkulator luki płacowej") z budżetem 300–500 zł, żeby zmierzyć, czy ktoś w ogóle tego szuka.
3. **Dzień 7–21.** Napisać do 5 kancelarii i 5 doradców HR, którzy robią webinary o jawności wynagrodzeń: "mam kalkulator, który liczy to, co pokazujecie na slajdach; chcecie go pokazać uczestnikom?" Jedna zgoda = 50–200 adresów HR-owców z problemem.
4. **Dzień 7–30.** 10 rozmów (po 20 minut) z HR-ami firm 150–500 osób z własnej sieci i LinkedIn. Jedno pytanie: "jak policzycie lukę za 2026 i ile jesteście gotowi za to zapłacić?" Notować dosłowne odpowiedzi.
5. **Dzień 30.** Decyzja: ≥ 30 adresów na liście i ≥ 3 osoby mówiące "zapłacimy 2–5 tys." → budować MVP (przeglądarkowy, bez backendu z danymi). Mniej → zamknąć landing, wziąć następny temat z kalendarza (e-Doręczenia), powtórzyć.

Równolegle, bez ryzyka: odpowiedzieć na 1–2 zlecenia z Useme typu "stadnina" / "CRM dla firmy usługowej" wyłącznie w celu odbycia rozmowy, nawet jeśli zlecenia się nie weźmie. To najtańszy sposób, żeby usłyszeć, jak mała firma opisuje swój problem.
