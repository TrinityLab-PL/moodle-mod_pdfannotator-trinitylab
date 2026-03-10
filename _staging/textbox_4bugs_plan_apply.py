#!/usr/bin/env python3
"""
Apply plan: Textbox 4 bugi (caret, wyśrodkowanie, rozmiar, klik/dwuklik).
Run from Moodle root. Edits: js_new/pdfannotator_new.v00054.js, styles.css.
"""
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')
CSS = os.path.join(root, 'mod', 'pdfannotator', 'styles.css')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

# --- Bug 4a: mouseup – textbox: only selectAnnotation, no showTextboxEditor
old_4a = """                if (hitGroup) {
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

new_4a = """                if (hitGroup) {
                    var data = hitGroup.getAttr('annotationData');
                    if (data && data.type === 'textbox') {
                        selectAnnotation(pageNumber, hitGroup);
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

if old_4a not in js:
    raise SystemExit('Bug 4a: mouseup textbox block not found')
js = js.replace(old_4a, new_4a, 1)

# --- Bug 4b: group click – remove textbox+alreadySelected showTextboxEditor
old_4b = """        group.on('click tap', function (event) {
            event.cancelBubble = true;
            var alreadySelected = state.activeAnnotation && state.activeAnnotation.annotationId === String(annotation.uuid);
            selectAnnotation(pageNumber, group);
            ensureCommentPanelVisible();
            loadCommentsForAnnotation(annotation.uuid, annotation.type);
            if (annotation.type === 'textbox' && alreadySelected) {
                var currentData = group.getAttr('annotationData') || annotation;
                showTextboxEditor(pageNumber, currentData);
            }
        });"""

new_4b = """        group.on('click tap', function (event) {
            event.cancelBubble = true;
            selectAnnotation(pageNumber, group);
            ensureCommentPanelVisible();
            loadCommentsForAnnotation(annotation.uuid, annotation.type);
        });"""

if old_4b not in js:
    raise SystemExit('Bug 4b: group click tap block not found')
js = js.replace(old_4b, new_4b, 1)

# --- Bug 1 + Bug 2 (part): showNewTextboxEditor – baselineOffset, lineHeight 1.25
old_1_2_new = """        var paddingTop = 5;
        var paddingLeft = 6;
        editor.style.left = (pointerX - paddingLeft) + 'px';
        editor.style.top = (pointerY - paddingTop) + 'px';
        editor.style.minWidth = '60px';
        editor.style.minHeight = '36px';
        editor.style.width = '60px';
        editor.style.height = '36px';
        editor.style.fontSize = displayFontSize + 'px';
        editor.style.fontFamily = editorFontFamily + ', sans-serif';
        editor.style.color = state.textColor || '#111827';
        editor.style.lineHeight = '1.2';"""

new_1_2_new = """        var paddingTop = 5;
        var paddingLeft = 6;
        var baselineOffset = Math.round(displayFontSize * 0.78);
        editor.style.left = (pointerX - paddingLeft) + 'px';
        editor.style.top = (pointerY - paddingTop - baselineOffset) + 'px';
        editor.style.minWidth = '60px';
        editor.style.minHeight = '36px';
        editor.style.width = '60px';
        editor.style.height = '36px';
        editor.style.fontSize = displayFontSize + 'px';
        editor.style.fontFamily = editorFontFamily + ', sans-serif';
        editor.style.color = state.textColor || '#111827';
        editor.style.lineHeight = '1.25';"""

if old_1_2_new not in js:
    raise SystemExit('Bug 1/2: showNewTextboxEditor padding/lineHeight block not found')
js = js.replace(old_1_2_new, new_1_2_new, 1)

# --- Bug 1: showNewTextboxEditor commit – unscaledBoxY with baselineOffset
old_1_commit = """            var unscaledBoxX = (pointerX - paddingLeft) / state.scale;
            var unscaledBoxY = (pointerY - paddingTop) / state.scale;"""

new_1_commit = """            var unscaledBoxX = (pointerX - paddingLeft) / state.scale;
            var unscaledBoxY = (pointerY - paddingTop - baselineOffset) / state.scale;"""

if old_1_commit not in js:
    raise SystemExit('Bug 1: showNewTextboxEditor commit unscaledBox not found')
js = js.replace(old_1_commit, new_1_commit, 1)

# --- Bug 2: showTextboxEditor – lineHeight 1.25 and measureEl 1.25 (do before global measureEl replace)
old_2_show = """        editor.style.color = annotationData.color || state.textColor || '#111827';
        pageElement.appendChild(editor);
        var measureEl = document.createElement('div');
        measureEl.setAttribute('aria-hidden', 'true');
        measureEl.style.cssText = 'position:absolute;left:-9999px;top:0;visibility:hidden;white-space:pre-wrap;word-wrap:break-word;pointer-events:none;margin:0;border:none;padding:0;';
        measureEl.style.fontSize = displayFontSize + 'px';
        measureEl.style.fontFamily = editorFontFamily + ', sans-serif';
        measureEl.style.lineHeight = '1.2';
        pageElement.appendChild(measureEl);
        function resizeEditorToContent() {
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
            fitTextboxAroundContent(tmp);"""

new_2_show = """        editor.style.color = annotationData.color || state.textColor || '#111827';
        editor.style.lineHeight = '1.25';
        pageElement.appendChild(editor);
        var measureEl = document.createElement('div');
        measureEl.setAttribute('aria-hidden', 'true');
        measureEl.style.cssText = 'position:absolute;left:-9999px;top:0;visibility:hidden;white-space:pre-wrap;word-wrap:break-word;pointer-events:none;margin:0;border:none;padding:0;';
        measureEl.style.fontSize = displayFontSize + 'px';
        measureEl.style.fontFamily = editorFontFamily + ', sans-serif';
        measureEl.style.lineHeight = '1.25';
        pageElement.appendChild(measureEl);
        function resizeEditorToContent() {
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
            fitTextboxAroundContent(tmp);"""

if old_2_show not in js:
    raise SystemExit('Bug 2: showTextboxEditor editor+measureEl block not found')
js = js.replace(old_2_show, new_2_show, 1)

# --- Bug 2: showNewTextboxEditor measureEl lineHeight 1.25 (only one left after above)
js = js.replace("measureEl.style.lineHeight = '1.2';", "measureEl.style.lineHeight = '1.25';")

# --- Bug 3: showNewTextboxEditor commit already has max(measure, editor) – ensure it's there; sync lineHeight in fitTextboxAroundContent is 1.25 (already fontSize*1.25). No code change needed for 3 if 2 is done; label uses 1.2 – change to 1.25 for consistency
# In drawAnnotation for textbox, labelEl.style.lineHeight = '1.2' -> '1.25'
js = js.replace(
    "labelEl.style.lineHeight = '1.2';",
    "labelEl.style.lineHeight = '1.25';",
    1
)

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

# --- CSS: Bug 2 – .tl-inline-text-editor padding 6px 6px, line-height 1.25
with open(CSS, 'r', encoding='utf-8') as f:
    css = f.read()

old_css = """.tl-inline-text-editor {
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

new_css = """.tl-inline-text-editor {
    position: absolute;
    z-index: 30;
    outline: none !important;
    outline-width: 0 !important;
    outline-style: none !important;
    -webkit-appearance: none;
    appearance: none;
    border-radius: 7px;
    padding: 6px;
    resize: none !important;
    overflow: hidden;
    background: rgba(240, 246, 253, 0.6);
    color: #111827;
    font-size: 14px;
    line-height: 1.25;
    -webkit-font-smoothing: subpixel-antialiased;
    -moz-osx-font-smoothing: auto;
    text-rendering: geometricPrecision;
    transform: translateZ(0);
}"""

if old_css not in css:
    raise SystemExit('Bug 2 CSS: .tl-inline-text-editor block not found')
css = css.replace(old_css, new_css, 1)

with open(CSS, 'w', encoding='utf-8') as f:
    f.write(css)

print('textbox_4bugs_plan_apply: OK')
