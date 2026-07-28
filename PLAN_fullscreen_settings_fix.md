---
name: Fullscreen settings fix
overview: Plan techniczny defaultfullscreen (backup/restore + admin default). NIE jest poleceniem wdrożenia. Deploy/rollback tylko po jawnej komendzie WDRAŻAJ/PRODUKCJA/GO DO WDROŻENIA oraz poza trwającymi lekcjami.
todos:
  - id: precheck-readonly
    content: "Faza 0 readonly: git status, DB SHOW COLUMNS, restore inspect, idempotencja 5 plików — raport SANITY zapisany"
    status: pending
  - id: pre-deploy-snapshot
    content: "Faza 1 deploy: snapshot, walidacja, .last_snapshot_fullscreen.txt, pełna komenda rollback PRZED patchem"
    status: pending
  - id: fix-backup-field
    content: defaultfullscreen w backup stepslib + install.xml
    status: pending
  - id: admin-default
    content: mod_pdfannotator/defaultfullscreen + mod_form (1x setDefault) + lang/en
    status: pending
  - id: post-deploy-verify
    content: Macierz testów A–I + logi + purge OK + raport końcowy
    status: pending
  - id: rollback-ready
    content: Runbook rollback z pełnymi 5 cp + precheck + maintenance OFF
    status: pending
isProject: false
---

# Fullscreen: admin default + kopiowanie kursu

**Lokalizacja kanoniczna planu:** `/home/piotrad/.cursor/plans/fullscreen_settings_fix_944bcb36.plan.md`  
**Kopia robocza w projekcie (MUST przed deployem):** `mod/pdfannotator/PLAN_fullscreen_settings_fix.md` — tylko `.md`, sync 1:1 z kanonicznym, bez deploy kodu.

---

## Status planu (NIE = zgoda na deploy)

**Status techniczny planu:** gotowy do wdrożenia po spełnieniu Go/No-Go poniżej.

**To NIE jest zgoda na deploy.** Wdrożenie wymaga **dwóch** warunków jednocześnie:

1. Jawna komenda: `WDRAŻAJ` / `PRODUKCJA` / `GO DO WDROŻENIA`
2. **Brak trwających lekcji** na produkcji (lub wyraźne OK operatora: `DEPLOY POZA LEKCJAMI: TAK`)

Deploy i rollback uruchamiają `edit-with-maintenance.sh` → krótki maintenance. **Zakaz deploy/rollback w trakcie lekcji.**

---

## BLOKADA WYKONANIA (MUST)

Ten plan **nie jest** poleceniem wdrożenia.

**Zakaz bez jawnej komendy produkcyjnej:**

- `edit-with-maintenance.sh`
- patchowania plików w `mod/pdfannotator/`
- purge cache poza skryptem (chyba że operator wyraźnie zezwoli)

**Zakaz bez OK poza lekcjami:**

- deploy i rollback w czasie aktywnych lekcji użytkowników

**Dozwolone bez komendy deploy:** czytanie kodu, prechecki readonly, aktualizacja tego planu (`.md`), przygotowanie komend jako tekstu.

**Zakaz rollbacku przez `--restore`:** skrypt `--restore` cofa wyłącznie `shared/index.js` (v100) — **nie dotyczy tego wdrożenia**. Rollback = `cp` 5 plików ze snapshotu (sekcja Rollback).

---

## Go / No-Go (przed patchem)

| # | Warunek | Wymagane |
|---|---------|----------|
| G1 | Komenda deploy (`WDRAŻAJ` / `PRODUKCJA` / `GO DO WDROŻENIA`) | TAK |
| G2 | Brak trwających lekcji LUB `DEPLOY POZA LEKCJAMI: TAK` | TAK |
| G3 | Raport **Fazy 0** zapisany (SANITY: OK, nie UNKNOWN) | TAK |
| G4 | Kolumna `mdl_pdfannotator.defaultfullscreen` potwierdzona (SHOW COLUMNS) | TAK |
| G5 | Restore readonly: brak filtracji `$data` w `process_pdfannotator()` | TAK |
| G6 | Idempotencja 5 plików zmienianych: baseline OK | TAK |
| G7 | `git status` — świadoma decyzja (clean lub znane lokalne zmiany) | TAK |
| G8 | Snapshot 5 plików + `.last_snapshot_fullscreen.txt` **przed** patchem | TAK |
| G9 | Pełna komenda rollback (5× `cp`, zero `...`) wypisana **przed** patchem | TAK |
| G10 | Rollback wykonawczy tylko po `ROLLBACK: TAK` | TAK |
| G11 | Zakaz `--restore` i zakaz podbijania `version.php` | TAK |
| G12 | Kopia planu zsynchronizowana: `mod/pdfannotator/PLAN_fullscreen_settings_fix.md` | TAK |

**NO-GO** jeśli którykolwiek G1–G12 nie spełniony.

---

## Diagnoza

### Problem 1 — brak globalnego admin default (tylko **nowe** aktywności)

**Stan obecny:**
- Checkbox **per aktywność** już istnieje w `mod_form.php` (Settings aktywności PDF) — **nie dodawać** drugiego.
- W **Site administration → Plugins → Activity modules → PDF Annotator** brakuje odpowiednika globalnego (jak `usevotes`, `useprint`).
- `mod_form.php` ma na sztywno `setDefault('defaultfullscreen', 0)` zamiast czytać global config.

**Cel deployu (Problem 1):**
- Dodać **tylko** wpis w [`settings.php`](settings.php) — checkbox w panelu admina wtyczki.
- W [`mod_form.php`](mod_form.php) **wyłącznie** podmienić `setDefault(..., 0)` → `setDefault(..., !empty($config->defaultfullscreen))` — bez nowego elementu formularza.

`setDefault()` nie przepisuje istniejących aktywności przy edycji.

### Problem 2 — kopiowanie kursu (biznesowy flow)

`defaultfullscreen` nie jest w `backup_pdfannotator_stepslib.php` → restore → DB default `0`.

**Obowiązkowa ścieżka testowa (biznes):** **course backup `.mbz` + restore do nowego kursu** — to odpowiada „kopiuję kurs A (WZÓR) nowemu klientowi”.  
**Obowiązkowo dodatkowo:** duplicate activity w tym samym kursie (źródło `defaultfullscreen=1` → kopia DB=1; nie z global default).  
Duplicate course — dodatkowo, jeśli faktycznie używany zamiast backup/restore.

Restore: **bez zmian kodu** po precheck readonly (sekcja Faza 0).

### install.xml

Sync świeżych instalacji — **nie** migracja produkcyjnej DB. Kolumna prod z upgrade `2025090301`.

---

## Namespace (zweryfikowane w kodzie)

- `settings.php`: `mod_pdfannotator/...`
- `mod_form.php`: `get_config('mod_pdfannotator')`
- Nowe: `mod_pdfannotator/defaultfullscreen`

---

## Zakres patcha (wyłącznie 5 plików)

| Plik | Zmiana |
|------|--------|
| `backup/moodle2/backup_pdfannotator_stepslib.php` | `'defaultfullscreen'` w tablicy pól |
| `db/install.xml` | FIELD `defaultfullscreen` |
| `settings.php` | **nowy** checkbox w panelu admina wtyczki (`mod_pdfannotator/defaultfullscreen`) |
| `mod_form.php` | **tylko** `setDefault` z global config — checkbox już jest, **bez** `addElement` |
| `lang/en/pdfannotator.php` | `global_setting_defaultfullscreen` + `_desc` (etykiety panelu admina) |

**Bez zmian (tylko precheck readonly):** `restore_pdfannotator_stepslib.php`, view, JS, `version.php`, `upgrade.php`.

**Języki:** tylko `lang/en`. Brak `lang/pl` — admin PL może widzieć EN/fallback (ograniczenie UX, nie regresja funkcjonalna).

---

## Faza 0 — prechecki readonly (PRZED maintenance, PRZED deploy)

Wykonać w **osobnej sesji** (bez `edit-with-maintenance.sh`). Wynik zapisać jako raport:

```
SANITY: OK|FAIL|UNKNOWN
SYNTAX (baseline): OK|SKIPPED
Faza0-restore: OK|FAIL
Faza0-idempotencja: OK|FAIL
Faza0-git: OK|NOTED
Faza0-db-column: OK|UNKNOWN|FAIL
```

### 0.1 Git (readonly)

```bash
cd /var/www/html/moodle/mod/pdfannotator && git status --short
```

Zanotować: clean / znane lokalne zmiany. Nie blokuje samo w sobie, ale wymaga świadomej decyzji operatora.

### 0.2 DB — kolumna (readonly)

```sql
SHOW COLUMNS FROM mdl_pdfannotator LIKE 'defaultfullscreen';
```

- Wynik z wierszem → OK
- Brak wiersza → **NO-GO** (osobny plan migracji)
- Brak uprawnień → **SANITY UNKNOWN / NO-GO** do potwierdzenia inną metodą readonly (np. phpMyAdmin SELECT, Moodle DB schema export). **Nie zakładać** braku kolumny.

**Zakaz SQL:** UPDATE / INSERT / DELETE / ALTER / DROP. Tylko SELECT / SHOW.

### 0.3 Restore — inspekcja funkcji (readonly)

Plik: `backup/moodle2/restore_pdfannotator_stepslib.php`

1. Przeczytać **całą** funkcję `process_pdfannotator()` i helpery wywołane z niej.
2. Grep pomocniczy:

```bash
grep -n 'process_pdfannotator\|unset\|array_intersect\|insert_record' \
  mod/pdfannotator/backup/moodle2/restore_pdfannotator_stepslib.php
```

**OK jeśli:** `insert_record('pdfannotator', $data)` bez unset/whitelist/filter na polach.  
**FAIL jeśli:** filtracja `$data` → NO-GO (wymaga zmiany restore, poza tym planem).

### 0.4 Idempotencja baseline (readonly, 5 plików)

| Plik | Komenda sprawdzająca | OK gdy |
|------|---------------------|--------|
| backup stepslib | `grep -c "'defaultfullscreen'" backup/moodle2/backup_pdfannotator_stepslib.php` | 0 (przed patchem) lub 1 (po patchu) |
| install.xml | `grep -c 'NAME="defaultfullscreen"' db/install.xml` | 0 lub 1 |
| settings.php | `grep -c 'mod_pdfannotator/defaultfullscreen' settings.php` | 0 lub 1 |
| mod_form.php | `grep -c "setDefault('defaultfullscreen'" mod_form.php` | 1 |
| lang/en | `grep -c "global_setting_defaultfullscreen'" lang/en/pdfannotator.php` | 0 lub 1 (bez `_desc` w liczeniu klucza — liczyć linię `$string['global_setting_defaultfullscreen']`) |

Przed patchem oczekiwany baseline: **0** w backup/install/settings/lang; **1** w mod_form (`setDefault(..., 0)`).

---

## Faza 1 — deploy (tylko po G1+G2 + Faza 0 OK)

**Jeden prompt = jedno** wywołanie:

```bash
cd /var/www/html/moodle && \
  ./mod/pdfannotator/edit-with-maintenance.sh --cmd '...' || true; \
  php admin/cli/maintenance.php --disable
```

### Nazwa snapshotu

Format: `vNNN_fullscreen_settings_YYYYMMDD_HHMMSS`

**Wybór `vNNN`:** weź najwyższy numer z istniejących katalogów `mod/pdfannotator/_backups/v*` i dodaj 1; jeśli brak — użyj `v181` lub kolejny uzgodniony. **Nigdy** literalne `vXXX`.

Przykład: `v181_fullscreen_settings_20260727_143000`

### Krok 0+1 — kolejność w jednym `--cmd`

Wewnątrz `--cmd`: `set -euo pipefail`

1. Ustaw root snapshotu (przykład; `vNNN` i timestamp z reguły powyżej):

```bash
SNAP_ROOT=mod/pdfannotator/_backups/vNNN_fullscreen_settings_YYYYMMDD_HHMMSS
SNAP_DIR="$SNAP_ROOT/mod/pdfannotator"
```

2. Utwórz **wszystkie** podkatalogi (bez `...`):

```bash
mkdir -p \
  "$SNAP_DIR/backup/moodle2" \
  "$SNAP_DIR/db" \
  "$SNAP_DIR/lang/en"
```

(`settings.php` i `mod_form.php` lądują bezpośrednio w `$SNAP_DIR`.)

3. Skopiuj 5 plików 1:1:

```bash
cp -f mod/pdfannotator/backup/moodle2/backup_pdfannotator_stepslib.php "$SNAP_DIR/backup/moodle2/"
cp -f mod/pdfannotator/db/install.xml "$SNAP_DIR/db/"
cp -f mod/pdfannotator/settings.php "$SNAP_DIR/"
cp -f mod/pdfannotator/mod_form.php "$SNAP_DIR/"
cp -f mod/pdfannotator/lang/en/pdfannotator.php "$SNAP_DIR/lang/en/"
```

4. **Walidacja snapshotu** — każdy z 5 plików istnieje i `[ -s plik ]`. Fail → **exit 1, bez patcha**:

```bash
test -s "$SNAP_DIR/backup/moodle2/backup_pdfannotator_stepslib.php"
test -s "$SNAP_DIR/db/install.xml"
test -s "$SNAP_DIR/settings.php"
test -s "$SNAP_DIR/mod_form.php"
test -s "$SNAP_DIR/lang/en/pdfannotator.php"
```

5. Zapisz **`$SNAP_ROOT`** (nie `$SNAP_DIR`) do `mod/pdfannotator/_backups/.last_snapshot_fullscreen.txt`:

```bash
printf '%s\n' "$SNAP_ROOT" > mod/pdfannotator/_backups/.last_snapshot_fullscreen.txt
```

6. **Wypisz pełną komendę rollback** (szablon w sekcji Rollback; `SNAP_ROOT` z pliku) — **przed patchem**
7. **Powtórka idempotencji** (komendy jak Faza 0.4) — stop conditions poniżej. Fail → **exit 1, bez patcha**
8. Patch (idempotentnie)
9. **Post-patch SYNTAX gate** (w tym samym `--cmd`, przed końcem maintenance):
   - `php -l` na 4 plikach PHP
   - `python3 -c "import xml.etree.ElementTree as ET; ET.parse('mod/pdfannotator/db/install.xml')"` (well-formed)
   - Fail → **exit 1** (snapshot zostaje; rollback po `ROLLBACK: TAK`)
10. Purge (w skrypcie `edit-with-maintenance.sh`)
11. Wypisz ponownie pełną komendę rollback (tekst, nie wykonuj)

### Stop conditions (w kroku 7)

**Przerwij bez patchowania (`exit 1`), jeśli:**

| Plik | Warunek STOP |
|------|--------------|
| backup stepslib | `grep -c "'defaultfullscreen'"` > 1 |
| install.xml | `grep -c 'NAME="defaultfullscreen"'` > 1 |
| settings.php | `grep -c 'mod_pdfannotator/defaultfullscreen'` > 1 |
| mod_form.php | `grep -c "setDefault('defaultfullscreen'"` > 1 |
| mod_form.php | po patchu nadal istnieje `setDefault('defaultfullscreen', 0)` obok nowego wpisu |
| lang/en | więcej niż jedna linia `$string['global_setting_defaultfullscreen']` (bez `_desc`) |

**Dodatkowo po patchu (krok 9):** SYNTAX FAIL → STOP, rekomendacja rollback.

### Purge fail

- Status deploy: **FAIL**
- **Bez auto-rollback**
- Diagnostyka outputu skryptu
- Rollback tylko jeśli objawy funkcjonalne (admin/form/view broken) lub operator `ROLLBACK: TAK`

---

## Szablon komendy rollback (PEŁNY — bez placeholderów)

Podstaw `SNAP_ROOT` = wartość z `.last_snapshot_fullscreen.txt` (katalog `.../vNNN_.../` bez `mod/pdfannotator` na końcu, lub pełna ścieżka względem `$MOODLE_ROOT`).

```bash
cd /var/www/html/moodle && \
SNAP_ROOT="$(cat mod/pdfannotator/_backups/.last_snapshot_fullscreen.txt)" && \
./mod/pdfannotator/edit-with-maintenance.sh --cmd "
  test -f \"\$SNAP_ROOT/mod/pdfannotator/backup/moodle2/backup_pdfannotator_stepslib.php\" &&
  test -f \"\$SNAP_ROOT/mod/pdfannotator/db/install.xml\" &&
  test -f \"\$SNAP_ROOT/mod/pdfannotator/settings.php\" &&
  test -f \"\$SNAP_ROOT/mod/pdfannotator/mod_form.php\" &&
  test -f \"\$SNAP_ROOT/mod/pdfannotator/lang/en/pdfannotator.php\" &&
  cp -f \"\$SNAP_ROOT/mod/pdfannotator/backup/moodle2/backup_pdfannotator_stepslib.php\" mod/pdfannotator/backup/moodle2/backup_pdfannotator_stepslib.php &&
  cp -f \"\$SNAP_ROOT/mod/pdfannotator/db/install.xml\" mod/pdfannotator/db/install.xml &&
  cp -f \"\$SNAP_ROOT/mod/pdfannotator/settings.php\" mod/pdfannotator/settings.php &&
  cp -f \"\$SNAP_ROOT/mod/pdfannotator/mod_form.php\" mod/pdfannotator/mod_form.php &&
  cp -f \"\$SNAP_ROOT/mod/pdfannotator/lang/en/pdfannotator.php\" mod/pdfannotator/lang/en/pdfannotator.php
" || true; \
php admin/cli/maintenance.php --disable
```

**Warunki rollback:** `ROLLBACK: TAK` + **poza lekcjami** (jak deploy).  
**Po rollbacku:** potwierdzić maintenance OFF.  
**Nie używać** `./edit-with-maintenance.sh --restore`.

### Po rollbacku — DB config

- Wpis `mod_pdfannotator/defaultfullscreen` w `mdl_config_plugins` może pozostać — **nie jest błędem sam w sobie**
- UI checkbox może zniknąć po rollbacku plików — wtedy tylko SQL readonly; DELETE tylko po osobnej zgodzie
- Wyłączenie w UI możliwe **tylko przed** rollbackiem plików lub gdy UI nadal renderuje ustawienie

---

## Macierz testów (kurs testowy / ukryty — poza lekcjami)

Raport końcowy: `SANITY: OK/FAIL`, `SYNTAX: OK/FAIL`, `REGRES: OK/FAIL`, `SMOKE: OK/FAIL`

### A. SYNTAX (po deploy)

- `php -l mod/pdfannotator/backup/moodle2/backup_pdfannotator_stepslib.php`
- `php -l mod/pdfannotator/settings.php`
- `php -l mod/pdfannotator/mod_form.php`
- `php -l mod/pdfannotator/lang/en/pdfannotator.php`
- `php -l mod/pdfannotator/view.php && php -l mod/pdfannotator/lib.php`
- **install.xml XMLDB OK:**
  - well-formed (ElementTree / xmldb editor)
  - FIELD `defaultfullscreen` w tabeli `pdfannotator`
  - TYPE=int, LENGTH=1, NOTNULL=true, DEFAULT=0, SEQUENCE=false
  - po `useprotectedcomments`, przed `timecreated`

### B. Global default — UI + DB (A/B/C)

Po każdym kroku: UI **oraz** DB po nazwie aktywności + course id + cm id.

1. **A** przy global=0 → zapisz → **DB A=0**
2. Global=1 w Site admin
3. Edytuj **A** → **DB A=0** (bez zmiany)
4. **B** nowa → **DB B=1**
5. Global=0 → **C** nowa → **DB C=0**

### C. Kopiowanie kursu (OBOWIĄZKOWE)

**Minimum (obowiązkowe oba):**

1. Course backup `.mbz` aktywności z `defaultfullscreen=1` → restore do **nowego kursu testowego** → DB=1, Settings UI włączone.
2. Duplicate activity w tym samym kursie: źródło=1 → kopia DB=1 (nie dziedziczy z global admin default).

### D. XML w `.mbz`

Rozpakuj; znajdź `activities/pdfannotator_*/pdfannotator.xml` **konkretnej** instancji testowej:

```xml
<defaultfullscreen>1</defaultfullscreen>
```

### E. Restore nowego `.mbz`

Restore OK; DB=1 (po nazwie + course id); view OK.

### F. Restore starego `.mbz`

**Wejście:** rozpakowany XML **bez** `<defaultfullscreen>` dla testowej instancji.  
Restore OK; DB=0; view OK.

### G. REGRES adnotacji

- Typy: point, area, textbox, text
- Zoom: 100%, 133%, 150%, 200%
- Tryb: normalny + fullscreen
- Akcja: utwórz, przeciągnij, zapisz, odśwież — pozycja bez skoku

### H. SMOKE fullscreen UI

1. Aktywność z `defaultfullscreen=1` → wejście w fullscreen (body class `pdfannotator-default-fullscreen` / `tl-pdf-fullscreen`)
2. Kontrolka fullscreen: ikona ~22px, tooltip „Full screen (ESC to exit)”
3. Klik → fullscreen; ikona „compress”; tooltip „Exit full screen (ESC)”
4. Wyjście: klik lub ESC → ikona „expand”
5. Aktywność z `defaultfullscreen=0` → **brak** auto-fullscreen przy wejściu
6. Konsola JS: brak błędów blokujących flow
7. Adnotacje + komentarze + nawigacja PDF działają

### I. Okno obserwacji (15–30 min, poza lekcjami)

- Logi PHP/Moodle: Site admin settings, formularz aktywności, view PDF
- Konsola JS w smoke fullscreen
- Brak nowych błędów `pdfannotator` / `defaultfullscreen`

---

## Szczegóły implementacji

### A. backup stepslib

```php
'useprivatecomments', 'useprotectedcomments', 'defaultfullscreen', 'timecreated', 'timemodified'
```

### B. install.xml

```xml
<FIELD NAME="defaultfullscreen" TYPE="int" LENGTH="1" NOTNULL="true" DEFAULT="0" SEQUENCE="false"/>
```

### C. settings.php (panel admina — **tu brakuje ustawienia**)

Dodać obok istniejących globalnych checkboxów (`usevotes`, `useprint`, …):

```php
$settings->add(new admin_setting_configcheckbox('mod_pdfannotator/defaultfullscreen',
    get_string('global_setting_defaultfullscreen', 'pdfannotator'),
    get_string('global_setting_defaultfullscreen_desc', 'pdfannotator'), 0));
```

Po deployu: **Site administration → Plugins → Activity modules → PDF Annotator** — nowy checkbox do zaznaczenia.

### D. mod_form.php (**bez nowego checkboxu**)

Checkbox `defaultfullscreen` **już istnieje** (L117–121). Zmienić wyłącznie domyślną wartość:

```php
$mform->setDefault('defaultfullscreen', !empty($config->defaultfullscreen));
```

Zastąpić (usunąć) stary: `setDefault('defaultfullscreen', 0)`. **Nie** dodawać `addElement` / `addHelpButton`.

### E. lang/en/pdfannotator.php

```php
$string['global_setting_defaultfullscreen'] = 'Open in fullscreen by default for new activities?';
$string['global_setting_defaultfullscreen_desc'] = 'Default for new PDF Annotator activities only. Per-activity Settings still apply.';
```

Jeśli klucz istnieje — **aktualizuj**, nie duplikuj.

---

## version.php i cache

- **Nie** zmieniać `$plugin->version` (`2026032862`)
- Purge tylko w `edit-with-maintenance.sh`

---

## Ograniczenia (nie naprawi się samym deployem)

- Kursy skopiowane **przed** fixem: `defaultfullscreen=0` w DB — wymaga nowego backupu + ponownej kopii lub osobnej operacji
- Stare `.mbz` bez pola — restore daje 0
- Rollback plików nie cofa `mdl_config_plugins` ani istniejących aktywności
- Global admin default: tylko nowe aktywności (formularz), nie masowa zmiana istniejących
- `.last_snapshot_fullscreen.txt` — pojedynczy wskaźnik; równoległe operacje mogą go nadpisać — jedna operacja na raz

---

## Traceability — mapowanie uwag audytowych → sekcja planu

| ID | Uwaga audytu | Sekcja planu |
|----|--------------|--------------|
| A1 | Rollback bez placeholderów | Szablon komendy rollback |
| A2 | Checklist [x] mylące | Traceability + todos `pending` (nie [x] wykonania) |
| A3 | Deploy poza lekcjami | Status planu G2, BLOKADA |
| A4 | SMOKE/REGRES rozwinięte | Macierz G, H |
| A5 | Audyt techniczny ≠ zgoda na deploy | Status planu (jawna komenda + poza lekcjami) |
| A6 | Stop conditions + post-patch SYNTAX | Krok 0+1 pkt 7–9 |
| A7 | Idempotencja — konkretne komendy | Faza 0.4, Stop conditions |
| A8 | SANITY raport zapisany | Faza 0 nagłówek |
| A9 | Rollback też poza lekcjami | Szablon rollback warunki |
| A10 | Zakaz --restore | BLOKADA, Rollback |
| A11 | Ścieżka biznesowa backup+restore | Diagnoza, Macierz C |
| A12 | Duplicate activity obowiązkowy | Diagnoza, Macierz C |
| A13 | Plan poza workspace | Nagłówek + kopia MUST w projekcie |
| A14 | .last_snapshot concurrency | Ograniczenia |
| A15 | Wybór vNNN | Nazwa snapshotu |
| A16 | lang/en only | Zakres patcha |
| A17 | git status | Faza 0.1 |
| A18 | XMLDB kryteria | Macierz A |
| A19 | Purge fail bez auto-rollback | Purge fail |
| A20 | SHOW COLUMNS permissions | Faza 0.2 |
| A21 | Restore pełna inspekcja | Faza 0.3 |
| A22 | mod_form idempotencja | Faza 0.4, Stop conditions |
| A23 | Komenda rollback przed patchem | Krok 0+1 pkt 6 |
| A24 | Config po rollback OK | Po rollbacku DB config |

---

## Checklist przed deployem (operator — wszystkie [ ] do odhaczenia ręcznie)

- [ ] G1: komenda WDRAŻAJ / PRODUKCJA / GO DO WDROŻENIA
- [ ] G2: brak lekcji LUB DEPLOY POZA LEKCJAMI: TAK
- [ ] Faza 0 raport zapisany (SANITY OK)
- [ ] Faza 0.2 DB kolumna OK
- [ ] Faza 0.3 restore OK
- [ ] Faza 0.4 idempotencja baseline OK
- [ ] Pełna komenda rollback przygotowana (5× cp)
- [ ] Deploy wykonany; SYNTAX post-patch OK
- [ ] Macierz testów B–I OK (C obejmuje backup+restore **oraz** duplicate activity)
- [ ] Kopia planu zsyncowana do `mod/pdfannotator/PLAN_fullscreen_settings_fix.md`
- [ ] Maintenance OFF potwierdzone

**Uwaga:** pozycje powyżej to **checklist operatora**, nie potwierdzenie wykonania przez plan.
