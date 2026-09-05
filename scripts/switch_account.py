"""微信多账号切换（通用版，需先填 accounts.json）

用法:
    python switch_account.py                 列出已配置的账号
    python switch_account.py 1               切换到 1 号账号
    python switch_account.py 1 --db-dir "D:/xwechat_files/你的wxid/db_storage"
                                             切换并把 db_dir 直接写进 config.json

作用:
    把 accounts.json 里指定账号的密钥文件复制为 ~/.wechat-cli/all_keys.json，
    并把 db_dir 写入 ~/.wechat-cli/config.json。

前提:
    各账号的密钥文件已用 extract_keys.py 提取好，例如：
    python extract_keys.py --db-dir "你的db_storage路径" --out ~/.wechat-cli/all_keys_account1.json
"""
import json
import os
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HOME = os.path.expanduser("~/.wechat-cli")
HERE = os.path.dirname(os.path.abspath(__file__))
CONF = os.path.join(HERE, "accounts.json")
EXAMPLE = os.path.join(HERE, "accounts.json.example")


def load_accounts():
    if not os.path.isfile(CONF):
        print("[!] 找不到 accounts.json")
        if os.path.isfile(EXAMPLE):
            print("    请把 accounts.json.example 复制成 accounts.json，再填你自己的 db / key")
        return None
    try:
        with open(CONF, encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        print("[!] accounts.json 解析失败：%s" % e)
        return None
    if not isinstance(data, dict) or not data:
        print("[!] accounts.json 内容为空或格式不对")
        return None
    return data


def main():
    accounts = load_accounts()
    if accounts is None:
        return 1

    args = sys.argv[1:]
    db_override = None
    if "--db-dir" in args:
        i = args.index("--db-dir")
        if i + 1 < len(args):
            db_override = args[i + 1]
        args = args[:i] + args[i + 2:]

    if not args:
        print("已配置的账号：")
        for k, v in sorted(accounts.items()):
            key_file = os.path.join(HOME, v.get("key", ""))
            mark = "已提取" if os.path.isfile(key_file) else "缺密钥文件"
            print("  %s: %s  [%s]" % (k, v.get("db", "(未填)"), mark))
        print("")
        print("用法: python switch_account.py <编号> [--db-dir <路径>]")
        return 0

    n = args[0]
    if n not in accounts:
        print("[!] 没有编号 %s，可用：%s" % (n, ", ".join(sorted(accounts))))
        return 1

    cfg = accounts[n]
    key_src = os.path.join(HOME, cfg.get("key", ""))
    if not cfg.get("key") or not os.path.isfile(key_src):
        print("[!] 密钥文件不存在：%s" % key_src)
        print("    先运行：python extract_keys.py --db-dir \"<db_storage>\" --out \"%s\"" % key_src)
        return 1

    os.makedirs(HOME, exist_ok=True)
    shutil.copy(key_src, os.path.join(HOME, "all_keys.json"))
    db = db_override or cfg.get("db", "")
    with open(os.path.join(HOME, "config.json"), "w", encoding="utf-8") as f:
        json.dump({"db_dir": db}, f, indent=2, ensure_ascii=False)
    print("[+] 已切换到账号%s: %s" % (n, db))
    return 0


if __name__ == "__main__":
    sys.exit(main())
