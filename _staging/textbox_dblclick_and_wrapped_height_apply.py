#!/usr/bin/env python3
"""
Plan: dwuklik w mouseup (state._lastTextboxClick), Bug 3 pomiar wysokości zawijania.
Uruchomić z katalogu Moodle. Modyfikuje: js_new/pdfannotator_new.v00054.js
"""
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

# --- 1. Bug 4: double-click detection at start of mouseup (after drawing block)
old_after_drawing = """                setTool('cursor');
                return;
            }

            if (tool === 'textbox' && pointer && !draftRect) {"""

new_after_drawing = """                setTool('cursor');
                return;
            }

            (function () {
                if (!pointer) {
                    state._lastTextboxClick = null;
                    return;
                }
                var domTarget = event && event.evt && event.evt.target;
                if (domTarget && domTarget.closest && (domTarget.closest('.tl-inline-text-editor') || domTarget.closest('.tl-save-textbox'))) {
                    return;
                }
                var pageState = getPageState(pageNumber);
                if (!pageState || !pageState.annotationLayer) {
                    state._lastTextboxClick = null;
                    return;
                }
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
                if (!hitGroup) {
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
                        var last = state._lastTextboxClick;
                        if (last && last.uuid === data.uuid && (Date.now() - last.time) < 400) {
                            state._lastTextboxClick = null;
                            showTextboxEditor(pageNumber, data);
                            return;
                        }
                        state._lastTextboxClick = { time: Date.now(), pageNumber: pageNumber, uuid: data.uuid };
                    } else {
                        state._lastTextboxClick = null;
                    }
                } else {
                    state._lastTextboxClick = null;
                }
            })();
            if (state._lastTextboxClick && (Date.now() - state._lastTextboxClick.time) < 400) {
                var justOpened = state._lastTextboxClick === null;
            }
            if (state._lastTextboxClick && state._lastTextboxClick.time && (Date.now() - state._lastTextboxClick.time) < 400) {
                var check = state._lastTextboxClick;
                if (check.pageNumber === pageNumber && getPageState(pageNumber)) {
                    var skipRest = false;
                    try {
                        if (state._dblclickJustHandled) {
                            skipRest = true;
                            state._dblclickJustHandled = false;
                        }
                    } catch (e) {}
                    if (skipRest) { return; }
                }
            }

            if (tool === 'textbox' && pointer && !draftRect) {"""

# Simplified: no IIFE so "return" exits mouseup handler. Let me simplify: when we call showTextboxEditor in the double-click block, we should return from the mouseup handler. So we need to wrap the double-click logic so that when we open the editor we return. The issue is the IIFE runs and might call showTextboxEditor and then we need to return from the outer mouseup. So instead of an IIFE that returns, we should do the logic inline and use a variable: var dblclickOpened = false; ... if (last && last.uuid === data.uuid && ...) { state._lastTextboxClick = null; showTextboxEditor(...); dblclickOpened = true; } ... then after the block, if (dblclickOpened) return;
# Let me rewrite: no IIFE. Just the block. When we detect double-click we set state._dblclickJustHandled = true and call showTextboxEditor and return. So we need a simple block that when it opens the editor it returns. So:
#   if (!pointer) { state._lastTextboxClick = null; }
#   else {
#     domTarget guard -> return
#     pageState, hit test
#     if hitGroup textbox:
#       if last && same uuid && < 400ms: showTextboxEditor, _lastTextboxClick = null, return
#       else: _lastTextboxClick = { ... }
#     else: _lastTextboxClick = null
#   }
# So we don't need the IIFE. We just need to add the block and when we call showTextboxEditor we return. So the block ends with "return;" when we open. So the code is linear. Let me remove the IIFE and the confusing "justOpened" / "skipRest" stuff.
</think>
Upraszczając blok dwukliku: bez IIFE, po showTextboxEditor — return.
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
StrReplace