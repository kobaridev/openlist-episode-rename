#!/usr/bin/env bash
# 基于 PyInstaller 单文件二进制构建 .deb 包
# 用法: bash scripts/build-deb.sh <binary_path> <version> <output_dir> [arch]
# arch 取值: amd64 / arm64（默认 amd64）
set -euo pipefail

BIN="$1"
VER="$2"
OUT="$3"
ARCH="${4:-amd64}"

PKG="openlist-episode-renamer"

ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT

mkdir -p "$ROOT/DEBIAN" "$ROOT/usr/bin" "$ROOT/lib/systemd/system" "$ROOT/usr/share/doc/$PKG"

install -m 0755 "$BIN" "$ROOT/usr/bin/$PKG"

cat > "$ROOT/DEBIAN/control" <<EOF
Package: ${PKG}
Version: ${VER}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: kobaridev <kobaridev@users.noreply.github.com>
Depends: libc6 (>= 2.17)
Description: OpenList TV-series batch rename tool (Web UI)
 Web-based renamer for OpenList libraries. Enter a directory, auto-detect
 episodes, fetch episode titles from TMDB, bulk-assign season/episode numbers,
 add media parameters, and rename with subtitle files following their video.
 Single self-contained binary: run 'openlist-episode-renamer' then open
 http://127.0.0.1:8000. Packaged with PyInstaller.
EOF

cat > "$ROOT/lib/systemd/system/${PKG}.service" <<EOF
[Unit]
Description=OpenList Episode Rename Web Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/${PKG} 0.0.0.0 8000
ExecStartPre=/bin/mkdir -p /var/lib/openlist-episode-rename
Environment=EPISODE_PATH=/var/lib/openlist-episode-rename
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

if [ -f LICENSE ]; then
    install -m 0644 LICENSE "$ROOT/usr/share/doc/$PKG/copyright"
fi
printf 'OpenList Episode Rename %s\n' "$VER" > "$ROOT/usr/share/doc/$PKG/changelog"

mkdir -p "$OUT"
dpkg-deb --build --root-owner-group "$ROOT" "$OUT/${PKG}_${VER}_${ARCH}.deb" >/dev/null
echo "$OUT/${PKG}_${VER}_${ARCH}.deb"