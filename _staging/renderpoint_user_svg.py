#!/usr/bin/env python3
"""
Update renderPoint in shared/index.js to use user's SVG: teardrop + yellow circle.
"""
import os
root = os.environ.get('MOODLE_ROOT', os.getcwd())
path = os.path.join(root, 'mod', 'pdfannotator', 'shared', 'index.js')

with open(path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the whole renderPoint body that builds outerSVG (keep function signature and return outerSVG).
# User SVG: tip at (1997,4611), viewBox 0 0 4000 5000. We use translated path (tip 0,0), viewBox -1500 -4222 3000 4222.
teardrop_d = (
    "M 1445,-2779 C 1445,-2526 1380,-2279 1252,-2059 1125,-1838 0,0 0,0 "
    "C 0,0 -1119,-1838 -1246,-2059 -1373,-2279 -1439,-2526 -1439,-2779 "
    "C -1439,-3033 -1372,-3281 -1246,-3501 -1119,-3722 -938,-3904 -718,-4031 -498,-4158 -250,-4222 4,-4222 "
    "C 257,-4222 504,-4156 724,-4030 945,-3903 1125,-3721 1248,-3500 1374,-3280 1441,-3033 1445,-2781 L 1445,-2779 Z"
)

old = """                                    let posX = a.x;
                                    let posY = a.y;

                                    let colorInner;
                                    let colorLine;
                                    if (a.color) {
                                        colorInner = 'rgba(255,237,0,.8)';
                                        colorLine = 'rgb(246,168,0)';
                                    } else {
                                        colorInner = 'rgba(142,186,229,.8)';
                                        colorLine = 'rgb(0,84,159)';
                                    }

                                    var outerSVG = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                                    var innerSVG = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                                    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                                    var path2 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                                    var circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                                    (0, _setAttributes2.default)(outerSVG, {
                                        width: SIZE / 2 + 1,
                                        height: SIZE,
                                        x: posX - SIZE / 4,
                                        y: posY - SIZE,
                                    });
                                    (0, _setAttributes2.default)(innerSVG, {
                                        width: SIZE,
                                        height: SIZE,
                                        x: 0,
                                        y: SIZE * 0.05 * -1,
                                        viewBox: '-16 -18 64 64',
                                    });
                                    (0, _setAttributes2.default)(path, {
                                        d: 'M0,47 Q0,28 10,15 A15,15 0,1,0 -10,15 Q0,28 0,47',
                                        stroke: 'none',
                                        fill: colorInner,
                                        transform: '',
                                    });
                                    (0, _setAttributes2.default)(path2, {
                                        d: 'M0,47 Q0,28 10,15 A15,15 0,1,0 -10,15 Q0,28 0,47',
                                        strokeWidth: 1,
                                        stroke: colorLine,
                                        fill: 'none',
                                    });
                                    (0, _setAttributes2.default)(circle, {
                                        cx: 0,
                                        cy: 4,
                                        r: 4,
                                        stroke: 'none',
                                        fill: colorLine,
                                    });
                                    innerSVG.appendChild(path);
                                    innerSVG.appendChild(path2);
                                    innerSVG.appendChild(circle);
                                    outerSVG.appendChild(innerSVG);

                                    return outerSVG;"""

new = """                                    let posX = a.x;
                                    let posY = a.y;

                                    var outerSVG = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                                    var innerSVG = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
                                    var pathTeardrop = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                                    var pathCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                                    (0, _setAttributes2.default)(outerSVG, {
                                        width: 16,
                                        height: SIZE,
                                        x: posX - 8,
                                        y: posY - SIZE,
                                    });
                                    (0, _setAttributes2.default)(innerSVG, {
                                        width: 16,
                                        height: SIZE,
                                        x: 0,
                                        y: 0,
                                        viewBox: '-1500 -4222 3000 4222',
                                    });
                                    (0, _setAttributes2.default)(pathTeardrop, {
                                        d: '%s',
                                        fill: 'rgb(114,159,207)',
                                        stroke: 'none',
                                    });
                                    (0, _setAttributes2.default)(pathCircle, {
                                        cx: 4,
                                        cy: -2878,
                                        r: 525,
                                        fill: 'rgb(247,205,0)',
                                        stroke: 'none',
                                    });
                                    innerSVG.appendChild(pathTeardrop);
                                    innerSVG.appendChild(pathCircle);
                                    outerSVG.appendChild(innerSVG);

                                    return outerSVG;""" % teardrop_d

if old not in js:
    raise SystemExit('renderPoint body not found in shared/index.js')
js = js.replace(old, new, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(js)
print('OK: renderPoint updated to user SVG in shared/index.js')
