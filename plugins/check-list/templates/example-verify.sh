#!/usr/bin/env bash
# example-verify.sh — 夾帶腳本的範例
# 這支腳本本身驗證 check-list plugin 的結構,同時示範一個可夾帶的驗證腳本長什麼樣:
#   有用法說明、有明確的通過條件、只讀不寫、退出碼有意義。
# 用法:在 repo 根目錄執行  bash verify-plugin.sh
# 通過條件:exit code 0,且最後一行輸出 "ALL PASS"
set -uo pipefail

fail=0
ok()   { printf '  PASS  %s\n' "$1"; }
bad()  { printf '  FAIL  %s\n' "$1"; fail=1; }

echo "== 1. 必要檔案存在 =="
for f in \
  .claude-plugin/marketplace.json \
  plugins/check-list/.claude-plugin/plugin.json \
  plugins/check-list/skills/check-list/SKILL.md \
  plugins/check-list/assets/handoff-page.html \
  plugins/check-list/templates/handoff.yaml
do
  [ -f "$f" ] && ok "$f" || bad "缺少 $f"
done

echo "== 2. JSON 合法 =="
for f in .claude-plugin/marketplace.json plugins/check-list/.claude-plugin/plugin.json; do
  if python -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8'))" "$f" 2>/dev/null; then
    ok "$f"
  else
    bad "$f 不是合法 JSON"
  fi
done

echo "== 3. SKILL.md 有 frontmatter 且宣告 name =="
if head -1 plugins/check-list/skills/check-list/SKILL.md | grep -q '^---$' &&
   grep -q '^name: check-list$' plugins/check-list/skills/check-list/SKILL.md; then
  ok "frontmatter 與 name"
else
  bad "SKILL.md frontmatter 或 name 有問題"
fi

echo "== 4. 資料契約欄位在頁面裡都找得到 =="
page=plugins/check-list/assets/handoff-page.html
for field in fromWho toWho createdAt summary taskId verify updatedBy sha256 interpreter; do
  grep -q "$field" "$page" && ok "$field" || bad "頁面缺少契約欄位 $field"
done

echo "== 5. 不該殘留舊用語 =="
if grep -rq "鐵則" --include='*.yaml' --include='*.md' . 2>/dev/null; then
  bad "仍有檔案含『鐵則』字眼"
else
  ok "沒有殘留舊用語"
fi

echo
if [ "$fail" -eq 0 ]; then echo "ALL PASS"; exit 0; else echo "HAS FAILURES"; exit 1; fi
