# RAM / Theatre – notatki wdrożeniowe

## Debug klienta (opcjonalnie)
- `debugLog` w `js_new/pdfannotator_new.v00054.js` wysyła dane tylko gdy w konsoli **przed** załadowaniem strony ustawisz:  
  `window.__TL_DEBUG_PDFANNOTATOR = 1;`  
  (w praktyce: zwykły użytkownik nie musi nic robić – domyślnie wyłączone.)
- Log `bug8_fullscreen` po wejściu w theatre uruchamia się tylko przy tym samym fladze.

## Co się zmieniło (skrót)
- Niższy budżet pikseli w theatre przy zoomie 100% (mniej RAM, nadal HiDPI).
- Po powrocie na kartę: brak odświeżania okna renderu, jeśli rozmiar/zoom/theatre/komentarze się nie zmieniły.
- Przy przełączeniu theatre: anulowanie renderów PDF w locie + szybsze przycięcie stron poza widokiem.
- Usunięte `console.log` z `fullscreen_enhanced.js` (mniej szumu w konsoli).

## Korekta ostrości theatre (wariant 1 → pełny rollback, 2026-04-25)
- Po pierwszej optymalizacji RAM użyto `pr * 1.08`, cap `2.5` — RAM bardzo dobry, minimalnie słabsza ostrość.
- **Wariant 1 był wdrożony** (`pr * 1.12`, cap `2.6`), ale w praktyce RAM skoczył ponad próg z planu (ok. 500–700 MB), więc **cofnięto** do `pr * 1.08`, cap `2.5`.
- Cache bundle: `locallib.php` → `?ver=574c2c12` (stan z pomiarem ok. 217 MB aktywnie / 174 MB po spoczynku).

## Decyzja dalszych kroków
- **Na teraz:** bez dalszego podnoszenia współczynnika theatre przy 100% zoom — najpierw stabilny RAM.
- Wariant 2 (`1.15` / `2.7`) **nie** rozważamy bez osobnej analizy (wariant 1 już podbił RAM za mocno).
- **Pełny rollback wykonany:** aktywny kod wrócił do wariantu `1.08` / `2.5` + `?ver=574c2c12`, czyli ostatniego stanu potwierdzonego bardzo niskim RAM.
- **Ponowne wdrożenie (ten sam wariant):** jeśli serwer był na stanie v177 (`574c2c11`, raster `1.22` / `3`), ponownie wdrożono identyczny pakiet zmian jak przy pierwszym sukcesie RAM (plan `ram-theatre-low-memory-restore` / pierwotny `ram-theatre-performance-rollout`).
