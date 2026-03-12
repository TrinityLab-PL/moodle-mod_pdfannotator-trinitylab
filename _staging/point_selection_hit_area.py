#!/usr/bin/env python3
"""Adjust point: add Rect in pinGroup for selection frame +12% up and clickable area +4px; remove outer Circle."""
import os
root = os.environ.get('MOODLE_ROOT', os.getcwd())
path = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(path, 'r', encoding='utf-8') as f:
    js = f.read()

old = """            pinGroup.add(new Konva.Circle({
                x: 4,
                y: -2878,
                radius: 525,
                fill: 'rgb(247,205,0)',
                listening: false
            }));
            group.add(pinGroup);
            group.add(new Konva.Circle({
                x: annotation.x * scale,
                y: annotation.y * scale,
                radius: 11,
                fill: 'transparent',
                strokeWidth: 0,
                listening: true
            }));
        } else if (annotation.type === 'area') {"""

new = """            pinGroup.add(new Konva.Circle({
                x: 4,
                y: -2878,
                radius: 525,
                fill: 'rgb(247,205,0)',
                listening: false
            }));
            var marginUnits = 4 / pathScale;
            var halfWidth = 1500 + marginUnits;
            var extraTop = 0.12 * pinUnitsH;
            var extraBottom = marginUnits;
            pinGroup.add(new Konva.Rect({
                x: -halfWidth,
                y: -pinUnitsH - extraTop,
                width: halfWidth * 2,
                height: pinUnitsH + extraTop + extraBottom,
                fill: 'transparent',
                listening: true
            }));
            group.add(pinGroup);
        } else if (annotation.type === 'area') {"""

if old not in js:
    raise SystemExit('Point pinGroup + outer Circle block not found')
js = js.replace(old, new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(js)
print('OK: point selection frame and hit area updated')
