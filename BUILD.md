# 建置說明

本 repo 只有繁體中文版（`zh-TW/`），內容是 mdBook 網頁版，另外用 Pandoc 產生 A4 PDF。`.github/workflows/deploy.yml` 會依序執行本文件描述的測試、建置、打包與發布步驟。

## 需要的工具

CI 會鎖定 Rust 與 mdBook 的版本，避免上游發布新版時意外改變建置結果。本機請安裝相同版本，並在目前的 shell 選用鎖定的 Rust 工具鏈：

```bash
rustup toolchain install 1.98.0 --profile minimal --no-self-update
export RUSTUP_TOOLCHAIN=1.98.0
cargo install mdbook --version 0.5.4 --locked
```

這兩個版本要和 `.github/workflows/deploy.yml` 裡的 `RUSTUP_TOOLCHAIN`、`MDBOOK_VERSION` 一致。確認新版本能通過測試和建置之後，再更新鎖定的版本。

完整流程還需要 Bash、Python 3.11 以上、`curl`、`zip`、Pandoc、XeLaTeX、JetBrains Mono、Noto Sans、Noto CJK，以及一套 emoji 或符號字型。

Ubuntu/Debian 可以這樣安裝 Rust 以外的相依套件：

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  python3 \
  curl \
  zip \
  pandoc \
  texlive-xetex \
  texlive-fonts-recommended \
  texlive-lang-chinese \
  lmodern \
  fonts-jetbrains-mono \
  fonts-noto-core \
  fonts-noto-cjk \
  fonts-symbola
```

CI 不安裝 `fonts-noto-cjk`，改為下載並驗證下面「PDF 字型」一節列出的固定版本字型檔。本機建置請保留這個套件，除非你也下載了那幾個字型檔。

macOS：

```bash
brew install python pandoc
brew install --cask \
  mactex-no-gui \
  font-jetbrains-mono \
  font-noto-sans \
  font-noto-sans-cjk-tc \
  font-noto-sans-mono-cjk-tc \
  font-noto-color-emoji
```

裝好 MacTeX 後請重開終端機。如果還是找不到 `xelatex`，用下面的指令重新整理 shell 路徑：

```bash
eval "$(/usr/libexec/path_helper)"
```

## 版本設定

`zh-TW/edition.toml` 存放不屬於共用腳本的在地化設定：PDF 目錄標題、封面日期格式、SEO locale 與預設描述、轉址頁文字，以及課程各段落的標準標題。書名、作者與語言代碼則放在 `zh-TW/book.toml`。

`scripts/` 裡的 Python 腳本會透過 `scripts/edition_config.py` 讀取並驗證這兩個檔案，版本清單定義在 `EDITION_CODES`。演算法放在 `scripts/`，文字或日期格式的調整請改 `zh-TW/edition.toml`。

## 共用的 mdBook 主題檔

favicon、程式碼區塊修正與分享按鈕的唯一來源是根目錄的 `favicon.svg` 和 `assets/mdbook/`。剛 clone 下來，或改了這些檔案之後，要先把它們複製到 `zh-TW/theme/`（這個目錄由腳本產生，不進 Git）：

```bash
python3 -B scripts/prepare_mdbook_assets.py
```

請在 `mdbook build` 或 `mdbook serve` 之前執行。部署流程會自動執行這一步。

## 測試用的相依套件

教學中用到的外部 crate 宣告在根目錄的 `test-deps/`，並提交了 `test-deps/Cargo.lock`，讓 CI 解析出的版本固定不變。執行 mdBook 測試前，先建置一次鎖定的相依套件：

```bash
cargo build --locked --manifest-path test-deps/Cargo.toml
```

然後用這些編譯好的相依套件測試整本書：

```bash
(cd zh-TW && mdbook test -L ../test-deps/target/debug/deps)
```

## 網頁版

在 repo 根目錄建置 mdBook 網站：

```bash
python3 -B scripts/prepare_mdbook_assets.py
(cd zh-TW && mdbook build)
```

產生的網站會放在 `zh-TW/book/`。寫作時可以改用 `(cd zh-TW && mdbook serve)` 即時預覽。

## PDF 字型

GitHub Actions 會把下面三個繁體中文字型檔下載到根目錄的 `build/fonts/`：

- `NotoSansCJKtc-Regular.otf`
- `NotoSansCJKtc-Bold.otf`
- `NotoSansMonoCJKtc-Regular.otf`

這些檔案鎖定在 Noto CJK 的 `f8d157532fbfaeda587e826d4cd5b21a49186f7c` 版本，建置 PDF 前會先驗證 SHA-256。

共用的 `print/header.tex` 會在這些檔案存在時載入它們，`zh-TW/print/header.tex` 只是一層包裝，負責提供在地化的章節標籤。這樣可以避免 Ubuntu 把泛 CJK 的 Noto 字型集解析成日文字面（例如 `NotoSansCJKjp-*`）。

本機通常用系統安裝的 Noto CJK 就夠了。如果要完全重現 CI 的字型選擇，把這三個檔案下載到 `build/fonts/` 即可。根目錄的 `build/` 不進 Git。

## A4 PDF

在 repo 根目錄執行列印流程：

```bash
bash scripts/build_print.sh zh-TW
```

會在 `zh-TW/` 底下產生：

- `book/rust-book-a4.pdf`
- `build/print/rust-book-a4.tex`
- `build/print/manuscript.md`
- `build/print/code-lines.txt`

列印流程以 `zh-TW/src/SUMMARY.md` 為準：

- `SUMMARY.md` 的第一層項目成為章，每章從新的一頁開始；
- 巢狀的課程檔案成為節，不會強制換頁；
- 「第一部」和「第二部」會成為置中的部扉頁。

目錄標題和封面日期格式來自 `zh-TW/edition.toml`。

PDF 封面右下角有一個 Creative Commons BY-NC-ND 4.0 的小圖示，下方附上授權網址。圖示存放在 `assets/cc-by-nc-nd-4.0-88x31.png`，來源是 Creative Commons 官方素材 `https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-nd.png`，PDF 中的連結指向 `https://creativecommons.org/licenses/by-nc-nd/4.0/`。

程式碼每行的可見寬度預設上限是 95 個字元，需要時可以針對單次建置調整：

```bash
CODE_LINE_LIMIT=100 bash scripts/build_print.sh zh-TW
```

## 讀者下載檔

`zh-TW/src/foreword.md` 提供 `book.pdf` 和 `rust-book-src.zip` 兩個下載連結，但上面的指令都不會產生這兩個檔名。部署流程會在列印流程之後，把 A4 PDF 複製成固定檔名，再把 `src/` 壓縮起來：

```bash
(cd zh-TW && cp book/rust-book-a4.pdf book/book.pdf)
(cd zh-TW/src && zip -r ../book/rust-book-src.zip .)
```

要在本機重現完整的發布內容或檢查下載檔時再執行，網頁版和 PDF 的建置本身不需要它們。

## 組合發布的網站

`zh-TW/book/` 只是 mdBook 的中間產物。GitHub Pages 實際收到的是另外組合出來的 `public/`，裡面有網頁版、讀者下載檔，以及根目錄的首頁轉址、404 頁等共用檔案。網頁版、PDF 和下載檔都建置好之後，在 repo 根目錄組合：

```bash
rm -rf public
mkdir -p public
cp index.html public/index.html
cp favicon.svg public/favicon.svg
cp 404.html public/404.html
cp robots.txt public/robots.txt
cp -r zh-TW/book public/zh-TW
```

接著依序執行三個發布腳本：

```bash
python3 scripts/normalize_public_urls.py public
python3 scripts/add_seo_metadata.py public
python3 scripts/generate_sitemap.py public
```

- `normalize_public_urls.py` 會產生沒有數字前綴的課程網址，改寫 HTML 和 mdBook 側欄的連結，並在舊的編號網址留下轉址頁。轉址頁的文字來自 `zh-TW/edition.toml`。
- `add_seo_metadata.py` 會替正式頁面加上 canonical、Open Graph 與 Twitter metadata。網站只有一個版本，所以不產生 hreflang 連結。
- `generate_sitemap.py` 會列出所有正式頁面，排除轉址頁（包括根目錄的 `index.html`）、`404.html` 和 mdBook 的 `print.html`。

根目錄的 `index.html` 只是轉址頁，會把訪客直接帶到 `/zh-TW/`。

組合出來的 `public/` 就是上傳到 GitHub Pages 的內容。它是產生出來的檔案，隨時可以刪掉重建。

## 部署流程

`.github/workflows/deploy.yml` 分成兩個 job：

- **build**：每次推送到 `main`，以及每個指向 `main` 的 pull request，都會執行完整的測試、網頁版、PDF 與網站組合。同一個 PR 有新的 push 時，會取消還在跑的舊檢查。
- **deploy**：只有推送到 `main` 時才會執行，把 build 上傳的網站部署到 GitHub Pages。

PDF 需要的 apt 套件（texlive、字型等）用 `awalsh128/cache-apt-pkgs-action` 快取，並鎖定在特定 commit。從快取還原的套件不會觸發 dpkg trigger，所以下一步會用 `mktexlsr` 和 `fmtutil-sys --byfmt xelatex` 重建 TeX 檔案索引與 xelatex 格式檔。套件清單有變動時，快取會自動重建；如果需要強制重建，把 `version` 的值加一即可（例如 `ubuntu-26.04-1` 改成 `ubuntu-26.04-2`）。

repo 的 Settings → Pages 必須把來源設成「GitHub Actions」，deploy job 才能成功。
