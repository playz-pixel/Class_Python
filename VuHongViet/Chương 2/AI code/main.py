#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO HOMEWORK SOLVER v2.0
Gemini AI  →  Python Code  →  GitHub
"""

import os, re, sys, base64, time
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("Thiếu thư viện. Chạy:  pip install requests")
    sys.exit(1)

# ══════════════════════════════════════════
#  MÀU ANSI
# ══════════════════════════════════════════
class C:
    RST  = "\033[0m";  BOLD = "\033[1m";  DIM  = "\033[2m"
    BLUE = "\033[34m"; CYAN = "\033[36m"; GRN  = "\033[32m"
    YLW  = "\033[33m"; RED  = "\033[31m"; WHT  = "\033[97m"
    BGb  = "\033[44m"

def ok(m):   print(f"  {C.GRN}+{C.RST}  {m}")
def er(m):   print(f"  {C.RED}x{C.RST}  {m}")
def wn(m):   print(f"  {C.YLW}!{C.RST}  {m}")
def nf(m):   print(f"  {C.CYAN}>{C.RST}  {m}")
def dm(m):   print(f"  {C.DIM}{m}{C.RST}")
def sep(c="─", w=54): print(f"  {C.DIM}{c*w}{C.RST}")

# ══════════════════════════════════════════
#  CẤU HÌNH
# ══════════════════════════════════════════
CONFIG_FILE = Path(__file__).parent / ".env"
OUTPUT_DIR  = Path(__file__).parent / "baitap"

MODELS = [
    "gemini-2.0-flash",       # Model mới nhất, cực nhanh
    "gemini-1.5-flash",       # Model ổn định
    "gemini-2.0-flash-lite",  # Bản nhẹ
    "gemini-1.5-pro",       # Model cũ, đôi khi ít bị rate-limit hơn
]

def load_cfg():
    d = dict(GEMINI_API_KEY="", GITHUB_TOKEN="", GITHUB_USER="",
             GITHUB_REPO="", GITHUB_BRANCH="main",
             OUTPUT_FOLDER="baitap", GEMINI_MODEL="gemini-2.0-flash")
    if CONFIG_FILE.exists():
        for ln in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, _, v = ln.partition("=")
                d[k.strip()] = v.strip()
    for k in d:
        if os.getenv(k):
            d[k] = os.getenv(k)
    return d

def save_cfg(cfg):
    lines = ["# Auto Homework Solver config\n"]
    for k, v in cfg.items():
        lines.append(f"{k}={v}\n")
    CONFIG_FILE.write_text("".join(lines), encoding="utf-8")

# ══════════════════════════════════════════
#  UI HELPERS
# ══════════════════════════════════════════
def clear(): os.system("cls" if os.name == "nt" else "clear")

def header():
    print()
    print(f"  {C.BGb}{C.WHT}{C.BOLD}  AUTO HOMEWORK SOLVER  {C.RST}  {C.DIM}v2.0{C.RST}")
    print(f"  {C.DIM}Gemini AI -> Python Code -> GitHub{C.RST}")
    sep("=")
    print()

def countdown(secs, label="Cho"):
    W = 30
    for rem in range(secs, 0, -1):
        filled = int(W * (secs - rem) / secs)
        bar = "#" * filled + "." * (W - filled)
        print(f"\r  [~]  {label}: [{C.CYAN}{bar}{C.RST}] {rem:>3}s ", end="", flush=True)
        time.sleep(1)
    print("\r" + " " * 68 + "\r", end="", flush=True)

def main_menu(cfg):
    g = f"{C.GRN}OK{C.RST}" if cfg.get("GEMINI_API_KEY") else f"{C.RED}--{C.RST}"
    h = f"{C.GRN}OK{C.RST}" if (cfg.get("GITHUB_TOKEN") and cfg.get("GITHUB_USER") and cfg.get("GITHUB_REPO")) else f"{C.RED}--{C.RST}"
    model = cfg.get("GEMINI_MODEL", "gemini-1.5-flash")
    print(f"  {C.BOLD}MENU CHINH{C.RST}")
    sep()
    print(f"  {C.CYAN}[1]{C.RST}  Nhap de bai tu ban phim")
    print(f"  {C.CYAN}[2]{C.RST}  Doc de bai tu file .txt")
    print(f"  {C.CYAN}[3]{C.RST}  Cau hinh API Keys & GitHub")
    print(f"  {C.CYAN}[4]{C.RST}  Kiem tra ket noi")
    print(f"  {C.CYAN}[0]{C.RST}  Thoat")
    sep()
    print(f"  Gemini [{g}]  GitHub [{h}]  Model: {C.DIM}{model}{C.RST}")
    print(f"  Repo: {C.DIM}{cfg.get('GITHUB_USER','?')}/{cfg.get('GITHUB_REPO','?')}{C.RST}")
    print()
    return input(f"  {C.BOLD}Chon [0-4]: {C.RST}").strip()

# ══════════════════════════════════════════
#  PARSE DE BAI
# ══════════════════════════════════════════
def parse(raw):
    pat = re.compile(r'(?:Bai|B\u00e0i|Exercise|C\u00e2u|Cau|Problem)\s*(\d+)\s*[:\.\-]', re.IGNORECASE)
    ms = list(pat.finditer(raw))
    if not ms:
        return {}
    out = {}
    for i, m in enumerate(ms):
        end = ms[i+1].start() if i+1 < len(ms) else len(raw)
        out[m.group(1)] = raw[m.start():end].strip()
    return out

def show_exercises(ex):
    print()
    print(f"  {C.BOLD}Tim thay {C.GRN}{len(ex)}{C.RST}{C.BOLD} bai tap:{C.RST}")
    sep()
    for n, txt in ex.items():
        prev = txt.replace('\n', ' ')[:65]
        print(f"  {C.CYAN}Bai {n}{C.RST}  {C.DIM}{prev}{'...' if len(txt)>65 else ''}{C.RST}")
    sep()

# ══════════════════════════════════════════
#  GEMINI  (retry + fallback)
# ══════════════════════════════════════════
class RateLimitError(Exception):
    def __init__(self, server_wait=0):
        self.server_wait = server_wait

def gemini_request(api_key, model, prompt):
    url = (f"https://generativelanguage.googleapis.com/v1beta/"
           f"models/{model}:generateContent?key={api_key}")
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
    }
    resp = requests.post(url, json=body, timeout=90)

    if resp.status_code == 429:
        wait = 0
        try:
            details = resp.json().get("error", {}).get("details", [])
            for detail in details:
                delay_str = str(detail.get("retryDelay", ""))
                if delay_str:
                    m = re.search(r"\d+", delay_str)
                    if m:
                        wait = int(m.group())
                        break
        except Exception:
            pass
        raise RateLimitError(wait)

    if resp.status_code != 200:
        msg = ""
        try:
            msg = resp.json().get("error", {}).get("message", "")
        except Exception:
            pass
        raise Exception(f"HTTP {resp.status_code}: {msg}")

    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"^```(?:python)?\s*\n?", "", text.strip())
    text = re.sub(r"\n?```\s*$", "", text.strip())
    return text.strip()


def call_gemini(exercise_text, number, api_key, preferred):
    prompt = (
        f"Ban la tro ly lap trinh Python cho sinh vien.\n"
        f"Hay viet code Python HOAN CHINH, CHAY DUOC de giai bai sau.\n\n"
        f"YEU CAU:\n"
        f"- Chi tra ve CODE PYTHON THUAN TUY\n"
        f"- KHONG co markdown, KHONG co ```python\n"
        f"- Dong dau: # Bai{number}.py\n"
        f"- Dung input() neu de yeu cau nhap lieu\n"
        f"- Comment tieng Viet, xu ly truong hop dac biet\n\n"
        f"DE BAI:\n{exercise_text}\n\n"
        f"Chi tra ve CODE PYTHON:"
    )

    ordered = [preferred] + [m for m in MODELS if m != preferred]
    # Free tier Gemini gioi han 15 req/phut, reset sau 60 giay
    MIN_WAIT = [65, 90, 120]

    for model in ordered:
        dm(f"[model: {model}]")
        for attempt in range(3):
            try:
                code = gemini_request(api_key, model, prompt)
                return code
            except RateLimitError as e:
                wait = max(e.server_wait if e.server_wait > 0 else 0, MIN_WAIT[attempt])
                print(f"\n  {C.YLW}!{C.RST}  Rate limit [{model}] - lan {attempt+1}/3")
                countdown(wait, "Reset quota Gemini")
                continue
            except Exception:
                raise  # loi khac -> throw ngay
        wn(f"{model} van bi gioi han -> thu model tiep theo...")

    raise Exception("Tat ca model deu bi rate-limit. Thu lai sau vai phut.")

# ══════════════════════════════════════════
#  GITHUB
# ══════════════════════════════════════════
def gh_hdr(token):
    return {"Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"}

def gh_sha(path, cfg):
    url = f"https://api.github.com/repos/{cfg['GITHUB_USER']}/{cfg['GITHUB_REPO']}/contents/{path}"
    r = requests.get(url, headers=gh_hdr(cfg["GITHUB_TOKEN"]), timeout=10)
    return r.json().get("sha") if r.status_code == 200 else None

def unique_gh(base, cfg):
    if not gh_sha(base, cfg):
        return base
    dot  = base.rfind(".")
    stem = base[:dot]
    ext  = base[dot:]
    for i in range(1, 200):
        p = f"{stem}_{i}{ext}"
        if not gh_sha(p, cfg):
            return p
    return f"{stem}_{int(time.time())}{ext}"

def push_gh(path, code, cfg):
    url = f"https://api.github.com/repos/{cfg['GITHUB_USER']}/{cfg['GITHUB_REPO']}/contents/{path}"
    sha = gh_sha(path, cfg)
    payload = {
        "message": f"Add {Path(path).name} [auto-solver {datetime.now().strftime('%Y-%m-%d %H:%M')}]",
        "content": base64.b64encode(code.encode("utf-8")).decode("utf-8"),
        "branch":  cfg["GITHUB_BRANCH"],
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=gh_hdr(cfg["GITHUB_TOKEN"]), json=payload, timeout=15)
    r.raise_for_status()
    return r.json()["content"]["html_url"]

# ══════════════════════════════════════════
#  PIPELINE
# ══════════════════════════════════════════
def run(raw, cfg, dry):
    exercises = parse(raw)
    if not exercises:
        er("Khong tim thay bai tap nao!")
        nf("Dinh dang: 'Bai 4:', 'Bai4:', 'Exercise 4:', 'Cau 4:'")
        return

    show_exercises(exercises)
    nums  = list(exercises.keys())
    total = len(nums)

    if dry:
        wn("DRY RUN - chi sinh code, khong day GitHub")
    else:
        ans = input(f"\n  {C.BOLD}Xu ly {C.CYAN}{total}{C.RST}{C.BOLD} bai? [Y/n]: {C.RST}").strip().lower()
        if ans == "n":
            wn("Da huy."); return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    preferred = cfg.get("GEMINI_MODEL", "gemini-2.0-flash")
    results   = []
    PAUSE     = 25  # giay giua cac bai

    for i, num in enumerate(nums):
        content   = exercises[num]
        base_name = f"Bai{num}.py"

        if i > 0:
            countdown(PAUSE, "Nghi giua bai")

        print()
        print(f"  {C.BOLD}{C.WHT}[{i+1}/{total}] Bai {num}{C.RST}  {C.DIM}{base_name}{C.RST}")
        sep()

        nf("Goi Gemini AI sinh code...")
        try:
            code = call_gemini(content, num, cfg["GEMINI_API_KEY"], preferred)
            ok(f"Sinh duoc {len(code.splitlines())} dong code")
        except Exception as e:
            er(f"Loi Gemini: {e}")
            results.append({"num": num, "file": base_name, "status": "GEMINI_ERROR"})
            continue

        local = OUTPUT_DIR / base_name
        c = 1
        while local.exists():
            local = OUTPUT_DIR / f"Bai{num}_{c}.py"; c += 1
        local.write_text(code, encoding="utf-8")
        ok(f"Luu local: {C.CYAN}{local}{C.RST}")

        if dry:
            wn("Dry run - bo qua GitHub")
            results.append({"num": num, "file": local.name, "status": "LOCAL_ONLY"})
            continue

        nf("Kiem tra file trung tren GitHub...")
        base_gh  = f"{cfg['OUTPUT_FOLDER']}/{base_name}"
        final_gh = unique_gh(base_gh, cfg)
        fname    = Path(final_gh).name
        if fname != base_name:
            wn(f"Doi ten -> {C.YLW}{fname}{C.RST}")

        nf(f"Day len {final_gh} ...")
        try:
            url = push_gh(final_gh, code, cfg)
            ok(f"GitHub: {C.CYAN}{url}{C.RST}")
            results.append({"num": num, "file": fname, "status": "OK", "url": url})
        except Exception as e:
            er(f"Loi GitHub: {e}")
            results.append({"num": num, "file": local.name, "status": "GITHUB_ERROR"})

    print(); sep("=")
    print(f"\n  {C.BOLD}KET QUA TONG KET{C.RST}"); sep()
    for r in results:
        if r["status"] == "OK":
            print(f"  {C.GRN}+{C.RST}  Bai {r['num']}  ->  {r['file']}  {C.DIM}{r.get('url','')[:55]}{C.RST}")
        elif r["status"] == "LOCAL_ONLY":
            print(f"  {C.YLW}>{C.RST}  Bai {r['num']}  ->  {r['file']}  {C.DIM}(local only){C.RST}")
        else:
            print(f"  {C.RED}x{C.RST}  Bai {r['num']}  ->  {r['file']}  {C.RED}[{r['status']}]{C.RST}")
    sep()
    ok_c = sum(1 for r in results if r["status"]=="OK")
    lo_c = sum(1 for r in results if r["status"]=="LOCAL_ONLY")
    er_c = sum(1 for r in results if "ERROR" in r["status"])
    print(f"  {C.GRN}GitHub: {ok_c}{C.RST}  |  {C.YLW}Local: {lo_c}{C.RST}  |  {C.RED}Loi: {er_c}{C.RST}  |  Tong: {total}")
    print(f"\n  Thu muc local: {C.CYAN}{OUTPUT_DIR}{C.RST}\n")

# ══════════════════════════════════════════
#  CAU HINH WIZARD
# ══════════════════════════════════════════
def setup(cfg):
    clear(); header()
    print(f"  {C.BOLD}CAU HINH{C.RST}"); sep()
    print(f"  {C.DIM}Bo trong = giu nguyen{C.RST}\n")

    fields = [
        ("GEMINI_API_KEY", "Gemini API Key",     "aistudio.google.com/app/apikey",              True),
        ("GITHUB_TOKEN",   "GitHub Token",        "github.com/settings/tokens -> tick repo",     True),
        ("GITHUB_USER",    "GitHub Username",     "",                                            False),
        ("GITHUB_REPO",    "GitHub Repo name",    "",                                            False),
        ("GITHUB_BRANCH",  "Branch",              "mac dinh: main",                              False),
        ("OUTPUT_FOLDER",  "Thu muc trong repo",  "mac dinh: baitap",                            False),
    ]
    for key, label, hint, secret in fields:
        cur  = cfg.get(key, "")
        disp = ("*"*min(len(cur),12)+"...") if secret and cur else (cur or "(trong)")
        if hint: dm(hint)
        v = input(f"  {C.BOLD}{label}{C.RST} [{disp}]: ").strip()
        if v: cfg[key] = v
        print()

    cur_model = cfg.get("GEMINI_MODEL", "gemini-2.0-flash")
    print(f"  {C.BOLD}Gemini Model{C.RST} {C.DIM}(1.5-flash khuyen dung cho free tier):{C.RST}")
    for i, m in enumerate(MODELS, 1):
        dot = f"{C.GRN}*{C.RST}" if m == cur_model else " "
        print(f"    {dot} [{i}] {m}")
    ch = input(f"  Chon [1-{len(MODELS)}, Enter=giu nguyen]: ").strip()
    if ch.isdigit() and 1 <= int(ch) <= len(MODELS):
        cfg["GEMINI_MODEL"] = MODELS[int(ch)-1]
    print()
    save_cfg(cfg)
    ok("Da luu vao .env")
    return cfg

# ══════════════════════════════════════════
#  KIEM TRA KET NOI
# ══════════════════════════════════════════
def check(cfg):
    print(); print(f"  {C.BOLD}KIEM TRA KET NOI{C.RST}"); sep()
    nf("Kiem tra Gemini API...")
    try:
        r = requests.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={cfg['GEMINI_API_KEY']}",
            timeout=10)
        if r.status_code == 200:
            names = [m["name"].split("/")[-1] for m in r.json().get("models", [])[:3]]
            ok(f"Gemini hoat dong. Models: {', '.join(names)}")
        else:
            er(f"Gemini: HTTP {r.status_code}")
    except Exception as e:
        er(f"Gemini: {e}")

    nf("Kiem tra GitHub...")
    try:
        r = requests.get(
            f"https://api.github.com/repos/{cfg['GITHUB_USER']}/{cfg['GITHUB_REPO']}",
            headers=gh_hdr(cfg["GITHUB_TOKEN"]), timeout=10)
        if r.status_code == 200:
            d = r.json()
            ok(f"GitHub: {d['full_name']} ({d['visibility']})")
        elif r.status_code == 404:
            er("Repo khong ton tai hoac token thieu quyen")
        elif r.status_code == 401:
            er("Token khong hop le")
        else:
            er(f"HTTP {r.status_code}")
    except Exception as e:
        er(f"GitHub: {e}")
    print()

# ══════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════
def main():
    cfg = load_cfg()
    while True:
        clear(); header()
        ch = main_menu(cfg)

        if ch == "1":
            clear(); header()
            print(f"  {C.BOLD}NHAP DE BAI TU BAN PHIM{C.RST}"); sep()
            print(f"\n  {C.DIM}Nhap de bai (go END o dong moi de ket thuc):{C.RST}\n")
            lines = []
            while True:
                try:
                    ln = input()
                except (EOFError, KeyboardInterrupt):
                    break
                if ln.strip().upper() == "END":
                    break
                lines.append(ln)
            raw = "\n".join(lines)
            if not raw.strip():
                wn("Khong co noi dung."); input("\n  Enter..."); continue
            dry = input(f"\n  {C.BOLD}Dry run (khong day GitHub)? [y/N]: {C.RST}").strip().lower() == "y"
            run(raw, cfg, dry)
            input(f"  {C.DIM}Enter de quay ve menu...{C.RST}")

        elif ch == "2":
            clear(); header()
            print(f"  {C.BOLD}DOC DE BAI TU FILE{C.RST}"); sep()
            p  = input(f"\n  {C.BOLD}Duong dan file{C.RST} (Enter = debai.txt): ").strip() or "debai.txt"
            fp = Path(p) if Path(p).is_absolute() else Path(__file__).parent / p
            if not fp.exists():
                er(f"Khong tim thay: {fp}"); input("\n  Enter..."); continue
            raw = fp.read_text(encoding="utf-8")
            ok(f"Doc {fp} ({len(raw)} ky tu)")
            dry = input(f"\n  {C.BOLD}Dry run (khong day GitHub)? [y/N]: {C.RST}").strip().lower() == "y"
            run(raw, cfg, dry)
            input(f"  {C.DIM}Enter de quay ve menu...{C.RST}")

        elif ch == "3":
            cfg = setup(cfg); input(f"\n  {C.DIM}Enter...{C.RST}")

        elif ch == "4":
            clear(); header(); check(cfg); input(f"  {C.DIM}Enter...{C.RST}")

        elif ch == "0":
            clear(); print(f"\n  {C.DIM}Tam biet!{C.RST}\n"); sys.exit(0)

if __name__ == "__main__":
    main()
