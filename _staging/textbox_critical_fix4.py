#!/usr/bin/env python3
import os

root = os.getcwd()
JS = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(JS, 'r', encoding='utf-8') as f:
    js = f.read()

old_line = "            var unscaledBoxY = (pointerY - paddingTop - caretOffset) / state.scale;\n"
new_line = "            var unscaledBoxY = (pointerY - paddingTop) / state.scale;\n"

if old_line not in js:
    raise SystemExit('unscaledBoxY line with caretOffset not found')

js = js.replace(old_line, new_line, 1)

with open(JS, 'w', encoding='utf-8') as f:
    f.write(js)

print('textbox_critical_fix4: OK')

