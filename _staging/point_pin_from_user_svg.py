#!/usr/bin/env python3
"""
Replace point pin with user's SVG: teardrop rgb(114,159,207) + circle rgb(247,205,0).
viewBox 0 0 4000 5000, tip at (1997,4611). Scale to 22px height (4222 units -> 22).
"""
import os
root = os.environ.get('MOODLE_ROOT', os.getcwd())
path_js = os.path.join(root, 'mod', 'pdfannotator', 'js_new', 'pdfannotator_new.v00054.js')

with open(path_js, 'r', encoding='utf-8') as f:
    js = f.read()

# Current block (teardrop + hit circle)
old = """        if (annotation.type === 'point') {
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

# User SVG: teardrop tip (1997,4611), height 4222. Translated path (tip at 0,0).
# Circle head center (2001,1733) -> (4,-2878), radius 525.
teardrop_data = (
    "M 1445,-2779 C 1445,-2526 1380,-2279 1252,-2059 1125,-1838 0,0 0,0 "
    "C 0,0 -1119,-1838 -1246,-2059 -1373,-2279 -1439,-2526 -1439,-2779 "
    "C -1439,-3033 -1372,-3281 -1246,-3501 -1119,-3722 -938,-3904 -718,-4031 -498,-4158 -250,-4222 4,-4222 "
    "C 257,-4222 504,-4156 724,-4030 945,-3903 1125,-3721 1248,-3500 1374,-3280 1441,-3033 1445,-2781 L 1445,-2779 Z"
)

new = """        if (annotation.type === 'point') {
            var pinH = 22;
            var pinUnitsH = 4222;
            var pathScale = (pinH / pinUnitsH) * scale;
            var pinGroup = new Konva.Group({
                x: annotation.x * scale,
                y: annotation.y * scale,
                offsetX: 0,
                offsetY: 0,
                scaleX: pathScale,
                scaleY: pathScale
            });
            pinGroup.add(new Konva.Path({
                x: 0,
                y: 0,
                data: '%s',
                fill: 'rgb(114,159,207)',
                listening: false
            }));
            pinGroup.add(new Konva.Circle({
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
        }""" % teardrop_data

if old not in js:
    raise SystemExit('Point block not found in v00054.js')
js = js.replace(old, new, 1)

with open(path_js, 'w', encoding='utf-8') as f:
    f.write(js)
print('OK: point pin from user SVG applied in v00054.js')
