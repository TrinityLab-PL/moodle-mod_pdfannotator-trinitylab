# PDF Annotator - Zgloszone problemy i sugestie

Data aktualizacji: 2026-08-26

## Dlug techniczny - link layer / Select (otwarte)

Kontekst: wdrozenie `v209_select_link_toggle_20260823_004029` (fix paritetu Select nad linkiem PDF; `reconstructPdfLinkSelectTap`). Ogolnie lepiej niz przed fixem, ale:

- [x] **Textbox - przesuwanie narzedziem Select (nad linkiem)**
  - Fix: v215 (`remapPdfLinkTransformerInteriorHit`), v218 (cursor + dblclick follow-up).
  - SMOKE PASS (2026-08-26): drag Textboxa Selectem nad linkiem dziala.
  - Backup: `v215_select_textbox_link_drag_20260826_175712`, `v218_textbox_cursor_dblclick_20260826_223753`.

- [ ] **Textbox nad linkiem - double-click reedycja: podwojna ramka (zaznaczenie + edytor)**
  - Wdrozone v219 (`v219_textbox_link_deselect_20260828_173058`): `clearSelection()` tuż przed `showTextboxEditor` w `openTextboxEditorGuarded`. Czeka na SMOKE.
  - Oczekiwane: po wejsciu w reedycje brak rownoleglego stanu „zaznaczone + edytor”; zachowanie jak poza linkiem (edytor bez wiszacego zaznaczenia / krzyzyka).

- [ ] **Textbox nad linkiem - resize kotwic: zaznaczenie w starym rozmiarze**
  - Wdrozone v219 (`v219_textbox_link_deselect_20260828_173058`): deselekcja w `finalizePdfLinkGestureOnUp` tylko dla resize kotwic Textboxa (`!pendingSnapshot` + `wasDragging` + type textbox). Czeka na SMOKE.
  - Oczekiwane: paritet z zachowaniem poza linkiem (po resize: odznaczenie, bez krzyzyka/kotwic; pozycja UI zgodna z aktualnym bbox).

- [ ] **Select nad linkiem przy zoom 150%**
  - Obecnie: przy powiekszeniu 150% pojawiaja sie problemy z klikaniem Select nad obszarem linku (hit-test / warstwa `<a>` vs Konva).
  - Oczekiwane: ten sam paritet zachowania co przy 100% (zaznaczanie, odznaczanie ramka, brak otwarcia URL na adnotacji).
  - Do sprawdzenia: rowniez 133% / 200% i fullscreen.

## Priorytet - funkcjonalne (otwarte)

- [x] **Textbox - regresja: wymaga 2 klikniec do wstawienia**
  - Fix A+B w kodzie (`ignoreNextTextboxClick` + `textboxNativeGesture` / `createGesture`).
  - SMOKE PASS (2026-08-26): potwierdzenie uzytkownika — 1 klik otwiera edytor (w tym po zamknieciu poprzedniego pola).
  - Plan: `/home/piotrad/.cursor/plans/textbox_single-click_fix_e41a065b.plan.md`
  - Powiazane: v192 (native drag), v197 (caret — bez regresji).

- [x] **Textbox - zapis przy scrollu (wariant A/B)**
  - v214 (`maybeCommitHiddenTextboxSession`): auto-zapis gdy pole calkowicie znika z widoku PDF (+1em), nie tylko przy zmianie strony.
  - SMOKE PASS (2026-08-26): 1-4, 3, 5A/5B, 6, 9, A, B.
  - Plany: `/home/piotrad/.cursor/plans/textbox_scroll_save_fix_cd2b433d.plan.md`, `/home/piotrad/.cursor/plans/textbox_hide-to-save_b047cf6b.plan.md`
  - Backup: `v214_textbox_hide_to_save_20260825_222051`

- [ ] **Przesuwanie obiektu `drawing` (kreska)**
  - Obecnie: jest lepiej, ale ramka przesuwania bywa znacznie obok samego obiektu (kreski).
  - Oczekiwane: ramka i obiekt poruszaja sie spojnie, bez rozjazdu.

- [ ] **Gruba kreska (szczegolnie krzywa)**
  - Obecnie: wizualnie zbyt "pusta", niewystarczajaco wypelniona.
  - Oczekiwane: bardziej pelna, jednolita, lepiej wypelniona kolorem.

- [ ] **Nieplanowane zaznaczanie tekstu PDF**
  - Obecnie: zdarza sie przypadkowe uruchamianie selection tekstu.
  - Oczekiwane: zaznaczanie tylko gdy uzytkownik faktycznie pracuje narzedziem zaznaczania.

- [ ] **Rozjazd zaznaczen `highlight` i `strikeout`**
  - Obecnie: marker i strikeout potrafia zaznaczac obok tekstu.
  - Oczekiwane: zaznaczenie idealnie pokrywa tekst.

## UX / UI (otwarte)

- [ ] **Menu / toolbar**
  - Obecnie: przyciski sa za male.
  - Oczekiwane: bardziej intuicyjne i nowoczesne menu, latwiejsze w uzyciu, wygodniejsze trafianie.

- [ ] **Komentarze KK dla obiektow bez komentarza**
  - Obecnie: obiekty/adnotacje, ktore z zalozenia nie maja komentarza, moga uruchamiac KK.
  - Oczekiwane: takie obiekty nie otwieraja KK i nie generuja zadnych "pseudo-komentarzy" typu:
    - "to jest obiekt/adnotacja, ktora nie uzywa komentarza"
    - ani podobnych placeholderow.

## Kontekst (potwierdzone obserwacje)

- [x] Wersja bazowa: `v91_drag_sync_point_textbox_area_drawing` (backup: 4 OK).
- [x] Palety kolorow w fullscreen: widoczne poprawnie.
- [x] Przesuwanie point/textbox/area: poprawione wzgledem stanu poczatkowego, ale powyzsze problemy nadal do domkniecia.

