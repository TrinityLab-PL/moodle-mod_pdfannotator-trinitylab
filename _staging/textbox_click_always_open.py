#!/usr/bin/env python3
"""Textbox: każdy klik w textbox otwiera edycję (fallback gdy hit = overlay)."""
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

old_block = """            if (tool === 'textbox' && pointer && !draftRect) {
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

new_block = """            if (tool === 'textbox' && pointer && !draftRect) {
                if (state.ignoreNextTextboxClick) {
                    state.ignoreNextTextboxClick = false;
                    return;
                }
                var domTarget = event && event.evt && event.evt.target;
                if (domTarget && domTarget.closest && (domTarget.closest('.tl-inline-text-editor') || domTarget.closest('.tl-textbox-label') || domTarget.closest('.tl-save-textbox'))) {
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
                if (!hitGroup) {
                    var pageState = getPageState(pageNumber);
                    if (pageState && pageState.annotationLayer) {
                        var children = pageState.annotationLayer.getChildren();
                        for (var i = children.length - 1; i >= 0; i--) {
                            var gr = children[i];
                            var ad = gr.getAttr && gr.getAttr('annotationData');
                            if (!ad || ad.type !== 'textbox') { continue; }
                            var rect = gr.getClientRect && gr.getClientRect();
                            if (rect && pointer.x >= rect.x && pointer.x <= rect.x + rect.width && pointer.y >= rect.y && pointer.y <= rect.y + rect.height) {
                                hitGroup = gr;
                                break;
                            }
                        }
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

if old_block not in js:
    raise SystemExit('textbox mouseup block not found')
js = js.replace(old_block, new_block, 1)

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

print('textbox_click_always_open: OK')
