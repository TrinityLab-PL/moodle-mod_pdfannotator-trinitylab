#!/usr/bin/env python3
"""Zapisuje scripts/copy_backup_to_root.sh (zgodnie z zasadami 4.1). Uruchomić z katalogu Moodle."""
import os
root = os.getcwd()
path = os.path.join(root, 'mod', 'pdfannotator', 'scripts', 'copy_backup_to_root.sh')
content = r'''#!/usr/bin/env bash
# Kopiuje backup z $HOME/trinity_lab_backup (lub COPY_BACKUP_SOURCE) do /root/trinity_lab_backup.
# Uruchomienie: sudo -E ./mod/pdfannotator/scripts/copy_backup_to_root.sh [nazwa_katalogu_backupu]
# Z -E HOME pozostaje ustawione. Bez argumentu: najnowszy katalog z ~/trinity_lab_backup (według mtime).

set -e
SOURCE_BASE="${COPY_BACKUP_SOURCE:-$HOME/trinity_lab_backup}"
ROOT_DEST="/root/trinity_lab_backup"

if [ -n "$1" ]; then
  NAME="$1"
  SOURCE="${SOURCE_BASE}/${NAME}"
  if [ ! -d "$SOURCE" ]; then
    echo "Błąd: brak katalogu: $SOURCE" >&2
    exit 1
  fi
else
  LAST=$(ls -td "$SOURCE_BASE"/v* 2>/dev/null | head -1)
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
'''
with open(path, 'w') as f:
    f.write(content)
os.chmod(path, 0o755)
print('copy_backup_to_root.sh: OK')
