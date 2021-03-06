# C 語言教學助理小工具

## Overview

批改大學部一年級計算機程式設計每週作業的小工具，幫助做出簡單的給分。用 Python 呼叫系統指令 `gcc` 來編譯 C 語言作業，接著傳入 `stdin` 作為輸入參數，擷取 `stdout` 並篩選輸出內容是否符合正規表達式，根據比對結果給予分數，最終匯出 `csv` 統整表格，作為給分參考。

> 該專案僅應用於高雄科技大學數位教學平台，在教師環境下匯出「全部學員附檔」，並將檔案內容套用於專案內，產生統整表格。

## Environment

- Ubuntu 20.04
- Python 3.8.10
- zsh 5.8 (x86_64-ubuntu-linux-gnu)
- gcc (Ubuntu 9.4.0-1ubuntu1~20.04) 9.4.0

## Usage

建立 python 虛擬環境，並安裝依賴套件。

```bash
pip install -r requirements.txt
# required gcc
```

複製 `example.ini` 並命名為 `env.ini`，設定需要的配置。接著執行 `main.py` 並輸出統整表格。

- main.py:

    主要程式進入點。

- assistant_tool.py:

    輔助工具，走訪資料夾內所有學生的作業，編譯並執行取得輸出，檢查與設定的答案是否相符，並根據結果產生給分。

- config.py:

    程式參數相關配置，包含輸入參數與輸出結果（正規表達式）。

## 已知問題

- 在 Windows 系統上在特殊中文路徑下無法正常解析路徑，使批改結果錯誤，因此僅適用在 Linux 下。
  - 解決辦法可以批量重新命名所有路徑，並映射新舊名稱來尋找原始名稱。