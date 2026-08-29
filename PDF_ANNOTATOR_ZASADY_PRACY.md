# Zasady pracy – PDF Annotator (Moodle)

**Zakres stosowania:** Ten dokument dotyczy wyłącznie projektu **PDF Annotator** (plugin Moodle `mod/pdfannotator`). Zasad tych nie stosować automatycznie w innych workspace’ach ani projektach.

---

## 1. Cel dokumentu

- Jedno miejsce z zasadami pracy przy tym projekcie.
- Minimalizacja tokenów: AI i człowiek odwołują się do tego pliku zamiast do wielu źródeł.

---

## 2. Zakres zmian

- Nie zmieniać kodu poza pluginem `mod/pdfannotator/`.
- Pliki objęte workflow: `shared/index.js` (chroniony), opcjonalnie `view.php`, `styles.css`, `fullscreen_enhanced.js` – w zależności od skryptu i backupu.
- **Tylko to, o co poproszono:** realizować wyłącznie elementy wyraźnie opisane w poleceniu użytkownika. Bez dodawania „ulepszeń”, domyślnych interpretacji ani zmian w parametrach, których użytkownik nie wymienił. Przykład: jeśli podano nową wartość paddingu w jednym wymiarze lub ogólnie „ciaśniejszy pion”, należy zachować istniejący padding poziomy (np. `12px`), o ile użytkownik go nie zmienił — skrót `padding: 0.17em` dla wszystkich boków **nie jest** równoważny „zmniejsz tylko pion”.

### 2.1 `version.php` — bez narzucania upgrade w GUI przy zmianach bez DB

- **Zasada:** jeśli zmiana **nie** obejmuje realnej migracji bazy (`db/install.xml`, `db/upgrade.php` itd.) i użytkownik **nie** polecił wyraźnie podniesienia wersji wydania, **nie wolno** zmieniać `$plugin->version` w `version.php`.
- **Dlaczego:** podbicie numeru w `version.php` skutkuje w Moodle oczekującym **upgrade** wtyczki (powiadomienia / przejście przez aktualizację) — to **nie może** być efektem ubocznym samych zmian w JS/CSS/kosmetyce ani „dla porządku”.
- **Cache bust zamiast `version.php`:** dla JS/CSS używać parametru `?ver=` w `locallib.php` (w razie potrzeby podbicie tego parametru). Odświeżenie cache Moodla po zmianach plików następuje przez wbudowane `php admin/cli/purge_caches.php` w `edit-with-maintenance.sh` (§5.0) — nie jako osobna ścieżka obok skryptu.
- **Baza:** asystent **nie** wykonuje ręcznych zmian w bazie (SQL) w celu podbijania numerów wersji.
- **Wyjątek — błąd „downgrade”:** gdy wersja w pliku jest **niższa** niż zapis w bazie, należy uzgodnić z użytkownikiem: przywrócenie zgodności numeru w pliku z bazą **albo** świadome podniesienie `$plugin->version` **powyżej** wartości z bazy; upgrade można wtedy wykonać z CLI (`php admin/cli/upgrade.php`), jeśli środowisko na to pozwala — żeby nie zmuszać do przechodzenia przez GUI bez potrzeby.

---

## 3. Edycja kodu (jak się robi zmiany – bash/skrypt)

## 3.1 Jeden bash na jeden prompt

- **Jeden prompt użytkownika** = **jedna odpowiedź** z **jednym bashem** (jednym wywołaniem `edit-with-maintenance.sh`).
- Wszystkie zmiany kodu wynikające z tego promptu muszą być zawarte w tym jednym wywołaniu (np. łańcuch poleceń w jednym `--cmd`, lub jeden skrypt w heredoc).
- Niedopuszczalne jest wielokrotne włączanie i wyłączanie trybu konserwacji w ramach jednego przejścia — użytkownicy nie mogą wielokrotnie widzieć niedostępnego serwera.
- Po wykonaniu tego jednego bashu asystent może podać użytkownikowi **kroki smoke testów** (instrukcje do ręcznego sprawdzenia); nie jest to kolejna zmiana kodu ani kolejne wywołanie skryptu.
- Od momentu, gdy użytkownik nakazuje „wdrożenie”, asystent wykonuje pracę w całości samodzielnie: nie pokazuje okienek do zatwierdzania i nie wymaga kliknięcia „Run” ani „akceptacji” po stronie użytkownika. SMOKE na końcu ma mieć charakter informacyjny (bez przerywania procesu w trakcie wdrożenia).


- **Edycja plików w `mod/pdfannotator/` (w tym chronionego pliku): wyłącznie przez skrypt.**  
  Skrypt: `mod/pdfannotator/edit-with-maintenance.sh`, uruchamiany z katalogu głównego Moodle (np. `/var/www/html/moodle`).
- **Wyjątek (bez maintenance):** pliki pomocnicze w katalogu pluginu, które **nie są używane w runtime** przez Moodle / PDF Annotator, np. logi, notatki, dokumentacja techniczna: `*.log`, `*.txt`, `*.md`.  
  - Te pliki można edytować bez trybu maintenance i bez `edit-with-maintenance.sh` (np. zwykłą edycją w Cursorrze).  
  - Nie wolno jednak do tego wyjątku zaliczać plików `.php`, `.js`, `.css`, plików językowych, konfiguracyjnych ani żadnych innych, które są ładowane przez Moodle lub front-end pluginu.
- **Zabronione:** StrReplace, Write, EditNotebook do plików w `mod/pdfannotator/` poza powyższym wyjątkiem dla czysto pomocniczych plików `*.log` / `*.txt` / `*.md`.
- **Dozwolone wyłącznie:**
  - Restore z backupu: `./mod/pdfannotator/edit-with-maintenance.sh --restore`
  - Dowolna edycja: `./mod/pdfannotator/edit-with-maintenance.sh --cmd '...'` (np. `sed`, `python3 << EOF ... EOF`).
- Skrypt sam wykonuje: maintenance on → odblokowanie pliku → polecenie → purge cache → maintenance off → blokada pliku.
- Opcjonalnie: `--lock` / `--unlock` (np. `sudo ... --lock` ustawia plik na 444).
- Jedna zmiana = jeden blok (maintenance + zmiana + purge w jednym wywołaniu skryptu). Rollback tylko przez jeden `--restore`.

### 3.2 Bezpieczeństwo trybu konserwacji (MUST)

- Skrypt `edit-with-maintenance.sh` **może zostawić Moodle w trybie konserwacji**, jeśli komenda w `--cmd` zakończy się błędem (exit != 0). **ABSOLUTNY ZAKAZ** kończenia promptu, gdy serwer mógł pozostać w maintenance.
- **Każde** wywołanie skryptu z `--cmd` musi być w bashu z **wymuszonym wyjściem z maintenance na końcu**:
  ```bash
  cd /var/www/html/moodle && \
    ./mod/pdfannotator/edit-with-maintenance.sh --cmd '...' || true; \
    php admin/cli/maintenance.php --disable
  ```
  (`|| true` tylko po to, żeby przy błędzie w `--cmd` bash nie zatrzymał się przed `maintenance.php --disable`; błąd skryptu = zmiany w stanie niepewnym, raportować użytkownikowi).
- Czas trwania maintenance (od `--enable` do `--disable`) ma być minimalny; docelowo **≤ 1–1,5 s**. Cały kod zmiany (sed/patch/python) musi być przygotowany i sprawdzony **przed** wywołaniem `edit-with-maintenance.sh` – wewnątrz maintenance wykonujemy tylko gotowy, krótki patch.
- W odpowiedzi **zawsze** raportować: czy skrypt zakończył się sukcesem (exit 0) czy błędem; że wykonano `php admin/cli/maintenance.php --disable`; **nie kończyć promptu** bez pewności, że maintenance jest wyłączony.

---

## 4. Backup

- Po każdej udanej zmianie: pełny backup wszystkich plików, które mogły być zmieniane. Najpierw lokalny snapshot w `mod/pdfannotator/_backups/`, potem gotowy bash dla roota kopiujący dokładnie ten snapshot do `/root/trinity_lab_backup/`.
- W skrypcie `edit-with-maintenance.sh` restore `shared/index.js` korzysta z wskaźnika `mod/pdfannotator/_backups/CURRENT_RESTORE.txt` (nazwa katalogu vNNN) oraz auto-wykrywania najwyższego `vNNN` w `/root/trinity_lab_backup/` lub `_backups/` — **nie trzeba** ręcznie edytować stałej ścieżki w skrypcie.
- **Nie wolno przywracać starszych backupów bez zgody użytkownika** — przywracać wyłącznie najnowszy backup lub wersję wskazaną przez użytkownika.
- Po backupie: diff do weryfikacji.

### 4.0 Stała procedura backupu (MUST)

- **Zawsze dwa poziomy backupu:**
  1. **Lokalny snapshot w pluginie** – pełna kopia `mod/pdfannotator` w `mod/pdfannotator/_backups/vXX_opis_TIMESTAMP/…`, wykonana przez `edit-with-maintenance.sh --cmd '...'` z `rsync` i walidacją anty-rekurencyjną (fail-closed):
     - `rsync -a --delete --exclude "_backups/" mod/pdfannotator/ "mod/pdfannotator/_backups/$BNAME/mod/pdfannotator/"`
     - walidacja po rsync: `test ! -d "mod/pdfannotator/_backups/$BNAME/mod/pdfannotator/_backups"`
     - przy FAIL walidacji: `rm -rf "mod/pdfannotator/_backups/$BNAME"` i zakończenie błędem (`exit 1`)
     - **dopiero po pozytywnej walidacji** zapis wskaźnika: `echo "$BNAME" > mod/pdfannotator/_backups/CURRENT_RESTORE.txt`
     - Ten snapshot musi być widoczny z konta użytkownika (np. `piotrad`).
  2. **Kopia dla roota** – po utworzeniu lokalnego snapshotu asystent **zawsze** podaje gotowe polecenie bash, które z konta `root` kopiuje **właśnie ten** snapshot z `_backups` do `/root/trinity_lab_backup/`.
     - Asystent **nie wykonuje** tej kopii automatycznie — to ma wykonać użytkownik (po prostu skopiujesz/wkleisz podaną komendę).
- **Asystent nigdy nie robi tylko backupu „na root‑cie” z pominięciem `_backups`.** Zawsze najpierw snapshot w `_backups`, potem bash do skopiowania go na konto `root`.

### 4.1 Wszystko gotowe – zero kroków ręcznych (MUST)

- **Użytkownik ma mieć wszystko gotowe** – żadnych list poleceń do ręcznego wpisywania, żadnych skryptów z COPY_BACKUP_SOURCE ani ścieżek do skryptu.
- Backup tworzyć w ścieżce **zapisywalnej bez sudo** (np. `$HOME/trinity_lab_backup/` lub `mod/pdfannotator/_backups/`).
- **Zawsze** dołączyć **jeden bash** do skopiowania backupu do `/root/trinity_lab_backup/` – w **tej samej strukturze** za każdym razem, z **tylko nazwą backupu** zmienioną na aktualną (np. `v106_opis_YYYYMMDD_HHMMSS`). Forma:

  ```bash
  sudo mkdir -p /root/trinity_lab_backup && \
  sudo cp -a /var/www/html/moodle/mod/pdfannotator/_backups/NAZWA_BACKUPU /root/trinity_lab_backup/ && \
  sudo chown -R root:root /root/trinity_lab_backup/NAZWA_BACKUPU && \
  echo "OK"
  ```

  (W odpowiedzi wstawić rzeczywistą nazwę katalogu backupu zamiast `NAZWA_BACKUPU`.)

### 4.2 Tryb "backup bez angażowania użytkownika" (MUST)

- Gdy użytkownik prosi o `pełny backup` / `full snapshot` (np. „Pełny backup moja_nazwa” — **tylko to** podaje użytkownik):
  1. Asystent wykonuje całość **samodzielnie** (bez pytań o wersję, `CURRENT_RESTORE`, `BACKUP_INDEX` ani prośby o kliknięcie `Run`).
  2. Asystent używa **jednego krótkiego wywołania** `edit-with-maintenance.sh --cmd '...'` i wykonuje sekwencję fail-closed: `rsync --exclude "_backups/"` -> walidacja braku `_backups` w nowym snapshotcie -> zapis `CURRENT_RESTORE.txt` wyłącznie po pozytywnej walidacji.
  3. Po wywołaniu zawsze wymusza `php admin/cli/maintenance.php --disable` w tym samym bashu.
  4. Asystent **nie kopiuje sam** do `/root/trinity_lab_backup`; podaje tylko gotowy bash dla użytkownika (§4.0, `sudo cp -a` z `_backups`).
  5. Asystent **nie edytuje** ręcznie `edit-with-maintenance.sh` / `BACKUP_INDEX` — restore jest dynamiczny (§4.3).
  6. Jeśli walidacja snapshotu FAIL: asystent usuwa nowy wadliwy snapshot, nie aktualizuje `CURRENT_RESTORE.txt`, raportuje błąd i kończy z maintenance OFF.
- Jeśli narzędzie terminalowe zwróci `failed to spawn: Aborted`:
  - asystent wykonuje automatyczny retry (do skutku w bieżącym promptcie, bez angażowania użytkownika),
  - retry ma używać prostszego, krótszego wariantu komendy (bez rozbudowanej logiki w jednej linii),
  - użytkownik dostaje dopiero wynik końcowy.
- Odpowiedź po backupie ma być krótka i zawsze zawierać:
  - nazwę snapshotu `vXX_opis_TIMESTAMP`,
  - potwierdzenie, że zapisano `CURRENT_RESTORE.txt` (bez prośby do użytkownika o ten krok),
  - informację o statusie maintenance,
  - gotowy bash do kopiowania snapshotu do `/root/trinity_lab_backup`.
- **Potwierdzenie kopii na root (`OK`):** gdy użytkownik po backupie odpowie samym tekstem `OK` (potwierdzenie wykonania basha `sudo cp -a` na root), asystent **nie komentuje** tego — przyjmuje do wiadomości i odpowiada wyłącznie: `OK` (oszczędność tokenów; bez podsumowań, ofert pomocy ani powtórzeń statusu backupu).

### 4.3 Restore pointer (MUST)

- Po snapshot w `_backups` zapisać wskaźnik **wyłącznie po pozytywnej walidacji anty-rekurencyjnej** (w tym samym `--cmd` co `rsync`): `echo "vNNN_opis_TIMESTAMP" > mod/pdfannotator/_backups/CURRENT_RESTORE.txt`
- To jest MUST. Bash `sudo cp -a` z §4.0 **nie** zapisuje wskaźnika.
- FAIL walidacji = brak aktualizacji wskaźnika + usunięcie nowego wadliwego snapshotu.
- Kopia na root: bash §4.0 albo opcjonalnie sudo ./mod/pdfannotator/scripts/copy_backup_to_root.sh vNNN_... (ten skrypt ustawia wskaźnik i przywraca właściciela pliku jak katalog `_backups`).
- Przy `--restore` skrypt wypisze użyty vNNN; ręczna edycja BACKUP_INDEX w skrypcie nie jest wymagana.

---

## 5. Testy przed i po (bramka)

### 5.0 Purge cache Moodla

- **Tylko w skrypcie:** `php admin/cli/purge_caches.php` jest wywoływane wewnątrz `mod/pdfannotator/edit-with-maintenance.sh` (`do_cmd` / `do_restore`). **Nie usuwać** tego z skryptu. Zmiany kodu pluginu idą wyłącznie przez ten skrypt (§3) — nie opisujemy oddzielnych ścieżek purge poza nim.

- Przed zmianą: SANITY, SYNTAX, REGRES, SMOKE. Raport: `SANITY: OK/FAIL`, `SYNTAX: OK/FAIL`, `REGRES: OK/FAIL`, `SMOKE: OK/FAIL`.
- **SANITY (CLI), snapshot referencyjny = trzeci najnowszy `vNNN` w `_backups/` (przedprzedostatni):**  
  Numer wersji to `v` + liczba na początku nazwy katalogu (np. `v221_…`). Sortowanie **numeryczne** po NNN. Źródło SANITY = **trzeci od góry** (najnowszy, przedostatni, **przedprzedostatni**). Przykład: najnowsze to v221, v220, v219 → SANITY sprawdza **v219**. Przy mniej niż trzech unikalnych NNN: **FAIL**. W raporcie podać wybrany katalog.  
  ```bash
  cd /var/www/html/moodle && \
    test -f mod/pdfannotator/shared/index.js && \
    test -f mod/pdfannotator/edit-with-maintenance.sh && \
    REF_NNN=$(ls -1 mod/pdfannotator/_backups | grep -oE '^v[0-9]+' | sed 's/^v//' | sort -n | uniq) && \
    test "$(echo "$REF_NNN" | wc -l)" -ge 3 && \
    REF_NNN=$(echo "$REF_NNN" | tail -3 | head -1) && \
    SNAP=$(ls -1d mod/pdfannotator/_backups/v${REF_NNN}_* 2>/dev/null | head -1) && \
    test -n "$SNAP" && \
    test -f "$SNAP/mod/pdfannotator/shared/index.js" && \
    echo "SANITY_REF=$(basename "$SNAP")"
  ```
  Kryterium zaliczenia: kod wyjścia `0`.
- **SYNTAX (CLI):**  
  PHP: `php -l mod/pdfannotator/view.php && php -l mod/pdfannotator/lib.php`.  
  JS: `node --check /var/www/html/moodle/mod/pdfannotator/shared/index.js` (jeśli brak node: SYNTAX: SKIPPED).
- **REGRES (ręcznie):** typy adnotacji (point, area, textbox, text), różne zoomy (np. 100%, 133%, 150%, 200%), tryb normalny i fullscreen; tworzenie, przeciąganie, zapis, odświeżenie — zgodność pozycji, brak niepożądanego przesunięcia.
- **SMOKE (ręcznie):** otwarcie PDF, ewentualnie czyszczenie cache przeglądarki i twarde odświeżenie, potem zwykłe F5 — brak błędów blokujących flow. Po wdrożeniu asystent nie prosi o „Run” ani akceptację; jeśli potrzebna jest odpowiedź zwrotna, ma to być wyłącznie krótkie „działa/nie działa”.
- Jeśli którykolwiek test ma FAIL — nie modyfikować kodu; najpierw naprawa.

---

## 6. Które pliki analizować

- **Do każdej zmiany:** tylko pliki faktycznie zmieniane (zazwyczaj `shared/index.js`, ewentualnie `view.php`, `lib.php`, `styles.css`, `fullscreen_enhanced.js`).
- **Syntax:** zawsze `view.php`, `lib.php`; dla JS — `shared/index.js` oraz inne zmieniane pliki .js.
- **Główny kod adnotacji/UI:** `mod/pdfannotator/shared/index.js` (duży plik) — analizować fragmenty (SemanticSearch, Grep, Read z limitem), nie cały plik.
- **Wejście PHP:** `view.php`, `lib.php`, `classes/output/index.php` — gdy zmiana dotyczy renderowania lub API.
- Unikać: czytania dużych plików w całości bez potrzeby; preferować wyszukiwanie po symbolu/funkcji i czytanie wycinków.

---

## 7. Minimalizacja tokenów

- Odwoływać się do tego jednego pliku zamiast do wielu (workflow, Zasady, SUPERPROMPT).
- Przed analizą: precyzyjne zapytania (SemanticSearch, Grep) zamiast „przeczytaj cały plik”.
- Instrukcje dla użytkownika: poza blokami kodu; w blokach kodu — tylko kod do skopiowania.
- Krótkie odpowiedzi; ewentualna numeracja zadań (Z1, Z2, …) dla jednoznaczności.
- Jedno zadanie na raz; po wcześniejszej zgodzie użytkownika na dany typ zmian retry wykonuj automatycznie (bez dodatkowej komendy "retry"), o ile mieści się to w pozostałych zasadach tego dokumentu.
- **Nie wymagaj komendy "dalej"** do kontynuacji, jeśli kolejny krok **nie jest rollbackiem**, **nie dotyka core Moodle**, i jest to **niski-risk hotfix/diagnostyka** w obrębie pluginu (bez ryzyka wyłączenia całego serwisu).

---

## 8. Styl komunikacji (dla AI)

- Krótko, bez gadulstwa; nie łączyć instrukcji z kodem w jednym bloku.
- Zakładany odbiorca: nie programista, ale nie zupełny nowicjusz.
- Unikać przesadnych pochwał; zamiast długich opisów — „problem w X / zmiana w Y”.

---

## 9. Zabronione

- **Zostawienie Moodle w trybie konserwacji** po zakończeniu promptu (niezależnie od przyczyny błędu). Po każdym wywołaniu `edit-with-maintenance.sh` w tym samym bashu musi nastąpić `php admin/cli/maintenance.php --disable`.
- W ramach jednego promptu użytkownika: wielokrotne wywołania `edit-with-maintenance.sh` (więcej niż jedno włączenie trybu konserwacji).
- Edycja plików w `mod/pdfannotator/` narzędziami Cursora (StrReplace, Write, EditNotebook) **z wyjątkiem** czysto pomocniczych plików `*.log` / `*.txt` / `*.md`, które nie są używane w runtime przez plugin.
- Dzielenie rollbacku na dwa kroki (tylko jeden `--restore`).
- Wykonywanie zmiany, gdy jakikolwiek test ma FAIL.
- Wykonywanie zmiany w kodzie poza trybem maintenance (skrypt to zapewnia) – nie dotyczy zmian w pomocniczych plikach `*.log` / `*.txt` / `*.md`, które nie są ładowane przez Moodle / front‑end pluginu.

---

## 10. Linki

- Kod źródłowy: <https://github.com/rwthmoodle/moodle-mod_pdfannotator>
- Fork: <https://github.com/Piotr-Fr/moodle-mod_pdfannotator_TL>
- Backup AI w pluginie: `/_ai_backup_TL` (jeśli używane).
