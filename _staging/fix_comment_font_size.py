#!/usr/bin/env python3
"""Fix point 5: same font size when editing and when saved (comments panel)."""
import os
root = os.environ.get('MOODLE_ROOT', os.getcwd())
css_path = os.path.join(root, 'mod', 'pdfannotator', 'styles.css')

with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# 1) .chat-message-text: force 14px !important so it overrides parent .pdfannotator-comment-list (12px)
css = css.replace(
    """.path-mod-pdfannotator .chat-message-text {
    display: inline-block;
    width: 100%;
    font-size: 14px;
}""",
    """.path-mod-pdfannotator .chat-message-text {
    display: inline-block;
    width: 100%;
    font-size: 14px !important;
}"""
)
# 2) Ensure paragraphs inside displayed comment are 14px
old_p = """.path-mod-pdfannotator :not(.questioncomment) > .chat-message-text p {
    margin-bottom: 0;
}"""
new_p = """.path-mod-pdfannotator :not(.questioncomment) > .chat-message-text p,
.path-mod-pdfannotator #comment-wrapper .chat-message-text p {
    margin-bottom: 0;
    font-size: 14px !important;
}"""
if old_p in css:
    css = css.replace(old_p, new_p)
elif ".path-mod-pdfannotator :not(.questioncomment) > .chat-message-text p {" in css and "font-size" not in css[css.find(".path-mod-pdfannotator :not(.questioncomment) > .chat-message-text p {"):css.find("}")+1]:
    css = css.replace(
        """.path-mod-pdfannotator :not(.questioncomment) > .chat-message-text p {
    margin-bottom: 0;
}""",
        new_p
    )

# 3) First .editor_atto_content block (border only): add font-size so editor content matches
old_atto1 = """.path-mod-pdfannotator #comment-wrapper .editor_atto_content {
    border-width: 0px 1px 1px 1px;
    border-style: solid;
    border-color: #8f959e;
}"""
new_atto1 = """.path-mod-pdfannotator #comment-wrapper .editor_atto_content {
    border-width: 0px 1px 1px 1px;
    border-style: solid;
    border-color: #8f959e;
    font-size: 14px !important;
}"""
if old_atto1 in css:
    css = css.replace(old_atto1, new_atto1)

# 4) Multi-selector block: add !important so theme cannot override
old_multi = """path-mod-pdfannotator #comment-wrapper .editor_atto_content {
    width: 100%;
    min-height: 10em !important;
    font-size: 14px;
}"""
new_multi = """path-mod-pdfannotator #comment-wrapper .editor_atto_content {
    width: 100%;
    min-height: 10em !important;
    font-size: 14px !important;
}"""
# Note: in file the selector starts with .path-mod-pdfannotator (with leading dot)
old_multi2 = """.path-mod-pdfannotator #myarea,
.path-mod-pdfannotator .chat-message textarea,
.path-mod-pdfannotator #comment-wrapper .editor_atto_content {
    width: 100%;
    min-height: 10em !important;
    font-size: 14px;
}"""
new_multi2 = """.path-mod-pdfannotator #myarea,
.path-mod-pdfannotator .chat-message textarea,
.path-mod-pdfannotator #comment-wrapper .editor_atto_content {
    width: 100%;
    min-height: 10em !important;
    font-size: 14px !important;
}"""
if old_multi2 in css:
    css = css.replace(old_multi2, new_multi2)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print('OK: comment font-size fix applied')
