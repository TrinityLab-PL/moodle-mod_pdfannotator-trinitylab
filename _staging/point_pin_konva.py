#!/usr/bin/env python3
"""Replace point Konva.Circle with pin Path (22px), same shape as renderPoint."""
import os
root = os.environ.get('MOODLE_ROOT', os.getcwd())
path = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(path, 'r', encoding='utf-8') as f:
    js = f.read()

old = """        if (annotation.type === 'point') {
            group.add(new Konva.Circle({
                x: annotation.x * scale,
                y: annotation.y * scale,
                radius: 10.4,
                fill: '#ef4444',
                stroke: '#ffffff',
                strokeWidth: 2
            }));
        }"""

new = """        if (annotation.type === 'point') {
            var pinH = 22;
            var pathScale = (pinH / 47) * scale;
            group.add(new Konva.Path({
                x: annotation.x * scale,
                y: annotation.y * scale,
                offsetX: 0,
                offsetY: 47,
                scaleX: pathScale,
                scaleY: pathScale,
                data: 'M0,47 Q0,28 10,15 A15,15 0,1,0 -10,15 Q0,28 0,47',
                fill: 'rgba(142,186,229,0.8)',
                stroke: 'rgb(0,84,159)',
                strokeWidth: 1,
                lineJoin: 'round',
                lineCap: 'round'
            }));
            group.add(new Konva.Circle({
                x: annotation.x * scale,
                y: annotation.y * scale,
                radius: 11,
                fill: 'transparent',
                strokeWidth: 0,
                listening: true
            }));
        }"""

if old not in js:
    raise SystemExit('Point block not found in v00054.js')
js = js.replace(old, new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(js)
print('OK: point pin shape updated in v00054.js')
