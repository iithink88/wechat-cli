"""设置 wechat-cli 的数据库目录（生成 ~/.wechat-cli/config.json）

为什么需要它：
    extract_keys.py 只负责提取密钥并写成 all_keys.json，
    但 wechat-cli 还需要 config.json 里的 db_dir 才知道去哪儿读数据库。
    微信 4.1+ 上 `wechat-cli init` 常常提取不到密钥（0 命中），
    所以密钥用 extract_keys.py 提取、路径用本脚本写入，是最稳的组合。

用法:
    python set_db_dir.py "你的db_storage路径"
    python set_db_dir.py --show                 查看当前配置

示例(Windows):
    python set_db_dir.py "C:/Users/你的用户名/Documents/xwechat_files/你的wxid/db_storage"
"""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HOME = os.path.expanduser("~/.wechat-cli")
CFG = os.path.join(HOME, "config.json")


def main():
    args = sys.argv[1:]

    if args and args[0] == "--show":
        if not os.path.isfile(CFG):
            print("尚未配置：%s" % CFG)
            return 1
        with open(CFG, encoding="utf-8-sig") as f:
            print(json.dumps(json.load(f), indent=2, ensure_ascii=False))
        return 0

    if not args:
        print("用法: python set_db_dir.py \"<db_storage 路径>\"")
        print("      python set_db_dir.py --show")
        return 1

    db_dir = args[0].strip().strip('"')
    if not os.path.isdir(db_dir):
        print("[!] 目录不存在：%s" % db_dir)
        print("    请确认微信已登录过，路径通常形如 .../xwechat_files/<wxid>/db_storage")
        cont = input("仍要写入吗？(y/N): ").strip().lower()
        if cont != "y":
            print("已取消")
            return 1

    os.makedirs(HOME, exist_ok=True)
    with open(CFG, "w", encoding="utf-8") as f:
        json.dump({"db_dir": db_dir}, f, indent=2, ensure_ascii=False)
    print("[+] 已写入 %s" % CFG)
    print("    db_dir = %s" % db_dir)
    print("")
    print("验证: wechat-cli sessions --limit 5 --format text")
    return 0


if __name__ == "__main__":
    sys.exit(main())
