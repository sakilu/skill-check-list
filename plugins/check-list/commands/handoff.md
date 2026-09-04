---
description: 把目前的工作寫成交接單,發布成連結交給別人或別的 agent 接手
argument-hint: "[要交接的專案或工作範圍;省略則詢問]"
allowed-tools: Read, Glob, Grep, Bash, Artifact, AskUserQuestion
---

以 `check-list` skill 的**模式 A(交出去)**產生交接單。

交接範圍:$1(空白則先問使用者是哪一個專案、哪一件工作)

照 `templates/handoff.yaml` 逐節收集脈絡,寫不出來的節照實寫「不知道」不要編。

先問清楚接手者在不在組織內——這決定要用哪個模式,兩者不能混用:
組織內用 `db`(組織內部版,發布前先把頁面範本複製到帶專案名的獨立路徑,避免覆蓋既有交接單);
組織外用 `artifact`(對外分享版,先組出 state JSON,用
`${CLAUDE_PLUGIN_ROOT}/scripts/gen-external.py` 套版後發布,不要自己手刻字串取代)。
組織外的 agent 交接不了,要老實告訴使用者。

回傳連結時要一併說明:artifact 預設私有,編輯權限需使用者自行設定。
