---
name: "Textbox: pozostałe bugi – zoom, szerokość, ramka, caret"
overview: "Plan naprawy: (1) szerokość po zapisie – 2 linie nie mają zamieniać się w 3; (2) pierwszy dwuklik – ramka Konva w tym samym rozmiarze co pole edycji; (3) pionowa pozycja caretu niezależna od zoomu; (4) spójny wygląd pola przy różnych zoomach. Tam, gdzie to poprawia działanie na różnych monitorach i zoomie – używać em (wewnętrzna typografia); pozycja i rozmiar overlayu w px."
todos:
  - id: width-save
    content: "Szerokość zapisu = szerokość edytora (brak zawężania przez fitTextbox)"
  - id: first-open-frame
    content: "Pierwszy dwuklik – po resizeEditorToContent zsynchronizować ramkę z edytorem"
  - id: caret-zoom
    content: "Caret – padding/line-height w em, spójna pozycja na różnych zoomach i monitorach"
  - id: smoke
    content: "Smoke: 2 linie→zapis→2 linie; ramka=edytor; caret przy 100%/150%"
isProject: false
---

# Plan: Textbox – pozostałe bugi (nagranie GIF + opis)

## Źródło

- Nagranie GIF: pierwszy dwuklik (ramka większa od textarea), zapis 2→3 linie (3. widoczna, ale nie powinno być 3), caret za wysoko, wygląd zależny od zoomu.
- Zasady: zmiany wyłącznie przez `edit-with-maintenance.sh --cmd '...'` (jeden bash, na końcu `|| true; php admin/cli/maintenance.php --disable`).
- Plik: `mod/pdfannotator/js_new/pdfannotator_new.v00054.js` (oraz ewentualnie `styles.css` dla careta).

### Zasada: em tam, gdzie poprawia działanie na różnych monitorach i zoomie

- **W em:** wszystko wewnątrz pola edycji zależne od typografii – **padding**, **line-height** (gdy ustawiane w CSS). Daje to spójną pozycję caretu i proporcje przy dowolnym zoomie i rozdzielczości; 1em = aktualny `font-size` elementu (ustawiany w JS w px), więc skaluje się z widokiem.
- **W px:** **pozycja i rozmiar** overlayu (left, top, width, height) – wynikają z układu strony PDF i skali, muszą pozostać w pikselach.

---

## 1. Bug: Z dwóch linii zapis robi trzy (błąd szerokości po zapisie)

**Obserwacja:** W edycji tekst ma 2 linie; po zapisie ten sam tekst wyświetla się jako 3 linie (obecnie wszystkie widoczne, ale liczba linii się zmienia).

**Przyczyna:** W `commit()` wywoływane jest `fitTextboxAroundContent(annotationData)`, które ustawia `annotationData.width` na szerokość wyliczoną z canvas (długość najdłuższej „linii” rozdzielonej tylko `\n`, bez zawijania). Ta szerokość może być **mniejsza** niż faktyczna szerokość edytora, w którym użytkownik widział 2 linie. Później ustawiamy `annotationData.width = Math.max(annotationData.width, editor.offsetWidth / scale)`, więc teoretycznie bierzemy szerszą wartość – ale jeśli gdzieś ta wartość jest nadpisywana lub zaokrąglana (np. przy zapisie/odczycie), etykieta `.tl-textbox-label` może dostać mniejszą szerokość i tekst zawinie się w 3 linie. Dodatkowo etykieta ma `textPaddingX = 6`, a pole ma `padding: 6px` – jeśli `boxWidth` jest liczone z zaokrągleń `Math.round(annotation.width * scale)`, można stracić 1–2 px i przy wąskim polu zyskać dodatkowe zawinięcie.

**Kierunek:**

- W **showTextboxEditor** i **showNewTextboxEditor** w `commit()`: **po** ewentualnym wywołaniu `fitTextboxAroundContent` (dla wysokości/pozycji) **wymusić** szerokość z edytora:
  - `annotationData.width = editor.offsetWidth / scale` (w edycji istniejącego)
  - `annotation.width = editor.offsetWidth / scale` (w nowym polu)
  Nie polegać na tym, że `Math.max(..., editor.offsetWidth/scale)` wystarczy – jawnie ustawiać szerokość zapisu na szerokość edytora, żeby liczba linii po zapisie się nie zmieniała.
- Opcjonalnie: w `drawAnnotation` dla textboxa upewnić się, że szerokość etykietki (np. `boxWidth - textPaddingX*2`) jest liczona tak, by nie tracić pikseli (np. `Math.ceil(annotation.width * scale) - textPaddingX*2` zamiast `Math.round(annotation.width * scale) - ...`), aby uniknąć zawężania przy zaokrągleniach.

**Miejsce:** `showTextboxEditor` – `commit()` (przed `redrawOneAnnotation`); `showNewTextboxEditor` – `commit()` (przy budowaniu obiektu `annotation`).

---

## 2. Bug: Pierwszy dwuklik – ramka pola w innym rozmiarze niż pole edycji

**Obserwacja:** Przy pierwszym dwukliku (Textbox/Cursor) na niezaznaczone pole tekstowe otwiera się edycja, ale ramka Konva (Rect) jest wyższa/szersza niż overlay textarea. Przy kolejnych dwuklikach (po ponownym zapisie) ramka i pole edycji mają już zgodne rozmiary.

**Przyczyna:** W `showTextboxEditor` wymiary textarea są początkowo ustawiane z `annotationData.width/height * scale`. Następnie wywoływane jest `resizeEditorToContent()`, które przez `fitTextboxAroundContent(tmp)` liczy rozmiar od treści i **zmienia** `editor.style.width/height` na dopasowane do zawartości. Ramka Konva (Rect + etykieta) **nie** jest w tym momencie aktualizowana – nadal odzwierciedla stare `annotationData.width/height`. Stąd rozjazd: ramka = stare (np. z poprzedniego zapisu lub domyślne), edytor = po resize do treści. Po zapisie zapisujemy poprawne wymiary i przy kolejnym otwarciu `annotationData` ma już dobre wartości, więc ramka i edytor się zgadzają.

**Kierunek:**

- W `showTextboxEditor`, **zaraz po** pierwszym wywołaniu `resizeEditorToContent()` (i ewentualnie `updateSaveBtnPos()`):
  - zaktualizować `annotationData.width` i `annotationData.height` do wymiarów faktycznie ustawionych na edytorze (w współrzędnych unscaled):  
    `annotationData.width = editor.offsetWidth / (state.scale || 1);`  
    `annotationData.height = editor.offsetHeight / (state.scale || 1);`
  - wywołać `redrawOneAnnotation(pageNumber, annotationData.uuid, annotationData)`, żeby ramka (Rect) i etykieta DOM były przerysowane w tych samych wymiarach co textarea.
- Dzięki temu przy pierwszym otwarciu ramka od razu będzie w tym samym rozmiarze co pole edycji; nie trzeba czekać na zapis.

**Miejsce:** `showTextboxEditor`, po bloku z `resizeEditorToContent` / `resizeEditorToContentWithBtn` i `updateSaveBtnPos()`, przed `editor.focus()` (albo tuż po `resizeEditorToContent()` w tej samej sekwencji).

---

## 3. Bug: Pionowa pozycja caretu zależy od zoomu

**Obserwacja:** Pozycja caretu (kursora) w polu edycji jest inna przy różnych poziomach zoomu; powinna być w każdym zoomie taka sama względem linii tekstu. Na różnych monitorach (rozdzielczość, skalowanie systemowe) stałe px pogłębiają rozjazd.

**Przyczyna:** Textarea ma `font-size` ustawiane w px jako `displayFontSize = editorFontSize * scale`, więc przy większym zoomie czcionka jest większa. Padding jest stały w px (`padding: 6px` w `.tl-inline-text-editor`). Stosunek padding/czcionka zmienia się z zoomem i między urządzeniami, więc względna pozycja caretu do linii bazowej tekstu może się przesuwać.

**Kierunek (em dla wewnętrznej typografii):**

- W **CSS** dla `.tl-inline-text-editor` ustawiać w **em** wszystko, co skaluje się z czcionką i ma wpływ na pozycję careta oraz wygląd na różnych monitorach:
  - **padding** w em (np. `padding: 0.4em` – przy 14px daje ~5,6px; dopasować tak, by wizualnie zbliżone do obecnych 6px). Dzięki temu odstęp wewnętrzny skaluje się z `font-size` (ustawianym w JS w px), więc ten sam stosunek przy każdym zoomie i rozdzielczości.
  - **line-height** – obecnie `1.25` (bez jednostki) jest OK; jeśli gdzieś ustawiane w px, rozważyć jednostkę względną (np. `1.25em` lub zostawić bez jednostki).
- W **JS**: jeśli jest ustawiany dodatkowy `top`/offset dla careta w px, zmienić na wartość zależną od rozmiaru czcionki (np. w em przez ustawienie `style.top` z wyliczeniem z `displayFontSize`) albo usunąć, jeśli wystarczy padding w em.
- Cel: ta sama wizualna pozycja caretu względem tekstu przy 100%, 133%, 150%, 200% oraz spójny wygląd na różnych monitorach.

**Miejsce:** `styles.css` – `.tl-inline-text-editor` (padding, ewentualnie line-height); ewentualnie w `pdfannotator_new.v00054.js` – ustawianie `editor.style.*` w `showTextboxEditor` / `showNewTextboxEditor`, jeśli jest tam offset w px.

---

## 4. Wygląd pola po zapisie zależny od zoomu

**Obserwacja:** Pole tekstowe po zapisie (np. z trzema liniami) wygląda różnie w zależności od ustawienia zoomu.

**Przyczyna:** Najpewniej skutek błędnych wymiarów (szerokość/wysokość) zapisanych lub odtwarzanych przy różnych zoomach – np. za wąska szerokość powoduje 3 linie, a przy innym zoomie ten sam błąd objawia się inaczej wizualnie. Może też być efekt zaokrągleń `Math.round(annotation.width * scale)` przy rysowaniu.

**Kierunek:**

- Traktować to jako efekt uboczny bugów 1 i 2: po poprawieniu zapisu szerokości (pkt 1) i synchronizacji ramki z edytorem przy pierwszym otwarciu (pkt 2) wygląd powinien być spójny przy różnych zoomach.
- Jeśli po tych zmianach nadal będzie rozjazd, w drugiej iteracji: ujednolicić sposób zaokrąglania w `drawAnnotation` (np. `Math.ceil` dla `boxWidth`/`boxHeight`, żeby nie obcinać treści).

---

## Kolejność wdrożenia

1. **Szerokość zapisu (pkt 1):** W obu `commit()` wymusić `width = editor.offsetWidth / scale` dla zapisywanego obiektu; ewentualnie dopracować zaokrąglenie w `drawAnnotation` dla textboxa.
2. **Ramka przy pierwszym dwukliku (pkt 2):** W `showTextboxEditor` po `resizeEditorToContent()` zaktualizować `annotationData.width/height` z edytora i wywołać `redrawOneAnnotation`.
3. **Caret (pkt 3):** W CSS dla `.tl-inline-text-editor` – padding (i ewentualnie line-height) w **em**, żeby pozycja careta i proporcje były niezależne od zoomu i spójne na różnych monitorach; ewentualnie korekta offsetów w JS.
4. **Weryfikacja (pkt 4):** Smoke testy: edycja 2 linii → zapis → nadal 2 linie; pierwszy dwuklik → ramka = rozmiar edytora; caret przy 100% i 150% w tej samej pozycji względem tekstu.

Wszystkie zmiany kodu w jednym skrypcie (np. Python w `_staging`) uruchomionym przez `edit-with-maintenance.sh --cmd '...'` (z `|| true` i `php admin/cli/maintenance.php --disable` na końcu).
