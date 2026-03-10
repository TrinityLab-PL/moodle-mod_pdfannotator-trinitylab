#!/usr/bin/env python3
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')
CSS = os.path.join(root, 'mod', 'pdfannotator', 'styles.css')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

# 1) Resize: mierzenie szerokości w nowrap (showTextboxEditor)
old_resize_show = """        function resizeEditorToContent() {
            var val = editor.value || ' ';
            measureEl.textContent = val;
            var contentW = measureEl.offsetWidth;
            var contentH = measureEl.offsetHeight;
            var padX = 6;
            var padY = 5;
            var w = Math.max(80, Math.ceil(contentW) + padX * 2 + 2);
            var h = Math.max(36, Math.ceil(contentH) + padY * 2 + 2);
            editor.style.width = w + 'px';
            editor.style.height = h + 'px';
        }"""

new_resize_show = """        function resizeEditorToContent() {
            var val = editor.value || ' ';
            measureEl.textContent = val;
            var prevWhiteSpace = measureEl.style.whiteSpace;
            measureEl.style.whiteSpace = 'nowrap';
            var contentW = measureEl.offsetWidth;
            measureEl.style.whiteSpace = prevWhiteSpace || 'pre-wrap';
            measureEl.style.width = (contentW + 2) + 'px';
            var contentH = measureEl.offsetHeight;
            var padX = 6;
            var padY = 5;
            var w = Math.max(80, Math.ceil(contentW) + padX * 2 + 2);
            var h = Math.max(36, Math.ceil(contentH) + padY * 2 + 2);
            editor.style.width = w + 'px';
            editor.style.height = h + 'px';
        }"""

if old_resize_show not in js:
    raise SystemExit('resizeEditorToContent(showTextboxEditor) not found')
js = js.replace(old_resize_show, new_resize_show, 1)

# 1) Resize: mierzenie szerokości w nowrap (showNewTextboxEditor)
old_resize_new = """        function resizeEditorToContent() {
            var val = editor.value || ' ';
            measureEl.textContent = val;
            var contentW = measureEl.offsetWidth;
            var contentH = measureEl.offsetHeight;
            var w = Math.max(60, Math.ceil(contentW) + paddingLeft * 2 + 2);
            var h = Math.max(36, Math.ceil(contentH) + paddingTop * 2 + 2);
            editor.style.width = w + 'px';
            editor.style.height = h + 'px';
        }"""

new_resize_new = """        function resizeEditorToContent() {
            var val = editor.value || ' ';
            measureEl.textContent = val;
            var prevWhiteSpace = measureEl.style.whiteSpace;
            measureEl.style.whiteSpace = 'nowrap';
            var contentW = measureEl.offsetWidth;
            measureEl.style.whiteSpace = prevWhiteSpace || 'pre-wrap';
            measureEl.style.width = (contentW + 2) + 'px';
            var contentH = measureEl.offsetHeight;
            var w = Math.max(60, Math.ceil(contentW) + paddingLeft * 2 + 2);
            var h = Math.max(36, Math.ceil(contentH) + paddingTop * 2 + 2);
            editor.style.width = w + 'px';
            editor.style.height = h + 'px';
        }"""

if old_resize_new not in js:
    raise SystemExit('resizeEditorToContent(showNewTextboxEditor) not found')
js = js.replace(old_resize_new, new_resize_new, 1)

# 2) Klik w istniejący textbox – wybór zamiast nowego pola
old_mouseup_textbox = """            if (tool === 'textbox' && pointer && !draftRect) {
                if (state.ignoreNextTextboxClick) {
                    state.ignoreNextTextboxClick = false;
                    return;
                }
                showNewTextboxEditor(pageNumber, pointer.x, pointer.y);
                return;
            }"""

new_mouseup_textbox = """            if (tool === 'textbox' && pointer && !draftRect) {
                if (state.ignoreNextTextboxClick) {
                    state.ignoreNextTextboxClick = false;
                    return;
                }
                var hit = stage.getIntersection(pointer);
                var hitGroup = null;
                if (hit) {
                    if (hit.getAttr && hit.getAttr('annotationData')) {
                        hitGroup = hit;
                    } else if (hit.getParent && hit.getParent().getAttr && hit.getParent().getAttr('annotationData')) {
                        hitGroup = hit.getParent();
                    }
                }
                if (hitGroup) {
                    var data = hitGroup.getAttr('annotationData');
                    if (data && data.type === 'textbox') {
                        selectAnnotation(pageNumber, hitGroup);
                        showTextboxEditor(pageNumber, data);
                        return;
                    }
                    if (data && data.type !== 'textbox') {
                        selectAnnotation(pageNumber, hitGroup);
                        setTool('cursor');
                        return;
                    }
                }
                showNewTextboxEditor(pageNumber, pointer.x, pointer.y);
                return;
            }"""

if old_mouseup_textbox in js:
    js = js.replace(old_mouseup_textbox, new_mouseup_textbox, 1)

# 3) Rect ramki textboxa: tylko tło, bez stroke
old_rect_textbox = """            group.add(new Konva.Rect({
                x: boxX,
                y: boxY,
                width: boxWidth,
                height: boxHeight,
                cornerRadius: 7,
                fill: 'rgba(235, 242, 252, 0.35)',
                stroke: 'rgba(148, 163, 184, 0.65)',
                strokeWidth: 1
            }));"""

new_rect_textbox = """            group.add(new Konva.Rect({
                x: boxX,
                y: boxY,
                width: boxWidth,
                height: boxHeight,
                cornerRadius: 7,
                fill: 'rgba(235, 242, 252, 0.35)',
                stroke: 'rgba(235, 242, 252, 0.35)',
                strokeWidth: 0
            }));"""

if old_rect_textbox not in js:
    raise SystemExit('textbox rect block not found')
js = js.replace(old_rect_textbox, new_rect_textbox, 1)

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

# 4) Centrowanie tekstu
with open(CSS, 'r', encoding='utf-8') as f:
    css = f.read()

old_inline = """.tl-inline-text-editor {
    position: absolute;
    z-index: 30;
    outline: none !important;
    outline-width: 0 !important;
    outline-style: none !important;
    -webkit-appearance: none;
    appearance: none;
    border-radius: 7px;
    padding: 5px 6px;
    resize: none !important;
    overflow: hidden;
    background: rgba(240, 246, 253, 0.6);
    color: #111827;
    font-size: 14px;
    -webkit-font-smoothing: subpixel-antialiased;
    -moz-osx-font-smoothing: auto;
    text-rendering: geometricPrecision;
    transform: translateZ(0);
}"""

if old_inline in css:
    css = css.replace(old_inline, new_inline, 1)

old_label = """.tl-textbox-label {
    position: absolute;
    z-index: 25;
    pointer-events: none;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: subpixel-antialiased;
    -moz-osx-font-smoothing: auto;
    text-rendering: geometricPrecision;
    transform: translateZ(0);
}"""

new_label = """.tl-textbox-label {
    position: absolute;
    z-index: 25;
    pointer-events: none;
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    -webkit-font-smoothing: subpixel-antialiased;
    -moz-osx-font-smoothing: auto;
    text-rendering: geometricPrecision;
    transform: translateZ(0);
}"""

if old_label not in css:
    raise SystemExit('.tl-textbox-label block not found in CSS')
css = css.replace(old_label, new_label, 1)

with open(CSS, 'w', encoding='utf-8') as f:
    f.write(css)

print('bugi_krytyczne_textbox_apply: OK')

