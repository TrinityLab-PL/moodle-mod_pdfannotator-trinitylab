#!/usr/bin/env python3
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')
CSS = os.path.join(root, 'mod', 'pdfannotator', 'styles.css')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

# 1) Mouseup: klik w inne adnotacje przełącza na Cursor, nie tworzy pola
old_mouseup = """            if (tool === 'textbox' && pointer && !draftRect) {
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
                }
                showNewTextboxEditor(pageNumber, pointer.x, pointer.y);
                return;
            }"""

new_mouseup = """            if (tool === 'textbox' && pointer && !draftRect) {
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

if old_mouseup in js:
    js = js.replace(old_mouseup, new_mouseup, 1)

# 2) Pozycja kursora: usunięcie caretOffset, top tuż nad kliknięciem
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

# 3) Resize: brak miękkiego zawijania – wrap=off dla textarea
old_new_editor = """        var editor = document.createElement('textarea');
        editor.className = 'tl-inline-text-editor';
        editor.value = '';"""

new_new_editor = """        var editor = document.createElement('textarea');
        editor.className = 'tl-inline-text-editor';
        editor.value = '';
        editor.setAttribute('wrap', 'off');"""

if old_new_editor in js:
    js = js.replace(old_new_editor, new_new_editor, 1)

old_existing_editor = """        var editor = document.createElement('textarea');
        editor.className = 'tl-inline-text-editor';
        editor.dataset.annotationId = String(annotationData.uuid);
        editor.value = annotationData.content || '';"""

new_existing_editor = """        var editor = document.createElement('textarea');
        editor.className = 'tl-inline-text-editor';
        editor.dataset.annotationId = String(annotationData.uuid);
        editor.value = annotationData.content || '';
        editor.setAttribute('wrap', 'off');"""

if old_existing_editor in js:
    js = js.replace(old_existing_editor, new_existing_editor, 1)

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

# 4) CSS: usunięcie centrowania tekstu w edytorze
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

print('textbox_followup_fix: OK')

