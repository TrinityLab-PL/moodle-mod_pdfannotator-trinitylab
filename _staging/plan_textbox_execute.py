#!/usr/bin/env python3
"""Plan Textbox: ramka off, mniejszy padding, Textbox aktywny po zapisie (bez rect)."""
import os

root = os.getcwd()
js_path = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')
css_path = os.path.join(root, 'mod', 'pdfannotator', 'styles.css')

with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# --- 4. Nie przełączać na Cursor po zamknięciu edytora (tylko cleanup w showNewTextboxEditor)
js = js.replace(
    """                editor.remove();
            } catch (e) {}
            setTool('cursor');
        }

        function commit(fromBlur) {""",
    """                editor.remove();
            } catch (e) {}
        }

        function commit(fromBlur) {""",
    1
)

# --- 2 + 3. showNewTextboxEditor: padding 5/6, bez border/boxShadow, bez focus listener
js = js.replace(
    """        var paddingTop = 10;
        var paddingLeft = 12;
        var caretOffset = displayFontSize * 0.72;
        editor.style.left = (pointerX - paddingLeft) + 'px';
        editor.style.top = (pointerY - paddingTop - caretOffset) + 'px';
        editor.style.minWidth = '60px';
        editor.style.minHeight = '36px';
        editor.style.width = '60px';
        editor.style.height = '36px';
        editor.style.fontSize = displayFontSize + 'px';
        editor.style.fontFamily = editorFontFamily + ', sans-serif';
        editor.style.color = state.textColor || '#111827';
        editor.style.lineHeight = '1.2';
        editor.style.border = '1px solid rgba(148, 163, 184, 0.4)';
        editor.style.outline = 'none';
        editor.style.boxShadow = '0 1px 4px rgba(15, 23, 42, 0.08)';
        editor.style.webkitFontSmoothing = 'subpixel-antialiased';
        editor.style.textRendering = 'geometricPrecision';

        editor.addEventListener('focus', function () {
            editor.style.border = '1px solid rgba(148, 163, 184, 0.4)';
            editor.style.outline = 'none';
            editor.style.boxShadow = '0 1px 4px rgba(15, 23, 42, 0.08)';
        });

        pageElement.appendChild(editor);""",
    """        var paddingTop = 5;
        var paddingLeft = 6;
        var caretOffset = displayFontSize * 0.72;
        editor.style.left = (pointerX - paddingLeft) + 'px';
        editor.style.top = (pointerY - paddingTop - caretOffset) + 'px';
        editor.style.minWidth = '60px';
        editor.style.minHeight = '36px';
        editor.style.width = '60px';
        editor.style.height = '36px';
        editor.style.fontSize = displayFontSize + 'px';
        editor.style.fontFamily = editorFontFamily + ', sans-serif';
        editor.style.color = state.textColor || '#111827';
        editor.style.lineHeight = '1.2';
        editor.style.outline = 'none';
        editor.style.webkitFontSmoothing = 'subpixel-antialiased';
        editor.style.textRendering = 'geometricPrecision';

        pageElement.appendChild(editor);""",
    1
)

# --- 3. showNewTextboxEditor resizeEditorToContent: formula z paddingLeft/paddingTop (już 6 i 5)
js = js.replace(
    """            var w = Math.max(60, Math.ceil(contentW) + paddingLeft * 2 + 4);
            var h = Math.max(36, Math.ceil(contentH) + paddingTop * 2 + 4);""",
    """            var w = Math.max(60, Math.ceil(contentW) + paddingLeft * 2 + 2);
            var h = Math.max(36, Math.ceil(contentH) + paddingTop * 2 + 2);""",
    1
)

# --- 3. showTextboxEditor: padX 6, padY 5
js = js.replace(
    """        function resizeEditorToContent() {
            var val = editor.value || ' ';
            measureEl.textContent = val;
            var contentW = measureEl.offsetWidth;
            var contentH = measureEl.offsetHeight;
            var padX = 12;
            var padY = 10;
            var w = Math.max(80, Math.ceil(contentW) + padX * 2 + 4);
            var h = Math.max(36, Math.ceil(contentH) + padY * 2 + 4);
            editor.style.width = w + 'px';
            editor.style.height = h + 'px';
        }
        editor.addEventListener('input', resizeEditorToContent);""",
    """        function resizeEditorToContent() {
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
        }
        editor.addEventListener('input', resizeEditorToContent);""",
    1
)

# --- 3. fitTextboxAroundContent
js = js.replace(
    """        var lineHeight = fontSize * 1.25;
        var textHeight = Math.max(lineHeight, lines.length * lineHeight);
        var paddingX = 10;
        var paddingY = 8;

        var newWidth = Math.max(40, Math.ceil(maxWidth + paddingX * 2));""",
    """        var lineHeight = fontSize * 1.25;
        var textHeight = Math.max(lineHeight, lines.length * lineHeight);
        var paddingX = 6;
        var paddingY = 5;

        var newWidth = Math.max(40, Math.ceil(maxWidth + paddingX * 2));""",
    1
)

# --- 3. transformend (textbox labelEl) - first block
js = js.replace(
    """            if (annotation.type === 'textbox') {
                var labelEl = activeGroup.getAttr('textboxLabelEl');
                if (labelEl) {
                    var padX = 12;
                    var padY = 10;
                    labelEl.style.left = (annotation.x * scale + padX) + 'px';
                    labelEl.style.top = (annotation.y * scale + padY) + 'px';
                    labelEl.style.width = Math.max(0, annotation.width * scale - padX * 2) + 'px';
                    labelEl.style.height = Math.max(0, annotation.height * scale - padY * 2) + 'px';
                }
            }
            activeGroup.setAttr('annotationData', annotation);
            persistAnnotation(annotation);
        });
        stage.add(annotationLayer);""",
    """            if (annotation.type === 'textbox') {
                var labelEl = activeGroup.getAttr('textboxLabelEl');
                if (labelEl) {
                    var padX = 6;
                    var padY = 5;
                    labelEl.style.left = (annotation.x * scale + padX) + 'px';
                    labelEl.style.top = (annotation.y * scale + padY) + 'px';
                    labelEl.style.width = Math.max(0, annotation.width * scale - padX * 2) + 'px';
                    labelEl.style.height = Math.max(0, annotation.height * scale - padY * 2) + 'px';
                }
            }
            activeGroup.setAttr('annotationData', annotation);
            persistAnnotation(annotation);
        });
        stage.add(annotationLayer);""",
    1
)

# --- 3. onAnnotationDragged / redraw label (padX padY)
js = js.replace(
    """            if (annotation.type === 'textbox') {
                var labelEl = group.getAttr('textboxLabelEl');
                if (labelEl) {
                    var padX = 12;
                    var padY = 10;
                    labelEl.style.left = (annotation.x * scale + padX) + 'px';
                    labelEl.style.top = (annotation.y * scale + padY) + 'px';
                }
            }
        } else if (annotation.type === 'drawing') {""",
    """            if (annotation.type === 'textbox') {
                var labelEl = group.getAttr('textboxLabelEl');
                if (labelEl) {
                    var padX = 6;
                    var padY = 5;
                    labelEl.style.left = (annotation.x * scale + padX) + 'px';
                    labelEl.style.top = (annotation.y * scale + padY) + 'px';
                }
            }
        } else if (annotation.type === 'drawing') {""",
    1
)

# --- 3. drawOneAnnotation textbox label
js = js.replace(
    """            var textPaddingX = 12;
            var textPaddingY = 10;
            var textFontSizePx = Math.max(10, Math.round((annotation.size || state.textSize || 14) * scale));""",
    """            var textPaddingX = 6;
            var textPaddingY = 5;
            var textFontSizePx = Math.max(10, Math.round((annotation.size || state.textSize || 14) * scale));""",
    1
)

# --- commit unscaledBox uses paddingLeft/paddingTop - already 6 and 5 in showNewTextboxEditor
# showNewTextboxEditor commit: unscaledBoxX = (pointerX - paddingLeft) - ok, variables stay

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)

# --- CSS: ramka off, padding mniejszy
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

old_css = """.tl-inline-text-editor {
    position: absolute;
    z-index: 30;
    border: 1px solid rgba(148, 163, 184, 0.5) !important;
    outline: none !important;
    outline-width: 0 !important;
    outline-style: none !important;
    -webkit-appearance: none;
    appearance: none;
    box-shadow: 0 1px 6px rgba(15, 23, 42, 0.1);
    border-radius: 7px;
    padding: 10px 12px;
    resize: none !important;
    overflow: hidden;
    background: rgba(240, 246, 253, 0.6);
    color: #111827;
    font-size: 14px;
    -webkit-font-smoothing: subpixel-antialiased;
    -moz-osx-font-smoothing: auto;
    text-rendering: geometricPrecision;
    transform: translateZ(0);
}

.tl-inline-text-editor:focus,
.tl-inline-text-editor:focus-visible,
.tl-inline-text-editor:active {
    outline: none !important;
    outline-width: 0 !important;
    outline-offset: 0 !important;
    border-color: rgba(148, 163, 184, 0.5) !important;
    box-shadow: 0 1px 6px rgba(15, 23, 42, 0.1) !important;
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
}

.tl-inline-text-editor:focus,
.tl-inline-text-editor:focus-visible,
.tl-inline-text-editor:active {
    outline: none !important;
    outline-width: 0 !important;
    outline-offset: 0 !important;
}"""

if old_css not in css:
    raise SystemExit('CSS block .tl-inline-text-editor not found')
css = css.replace(old_css, new_css, 1)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print('OK: textbox plan applied')
