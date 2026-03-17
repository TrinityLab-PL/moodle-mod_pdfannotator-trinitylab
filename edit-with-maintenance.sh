#!/usr/bin/env bash
# Jedyna dozwolona brama do edycji plików PDF Annotator.
# Zawsze: maintenance on → odblokowanie pliku → zmiana → purge → maintenance off → blokada.
# Uruchamiać z katalogu głównego Moodle lub z dowolnego miejsca (skrypt sam znajdzie root).

set -e
MOODLE_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$MOODLE_ROOT"

MAINTENANCE_ENABLED=0
cleanup_on_exit() {
  if [ "$MAINTENANCE_ENABLED" = 1 ]; then
    php admin/cli/maintenance.php --disable 2>/dev/null || true
    lock_file 2>/dev/null || true
  fi
}
trap cleanup_on_exit EXIT

BACKUP_INDEX="/root/trinity_lab_backup/v100_full_snapshot_pdfannotator_20260309_071509/mod/shared/index.js"
PROTECTED_FILES=(
  "mod/pdfannotator/shared/index.js"
  "mod/pdfannotator/styles.css"
  "mod/pdfannotator/js_new/pdfannotator_new.v00054.js"
  "mod/pdfannotator/templates/index.mustache"
  "mod/pdfannotator/fullscreen_enhanced.js"
)

lock_file() {
  for f in "${PROTECTED_FILES[@]}"; do
    [ -f "$MOODLE_ROOT/$f" ] && chmod 444 "$MOODLE_ROOT/$f"
  done
}

unlock_file() {
  for f in "${PROTECTED_FILES[@]}"; do
    [ -f "$MOODLE_ROOT/$f" ] && chmod 644 "$MOODLE_ROOT/$f"
  done
}

do_restore() {
  php admin/cli/maintenance.php --enable
  MAINTENANCE_ENABLED=1
  unlock_file
  cp -f "$BACKUP_INDEX" "$MOODLE_ROOT/mod/pdfannotator/shared/index.js"
  php admin/cli/purge_caches.php
  php admin/cli/maintenance.php --disable
  lock_file
  grep -n "calcDelta" "$MOODLE_ROOT/mod/pdfannotator/shared/index.js" | head -3
}

do_cmd() {
  local cmd="$1"
  php admin/cli/maintenance.php --enable
  MAINTENANCE_ENABLED=1
  unlock_file
  eval "$cmd"
  php admin/cli/purge_caches.php
  php admin/cli/maintenance.php --disable
  lock_file
}

case "${1:-}" in
  --lock)
    lock_file
    echo "Zablokowano zapis (444): ${PROTECTED_FILES[*]}"
    ;;
  --unlock)
    unlock_file
    echo "Odblokowano zapis (644) – pamiętaj o maintenance przy edycji"
    ;;
  --restore)
    do_restore
    ;;
  --cmd)
    shift
    do_cmd "$*"
    ;;
  *)
    echo "Użycie:"
    echo "  $0 --lock                    # ustaw plik tylko do odczytu (444)"
    echo "  $0 --unlock                  # zezwól na zapis (644)"
    echo "  $0 --restore                 # przywróć shared/index.js z najnowszego backupu (v*)"
    echo "  $0 --cmd 'sed -i \"s/a/b/\" $PROTECTED'  # wykonaj polecenie z maintenance"
    exit 1
    ;;
esac
