#!/usr/bin/env python3
"""Add green check save button during textbox edit; re-add ignoreNextTextboxClick in mouseup."""
JS = 'mod/pdfannotator/js_new/pdfannotator_new.v00054.js'

def main():
    with open(JS, 'r', encoding='utf-8') as f:
        s = f.read()

    # 1) mouseup: re-add ignoreNextTextboxClick so after save (check or Ctrl+Enter) next click doesn't create
    old_mup = """            if (tool === 'textbox' && pointer && !draftRect) {
                showNewTextboxEditor(pageNumber, pointer.x, pointer.y);
                return;
            }"""
    new_mup = """            if (tool === 'textbox' && pointer && !draftRect) {
                if (state.ignoreNextTextboxClick) {
                    state.ignoreNextTextboxClick = false;
                    return;
                }
                showNewTextboxEditor(pageNumber, pointer.x, pointer.y);
                return;
            }"""
    if old_mup not in s:
        raise SystemExit('mouseup textbox block not found')
    s = s.replace(old_mup, new_mup, 1)

    # 2) showTextboxEditor: add save button after resizeEditorToContent and listeners, before editor.focus
    old_edit = """        editor.addEventListener('input', resizeEditorToContent);
        editor.addEventListener('keyup', resizeEditorToContent);
        resizeEditorToContent();
        editor.addEventListener('mousedown', function (event) { event.stopPropagation(); });
        editor.addEventListener('click', function (event) { event.stopPropagation(); });
        editor.addEventListener('dblclick', function (event) { event.stopPropagation(); });
        editor.focus();
        editor.select();

        var committed = false;
        function commit() {
            if (committed) {
                return;
            }
            committed = true;
            state.ignoreNextTextboxClick = true;
            if (measureEl && measureEl.parentNode) {
                measureEl.parentNode.removeChild(measureEl);
            }
            annotationData.content = editor.value || '';"""
    new_edit = """        editor.addEventListener('input', resizeEditorToContent);
        editor.addEventListener('keyup', resizeEditorToContent);
        resizeEditorToContent();
        var saveBtn = document.createElement('button');
        saveBtn.type = 'button';
        saveBtn.className = 'tl-save-textbox';
        saveBtn.setAttribute('aria-label', 'Save');
        saveBtn.innerHTML = '<i class="fa fa-check" aria-hidden="true"></i>';
        saveBtn.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); commit(); });
        saveBtn.addEventListener('mousedown', function (e) { e.stopPropagation(); });
        pageElement.appendChild(saveBtn);
        function updateSaveBtnPos() {
            saveBtn.style.left = (editor.offsetLeft + editor.offsetWidth - 12) + 'px';
            saveBtn.style.top = (editor.offsetTop - 12) + 'px';
        }
        var resizeEditorToContentWithBtn = function () {
            resizeEditorToContent();
            updateSaveBtnPos();
        };
        editor.removeEventListener('input', resizeEditorToContent);
        editor.removeEventListener('keyup', resizeEditorToContent);
        editor.addEventListener('input', resizeEditorToContentWithBtn);
        editor.addEventListener('keyup', resizeEditorToContentWithBtn);
        updateSaveBtnPos();
        editor.addEventListener('mousedown', function (event) { event.stopPropagation(); });
        editor.addEventListener('click', function (event) { event.stopPropagation(); });
        editor.addEventListener('dblclick', function (event) { event.stopPropagation(); });
        editor.focus();
        editor.select();

        var committed = false;
        function commit() {
            if (committed) {
                return;
            }
            committed = true;
            state.ignoreNextTextboxClick = true;
            if (saveBtn && saveBtn.parentNode) {
                saveBtn.parentNode.removeChild(saveBtn);
            }
            if (measureEl && measureEl.parentNode) {
                measureEl.parentNode.removeChild(measureEl);
            }
            annotationData.content = editor.value || '';"""
    if old_edit not in s:
        raise SystemExit('showTextboxEditor block not found')
    s = s.replace(old_edit, new_edit, 1)

    # 3) showTextboxEditor Escape: remove save button
    old_escape = """            if (event.key === 'Escape') {
                committed = true;
                if (measureEl && measureEl.parentNode) {
                    measureEl.parentNode.removeChild(measureEl);
                }
                if (labelEl) {
                    labelEl.style.visibility = 'visible';
                }
                editor.remove();
                return;
            }"""
    new_escape = """            if (event.key === 'Escape') {
                committed = true;
                if (saveBtn && saveBtn.parentNode) {
                    saveBtn.parentNode.removeChild(saveBtn);
                }
                if (measureEl && measureEl.parentNode) {
                    measureEl.parentNode.removeChild(measureEl);
                }
                if (labelEl) {
                    labelEl.style.visibility = 'visible';
                }
                editor.remove();
                return;
            }"""
    if old_escape not in s:
        raise SystemExit('Escape block not found')
    s = s.replace(old_escape, new_escape, 1)

    # 4) showNewTextboxEditor: add save button after resizeEditorToContent, update position on resize, remove in cleanup/commit
    old_new = """        editor.addEventListener('input', resizeEditorToContent);
        editor.addEventListener('keyup', resizeEditorToContent);
        resizeEditorToContent();

        editor.addEventListener('mousedown', function (event) { event.stopPropagation(); });
        editor.addEventListener('click', function (event) { event.stopPropagation(); });
        editor.addEventListener('dblclick', function (event) { event.stopPropagation(); });

        editor.focus();
        editor.select();

        var committed = false;

        function cleanup() {
            try {
                if (measureEl && measureEl.parentNode) {
                    measureEl.parentNode.removeChild(measureEl);
                }
                editor.remove();
            } catch (e) {}
            setTool('cursor');
        }"""
    new_new = """        var saveBtn = document.createElement('button');
        saveBtn.type = 'button';
        saveBtn.className = 'tl-save-textbox';
        saveBtn.setAttribute('aria-label', 'Save');
        saveBtn.innerHTML = '<i class="fa fa-check" aria-hidden="true"></i>';
        saveBtn.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); commit(); });
        saveBtn.addEventListener('mousedown', function (e) { e.stopPropagation(); });
        pageElement.appendChild(saveBtn);
        function updateSaveBtnPos() {
            saveBtn.style.left = (editor.offsetLeft + editor.offsetWidth - 12) + 'px';
            saveBtn.style.top = (editor.offsetTop - 12) + 'px';
        }
        function resizeAndUpdateBtn() {
            resizeEditorToContent();
            updateSaveBtnPos();
        }
        editor.addEventListener('input', resizeAndUpdateBtn);
        editor.addEventListener('keyup', resizeAndUpdateBtn);
        resizeAndUpdateBtn();

        editor.addEventListener('mousedown', function (event) { event.stopPropagation(); });
        editor.addEventListener('click', function (event) { event.stopPropagation(); });
        editor.addEventListener('dblclick', function (event) { event.stopPropagation(); });

        editor.focus();
        editor.select();

        var committed = false;

        function cleanup() {
            try {
                if (saveBtn && saveBtn.parentNode) {
                    saveBtn.parentNode.removeChild(saveBtn);
                }
                if (measureEl && measureEl.parentNode) {
                    measureEl.parentNode.removeChild(measureEl);
                }
                editor.remove();
            } catch (e) {}
            setTool('cursor');
        }"""
    if old_new not in s:
        raise SystemExit('showNewTextboxEditor block not found')
    s = s.replace(old_new, new_new, 1)

    with open(JS, 'w', encoding='utf-8') as f:
        f.write(s)
    print('Patched:', JS)

    # 5) CSS: green save button (same size/positioning as delete, check icon)
    CSS = 'mod/pdfannotator/styles.css'
    with open(CSS, 'r', encoding='utf-8') as f:
        css = f.read()
    insert_after = """.tl-delete-annotation i {
    font-size: 13px;
    line-height: 1;
}

.tl-shoelace-toolbar"""
    new_block = """.tl-delete-annotation i {
    font-size: 13px;
    line-height: 1;
}

.tl-save-textbox {
    position: absolute;
    z-index: 41;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    border: 0;
    background: #059669;
    color: #fff;
    font-weight: 700;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}
.tl-save-textbox i {
    font-size: 14px;
    line-height: 1;
}

.tl-shoelace-toolbar"""
    if insert_after not in css:
        raise SystemExit('CSS insert point not found')
    if '.tl-save-textbox' in css:
        print('CSS already has .tl-save-textbox')
    else:
        css = css.replace(insert_after, new_block, 1)
        with open(CSS, 'w', encoding='utf-8') as f:
            f.write(css)
        print('Patched:', CSS)

if __name__ == '__main__':
    main()
