# ADR: tablica wieloosobowa (Krok 0 — decyzje produktowe i architektura zapisu)

| Pole | Wartość |
|------|---------|
| Status | **Zaakceptowane** — bramka wymagań przed migracją DB / kodem Wb |
| Data | 2026-10-21 |
| Plan normatywny | [`konva_whiteboard_rollout_bbbc65d9.plan.md`](/home/piotrad/.cursor/plans/konva_whiteboard_rollout_bbbc65d9.plan.md) |
| Superaudyt (archiwum) | [`whiteboard_realtime_rollout_0cb31769.plan.md`](/home/piotrad/.cursor/plans/whiteboard_realtime_rollout_0cb31769.plan.md) |

Ten dokument jest **krótkim, podpisanym skrótem** ustaleń z czatu i planu. W razie sprzeczności obowiązuje plan normatywny; ADR służy audytowi i onboardingu.

---

## 1. Cel i kontekst

W pluginie PDF Annotator (Moodle) dodajemy **wieloosobowe tablice** nad PDF: kotwica na stronie, pełnoekranowa nakładka, ten sam pasek narzędzi co przy PDF, zapis w bazie Moodle, synchronizacja na żywo przez Node (Socket.IO) na localhost za Apache WSS.

**Poza v1:** undo/redo, wstawianie obrazków, edycja na telefonie, osobny toolbar tablicy, tldraw/Excalidraw, Redis/PM2 jako wymóg.

---

## 2. Decyzje już zamknięte przed implementacją

### 2.1 Silnik i integracja

| Temat | Decyzja |
|-------|---------|
| Silnik canvas | **Konva.js** (MIT, już w module) |
| Real-time | **Socket.IO** (MIT), jeden proces Node pod **systemd**, `127.0.0.1:3001`, proxy Apache same-origin |
| Źródło prawdy | **Moodle DB** (+ File API); Node **nie** łączy się bezpośrednio z DB |
| Auth | Sesja Moodle; ticket HMAC w tle; **brak dodatkowego loginu** |
| Zakres WS | Tylko rysunek tablicy + **presence**; komentarze PDF w `action.php` |
| Wiele tablic | UUID, kotwica, osobny rekord DB i pokój realtime na tablicę |
| Nakładka | Zakrywa PDF i komentarze; **toolbar zostaje**; w trybie Wb znika przycisk iWb |
| Eksport | PNG, SVG, PDF — **tylko tablica**, bez podkładu PDF; PDF = **jedna strona** całej planszy (skala ISO 14 400 pt max) |

### 2.2 P0.1 — powierzchnia

- **Jedna ciągła plansza**; `+` na krawędzi **podwaja** wymiar w górę / dół / lewo / prawo.
- Współrzędne obiektów **nie przesuwają się** przy powiększeniu; kreska może przechodzić przez dawną granicę jako **jeden obiekt**.
- Równoczesne powiększenia: **suma granic**, bez LWW cofającego rozmiar.
- Szczegóły limitów rozmiaru → sekcja 2.4.

### 2.3 P0.2 — toolbar

- Ten sam **`tl-express-toolbar`**: layout, ikony FA/SVG, styl Open Sans / `#3b3e3e`.
- Narzędzia PDF mapowane na Wb (area → prostokąt, highlight → marker, strikeout → linia, point → **pinezka z notatką**, ta sama ikona pinezki).
- Zoom toolbara = **tylko tablica**; strony PDF i „Open comments” → **disabled** na Wb.
- Clear board → z potwierdzeniem (UI w Kroku 5).

### 2.4 P0.3 — limity (v1)

| Limit | Wartość | Próg UI |
|-------|---------|---------|
| Edytorzy / pokój | 30 miękko, **40 twardo** (41+ = podgląd) | komunikat od 30 |
| Obiekty / tablica | **5 000** | ostrzeżenie 80%, stop nowych 100% |
| JSON snapshot | **3 MiB** | j.w. |
| Start planszy | 1200 × 800 | — |
| Max bok planszy | **8 000** jednostek (~2,8 m) | brak dalszego `+` |
| Zoom Wb | 10–400% | clamp |
| Event / chunk | 64 KiB / 16 KiB | odrzucenie |
| Liczba tablic / PDF | **bez limitu sztuk** | quota dysku Moodle |

Spike/load test może doprecyzować liczby w **±20%**, bez przekraczania 40 edytorów i 5 000 obiektów bez nowej decyzji.

### 2.5 P0.4 — trwałość i UX (jak Miro)

- **Trwałe** = zapis potwierdzony w **Moodle DB** (durable ACK), nie tylko w Node.
- **RPO = 0** dla stanu wewnętrznego „zapisane trwale”.
- **UI:** cisza gdy OK; baner tylko przy problemie (brak połączenia, błąd zapisu, konflikt, tryb tylko odczytu).
- Krótki zanik sieci (~do 3 s): cichy reconnect; outbox w przeglądarce, ponawianie idempotentne.
- **Node niedostępny:** jawny **tryb tylko do odczytu** — bez cichego rysowania „obok” realtime.
- Zamknięcie tablicy z niewysłaną kolejką → potwierdzenie użytkownika.
- **RTO** realtime → runbook przed pilotem (nie pokazywać uczniowi).

### 2.6 Uprawnienia i grupy (2026-10-21)

- **Student / nauczyciel / manager:** tworzenie, podgląd, edycja, **eksport**.
- **Tylko nauczyciel / manager:** **usuwanie** dowolnej tablicy (student **nie** usuwa własnej).
- **Gość / anonim:** bez create/edit/delete/export/presence; statyczny podgląd tylko przy **osobnej** capability (domyślnie off).
- **Grupy Moodle:** separate = izolacja; visible = inne grupy read-only; brak grup = wspólna przestrzeń.
- `creatorid` = audyt, nie własność.

### 2.7 Urządzenia (2026-10-21)

- **Komputer i tablet:** pełna edycja.
- **Telefon:** otwarcie, pan, zoom, eksport — **bez rysowania** w v1.

---

## 3. ADR: synchronizacja i zapis (do implementacji)

**Problem:** wielu użytkowników, jeden VPS, restart Node — jak uniknąć utraty pracy i rozjechanych wersji tablicy?

**Decyzja:**

1. **Moodle** trzyma wersjonowany **snapshot** + krótki **journal** operacji (`pdfannotator_whiteboard_ops`).
2. **Node** jest **sekwencerem** pokoju (`serverSeq`), nie magazynem trwałym; zapis przez **podpisany loopback API** do PHP.
3. **Durable ACK:** broadcast „kanoniczny” dopiero po OK z Moodle; stan UI „zdrowy” zakłada trwałość w DB (bez napisu „Zapisane”).
4. **Konflikty:** kolejność `serverSeq`; typowane operacje; **delete → tombstone**; **clear-board → `boardEpoch++`** (stare op nie wskrzeszają).
5. **Join/reconnect:** baseline z DB, bufor operacji w trakcie sync, luka/epoch → **pełny resync**; IndexedDB = tylko niepotwierdzony outbox.
6. **Podgląd kreski:** volatile chunks; finalny stroke = trwała operacja.
7. **Degraded:** brak Node → read-only (zgodnie z P0.4); brak równoległego zapisu full-snapshot z klienta po włączeniu realtime.

**Kontrakt sceny:** wersjonowany **`WhiteboardScene`**, nie surowe `stage.toJSON()`.

**Autosave (client outbox):** debounce ~2 s, maxWait ~5 s; `beforeunload` best-effort.

---

## 4. Konsekwencje

- Wymagana migracja DB, capabilities, endpointy PHP, usługa Node, spike Konva przed produkcją.
- Load test **obowiązkowy** dla profilu **30/40** edytorów.
- Krok 1 (readiness VPS) **bez instalacji** do osobnej zgody użytkownika.
- Zmiany kodu pluginu wyłącznie przez `edit-with-maintenance.sh` ([PDF_ANNOTATOR_ZASADY_PRACY.md](PDF_ANNOTATOR_ZASADY_PRACY.md)).

---

## 5. Następne kroki (poza tym ADR)

1. **Krok 1** — audyt readiness i runbook rollback (read-only).
2. **Krok 2** — spike Konva (toolbar, plansza, eksport, pomiary).
3. Dopiero po bramkach: security baseline → model DB → produkt lokalny → realtime.

---

*Dokument utworzony w ramach Krok 0 planu rollout tablicy. Aktualizacje decyzji P0 wymagają edycji tego pliku i planu normatywnego.*
