---
description: 從交接單連結接手工作,讀取待辦並回寫進度
argument-hint: "<交接單連結>"
allowed-tools: Read, Glob, Grep, Bash, Artifact
---

以 `check-list` skill 的**模式 B(接手)**接手工作。

交接單連結:$1(空白則跟使用者要,不要猜)

先把 sections 的脈絡與雷區全部讀完再動手。開工前把該項改成 doing,
一次只認領一項。做完或卡住都要回寫狀態並加註記,verify 沒過不准標 done。
