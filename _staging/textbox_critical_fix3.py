#!/usr/bin/env python3
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

# 1) showTextboxEditor: użyj fitTextboxAroundContent do wyliczenia szerokości/wysokości
old_show_resize = """        function resizeEditorToContent() {
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

new_show_resize = """        function resizeEditorToContent() {
            var tmp = {
                size: editorFontSize,
                font: editorFontFamily,
                color: annotationData.color || state.textColor || '#111827',
                content: editor.value || '',
                width: Math.max(1, annotationData.width || 1),
                height: Math.max(1, annotationData.height || 1),
                x: annotationData.x || 0,
                y: annotationData.y || 0
            };
            fitTextboxAroundContent(tmp);
            var scale = state.scale || 1;
            var w = Math.max(80, Math.ceil(tmp.width * scale));
            var h = Math.max(36, Math.ceil(tmp.height * scale));
            editor.style.width = w + 'px';
            editor.style.height = h + 'px';
        }"""

if old_show_resize in js:
    js = js.replace(old_show_resize, new_show_resize, 1)

# 2) showNewTextboxEditor: użyj fitTextboxAroundContent dla nowego pola
old_new_resize = """        function resizeEditorToContent() {
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

new_new_resize = """        function resizeEditorToContent() {
            var tmp = {
                size: editorFontSize,
                font: editorFontFamily,
                color: state.textColor || '#111827',
                content: editor.value || '',
                width: 1,
                height: 1,
                x: 0,
                y: 0
            };
            fitTextboxAroundContent(tmp);
            var scale = state.scale || 1;
            var w = Math.max(60, Math.ceil(tmp.width * scale));
            var h = Math.max(36, Math.ceil(tmp.height * scale));
            editor.style.width = w + 'px';
            editor.style.height = h + 'px';
        }"""

if old_new_resize in js:
    js = js.replace(old_new_resize, new_new_resize, 1)

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

print('textbox_critical_fix3: OK')

