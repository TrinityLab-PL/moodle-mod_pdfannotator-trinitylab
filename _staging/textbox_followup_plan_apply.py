#!/usr/bin/env python3
"""
Plan: dblclick bez zaznaczenia, caret -3px, wymiary created z annotation.
Uruchomić z katalogu Moodle. Modyfikuje: js_new/pdfannotator_new.v00054.js
"""
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

# --- 1. Bug 4: stage dblclick -> hit na annotation layer -> showTextboxEditor
old_mouseup_end = """            }
        });
    }

    function rectToolPayload(tool, rect) {"""

new_mouseup_end = """            }
        });

        stage.on('dblclick dbltap', function (event) {
            var domTarget = event && event.evt && event.evt.target;
            if (domTarget && domTarget.closest && (domTarget.closest('.tl-inline-text-editor') || domTarget.closest('.tl-save-textbox'))) {
                return;
            }
            var pointer = stage.getPointerPosition();
            if (!pointer) { return; }
            var pageState = getPageState(pageNumber);
            if (!pageState || !pageState.annotationLayer) { return; }
            var hit = pageState.annotationLayer.getIntersection(pointer);
            var hitGroup = null;
            if (hit) {
                var n = hit;
                while (n) {
                    if (n.getAttr && n.getAttr('annotationData')) {
                        hitGroup = n;
                        break;
                    }
                    n = n.getParent && n.getParent();
                }
            }
            if (!hitGroup && pageState.annotationLayer) {
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
            if (hitGroup) {
                var data = hitGroup.getAttr('annotationData');
                if (data && data.type === 'textbox' && data.uuid) {
                    showTextboxEditor(pageNumber, data);
                }
            }
        });
    }

    function rectToolPayload(tool, rect) {"""

if old_mouseup_end not in js:
    raise SystemExit('1. mouseup end block not found')
js = js.replace(old_mouseup_end, new_mouseup_end, 1)

# --- 2. Bug 1+2: caret obniżenie o 3 px
js = js.replace(
    "editor.style.top = (pointerY - paddingTop - baselineOffset) + 'px';",
    "editor.style.top = (pointerY - paddingTop - baselineOffset + 3) + 'px';",
    1
)
js = js.replace(
    "var unscaledBoxY = (pointerY - paddingTop - baselineOffset) / state.scale;",
    "var unscaledBoxY = (pointerY - paddingTop - baselineOffset + 3) / state.scale;",
    1
)

# --- 3. Bug 3: created.width/height/x/y z annotation przed drawAnnotation
old_then = """            }).then(function (created) {
                if (!created || !created.uuid) {
                    return;
                }
                var createdGroup = drawAnnotation(pageNumber, created);"""

new_then = """            }).then(function (created) {
                if (!created || !created.uuid) {
                    return;
                }
                created.width = annotation.width;
                created.height = annotation.height;
                created.x = annotation.x;
                created.y = annotation.y;
                var createdGroup = drawAnnotation(pageNumber, created);"""

if old_then not in js:
    raise SystemExit('3. then(created) block not found')
js = js.replace(old_then, new_then, 1)

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

print('textbox_followup_plan_apply: OK')
