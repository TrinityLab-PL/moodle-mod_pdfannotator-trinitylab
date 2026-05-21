# Kopia planu (do otwarcia w edytorze)

Oryginał Cursor: `~/.cursor/plans/ram-theatre-low-memory-restore_670716a9.plan.md` — jeśli nie otwiera się z projektu Moodle, użyj **tego pliku** w `mod/pdfannotator/`.

---

name: ram-theatre-low-memory-restore
overview: "Odtworzony plan, który wcześniej dał bardzo niski RAM w PDF Annotatorze: około 217 MB aktywnie i 174 MB po 30 sekundach spokoju. To jest tylko plan do ponownego zatwierdzenia, bez wdrażania zmian w kodzie."
todos:
  - id: restore-lowram-baseline
    content: "Potwierdzić punkt startowy: backup v177 / stan sprzed optymalizacji RAM i aktualny `?ver` bundle."
    status: completed
  - id: restore-lowram-raster
    content: "Przygotować zmianę `rasterPixelRatioForLayout()` na wariant niskiego RAM: `Math.min(2.5, pr * 1.08)`."
    status: completed
  - id: restore-lowram-visibility
    content: "Przygotować guard po powrocie na kartę: nie renderować PDF ponownie, jeśli widok/zoom/tryb/rozmiar się nie zmieniły."
    status: completed
  - id: restore-lowram-toggle-prune
    content: Przygotować anulowanie renderów i przycięcie dalekich stron przy wejściu/wyjściu z theatre.
    status: completed
  - id: restore-lowram-debug-cleanup
    content: Przygotować wyłączenie debug-logów bez flagi oraz usunięcie `console.log` z `fullscreen_enhanced.js`.
    status: completed
  - id: restore-lowram-validation
    content: "Zaplanować walidację ręczną: RAM, theatre, powrót na kartę i adnotacje po wdrożeniu."
    status: completed
isProject: false

---

# Plan: RAM I Theatre - Wariant Niskiego Zużycia Pamięci

## Punkt Odniesienia
To jest odtworzony plan z dzisiejszego udanego wdrożenia RAM. Po jego wdrożeniu użytkownik zgłosił wynik: około 217 MB aktywnie i 174 MB po 30 sekundach spokoju, przy minimalnie słabszej ostrości theatre.

Źródła odtworzenia:
- Istniejący plan: `/home/piotrad/.cursor/plans/ram-theatre-performance-rollout_71d7213f.plan.md`
- Transkrypt wdrożenia: wątek RAM w czacie Cursor (ID: 574c2c94-5f6d-43d0-9b5f-e5560dad37a8)
- Potwierdzenie wyniku użytkownika: 217 MB aktywnie / 174 MB po spoczynku, tuż po wdrożeniu tego wariantu.

## Cel
Zmniejszyć zużycie RAM przy PDF 35 stron, szczególnie po wejściu w theatre/fullscreen i po powrocie na kartę, bez ruszania geometrii adnotacji i bez zmiany silnika PDF.

Nie próbujemy teraz poprawiać ostrości. Priorytetem jest powrót do wariantu, który realnie dał bardzo niski RAM.

## Pliki Do Zmiany Przy Wdrożeniu
- `/var/www/html/moodle/mod/pdfannotator/js_new/pdfannotator_new.v00054.js`
- `/var/www/html/moodle/mod/pdfannotator/locallib.php`
- `/var/www/html/moodle/mod/pdfannotator/fullscreen_enhanced.js`
- Opcjonalne notatki/szablony pomiaru: `RAM_THEATRE_BASELINE.md`, `RAM_THEATRE_IMPLEMENTATION_NOTES.md`

## Zmiana 1: Budżet Renderu Theatre
W `rasterPixelRatioForLayout()` zmienić theatre + zoom 100% z poprzedniego mocnego ustawienia:

```js
return Math.min(3, pr * 1.22);
```

na wariant niskiego RAM:

```js
return Math.min(2.5, pr * 1.08);
```

To jest główny element redukcji pamięci. Nie używać późniejszych prób `1.12 / 2.6`, `1.15 / 2.7` ani zmian typu `canvas 1x1`.

## Zmiana 2: Powrót Na Kartę Bez Niepotrzebnego Renderu
Dodać zapamiętywanie prostego „podpisu” aktualnego widoku PDF po renderze. Podpis obejmuje m.in. theatre/fullscreen, zoom, skalę, rozmiar viewer/content-wrapper i stan komentarzy.

Po `visibilitychange`, jeśli podpis widoku się nie zmienił, nie uruchamiać ponownie renderowania PDF. To ogranicza skoki RAM po samym kliknięciu z powrotem w kartę.

Kluczowe elementy do odtworzenia:
- `state.lastPdfRenderEnvSig`
- `state.lastPdfRenderEnvTs`
- `computePdfRenderEnvSignature()`
- ustawienie podpisu na końcu `scheduleRenderWindowUpdate()`
- pominięcie `scheduleRenderWindowUpdate(false)` w `runAnnotationRecovery()`, gdy podpis się nie zmienił
- reset podpisu przy `clearViewer()` i `reflowPdfForScaleChange()`

## Zmiana 3: Theatre Toggle Bez Niepotrzebnej Pracy W Tle
Na początku `toggleTheaterMode()` anulować aktywne renderowania PDF i szybko przyciąć strony poza najbliższym oknem widoku.

Odtworzyć logikę:
- `cancelAllPdfRenderTasks()` na początku przełączania theatre
- krótkie `setTimeout(..., 0)`
- `getVisiblePageRange()`
- `pruneFarPages(Math.max(1, from - 1), Math.min(numPages, to + 1))`

Nie zmieniać geometrii pozycji PDF ani zasad zapisu adnotacji.

## Zmiana 4: Debug Tylko Na Żądanie
`debugLog()` oraz opóźniony `logBug8Fullscreen` mają działać tylko wtedy, gdy przed załadowaniem strony ustawiono:

```js
window.__TL_DEBUG_PDFANNOTATOR = 1;
```

Normalny użytkownik nie powinien uruchamiać tych debugowych requestów.

## Zmiana 5: Uproszczenie Logów W fullscreen_enhanced.js
Usunąć aktywne `console.log` z `fullscreen_enhanced.js`. Logika przycisku fullscreen zostaje bez zmian.

## Cache JS
Jeśli stan startowy jest backup v177 / `?ver=574c2c11`, wdrożenie wariantu niskiego RAM powinno podbić bundle do:

```php
pdfannotator_new.v00054.js?ver=574c2c12
```

Jeśli serwer ma już inną wersję cache, trzeba użyć nowej wartości, ale zawartość kodu ma odpowiadać dokładnie wariantowi niskiego RAM, nie późniejszym eksperymentom z ostrością.

## Czego Nie Robić
- Nie wdrażać `1.12 / 2.6` ani `1.15 / 2.7`.
- Nie dodawać `canvas.width = 1` / `canvas.height = 1` jako osobnej poprawki prune.
- Nie zmieniać silnika PDF.
- Nie ruszać zapisu, pozycji ani formatów adnotacji.
- Nie mieszać tego z kolejną próbą poprawy ostrości.

## Testy Przed I Po Wdrożeniu
W projekcie obowiązuje wdrażanie przez `edit-with-maintenance.sh`; przy faktycznym wdrożeniu trzeba wykonać wymagane SANITY/SYNTAX i po wszystkim upewnić się, że maintenance jest wyłączony.

Test ręczny po wdrożeniu:
- Otworzyć ten sam PDF 35 stron.
- Zrobić twarde odświeżenie: Ctrl+Shift+R, potem F5.
- Sprawdzić RAM w normal i theatre przy zoom 100%.
- Wejść ikoną fullscreen/theatre i po 30 sekundach spokoju sprawdzić RAM.
- Wykonać 5 przełączeń normal/theatre.
- Sprawdzić point, area, textbox, text: dodaj, przeciągnij, zapisz, odśwież, usuń.
- Zostawić kartę w tle, wrócić po kilku minutach i sprawdzić, czy samo uaktywnienie karty nie robi dużego skoku RAM.

## Kryteria Sukcesu
- RAM wraca w okolice wcześniej potwierdzonego wyniku: około 217 MB aktywnie i około 174 MB po spoczynku, przy podobnym scenariuszu.
- Theatre działa, ale ostrość może być minimalnie słabsza niż w stanie v177.
- Brak skoku pozycji PDF przy normal/theatre.
- Adnotacje działają bez regresji.
- Brak błędów UI blokujących pracę.

## Rollback
Jeśli ten wariant nie daje niskiego RAM po poprawnym odświeżeniu i zamknięciu starej karty PDF, nie dokładamy kolejnych mikro-poprawek. Wtedy porównujemy działający backup z aktywnymi plikami bajtowo i dopiero na tej podstawie decydujemy o następnym kroku.
