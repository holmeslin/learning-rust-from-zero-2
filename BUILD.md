# 建置說明

本 repo 只有繁體中文版（`zh-TW/`），內容是 mdBook 網頁版。`.github/workflows/deploy.yml` 會依序執行本文件描述的測試、建置、打包與發布步驟。

## 需要的工具

CI 會鎖定 Rust 與 mdBook 的版本，避免上游發布新版時意外改變建置結果。本機請安裝相同版本，並在目前的 shell 選用鎖定的 Rust 工具鏈：

```bash
rustup toolchain install 1.98.0 --profile minimal --no-self-update
export RUSTUP_TOOLCHAIN=1.98.0
cargo install mdbook --version 0.5.4 --locked
```

這兩個版本要和 `.github/workflows/deploy.yml` 裡的 `RUSTUP_TOOLCHAIN`、`MDBOOK_VERSION` 一致。確認新版本能通過測試和建置之後，再更新鎖定的版本。

完整流程還需要 Bash、Python 3.11 以上與 `zip`。

Ubuntu/Debian 可以這樣安裝 Rust 以外的相依套件：

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  python3 \
  zip
```

macOS：

```bash
brew install python
```

## 版本設定

`zh-TW/edition.toml` 存放不屬於共用腳本的在地化設定：SEO locale 與預設描述，以及轉址頁文字。書名、作者與語言代碼則放在 `zh-TW/book.toml`。

`scripts/` 裡的 Python 腳本會透過 `scripts/edition_config.py` 讀取並驗證這兩個檔案，版本清單定義在 `EDITION_CODES`。演算法放在 `scripts/`，文字的調整請改 `zh-TW/edition.toml`。

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

## 讀者下載檔

`zh-TW/src/foreword.md` 提供 `rust-book-src.zip` 的下載連結，但上面的指令不會產生這個檔名。部署流程會在網頁版建置好之後，把 `src/` 壓縮起來：

```bash
(cd zh-TW/src && zip -r ../book/rust-book-src.zip .)
```

要在本機重現完整的發布內容或檢查下載檔時再執行，網頁版的建置本身不需要它。

## 組合發布的網站

`zh-TW/book/` 只是 mdBook 的中間產物。GitHub Pages 實際收到的是另外組合出來的 `public/`，裡面有網頁版、讀者下載檔，以及根目錄的首頁轉址、404 頁等共用檔案。網頁版和下載檔都建置好之後，在 repo 根目錄組合：

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

- **build**：每次推送到 `main`，以及每個指向 `main` 的 pull request，都會執行完整的測試、網頁版、讀者下載檔與網站組合。同一個 PR 有新的 push 時，會取消還在跑的舊檢查。
- **deploy**：只有推送到 `main` 時才會執行，把 build 上傳的網站部署到 GitHub Pages。

repo 的 Settings → Pages 必須把來源設成「GitHub Actions」，deploy job 才能成功。
