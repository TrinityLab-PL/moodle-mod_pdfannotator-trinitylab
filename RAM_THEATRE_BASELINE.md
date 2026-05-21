# Baseline RAM / Theatre (PDF ~35 stron)

Wypełnij **przed** pierwszą zmianą kodu i **po** wdrożeniu (ta sama przeglądarka, ten sam dokument).

## Jak czytać RAM
Chrome: **Shift+Esc** → Menedżer zadań → kolumna **Pamięć** dla karty z PDF.

## Scenariusze (zapisz liczby MB)

| Scenariusz | Normal (spokój ~1 min) | Theatre (spokój ~1 min) | Uwagi |
|------------|------------------------|-------------------------|--------|
| Zoom 100% | | | |
| Zoom 150% | | | |
| Zoom 200% | | | |

## Przełączanie widoku
Wykonaj **5×** normal → theatre → normal (bez przewijania między cyklami). Zapisz **najwyższy** odczyt RAM w trakcie i **wartość po ~30 s spokoju**.

| Zoom | Peak RAM (MB) | Po spokoju (MB) |
|------|---------------|-----------------|
| 100% | | |
| 150% | | |
| 200% | | |

## Karta w tle
1. Zostaw kartę z PDF **5+ min** w tle (inna karta na wierzchu).  
2. Wróć na PDF, **nic nie rób przez 30 s**.  
3. Zapisz RAM **tuż po powrocie** i **po 30 s**.

| Tryb | RAM tuż po powrocie | RAM po 30 s |
|------|---------------------|-------------|
| Normal | | |
| Theatre | | |

## Jakość (tak / nie)
- PDF wygląda ostro (brak „mgły”) przy 100% i 150%:  
- Adnotacje: dodaj / przesuń / zapisz / odśwież — bez problemu:  
- Theatre ↔ normal bez utraty pozycji strony:  

## Data / wersja bundle
- Data pomiaru:  
- `locallib.php` `?ver=` dla `pdfannotator_new.v00054.js`:  

## Po wdrożeniu (2026-04-25)
- Parametr cache JS dla wariantu niskiego RAM: **`?ver=574c2c12`** (twardy refresh po każdej zmianie bundle).
- **Ponowne wdrożenie:** po powrocie kodu do stanu zbliżonego do backupu v177 (`?ver=574c2c11`) ponownie zastosowano plan „RAM I Theatre” (raster `1.08` / cap `2.5`, guard `visibilitychange`, prune przy theatre, debug tylko na flagę, bez `console.log` w `fullscreen_enhanced.js`).
- Wypełnij tabelę **ponownie** po kilku dniach użytkowania, jeśli chcesz porównać trend RAM.

## Baseline przed korektą ostrości theatre (wariant 1)
- **RAM w aktywności:** ok. 217 MB (Chrome, ta sama karta PDF).
- **RAM po 30 s spokoju:** ok. 174 MB.
- **Ostrość theatre:** bardzo dobra, ale użytkownik zauważył **minimalnie** słabszą ostrość względem poprzedniego, mocniejszego ustawienia renderu.
- **Cel korekty:** lekko podnieść jakość bitmapy w theatre przy zoomie 100%, bez powrotu do dawnych skoków 600–800 MB.
