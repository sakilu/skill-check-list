# check-list

工作交接單。把一件工作寫成別人接得住的東西,產物是一個網頁連結:
人可以開來看、勾選、留言,agent 可以讀待辦、回寫進度,兩邊看到同一份狀態。

## 用法

```
/check-list:handoff <專案>       # 交出去:產生交接單,回傳連結
/check-list:pickup <連結>        # 接手:讀待辦、執行、回寫進度
```

也可以直接說「把這個交接出去」「接手這份工作」。

## 任務狀態

| 狀態 | 意義 |
|---|---|
| `todo` | 還沒人動 |
| `doing` | 有人正在做,開工前要先認領 |
| `done` | 做完且 `verify` 通過 |
| `blocked` | 卡住,註記要寫清楚卡在哪、試過什麼 |

`verify` 沒過不准標 `done`。交接單的價值全在狀態可信。

## 兩個限制

- 交接單發布時**一律私有**,編輯權限要擁有者在 artifact 分享選單手動設定。
- **組織內部版不能公開分享**,讀寫者必須是同組織的登入成員。要交給組織外的人,
  用對外分享版(`artifact` 能力自我發布)——但組織外的 **agent** 交接不了,
  那個模式只有瀏覽器裡的人點擊能寫回進度,平台限制,不是還沒做的功能。

## 內附範本與工具

| 檔案 | 用途 |
|---|---|
| `templates/handoff.yaml` | 交接單骨架:至少要交代哪些節、每項任務要有哪些欄位 |
| `templates/example-verify.sh` | 可夾帶驗證腳本的寫法範例 |
| `assets/handoff-page.html` | 組織內部版頁面(db),同一份服務所有交接單 |
| `assets/handoff-external.html` | 對外分享版範本(artifact),發布前要先套版 |
| `scripts/gen-external.py` | 套版工具,把 state JSON 填進對外版範本 |

任務的 `verify` 欄位要用**該專案實際能跑的指令**,不內建語言別範本——
套來的通用指令跑不起來,比沒有驗證條件更糟。

資料契約與其他 skill 的接法見 `skills/check-list/references/integration.md`。
