/**
 * Enhanced Fullscreen for PDF Annotator - Trinity Lab
 * Simplified version without AMD compilation
 * @author Piotr Fr 2025
 */

(function() {
    'use strict';
    
    console.log('TL Fullscreen Enhanced loaded (simple version)');

    // Auto-start theater mode if defaultfullscreen=1
    function tryAutoTheater() {
        var container = document.querySelector('#pdfannotator_index');
        if (!container || container.getAttribute('data-default-fullscreen') !== '1') return;
        var btn = document.querySelector('[data-proxy-action="fullscreen"]');
        if (window.tlToggleTheaterMode && btn) {
            window.tlToggleTheaterMode();
            document.body.classList.remove('pdfannotator-default-fullscreen');
            btn.innerHTML = '<svg viewBox="0 0 2300 2300" width="28" height="28" fill="none" xmlns="http://www.w3.org/2000/svg"><path stroke="rgb(59,62,62)" stroke-width="200" stroke-linecap="round" stroke-linejoin="round" d="M 825,826 L 825,126 M 125,826 L 825,826 M 825,1474 L 825,2174 M 125,1474 L 825,1474 M 1476,826 L 1476,126 M 2176,826 L 1476,826 M 1476,1474 L 1476,2174 M 2176,1474 L 1476,1474"/></svg>';
        } else {
            setTimeout(tryAutoTheater, 200);
        }
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() { setTimeout(tryAutoTheater, 0); });
    } else {
        setTimeout(tryAutoTheater, 0);
    }
    
    // Czekamy aż DOM będzie gotowy
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            initFullscreen();
            patchNewUIFullscreenWithRetries();
        });
    } else {
        setTimeout(initFullscreen, 2000);
        setTimeout(patchNewUIFullscreenWithRetries, 100);
    }

    function setFullscreenButtonStateGeneric(btn, inFullscreen) {
        if (!btn) return;
        var iconStyle = 'font-size:22px;line-height:0;display:block;';
        if (inFullscreen) {
            btn.innerHTML = "<svg viewBox=\"0 0 2300 2300\" width=\"28\" height=\"28\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path stroke=\"rgb(59,62,62)\" stroke-width=\"200\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M 825,826 L 825,126 M 125,826 L 825,826 M 825,1474 L 825,2174 M 125,1474 L 825,1474 M 1476,826 L 1476,126 M 2176,826 L 1476,826 M 1476,1474 L 1476,2174 M 2176,1474 L 1476,1474\"/></svg>";
            if (btn.setAttribute) { btn.setAttribute('data-tooltip-text', 'Exit full screen (ESC)'); btn.setAttribute('aria-label', 'Exit full screen (ESC)'); }
            btn.title = '';
        } else {
            btn.innerHTML = "<svg viewBox=\"0 0 2300 2300\" width=\"28\" height=\"28\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path stroke=\"rgb(59,62,62)\" stroke-width=\"200\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M 125,126 L 125,826 M 825,126 L 125,126 M 125,2174 L 125,1474 M 825,2174 L 125,2174 M 2176,126 L 2176,826 M 1476,126 L 2176,126 M 2176,2174 L 2176,1474 M 1476,2174 L 2176,2174\"/></svg>";
            if (btn.setAttribute) { btn.setAttribute('data-tooltip-text', 'Full screen (ESC to exit)'); btn.setAttribute('aria-label', 'Full screen (ESC to exit)'); }
            btn.title = '';
        }
    }

    function patchNewUIFullscreenButton() {
        var btn = document.querySelector('[data-proxy-action="fullscreen"]');
        if (!btn || btn.getAttribute('data-tl-patched') === '1') return btn;
        console.log('TL Fullscreen: patching New UI fullscreen button');
        btn.setAttribute('data-tl-patched', '1');
        btn.id = 'tl-fullscreen-btn';
        btn.classList.add('tl-fullscreen-proxy-btn');
        setFullscreenButtonStateGeneric(btn, !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement));
        function onFullscreenChange() {
            var inFs = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
            setFullscreenButtonStateGeneric(btn, inFs);
        }
        document.addEventListener('fullscreenchange', onFullscreenChange);
        document.addEventListener('webkitfullscreenchange', onFullscreenChange);
        document.addEventListener('mozfullscreenchange', onFullscreenChange);
        document.addEventListener('msfullscreenchange', onFullscreenChange);
        return btn;
    }

    function patchNewUIFullscreenWithRetries() {
        if (patchNewUIFullscreenButton()) return;
        var delays = [800, 1500, 3000, 5000, 8000];
        delays.forEach(function(ms) {
            setTimeout(function() {
                if (patchNewUIFullscreenButton()) {
                    console.log('TL Fullscreen: New UI button patched at ' + ms + 'ms');
                }
            }, ms);
        });
        var observer = new MutationObserver(function() {
            if (patchNewUIFullscreenButton()) {
                console.log('TL Fullscreen: New UI button patched via MutationObserver');
                observer.disconnect();
            }
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    function initFullscreen() {
        var isFullscreen = false;
        var pdfContainer = document.querySelector('#viewer');
        
        if (!pdfContainer) {
            console.log('PDF container not found');
            return;
        }
        
        // Znajdź lub stwórz przycisk fullscreen
        var fullscreenBtn = document.querySelector('#toggle_fullscreen, .fullscreen-button, [title*="fullscreen"]');
        
        if (!fullscreenBtn) {
            var toolbarContent = document.querySelector("#toolbarContent");
            if (toolbarContent) {
                fullscreenBtn = document.createElement("button");
                fullscreenBtn.id = "tl-fullscreen-btn";
                fullscreenBtn.className = "btn btn-secondary";
                fullscreenBtn.innerHTML = "<svg viewBox=\"0 0 2300 2300\" width=\"28\" height=\"28\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path stroke=\"rgb(59,62,62)\" stroke-width=\"200\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M 125,126 L 125,826 M 825,126 L 125,126 M 125,2174 L 125,1474 M 825,2174 L 125,2174 M 2176,126 L 2176,826 M 1476,126 L 2176,126 M 2176,2174 L 2176,1474 M 1476,2174 L 2176,2174\"/></svg>";
                fullscreenBtn.setAttribute('data-tooltip-text', 'Full screen (ESC to exit)'); fullscreenBtn.title = '';
                fullscreenBtn.style.marginLeft = "5em";
                fullscreenBtn.style.minWidth = "42px";
                fullscreenBtn.style.minHeight = "38px";
                var dropdownButton = document.querySelector("#toolbar-dropdown-button");
                toolbarContent.insertBefore(fullscreenBtn, dropdownButton);
            } else {
                console.log('Toolbar not found');
                return;
            }
        }
        fullscreenBtn.id = 'tl-fullscreen-btn';
        fullscreenBtn.innerHTML = "<svg viewBox=\"0 0 2300 2300\" width=\"28\" height=\"28\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path stroke=\"rgb(59,62,62)\" stroke-width=\"200\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M 125,126 L 125,826 M 825,126 L 125,126 M 125,2174 L 125,1474 M 825,2174 L 125,2174 M 2176,126 L 2176,826 M 1476,126 L 2176,126 M 2176,2174 L 2176,1474 M 1476,2174 L 2176,2174\"/></svg>";
        fullscreenBtn.setAttribute('data-tooltip-text', 'Full screen (ESC to exit)'); fullscreenBtn.title = '';
        fullscreenBtn.style.marginLeft = "5em";
        fullscreenBtn.style.minWidth = "42px";
        fullscreenBtn.style.minHeight = "38px";

        function setFullscreenButtonState(inFullscreen) {
            var fsBtn = document.querySelector('#tl-fullscreen-btn');
            if (!fsBtn) return;
            if (inFullscreen) {
                fsBtn.innerHTML = "<svg viewBox=\"0 0 2300 2300\" width=\"28\" height=\"28\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path stroke=\"rgb(59,62,62)\" stroke-width=\"200\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M 825,826 L 825,126 M 125,826 L 825,826 M 825,1474 L 825,2174 M 125,1474 L 825,1474 M 1476,826 L 1476,126 M 2176,826 L 1476,826 M 1476,1474 L 1476,2174 M 2176,1474 L 1476,1474\"/></svg>";
                if (fsBtn.setAttribute) { fsBtn.setAttribute('data-tooltip-text', 'Exit full screen (ESC)'); fsBtn.setAttribute('aria-label', 'Exit full screen (ESC)'); }
                fsBtn.title = '';
            } else {
                fsBtn.innerHTML = "<svg viewBox=\"0 0 2300 2300\" width=\"28\" height=\"28\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path stroke=\"rgb(59,62,62)\" stroke-width=\"200\" stroke-linecap=\"round\" stroke-linejoin=\"round\" d=\"M 125,126 L 125,826 M 825,126 L 125,126 M 125,2174 L 125,1474 M 825,2174 L 125,2174 M 2176,126 L 2176,826 M 1476,126 L 2176,126 M 2176,2174 L 2176,1474 M 1476,2174 L 2176,2174\"/></svg>";
                if (fsBtn.setAttribute) { fsBtn.setAttribute('data-tooltip-text', 'Full screen (ESC to exit)'); fsBtn.setAttribute('aria-label', 'Full screen (ESC to exit)'); }
                fsBtn.title = '';
            }
        }

        // Funkcja włączania fullscreen
        function enterFullscreen() {
            // Ukryj wszystko poza PDF
            document.body.classList.add('tl-pdf-fullscreen');

            // Zoom 200%: sync class once (no 50ms polling — avoids reflow/blur during toolbar zoom)
            (function syncZoom200Class() {
                var cw = document.getElementById('content-wrapper');
                if (!cw) {
                    return;
                }
                var sel = document.querySelector('select.scale, [data-proxy-action="zoom-select"]');
                var v = sel ? parseFloat(sel.value) : NaN;
                if (Number.isFinite(v) && v >= 2.0) {
                    cw.classList.add('zoom-200');
                } else {
                    cw.classList.remove('zoom-200');
                }
            })();
            document.documentElement.style.height = '100%';
            document.body.style.height = '100%';
            
            var elementsToHide = document.querySelectorAll('#page-header, #page-footer, .breadcrumb, nav:not(#pdftoolbar), .navbar, #block-region-side-pre, #block-region-side-post, .commentscontainer, #commentscontainer, .rightcolumn, #nav-drawer');
            elementsToHide.forEach(function(el) {
                el.style.display = 'none';
            });
            
            // Rozciągnij PDF
            pdfContainer.classList.add('tl-fullscreen-active');
            
            // Dodaj przycisk zamykający
            if (!document.getElementById('tl-exit-fullscreen')) {
                var exitBtn = document.createElement('button');
                exitBtn.id = 'tl-exit-fullscreen';
                exitBtn.innerHTML = '<i class="fa fa-times"></i>';
                exitBtn.title = 'Zamknij pełny ekran (ESC)';
                exitBtn.onclick = exitFullscreen;
                document.body.appendChild(exitBtn);
            }
            
            setFullscreenButtonState(true);
            isFullscreen = true;
        }
        
        // Funkcja wyłączania fullscreen
        function exitFullscreen() {
            // Przywróć widoczność
            document.body.classList.remove('tl-pdf-fullscreen');
            
            var elementsToShow = document.querySelectorAll('#page-header, #page-footer, .breadcrumb, nav, .navbar, #block-region-side-pre, #block-region-side-post, .commentscontainer, #commentscontainer, .rightcolumn, #nav-drawer');
            elementsToShow.forEach(function(el) {
                el.style.display = '';
            });
            
            pdfContainer.classList.remove('tl-fullscreen-active');
            
            var exitBtn = document.getElementById('tl-exit-fullscreen');
            if (exitBtn) {
                exitBtn.remove();
            }
            
            setFullscreenButtonState(false);
            isFullscreen = false;
        }
        
        // Kliknięcie w przycisk fullscreen
        fullscreenBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.tlToggleTheaterMode) {
                window.tlToggleTheaterMode();
            }
        });
        

    }
})();


// Toggle komentarzy - JEDYNY (skipped for tl-layout-v4 — pdfannotator_new handles state)
(function() {
    setTimeout(function() {
    console.log("CC setTimeout start");
        var rootV4 = document.querySelector('#pdfannotator_index.tl-layout-v4');
        if (rootV4) { console.log('CC skipped: tl-layout-v4'); return; }
        var wrapper = document.querySelector('#comment-wrapper');
        var toolbarContent = document.querySelector('#toolbarContent');
        var fullscreenBtn = document.querySelector('#tl-fullscreen-btn');
        console.log("CC check elements:", wrapper, toolbarContent, fullscreenBtn);
        if (!wrapper || !toolbarContent) return;
        
        var btn = document.createElement('button');
        btn.id = 'tl-toggle-comments';
        btn.className = 'btn btn-secondary';
        btn.innerHTML = '<i class="fa fa-chevron-right"></i> Close comments';
        btn.style.marginLeft = '80px';
        
        if (fullscreenBtn) {
            fullscreenBtn.parentNode.insertBefore(btn, fullscreenBtn.nextSibling);
        }
        
        // Stan początkowy przycisku - kk domyślnie zamknięta
        if (wrapper.classList.contains('tl-comments-hidden')) {
            btn.innerHTML = '<i class="fa fa-chevron-left"></i> Open comments';
        } else {
            btn.innerHTML = '<i class="fa fa-chevron-right"></i> Close comments';
        }

        btn.onclick = function() {
            var commentWrapper = document.getElementById('comment-wrapper');
            if (commentWrapper.classList.contains('tl-comments-hidden')) {
                commentWrapper.classList.remove('tl-comments-hidden');
                commentWrapper.style.display = 'block';
                btn.innerHTML = '<i class="fa fa-chevron-right"></i> Close comments';
            } else {
                commentWrapper.classList.add('tl-comments-hidden');
                commentWrapper.style.display = 'none';
                btn.innerHTML = '<i class="fa fa-chevron-left"></i> Open comments';
            }
        };
    }, 500);
})();

// Globalna funkcja do fixowania layoutu wielostronicowych PDF
window.fixMultipagePDFLayout = function() {
    if (!document.body.classList.contains('tl-pdf-fullscreen')) return;
    if (document.querySelector('#pdfannotator_index.tl-layout-v4')) return;
    if (document.querySelector('#viewer .page.tl-page-shell')) {
        return;
    }

    const pages = document.querySelectorAll('#viewer .page');
    if (pages.length <= 1) return;
    
    let currentTop = 100;
    
    pages.forEach((page) => {
        page.style.position = 'absolute';
        page.style.top = currentTop + 'px';
        page.style.left = '0';
        page.style.transform = '';
        
        const canvas = page.querySelector('canvas');
        if (canvas) {
            const canvasHeight = parseInt(canvas.style.height) || canvas.offsetHeight;
            currentTop += canvasHeight + 20;
        }
    });
    
    const viewer = document.querySelector('#viewer');
    if (viewer) {
        viewer.style.height = currentTop + 'px';
    }
};

// Legacy position enforcer disabled (new viewer manages page flow).
let positionInterval = null;
function startPositionEnforcer() {
    if (positionInterval) {
        clearInterval(positionInterval);
        positionInterval = null;
    }
}

// Uruchom przy fullscreen
document.addEventListener('fullscreenchange', function() {
    if (document.fullscreenElement) {
        setTimeout(() => {
            window.fixMultipagePDFLayout();
            startPositionEnforcer();
        }, 500);
    }
});

// Reset po wyjściu
document.addEventListener('fullscreenchange', function() {
    if (!document.fullscreenElement) {
        if (document.querySelector('#viewer .page.tl-page-shell')) {
            return;
        }
        const pages = document.querySelectorAll('#viewer .page');
        pages.forEach(page => {
            page.style.position = '';
            page.style.top = '';
            page.style.left = '';
            page.style.transform = '';
            page.style.margin = '';
        });
        const viewer = document.querySelector('#viewer');
        if (viewer) viewer.style.height = '';
    }
});

// Obsługa zoom (legacy relayout disabled for new viewer)
setTimeout(function() {
    const scaleSelect = document.querySelector('.scale');
    if (scaleSelect) {
        scaleSelect.addEventListener('change', function() {
            if (document.body.classList.contains('tl-pdf-fullscreen') && !document.querySelector('#viewer .page.tl-page-shell')) {
                setTimeout(() => window.fixMultipagePDFLayout(), 500);
            }
        });
    }
}, 1000);

// Nasłuchuj kliknięcie Delete i napraw modal
document.addEventListener('click', function(e) {
    if (!document.body.classList.contains('tl-pdf-fullscreen')) return;
    
    const target = e.target;
    const isDelete = (target.tagName === 'IMG' && target.src && target.src.includes('delete')) ||
                     (target.querySelector && target.querySelector('img[src*="delete"]'));
    
    if (isDelete) {
        setTimeout(() => {
            const modal = document.querySelector('.modal[role="dialog"]');
            if (modal) {
                modal.style.zIndex = 999999999;
                const yesBtn = modal.querySelector('button[data-action="save"]') || 
                              modal.querySelector('.btn-primary');
                if (yesBtn) yesBtn.focus();
            }
        }, 500);
    }
});

// Auto-focus na Yes w modalu (normalny + fullscreen)
const modalObserver = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
        mutation.addedNodes.forEach(function(node) {
            if (node.classList && node.classList.contains('modal')) {
                setTimeout(() => {
                    const yesBtn = node.querySelector('button[data-action="save"]') || 
                                  node.querySelector('.btn-primary');
                    if (yesBtn) yesBtn.focus();
                }, 300);
            }
        });
    });
});

modalObserver.observe(document.body, { childList: true, subtree: true });


// Przenieś modal do fullscreen (polling disabled; MutationObserver handles this path)

// Fix overlay position
document.addEventListener('DOMNodeInserted', function(e) {
    if (e.target.id === 'pdf-annotate-edit-overlay') {
        var isFullscreen = document.body.classList.contains('tl-pdf-fullscreen');
        if (isFullscreen) {
            e.target.style.transform = 'translate(-10px, -10px)';
        }
    }
});
