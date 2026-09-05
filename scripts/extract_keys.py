"""微信 4.1.12+ 密钥提取（通用版）：
用法: python extract_keys.py --db-dir <db_storage目录> [--out <all_keys.json路径>]
原理: dump Weixin.exe 进程内存中 com.Tencent.WCDB.Config.Cipher 对象的 blob，
      blob 内含 (派生后 32B 密钥 + 16B salt) 十六进制对，直接 HMAC 校验匹配数据库。
注意: 必须当前登录账号 == 目标 db_dir 账号；密钥属于登录中的账号。
"""
import argparse, ctypes, ctypes.wintypes as wt, glob, hashlib, json, os, re, struct, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wcdb_key_tool_windows import collect_db_files, verify_enc_key

kernel32 = ctypes.windll.kernel32
MEM_COMMIT = 0x1000
READABLE = {0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80}
WINDOWS_CONFIG_CIPHER_NAME = b"com.Tencent.WCDB.Config.Cipher"
WINDOWS_MAX_USER_ADDRESS = 0x0000_8000_0000_0000
WINDOWS_CONFIG_BLOB_MAX = 1024

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_uint64), ("AllocationBase", ctypes.c_uint64),
                ("AllocationProtect", wt.DWORD), ("_pad1", wt.DWORD),
                ("RegionSize", ctypes.c_uint64), ("State", wt.DWORD),
                ("Protect", wt.DWORD), ("Type", wt.DWORD), ("_pad2", wt.DWORD)]

def read_mem(h, addr, sz):
    buf = ctypes.create_string_buffer(sz); n = ctypes.c_size_t(0)
    if kernel32.ReadProcessMemory(h, ctypes.c_uint64(addr), buf, sz, ctypes.byref(n)):
        return buf.raw[: n.value]
    return None

def enum_regions(h):
    regs = []; addr = 0; mbi = MBI()
    while addr < 0x7FFFFFFFFFFF:
        if kernel32.VirtualQueryEx(h, ctypes.c_uint64(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)) == 0:
            break
        if mbi.State == MEM_COMMIT and mbi.Protect in READABLE and 0 < mbi.RegionSize < 500*1024*1024:
            regs.append((mbi.BaseAddress, mbi.RegionSize))
        nxt = mbi.BaseAddress + mbi.RegionSize
        if nxt <= addr: break
        addr = nxt
    return regs

def iter_chunks(regions, h, overlap=0, chunk_size=2*1024*1024):
    for base, size in regions:
        offset = 0; tail = b""; tail_base = base
        while offset < size:
            cur = min(chunk_size, size - offset)
            chunk = read_mem(h, base + offset, cur) or b""
            data_base = tail_base if tail else base + offset
            data = tail + chunk
            if data:
                yield data_base, data
                if overlap:
                    tail = data[-overlap:]; tail_base = data_base + max(0, len(data) - len(tail))
                else:
                    tail = b""; tail_base = base + offset + cur
            else:
                tail = b""; tail_base = base + offset + cur
            offset += cur

def find_bytes(regions, h, needle):
    addrs = set(); overlap = max(0, len(needle) - 1)
    for dbase, hay in iter_chunks(regions, h, overlap=overlap):
        pos = hay.find(needle)
        while pos >= 0:
            addrs.add(dbase + pos); pos = hay.find(needle, pos + 1)
    return addrs

def u64(d, o):
    return struct.unpack_from("<Q", d, o)[0] if o >= 0 and o + 8 <= len(d) else 0

def get_pids():
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Weixin.exe", "/FO", "CSV", "/NH"],
                       capture_output=True, text=True, errors="replace", encoding="mbcs")
    pids = []
    for line in r.stdout.strip().split("\n"):
        if not line.strip(): continue
        p = line.strip('"').split('","')
        if len(p) >= 5:
            pids.append((int(p[1]), int(p[4].replace(",", "").replace(" K", "").strip() or "0")))
    pids.sort(key=lambda x: x[1], reverse=True)
    return pids

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-dir", required=True)
    ap.add_argument("--out", default=os.path.expanduser("~/.wechat-cli/all_keys.json"))
    args = ap.parse_args()
    db_files, salt_to_dbs = collect_db_files(args.db_dir)
    page1 = {s: p1 for _r, _p, _z, s, p1 in db_files}
    rel = {s: r for r, _p, _z, s, _p1 in db_files}
    print(f"[*] db files: {len(db_files)}, salts: {len(salt_to_dbs)}")

    blobs = []
    for pid, _m in get_pids():
        h = kernel32.OpenProcess(0x0010 | 0x0400, False, pid)
        if not h: continue
        try:
            regions = enum_regions(h)
            needles = find_bytes(regions, h, WINDOWS_CONFIG_CIPHER_NAME)
            print(f"[*] pid={pid} needle hits: {len(needles)}")
            pairs = [struct.pack("<Q", a) + struct.pack("<Q", len(WINDOWS_CONFIG_CIPHER_NAME)) for a in needles]
            for base, data in iter_chunks(regions, h, overlap=0x80):
                for pat in pairs:
                    pos = data.find(pat)
                    while pos >= 0:
                        node = read_mem(h, base + pos - 0x10, 0x50)
                        if node and len(node) >= 0x40 and u64(node, 0x10) in needles and u64(node, 0x18) == len(WINDOWS_CONFIG_CIPHER_NAME):
                            cptr = u64(node, 0x28)
                            if 0x10000 <= cptr < WINDOWS_MAX_USER_ADDRESS:
                                obj = read_mem(h, cptr + 0x88, 0x28)
                                if obj and len(obj) >= 0x18:
                                    dptr = u64(obj, 0x8); dlen = u64(obj, 0x10)
                                    if 0 < dlen <= WINDOWS_CONFIG_BLOB_MAX and 0x10000 <= dptr < WINDOWS_MAX_USER_ADDRESS:
                                        blob = read_mem(h, dptr, int(dlen))
                                        if blob and len(blob) == dlen:
                                            blobs.append(blob)
                        pos = data.find(pat, pos + 1)
        finally:
            kernel32.CloseHandle(h)
    print(f"[*] blobs: {len(blobs)}")

    hex_re = re.compile(rb"[xX]'([0-9a-fA-F]{64,192})'")
    cands = set()
    for blob in blobs:
        for m in hex_re.finditer(blob): cands.add(m.group(1).decode().lower())
        for m in re.finditer(rb"([0-9a-fA-F]{64,192})", blob): cands.add(m.group(1).decode().lower())
    found = {}
    for c in cands:
        b = bytes.fromhex(c)
        if len(b) < 32: continue
        for start_key in (0, 16):
            if start_key + 32 > len(b): continue
            k = b[start_key:start_key + 32]
            for s in salt_to_dbs:
                if s in found: continue
                if verify_enc_key(k, page1[s]):
                    found[s] = k.hex()
                    print(f"  [OK] {rel[s]}  key={k.hex()[:16]}...")
    print(f"[*] matched {len(found)}/{len(salt_to_dbs)}")
    for s in salt_to_dbs:
        if s not in found:
            print(f"  MISSING: {rel[s]} salt={s}")

    if not found:
        print("[!] 无命中：确认当前登录账号 == 目标 db_dir，或微信重启后重试")
        sys.exit(1)
    result = {}
    for r, _p, z, s, _p1 in db_files:
        if s in found:
            result[r] = {"enc_key": found[s], "salt": s, "size_mb": round(z / 1024 / 1024, 1)}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"[+] saved {len(result)} keys -> {args.out}")

if __name__ == "__main__":
    main()
