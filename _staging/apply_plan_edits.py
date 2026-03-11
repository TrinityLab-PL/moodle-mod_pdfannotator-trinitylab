#!/usr/bin/env python3
"""Apply plan edits: Bug 1, 2, 3, 4, 5 for PDF Annotator."""
import os

MOODLE = os.environ.get('MOODLE_ROOT', '/var/www/html/moodle')
BASE = os.path.join(MOODLE, 'mod/pdfannotator')
CSS = os.path.join(BASE, 'styles.css')
JS = os.path.join(BASE, 'js_new', 'pdfannotator_new.v00054.js')

def main():
    # --- Bug 1 & 5: styles.css ---
    with open(CSS, 'r', encoding='utf-8') as f:
        css = f.read()

    # Bug 5: .tl-textbox-label - align top, text left
    css = css.replace(
        '''.tl-textbox-label {
    position: absolute;
    z-index: 25;
    pointer-events: none;
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;''',
        '''.tl-textbox-label {
    position: absolute;
    z-index: 25;
    pointer-events: none;
    margin: 0;
    padding: 0;
    display: flex;
    align-items: flex-start;
    justify-content: flex-start;
    text-align: left;'''
    )

    # Bug 1: fullscreen text color - insert after .tl-textbox-label block (before .tl-inline-text-editor::selection)
    insert_marker = '.tl-inline-text-editor::selection {'
    fullscreen_block = '''
/* Fullscreen: force dark text for inline editor and textbox label */
body.tl-pdf-fullscreen .tl-inline-text-editor,
body.tl-pdf-fullscreen .tl-textbox-label {
    color: #111827 !important;
}

'''
    if fullscreen_block.strip() not in css and insert_marker in css:
        css = css.replace(insert_marker, fullscreen_block + insert_marker)

    with open(CSS, 'w', encoding='utf-8') as f:
        f.write(css)

    # --- JS edits ---
    with open(JS, 'r', encoding='utf-8') as f:
        js = f.read()

    # Bug 2.2: clearSelection at start of mouseup/touchend when pointer exists
    old = "            if (pointer) {\n                var domTarget = event && event.evt && event.evt.target;"
    new = "            if (pointer) {\n                clearSelection();\n                var domTarget = event && event.evt && event.evt.target;"
    if old in js and "clearSelection();\n                var domTarget" not in js:
        js = js.replace(old, new)

    # Bug 4: overlay (transformer) hit check before opening new textbox
    old4 = """                var pageState = getPageState(pageNumber);
                var hit = (pageState && pageState.annotationLayer)
                    ? pageState.annotationLayer.getIntersection(pointer)
                    : stage.getIntersection(pointer);
                var hitGroup = null;"""
    new4 = """                var pageState = getPageState(pageNumber);
                var overlayHit = pageState && pageState.overlayLayer ? pageState.overlayLayer.getIntersection(pointer) : null;
                if (overlayHit && pageState) {
                    var node = overlayHit;
                    while (node) {
                        if (node === pageState.transformer) {
                            return;
                        }
                        node = node.getParent ? node.getParent() : null;
                    }
                }
                var hit = (pageState && pageState.annotationLayer)
                    ? pageState.annotationLayer.getIntersection(pointer)
                    : stage.getIntersection(pointer);
                var hitGroup = null;"""
    if old4 in js and "overlayHit" not in js.split("if (tool === 'textbox'")[1].split("showNewTextboxEditor")[0]:
        js = js.replace(old4, new4)

    # Bug 3: empty content - set ignoreNextTextboxClick before cleanup
    old3 = """            var content = String(editor.value || '').trim();
            if (!content) {
                cleanup();
                return;
            }

            var pageState = getPageState(pageNumber);
            if (!pageState) {
                cleanup();
                return;
            }

            var unscaledBoxX = (pointerX - paddingLeft) / state.scale;"""
    new3 = """            var content = String(editor.value || '').trim();
            if (!content) {
                state.ignoreNextTextboxClick = true;
                cleanup();
                return;
            }

            var pageState = getPageState(pageNumber);
            if (!pageState) {
                cleanup();
                return;
            }

            var unscaledBoxX = (pointerX - paddingLeft) / state.scale;"""
    if "state.ignoreNextTextboxClick = true;" not in js or "if (!content)" in js:
        js = js.replace(
            """            var content = String(editor.value || '').trim();
            if (!content) {
                cleanup();
                return;
            }""",
            """            var content = String(editor.value || '').trim();
            if (!content) {
                state.ignoreNextTextboxClick = true;
                cleanup();
                return;
            }"""
        )

    # Bug 2.1: showNewTextboxEditor - do not select after create
    old2a = """                if (createdGroup) {
                    selectAnnotation(pageNumber, createdGroup);
                }
                ensureCommentPanelVisible();
                loadCommentsForAnnotation(created.uuid, created.type);
            }).catch(function (error) {
                console.error('Create annotation failed', error);
            }).finally(function () {
                cleanup();
            });
        }

        editor.addEventListener('blur', function () { commit(true); });
        editor.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                committed = true;
                cleanup();"""
    new2a = """                if (createdGroup) {
                    clearSelection();
                }
                ensureCommentPanelVisible();
                loadCommentsForAnnotation(created.uuid, created.type);
            }).catch(function (error) {
                console.error('Create annotation failed', error);
            }).finally(function () {
                cleanup();
            });
        }

        editor.addEventListener('blur', function () { commit(true); });
        editor.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                committed = true;
                cleanup();"""
    js = js.replace(
        """                if (createdGroup) {
                    selectAnnotation(pageNumber, createdGroup);
                }
                ensureCommentPanelVisible();
                loadCommentsForAnnotation(created.uuid, created.type);""",
        """                if (createdGroup) {
                    clearSelection();
                }
                ensureCommentPanelVisible();
                loadCommentsForAnnotation(created.uuid, created.type);"""
    )

    # Bug 2.1: createAnnotation - do not select after create
    js = js.replace(
        """            if (createdGroup) {
                selectAnnotation(pageNumber, createdGroup);
            }
            ensureCommentPanelVisible();
            loadCommentsForAnnotation(created.uuid, created.type);
            if (created.type === 'textbox') {""",
        """            if (createdGroup) {
                clearSelection();
            }
            ensureCommentPanelVisible();
            loadCommentsForAnnotation(created.uuid, created.type);
            if (created.type === 'textbox') {"""
    )

    # Bug 2.1: showTextboxEditor commit() - add clearSelection after editor.remove()
    js = js.replace(
        """            redrawOneAnnotation(pageNumber, annotationData.uuid, annotationData);
            persistAnnotation(annotationData);
            editor.remove();
        }
        editor.addEventListener('blur', function () { commit(true); });
        editor.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                committed = true;
                if (saveBtn && saveBtn.parentNode) {""",
        """            redrawOneAnnotation(pageNumber, annotationData.uuid, annotationData);
            persistAnnotation(annotationData);
            editor.remove();
            clearSelection();
        }
        editor.addEventListener('blur', function () { commit(true); });
        editor.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                committed = true;
                if (saveBtn && saveBtn.parentNode) {"""
    )

    # Bug 2.1: showTextboxEditor Escape - add clearSelection after editor.remove()
    js = js.replace(
        """                if (labelEl) {
                    labelEl.style.visibility = 'visible';
                }
                editor.remove();
                return;
            }
            if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {""",
        """                if (labelEl) {
                    labelEl.style.visibility = 'visible';
                }
                editor.remove();
                clearSelection();
                return;
            }
            if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {"""
    )

    with open(JS, 'w', encoding='utf-8') as f:
        f.write(js)

    print('OK: CSS and JS updated')

if __name__ == '__main__':
    main()
