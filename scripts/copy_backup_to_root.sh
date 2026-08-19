#!/usr/bin/env bash
# Kopiuje backup z mod/pdfannotator/_backups (lub COPY_BACKUP_SOURCE) do /root/trinity_lab_backup.
# Uruchomienie: sudo -E ./mod/pdfannotator/scripts/copy_backup_to_root.sh [nazwa_katalogu_backupu]
# Z -E HOME pozostaje ustawione. Bez argumentu: najnowszy katalog z ~/trinity_lab_backup (według mtime).

set -e
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_BASE="${COPY_BACKUP_SOURCE:-$PLUGIN_ROOT/_backups}"
ROOT_DEST="/root/trinity_lab_backup"

if [ -n "$1" ]; then
  NAME="$1"
  SOURCE="${SOURCE_BASE}/${NAME}"
  if [ ! -d "$SOURCE" ]; then
    echo "Błąd: brak katalogu: $SOURCE" >&2
    exit 1
  fi
else
  LAST=$(ls -1 "$SOURCE_BASE" 2>/dev/null | grep -E "^v[0-9]+_" | sort -V | tail -1)
  [ -n "$LAST" ] && LAST="$SOURCE_BASE/$LAST"
  if [ -z "$LAST" ]; then
    echo "Błąd: brak backupów w $SOURCE_BASE" >&2
    exit 1
  fi
  NAME=$(basename "$LAST")
  SOURCE="$LAST"
  echo "Użyto ostatniego backupu: $NAME"
fi

mkdir -p "$ROOT_DEST"
cp -a "$SOURCE" "$ROOT_DEST/"
chown -R root:root "$ROOT_DEST/$NAME"
echo "OK: $ROOT_DEST/$NAME"
PTR="$PLUGIN_ROOT/_backups/CURRENT_RESTORE.txt"
echo "$NAME" > "$PTR"
if [ "$(id -u)" = 0 ]; then
  chown --reference="$PLUGIN_ROOT/_backups" "$PTR" 2>/dev/null || true
  chmod a+r "$PTR" 2>/dev/null || true
fi
echo "Wskaźnik restore: $PTR"
