"""
產生一份「對外分享」交接單的 HTML,填入 assets/handoff-external.html 範本。

用鎖定特定標籤的正則替換,不做整檔盲目字串取代——後者只要檔案裡任何角落
(含註解、程式碼字面文字)剛好出現同一個佔位字串,就會被誤傷而炸掉頁面
(這是實測踩過的真實錯誤,不是假設性的顧慮)。

用法:
    python gen-external.py <template.html> <state.json> <out.html>

state.json 的結構見 skills/check-list/references/integration.md 的資料契約,
與內部版(db 版)完全相同的欄位:meta / sections / tasks / notes / files。
"""
import io, json, re, sys, argparse

# 對外版沒有 db,整份 state(tasks/sections/notes/files 連結記錄)都跟著文件
# 一起傳輸與重新發布,不像 db 版只有被讀到的文件才算數。files 現在只存連結,
# 不再內嵌內容,所以正常情況下不會撐大;這裡給一個軟性警告,不是硬限制。
WARN_BYTES = 200_000


def generate(template_path, state, out_path):
    tpl = io.open(template_path, encoding="utf-8").read()

    state_json = json.dumps(state, ensure_ascii=False).replace("</", "<\\/")
    title = str((state.get("meta") or {}).get("title") or "工作交接單")

    def esc_title(s):
        return (s.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace('"', "&quot;"))

    # [\s\S]*? 是非貪婪比對,鎖定「第一個真正的 </script>」字面文字為界,
    # 不會被 JSON 內容裡任何單獨出現的 "<" 字元打斷比對範圍。
    out, n1 = re.subn(
        r'(<script type="application/json" id="handoff-state">)[\s\S]*?(</script>)',
        lambda m: m.group(1) + state_json + m.group(2),
        tpl, count=1,
    )
    if n1 != 1:
        raise SystemExit("找不到 handoff-state script 標籤,範本可能被改過")

    out, n2 = re.subn(
        r"(<title>)[\s\S]*?(</title>)",
        lambda m: m.group(1) + esc_title(title) + m.group(2),
        out, count=1,
    )
    if n2 != 1:
        raise SystemExit("找不到 title 標籤,範本可能被改過")

    if "__INITIAL_STATE__" in out or "__INITIAL_TITLE__" in out:
        raise SystemExit("佔位字串仍有殘留,產生失敗")

    io.open(out_path, "w", encoding="utf-8", newline="\n").write(out)

    size = len(out.encode("utf-8"))
    if size > WARN_BYTES:
        sys.stderr.write(
            "警告:產出檔案 %d bytes,超過建議上限 %d bytes。"
            "每次勾選或留言都會整份重新發布,檔案太大會讓對外分享版變慢、"
            "也更容易把接手者的 context 灌爆。考慮拿掉大型附件改用外部連結。\n"
            % (size, WARN_BYTES)
        )
    return out, size


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("state_json_file")
    ap.add_argument("out")
    args = ap.parse_args()
    state = json.load(io.open(args.state_json_file, encoding="utf-8"))
    _, size = generate(args.template, state, args.out)
    print("written:", args.out, "bytes:", size)
