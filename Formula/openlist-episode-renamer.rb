# Homebrew formula：OpenList 剧集批量重命名工具（macOS）
#
# 安装（Release 资产 openlist-episode-renamer-macos-arm64.tar.gz）：
#   brew install https://raw.githubusercontent.com/kobaridev/openlist-episode-renamer/main/Formula/openlist-episode-renamer.rb
# 或本地安装：
#   brew install ./Formula/openlist-episode-renamer.rb
#
# Intel (x64) 机型：请将下方 url 中 arm64 改为 x64。
# 每次发版后需把 url 的 release tag 更新到最新版本。
class OpenlistEpisodeRenamer < Formula
  desc "OpenList TV-series batch rename tool (Web UI, self-contained binary)"
  homepage "https://github.com/kobaridev/openlist-episode-renamer"
  url "https://github.com/kobaridev/openlist-episode-renamer/releases/download/v0.0.9/openlist-episode-renamer-macos-arm64.tar.gz"
  # 发版后可固定校验值： shasum -a 256 <tar.gz>；暂用 :no_check 避免每次发版都要改 formula
  sha256 :no_check

  def install
    bin.install "openlist-episode-renamer"
  end

  def caveats
    <<~EOS
      启动工具：
        openlist-episode-renamer

      浏览器访问 http://127.0.0.1:8000 登录你的 OpenList 即可。
      首次被 Gatekeeper 拦截时：系统设置 → 隐私与安全性 → 仍要打开；
      或用: xattr -d com.apple.quarantine #{bin}/openlist-episode-renamer
    EOS
  end

  test do
    assert_predicate bin/"openlist-episode-renamer", :exist?
  end
end