#!/usr/bin/env bash
# Build the Linux AppImage and a tar.gz fallback.
#
# Requirements (build host):
#   - Python 3.11+ with requirements.txt + requirements-dev.txt installed
#   - appimagetool on PATH
#   - Pillow installed (for scripts/make_icons.py)
#   - apt: libxcb-cursor0 libxkbcommon-x11-0  (and the rest installed by CI)
#
# Run from the repo root:
#   bash scripts/build_linux.sh
set -euo pipefail

ROOT="$(cd "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

VERSION="$(git describe --tags --always 2>/dev/null || echo dev)"
echo "[build_linux] version=${VERSION}"

# 1. Icons (idempotent; safe to re-run)
python scripts/make_icons.py

# 2. PyInstaller (--onedir)
rm -rf build dist
pyinstaller build_linux.spec

# 3. AppDir staging
APPDIR="packaging/AppDir"
rm -rf "${APPDIR}/usr"
mkdir -p "${APPDIR}/usr/bin"
cp -r dist/TranslateApp "${APPDIR}/usr/bin/"
cp assets/icon.png "${APPDIR}/translateapp.png"

# 4. AppImage
OUT_APPIMAGE="TranslateApp-${VERSION}-x86_64.AppImage"
appimagetool "${APPDIR}" "${OUT_APPIMAGE}"
echo "[build_linux] wrote ${OUT_APPIMAGE}"

# 5. Tarball (no AppImage runtime required)
OUT_TARBALL="TranslateApp-${VERSION}-linux-x86_64.tar.gz"
tar -czf "${OUT_TARBALL}" -C dist TranslateApp
echo "[build_linux] wrote ${OUT_TARBALL}"
