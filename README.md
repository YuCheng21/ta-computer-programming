# C 語言教學助理小工具

## Overview

批改每週作業的小工具，幫助做出簡單的給分。用 Python 呼叫系統指令 `gcc` 來編譯 C 語言作業，接著傳入 `stdin` 作為輸入參數，擷取 `stdout` 並篩選輸出內容是否符合正規表達式，根據比對結果給予分數，最終匯出 `csv` 統整表格，作為給分參考。

## Environment

- Ubuntu 20.04
- Python 3.8.10
- Shell
    - zsh

## Usage

建立 python 虛擬環境，並安裝依賴套件。

```
pip install -r requirements.txt
```

執行 `main.py` 並輸出統整表格。

- main.py:

    主要程式進入點，走訪資料夾內所有學生的作業，編譯並執行取得輸出，檢查與設定的答案是否相符，並根據結果產生給分。

- config.py:

    程式參數相關配置，包含輸入參數與輸出結果（正規表達式）。