#!/usr/bin/env python3
"""Apply scroll-jump fix and Option A (localStorage last position) to pdfannotator_new.v00054.js.
Run from Moodle root; edits mod/pdfannotator/js_new/pdfannotator_new.v00054.js."""
import sys

path = "mod/pdfannotator/js_new/pdfannotator_new.v00054.js"

with open(path, "r", encoding="utf-8") as f:
    s = f.read()

# 1) Bootstrap: use localStorage when page===1 for last position restore
old1 = """        state.initialPage = page || 1;
        state.annoid = annoid;"""
new1 = """        var posKey = 'pdfannotator_pos_' + contextId;
        var stored = null;
        if (page !== 1) {
            state.initialPage = page;
        } else {
            try {
                var raw = typeof localStorage !== 'undefined' && localStorage.getItem(posKey);
                if (raw) { stored = JSON.parse(raw); }
            } catch (e) {}
            if (stored && typeof stored.page === 'number' && stored.page >= 1) {
                state.initialPage = stored.page;
                state.savedScrollTop = typeof stored.scrollTop === 'number' ? stored.scrollTop : 0;
            } else {
                state.initialPage = 1;
            }
        }
        state.annoid = annoid;"""
if old1 not in s:
    print("ERROR: Bootstrap block not found", file=sys.stderr)
    sys.exit(1)
s = s.replace(old1, new1)

# 2) bindViewerScroll: debounced save of page+scrollTop to localStorage
old2 = """    function bindViewerScroll() {
        var viewer = viewerEl();
        if (!viewer) {
            return;
        }
        viewer.addEventListener('scroll', function () {
            var current = getCurrentPage();
            var currentPageInput = document.getElementById('currentPage');
            if (currentPageInput) {
                currentPageInput.value = String(current);
            }
            updatePageCounter(current);
            updateDeleteButtonPosition();
        });
    }"""
new2 = """    function bindViewerScroll() {
        var viewer = viewerEl();
        if (!viewer) {
            return;
        }
        var savePosTimer = null;
        viewer.addEventListener('scroll', function () {
            var current = getCurrentPage();
            var currentPageInput = document.getElementById('currentPage');
            if (currentPageInput) {
                currentPageInput.value = String(current);
            }
            updatePageCounter(current);
            updateDeleteButtonPosition();
            if (savePosTimer) clearTimeout(savePosTimer);
            savePosTimer = setTimeout(function () {
                var key = 'pdfannotator_pos_' + state.contextId;
                if (state.contextId != null) {
                    var p = getCurrentPage();
                    var top = viewer.scrollTop;
                    try { localStorage.setItem(key, JSON.stringify({ page: p, scrollTop: top })); } catch (e) {}
                }
                savePosTimer = null;
            }, 400);
        });
    }"""
if old2 not in s:
    print("ERROR: bindViewerScroll block not found", file=sys.stderr)
    sys.exit(1)
s = s.replace(old2, new2)

# 3) chain.then: only scrollToPage when user has not scrolled; restore savedScrollTop
old3 = """        chain.then(function () {
            var targetPage = Math.max(1, Math.min(state.pdf.numPages, parseInt(state.initialPage || 1, 10) || 1));
            scrollToPage(targetPage);
            requestAnimationFrame(function () {
                setTimeout(function () { startAnnotationWarmup(); }, 150);
            });
        }).catch(function (error) {"""
new3 = """        chain.then(function () {
            var viewer = viewerEl();
            var targetPage = Math.max(1, Math.min(state.pdf.numPages, parseInt(state.initialPage || 1, 10) || 1));
            if (viewer && viewer.scrollTop <= 80) {
                scrollToPage(targetPage);
            }
            if (viewer && state.savedScrollTop != null) {
                viewer.scrollTop = Math.max(0, Math.min(state.savedScrollTop, viewer.scrollHeight - viewer.clientHeight));
                state.savedScrollTop = null;
            }
            requestAnimationFrame(function () {
                setTimeout(function () { startAnnotationWarmup(); }, 150);
            });
        }).catch(function (error) {"""
if old3 not in s:
    print("ERROR: chain.then block not found", file=sys.stderr)
    sys.exit(1)
s = s.replace(old3, new3)

with open(path, "w", encoding="utf-8") as f:
    f.write(s)
print("OK")
