#!/usr/bin/env python3
"""Set SIZE=22 for renderPoint in shared/index.js (pin 22px in export)."""
import os
root = os.environ.get('MOODLE_ROOT', os.getcwd())
path = os.path.join(root, 'mod', 'pdfannotator', 'shared', 'index.js')

with open(path, 'r', encoding='utf-8') as f:
    js = f.read()

# Only the SIZE in the renderPoint module (before "Create SVGElement from an annotation")
old = """                                var SIZE = 20;
                                var D =
                                    'M499.968 214.336q-113.832 0 -212.877 38.781t-157.356 104.625 -58.311 142.29q0 62.496 39.897 119.133t112.437 97.929l48.546 27.9 -15.066 53.568q-13.392 50.778 -39.06 95.976 84.816 -35.154 153.45 -95.418l23.994 -21.204 31.806 3.348q38.502 4.464 72.54 4.464 113.832 0 212.877 -38.781t157.356 -104.625 58.311 -142.29 -58.311 -142.29 -157.356 -104.625 -212.877 -38.781z';
                                /**
                                 * Create SVGElement from an annotation definition."""

new = """                                var SIZE = 22;
                                var D =
                                    'M499.968 214.336q-113.832 0 -212.877 38.781t-157.356 104.625 -58.311 142.29q0 62.496 39.897 119.133t112.437 97.929l48.546 27.9 -15.066 53.568q-13.392 50.778 -39.06 95.976 84.816 -35.154 153.45 -95.418l23.994 -21.204 31.806 3.348q38.502 4.464 72.54 4.464 113.832 0 212.877 -38.781t157.356 -104.625 58.311 -142.29 -58.311 -142.29 -157.356 -104.625 -212.877 -38.781z';
                                /**
                                 * Create SVGElement from an annotation definition."""

if old not in js:
    raise SystemExit('renderPoint SIZE block not found in shared/index.js')
js = js.replace(old, new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(js)
print('OK: renderPoint SIZE=22 in shared/index.js')
