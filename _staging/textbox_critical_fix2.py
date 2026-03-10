#!/usr/bin/env python3
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')
CSS = os.path.join(root, 'mod', 'pdfannotator', 'styles.css')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

# 1) stage mouseup: podpisz event i dodaj domTarget guard + poprawka dla innych typów
if "stage.on('mouseup touchend', function () {" in js:
    js = js.replace("stage.on('mouseup touchend', function () {",
                    "stage.on('mouseup touchend', function (event) {", 1)

old_textbox_branch = """            if (tool === 'textbox' && pointer && !draftRect) {
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

new_textbox_branch = """            if (tool === 'textbox' && pointer && !draftRect) {
                if (state.ignoreNextTextboxClick) {
                    state.ignoreNextTextboxClick = false;
                    return;
                }
                var domTarget = event && event.evt && event.evt.target;
                if (domTarget && domTarget.closest && (domTarget.closest('.tl-inline-text-editor') || domTarget.closest('.tl-textbox-label'))) {
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

if old_textbox_branch in js:
    js = js.replace(old_textbox_branch, new_textbox_branch, 1)

# 2) showNewTextboxEditor: pozycja kursora tuż przy kliknięciu (bez caretOffset)
old_pos = """        var paddingTop = 5;
        var paddingLeft = 6;
        editor.style.left = (pointerX - paddingLeft) + 'px';
        editor.style.top = (pointerY - paddingTop) + 'px';"""

if old_pos not in js:
    old_pos = """        var paddingTop = 5;
        var paddingLeft = 6;
        var caretOffset = displayFontSize * 0.72;
        editor.style.left = (pointerX - paddingLeft) + 'px';
        editor.style.top = (pointerY - paddingTop - caretOffset) + 'px';"""

new_pos = """        var paddingTop = 5;
        var paddingLeft = 6;
        editor.style.left = (pointerX - paddingLeft) + 'px';
        editor.style.top = (pointerY - paddingTop) + 'px';"""

if old_pos in js:
    js = js.replace(old_pos, new_pos, 1)

# 3) Resize: na razie tylko wrap='off' na edytorach – już ustawione w poprzednim skrypcie, więc tu nic nie zmieniamy

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

# 4) CSS: usunięcie text-align:center z tl-inline-text-editor (jeśli jeszcze jest)
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
    text-align: center;
    -webkit-font-smoothing: subpixel-antialiased;
    -moz-osx-font-smoothing: auto;
    text-rendering: geometricPrecision;
    transform: translateZ(0);
}"""

new_inline = """.tl-inline-text-editor {
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

with open(CSS, 'w', encoding='utf-8') as f:
    f.write(css)

print('textbox_critical_fix2: OK')

