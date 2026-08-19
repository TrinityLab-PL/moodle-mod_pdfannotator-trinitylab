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

BACKUP_POINTER="$MOODLE_ROOT/mod/pdfannotator/_backups/CURRENT_RESTORE.txt"
BACKUP_HARDCODED_FALLBACK="v189_tab_utf8_20260818_205924"

backup_index_path_for_name() {
  local name="$1"
  local p
  for p in \
    "/root/trinity_lab_backup/${name}/mod/pdfannotator/shared/index.js" \
    "$MOODLE_ROOT/mod/pdfannotator/_backups/${name}/mod/pdfannotator/shared/index.js"; do
    if [ -f "$p" ]; then
      echo "$p"
      return 0
    fi
  done
  return 1
}

find_latest_backup_index() {
  local base_dir="$1"
  local name
  name=$(ls -1 "$base_dir" 2>/dev/null | grep -E "^v[0-9]+_" | sort -V | tail -1)
  [ -z "$name" ] && return 1
  backup_index_path_for_name "$name"
}

resolve_backup_index() {
  local name path
  if [ -f "$BACKUP_POINTER" ]; then
    name=$(head -1 "$BACKUP_POINTER" | tr -d "[:space:]")
    if [ -n "$name" ]; then
      path=$(backup_index_path_for_name "$name" 2>/dev/null) && { echo "$path"; return 0; }
      echo "WARN: CURRENT_RESTORE.txt -> ${name} brak index.js, fallback auto-detect" >&2
    fi
  fi
  path=$(find_latest_backup_index "/root/trinity_lab_backup" 2>/dev/null) && { echo "$path"; return 0; }
  path=$(find_latest_backup_index "$MOODLE_ROOT/mod/pdfannotator/_backups" 2>/dev/null) && { echo "$path"; return 0; }
  path=$(backup_index_path_for_name "$BACKUP_HARDCODED_FALLBACK" 2>/dev/null) && {
    echo "WARN: hardcoded fallback $BACKUP_HARDCODED_FALLBACK" >&2
    echo "$path"
    return 0
  }
  echo "Błąd: nie można rozwiązać ścieżki backup index.js" >&2
  return 1
}

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
  local BACKUP_INDEX
  BACKUP_INDEX=$(resolve_backup_index) || exit 1
  echo "Restore from: $(echo "$BACKUP_INDEX" | grep -oE 'v[0-9]+_[^/]+' | head -1)"
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
    echo "  $0 --restore                 # przywróć shared/index.js (CURRENT_RESTORE.txt lub auto vNNN)"
    echo "  $0 --cmd 'sed -i \"s/a/b/\" $PROTECTED'  # wykonaj polecenie z maintenance"
    exit 1
    ;;
esac
