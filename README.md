# skill-check-list

工作交接單的 Claude Code plugin,**以及它自己的 plugin marketplace**。
一個 repo 同時扮演兩個角色,團隊只要 add 這個 repo 就能裝。

把一件工作寫成別人接得住的東西:產物是一個網頁連結,
人可以開來看、勾選、留言,agent 可以讀待辦、回寫進度,兩邊看到同一份狀態。

私有 repo。安裝者必須有本 repo 的 GitHub 讀取權。

## 安裝

```
/plugin marketplace add sakilu/skill-check-list
/plugin install check-list@skill-check-list
```

第一步會用你本機的 git 認證去 clone 私有 repo(優先走 SSH)。若失敗,先確認:

```powershell
gh auth status                                             # 已登入,且帳號在本 repo 的協作者名單內
git ls-remote git@github.com:sakilu/skill-check-list.git    # 能列出 ref 才代表金鑰通了
```

用 SSH 的人要先把公鑰加到 GitHub;用 HTTPS 的人要有 credential helper 或 PAT。

### CLI 與桌面版裝一次就好

安裝是 **user scope**:設定寫進 `~/.claude/settings.json` 的 `enabledPlugins` 與
`extraKnownMarketplaces`,plugin 本體解到 `~/.claude/plugins/cache/`。
同一台機器上的 Claude Code —— 終端機 CLI、桌面版、IDE 擴充 —— 都讀這一份,
**不需要分別安裝**。

例外是 **claude.ai/code 網頁版**:它跑在雲端,吃不到你本機的 `~/.claude`,
要在那邊用得在該環境重新 add + install。

## 用法

```
/check-list:handoff erp          # 把 erp 的工作寫成交接單,回傳連結
/check-list:pickup <連結>         # 從連結接手,讀待辦、回寫進度
```

也可以直接說「把這個交接出去」「接手這份工作」,skill 會自己被觸發。

## 兩種交接單

平台對 artifact 的兩種能力有不同限制,所以交接單分兩種模式,不能混用:

| | 組織內部版(預設) | 對外分享版 |
|---|---|---|
| 接手者 | 同組織登入成員 | 組織外的人 |
| agent 能不能結構化讀寫 | 能 | **不能**,只有瀏覽器裡的人點擊能寫回 |
| 平台能力 | `db` | `artifact`(自我發布) |

組織外的 **agent** 交接不了——這是平台限制,不是還沒做的功能。詳見
`plugins/check-list/skills/check-list/references/integration.md`。

## 兩個限制,裝之前先知道

1. **交接單發布時一律私有。** 要由擁有者在 artifact 畫面的分享選單設成可編輯,
   接手者才開得了、寫得進去。這一步無法由工具代勞。
2. **組織內部版不能公開分享。** 這是宣告 `db` 能力的 artifact 的平台限制:
   讀寫的人都必須是同組織的登入成員。要交給組織外的人,用對外分享版。

## 改完之後怎麼生效

**版號就是快取的 key。改了內容不動版號,所有人都拿不到新版。**

裝好的 plugin 被解到 `~/.claude/plugins/cache/skill-check-list/check-list/<版號>/`。
`marketplace update` 只更新 marketplace 的目錄清單,**不會**把已安裝的 plugin 換版本,
也不會重抓同版號的內容。所以發布新版一定要三步都做:

```bash
# 1. 兩個檔的 version 一起改,不能只改一個
#    .claude-plugin/marketplace.json    → plugins[0].version
#    plugins/check-list/.claude-plugin/plugin.json → version
git commit -am "..." && git push
```

```powershell
# 2. 拉新的目錄清單
claude plugin marketplace update skill-check-list

# 3. 真正換版。必須用 update——install 對已安裝的 plugin 只會回
#    「already installed」然後什麼都不做,你用的還是舊版
claude plugin update check-list@skill-check-list

# 換版後要重開 Claude Code 才會生效
```

確認自己跑的是哪一版:

```powershell
claude plugin details check-list                       # 顯示的版號
python -c "import json;print(json.load(open(r'$env:USERPROFILE\.claude\plugins\installed_plugins.json'))['plugins']['check-list@skill-check-list'])"
```

第二行印出的 `installPath` 才是**實際載入**的目錄。它跟 `details` 顯示的版號可能不一致——
不一致就代表第 3 步沒做。

**開發時** —— 改成指向本機目錄,存檔即生效,不必動版號:

```
/plugin marketplace remove skill-check-list
/plugin marketplace add <本 repo 的本機絕對路徑>
```

改完記得切回 GitHub 來源,以免自己用的版本跟團隊拿到的不一樣。

## 架構

```
skill-check-list/
├─ .claude-plugin/marketplace.json          分發層:團隊 add 這個 repo 就看得到 plugin
└─ plugins/check-list/
   ├─ .claude-plugin/plugin.json
   ├─ templates/                            資料層:交接單該長什麼樣
   │  ├─ handoff.yaml                          骨架,一份合格交接單至少要交代哪些節
   │  └─ example-verify.sh                     可夾帶驗證腳本的寫法範例
   ├─ assets/
   │  ├─ handoff-page.html                  組織內部版頁面,發布成 db artifact
   │  └─ handoff-external.html              對外分享版範本,發布前要先套版填資料
   ├─ scripts/gen-external.py               套版工具:把 state JSON 填進對外版範本
   ├─ skills/check-list/
   │  ├─ SKILL.md                           執行層:交出去 / 接手兩個模式
   │  └─ references/integration.md             其他 skill 作者怎麼接、資料契約
   └─ commands/                             handoff.md、pickup.md
                                            (指令為 /check-list:handoff、/check-list:pickup)
```

**為什麼把骨架抽成資料層**:新增一種工作類型的交接規則只是加一個 yaml,
不用動 SKILL.md,也不會把用不到的內容灌進別人的 context。

**為什麼組織內部版頁面是純資料驅動**:同一份 HTML 服務所有交接單,內容全部放在
artifact 的 db。人在網頁上勾選,agent 用 `read_db` / `write_db` 讀寫,
兩邊是同一份狀態而不是兩份拷貝。

**為什麼對外分享版要先套版**:`artifact`(自我發布)能力沒有資料庫,狀態只能
直接寫進頁面本身。`gen-external.py` 用鎖定標籤邊界的正則替換套版——
不要自己手刻整檔字串取代,已經實測踩過坑:整檔取代連範本自己程式碼裡
提到佔位字串名稱的地方都會被誤傷,炸掉 JS 語法讓整頁空白。

## 資料契約

跨 agent 的介面,改欄位名會弄壞所有接手方:

| 路徑 | 欄位 |
|---|---|
| `meta/handoff` | `title` `project` `fromWho` `toWho` `createdAt` `status` `summary` |
| `sections/<id>` | `order` `label` `body` |
| `tasks/<id>` | `order` `title` `why` `how` `verify` `state` `updatedAt` `updatedBy` |
| `notes/<id>` | `taskId` `body` `author` `createdAt` |
| `files/<id>` | `name` `taskId` `kind` `interpreter` `body` `sha256` `size` `purpose` `addedBy` `addedAt` |

`state` 只能是 `todo` / `doing` / `done` / `blocked`。
完整說明見 `plugins/check-list/skills/check-list/references/integration.md`。

## 上下文成本

實測(七項任務、六節脈絡、一支 1.8 KB 夾帶腳本的交接單):

| 項目 | 成本 |
|---|---|
| 每個 session 都付 | ~225 tok |
| skill 觸發載入 SKILL.md | ~2.6k tok |
| 接手時讀取交接單內容 | ~2.5k tok |

讀取的 2.5k 裡,**那支 1.8 KB 的腳本就佔 27%** —— 附件是唯一會失控的部分。
所以 `kind: script` 上限訂在 16 KB(約 400 行),而且:

- 寫入大內容用 `write_db` 的 `file_path`,body 從磁碟直接進 db,不過上下文
- 讀取附件用 `read_db` 的 `out_dir` 加 `where taskId`,回傳檔名而非內容
- 絕不 `list` 整個 `files` 集合

## 這個 plugin 刻意不做的事

**不內建語言別的驗證範本。** 任務的 `verify` 欄位要用該專案**實際能跑的指令**——
從 `package.json`、`Makefile`、CI 設定裡取,寫進去前自己跑過一次確認會過。
套來的通用指令跑不起來,比沒有驗證條件更糟,而且會讓接手者以為驗過了。

**不做專案管理。** 工作怎麼拆由呼叫者決定,這個 plugin 只負責把它變成別人接得住的形式。

## 貢獻

送出前先驗 manifest:

```powershell
claude plugin validate plugins/check-list    # plugin manifest
claude plugin validate .                     # marketplace manifest
```

改動內容的話,記得依〈改完之後怎麼生效〉一併升版號——不升版號,所有人都拿不到新版。
