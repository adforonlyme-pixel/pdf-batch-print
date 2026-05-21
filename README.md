# PDF 批次列印工具

一個簡單的 Windows 小工具，可將指定資料夾內的所有 PDF 批次發送至印表機，支援自訂頁數與雙面列印。

---

## 📥 下載與使用（一般使用者）

> **完全不需要安裝任何東西！**

1. 點擊右側 **[Releases](../../releases/latest)** → 下載 `PDF批次列印工具.zip`
2. 解壓縮到任意資料夾
3. 雙擊 `PDF批次列印工具.exe`
4. 依序選擇印表機、PDF 資料夾、頁數、雙面設定，按下開始即可

> ✅ 僅支援 **Windows 10 / 11**

---

## 功能特色

- 📂 瀏覽選擇 PDF 所在資料夾
- 🖨️ 支援所有已安裝的印表機
- 📄 彈性頁數設定（全部 / 自訂如 `1-3,5`）
- 🔄 雙面列印（單面 / 長邊翻頁 / 短邊翻頁）
- ⚠️ 列印失敗時顯示錯誤清單

---

## 🛠️ 開發者：如何從原始碼打包

本專案使用 **GitHub Actions** 自動打包，無需在本機安裝任何工具。

### 發布新版本的步驟

```bash
# 1. 在 GitHub 上 fork 或 clone 此 repo
git clone https://github.com/你的帳號/pdf-batch-print.git
cd pdf-batch-print

# 2. 修改程式碼後 commit
git add .
git commit -m "你的修改說明"
git push

# 3. 打上版本 tag，推送後自動觸發打包與發布
git tag v1.0.0
git push origin v1.0.0
```

推送 tag 後，GitHub Actions 會自動：
- 安裝 Python 與相依套件
- 下載 SumatraPDF
- 打包成 `.exe`
- 壓縮並上傳到 Releases

也可以到 GitHub repo 的 **Actions** 頁面，手動點擊「執行」觸發打包。

---

## 授權聲明

本工具使用 [MIT License](LICENSE)。

本工具於打包時內嵌 [SumatraPDF](https://www.sumatrapdfreader.org/)，其授權為 [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)。
