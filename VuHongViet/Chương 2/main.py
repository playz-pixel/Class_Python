#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════╗
║     AUTO HOMEWORK SOLVER  v1.0           ║
║     Gemini AI  →  Python  →  GitHub      ║
╚══════════════════════════════════════════╝
Chạy: python main.py
"""

import os, re, sys, base64, json, textwrap, time
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("Thiếu thư viện requests. Chạy:  pip install requests")
    sys.exit(1)

# ══════════════════════════════════════════
#  MÀU SẮC ANSI
# ══════════════════════════════════════════
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    BLUE   = "\033[34m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    WHITE  = "\033[97m"
    BG_BLUE   = "\033[44m"
    BG_BLACK  = "\033[40m"

def ok(msg):    print(f"  {C.GREEN}✓{C.RESET}  {msg}")
def err(msg):   print(f"  {C.RED}✗{C.RESET}  {msg}")
def warn(msg):  print(f"  {C.YELLOW}⚠{C.RESET}  {msg}")
def info(msg):  print(f"  {C.CYAN}→{C.RESET}  {msg}")
def dim(msg):   print(f"  {C.DIM}{msg}{C.RESET}")
def sep(char="─", width=54): print(f"  {C.DIM}{char*width}{C.RESET}")

# ══════════════════════════════════════════
#  FILE CẤU HÌNH
# ══════════════════════════════════════════
CONFIG_FILE = Path(__file__).parent / ".env"
OUTPUT_DIR  = Path(__file__).parent / "baitap"

def load_config() -> dict:
    cfg = {
        "GEMINI_API_KEY": "",
        "GITHUB_TOKEN":   "",
        "GITHUB_USER":    "",
        "GITHUB_REPO":    "",
        "GITHUB_BRANCH":  "main",
        "OUTPUT_FOLDER":  "baitap",
    }
    # Đọc từ .env nếu có
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                cfg[k.strip()] = v.strip()
    # Override từ biến môi trường
    for k in cfg:
        if os.getenv(k):
            cfg[k] = os.getenv(k)
    return cfg

def save_config(cfg: dict):
    lines = ["# Auto Homework Solver — Cấu hình\n"]
    for k, v in cfg.items():
        lines.append(f"{k}={v}\n")
    CONFIG_FILE.write_text("".join(lines), encoding="utf-8")

# ══════════════════════════════════════════
#  HEADER & MENU
# ══════════════════════════════════════════
def clear(): os.system("cls" if os.name == "nt" else "clear")

def header():
    print()
    print(f"  {C.BG_BLUE}{C.WHITE}{C.BOLD}  AUTO HOMEWORK SOLVER  {C.RESET}  {C.DIM}v1.0{C.RESET}")
    print(f"  {C.DIM}Gemini AI → Python Code → GitHub{C.RESET}")
    sep("═")
    print()

def menu_main(cfg: dict) -> str:
    gemini_ok = "✓" if cfg.get("GEMINI_API_KEY") else "✗"
    github_ok = "✓" if (cfg.get("GITHUB_TOKEN") and cfg.get("GITHUB_USER") and cfg.get("GITHUB_REPO")) else "✗"
    gemini_c  = C.GREEN if cfg.get("GEMINI_API_KEY") else C.RED
    github_c  = C.GREEN if github_ok == "✓" else C.RED

    print(f"  {C.BOLD}MENU CHÍNH{C.RESET}")
    sep()
    print(f"  {C.CYAN}[1]{C.RESET}  Nhập đề bài từ bàn phím")
    print(f"  {C.CYAN}[2]{C.RESET}  Đọc đề bài từ file .txt")
    print(f"  {C.CYAN}[3]{C.RESET}  Cấu hình API Keys & GitHub")
    print(f"  {C.CYAN}[4]{C.RESET}  Kiểm tra kết nối")
    print(f"  {C.CYAN}[0]{C.RESET}  Thoát")
    sep()
    print(f"  Gemini: {gemini_c}{gemini_ok}{C.RESET}  |  GitHub: {github_c}{github_ok}{C.RESET}  |  Repo: {C.DIM}{cfg.get('GITHUB_USER','?')}/{cfg.get('GITHUB_REPO','?')}{C.RESET}")
    print()
    return input(f"  {C.BOLD}Chọn [{C.CYAN}0-4{C.RESET}{C.BOLD}]{C.RESET}: ").strip()

# ══════════════════════════════════════════
#  NHẬP ĐỀ BÀI
# ══════════════════════════════════════════
def input_multiline() -> str:
    """Nhập nhiều dòng, kết thúc bằng dòng trống liên tiếp hoặc 'END'."""
    print(f"\n  {C.DIM}Nhập đề bài (gõ {C.YELLOW}END{C.DIM} ở dòng mới để kết thúc):{C.RESET}\n")
    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)

def input_from_file() -> tuple[str, str]:
    """Nhập đường dẫn file, đọc nội dung."""
    print()
    path_str = input(f"  {C.BOLD}Đường dẫn file .txt{C.RESET} (Enter = debai.txt): ").strip()
    if not path_str:
        path_str = "debai.txt"
    path = Path(path_str)
    if not path.is_absolute():
        path = Path(__file__).parent / path
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy: {path}")
    content = path.read_text(encoding="utf-8")
    return content, str(path)

# ══════════════════════════════════════════
#  PARSE ĐỀ BÀI
# ══════════════════════════════════════════
def parse_exercises(raw: str) -> dict[str, str]:
    pattern = re.compile(
        r'(?:Bài|Bai|Exercise|Câu|Cau|Problem)\s*(\d+)\s*[:\.\-]',
        re.IGNORECASE
    )
    matches = list(pattern.finditer(raw))
    if not matches:
        return {}
    result = {}
    for i, m in enumerate(matches):
        num   = m.group(1)
        start = m.start()
        end   = matches[i+1].start() if i+1 < len(matches) else len(raw)
        result[num] = raw[start:end].strip()
    return result

def preview_exercises(exercises: dict):
    print()
    print(f"  {C.BOLD}Tìm thấy {C.GREEN}{len(exercises)}{C.RESET}{C.BOLD} bài tập:{C.RESET}")
    sep()
    for num, content in exercises.items():
        preview = content.replace('\n', ' ')[:70]
        dots = "..." if len(content) > 70 else ""
        print(f"  {C.CYAN}Bài {num}{C.RESET}  {C.DIM}{preview}{dots}{C.RESET}")
    sep()

# ══════════════════════════════════════════
#  GEMINI API
# ══════════════════════════════════════════
def call_gemini(exercise_text: str, number: str, api_key: str) -> str:
    prompt = f"""Bạn là trợ lý lập trình Python cho sinh viên.
Hãy viết code Python HOÀN CHỈNH và CHẠY ĐƯỢC để giải bài tập sau.

YÊU CẦU:
- Chỉ trả về CODE PYTHON THUẦN TÚY
- KHÔNG có markdown, KHÔNG có ```python, KHÔNG có giải thích ngoài code
- Đầu file: # Bai{number}.py — mô tả ngắn
- Có input() nếu đề bài yêu cầu nhập liệu
- Comment tiếng Việt giải thích từng bước
- Xử lý trường hợp đặc biệt (delta âm, chia 0, v.v.)

ĐỀ BÀI:
{exercise_text}

Chỉ trả về CODE PYTHON, không thêm bất kỳ văn bản nào khác."""

    # Thử lần lượt các model, fallback nếu bị rate-limit
    MODELS = [
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
    ]
    MAX_RETRIES = 4
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
    }

    last_err = None
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 429:
                    # Lấy thời gian retry-after nếu có, không thì tăng dần
                    retry_after = int(resp.headers.get("Retry-After", 0))
                    wait = retry_after if retry_after > 0 else (attempt * 15)
                    print(f"\r  {C.YELLOW}⚠{C.RESET}  [{model}] Rate limit — chờ {wait}s (lần {attempt}/{MAX_RETRIES})...  ", end="", flush=True)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                code = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                code = re.sub(r"^```(?:python)?\n?", "", code.strip(), flags=re.MULTILINE)
                code = re.sub(r"\n?```$", "", code.strip(), flags=re.MULTILINE)
                if model != "gemini-2.0-flash":
                    print(f"\r  {C.DIM}(dùng fallback model: {model}){C.RESET}          ")
                return code.strip()
            except Exception as e:
                last_err = e
                if "429" not in str(e):
                    raise  # Lỗi khác thì throw luôn
        # Hết retry cho model này → thử model tiếp theo
        print(f"\r  {C.YELLOW}⚠{C.RESET}  {model} vẫn bị rate-limit → thử model khác...  ")

    raise Exception(f"Tất cả model đều bị rate-limit: {last_err}")

# ══════════════════════════════════════════
#  GITHUB API
# ══════════════════════════════════════════
def gh_headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

def gh_file_sha(path: str, cfg: dict) -> str | None:
    url = f"https://api.github.com/repos/{cfg['GITHUB_USER']}/{cfg['GITHUB_REPO']}/contents/{path}"
    r = requests.get(url, headers=gh_headers(cfg["GITHUB_TOKEN"]), timeout=10)
    return r.json().get("sha") if r.status_code == 200 else None

def get_unique_gh_path(base_path: str, cfg: dict) -> str:
    if not gh_file_sha(base_path, cfg):
        return base_path
    stem = base_path[:base_path.rfind(".")]
    ext  = base_path[base_path.rfind("."):]
    for i in range(1, 100):
        candidate = f"{stem}_{i}{ext}"
        if not gh_file_sha(candidate, cfg):
            return candidate
    return f"{stem}_{int(time.time())}{ext}"

def push_to_github(file_path: str, code: str, cfg: dict) -> str:
    url = f"https://api.github.com/repos/{cfg['GITHUB_USER']}/{cfg['GITHUB_REPO']}/contents/{file_path}"
    sha = gh_file_sha(file_path, cfg)
    payload = {
        "message": f"Add {Path(file_path).name} [auto-solver {datetime.now().strftime('%Y-%m-%d %H:%M')}]",
        "content": base64.b64encode(code.encode("utf-8")).decode("utf-8"),
        "branch":  cfg["GITHUB_BRANCH"],
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=gh_headers(cfg["GITHUB_TOKEN"]), json=payload, timeout=15)
    r.raise_for_status()
    return r.json()["content"]["html_url"]

# ══════════════════════════════════════════
#  PROGRESS BAR
# ══════════════════════════════════════════
def progress_bar(current: int, total: int, label: str = "", width: int = 40):
    pct   = int(current / total * 100) if total else 0
    filled= int(width * current / total) if total else 0
    bar   = "█" * filled + "░" * (width - filled)
    print(f"\r  {C.CYAN}{bar}{C.RESET} {pct:>3}%  {C.DIM}{label[:30]:<30}{C.RESET}", end="", flush=True)

# ══════════════════════════════════════════
#  PIPELINE CHÍNH
# ══════════════════════════════════════════
def run_pipeline(raw_text: str, cfg: dict, dry_run: bool = False):
    exercises = parse_exercises(raw_text)
    if not exercises:
        err("Không tìm thấy bài tập nào!")
        info("Định dạng hỗ trợ: 'Bài 4:', 'Bai4:', 'Exercise 4:', 'Câu 4:'")
        return

    preview_exercises(exercises)

    # Xác nhận
    nums  = list(exercises.keys())
    total = len(nums)

    if dry_run:
        warn("Chế độ DRY RUN — chỉ sinh code, không đẩy GitHub")
    else:
        yesno = input(f"\n  {C.BOLD}Tiến hành xử lý {C.CYAN}{total}{C.RESET}{C.BOLD} bài? [Y/n]{C.RESET}: ").strip().lower()
        if yesno == "n":
            warn("Đã hủy.")
            return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print()
    sep("═")

    results = []
    DELAY_BETWEEN = 4  # giây chờ giữa các bài để tránh rate-limit

    for i, num in enumerate(nums):
        content   = exercises[num]
        base_name = f"Bai{num}.py"

        # Countdown giữa các bài (bỏ qua bài đầu)
        if i > 0:
            for remaining in range(DELAY_BETWEEN, 0, -1):
                print(f"\r  {C.DIM}Chờ {remaining}s trước bài tiếp theo...{C.RESET}   ", end="", flush=True)
                time.sleep(1)
            print("\r" + " "*55 + "\r", end="")

        print()
        print(f"  {C.BOLD}{C.WHITE}[{i+1}/{total}] Bài {num}{C.RESET}  {C.DIM}{base_name}{C.RESET}")
        sep()

        # ── Gemini ──
        info("Gọi Gemini AI sinh code...")
        try:
            code = call_gemini(content, num, cfg["GEMINI_API_KEY"])
            ok(f"Sinh được {len(code.splitlines())} dòng code")
        except Exception as e:
            err(f"Lỗi Gemini: {e}")
            results.append({"num": num, "file": base_name, "status": "GEMINI_ERROR"})
            continue

        # ── Lưu local ──
        local_path = OUTPUT_DIR / base_name
        counter = 1
        while local_path.exists():
            local_path = OUTPUT_DIR / f"Bai{num}_{counter}.py"
            counter += 1
        local_path.write_text(code, encoding="utf-8")
        ok(f"Lưu local: {C.CYAN}{local_path}{C.RESET}")

        if dry_run:
            warn("Dry run — bỏ qua GitHub")
            results.append({"num": num, "file": local_path.name, "status": "LOCAL_ONLY"})
            continue

        # ── GitHub ──
        info("Kiểm tra file trùng trên GitHub...")
        base_gh   = f"{cfg['OUTPUT_FOLDER']}/{base_name}"
        final_gh  = get_unique_gh_path(base_gh, cfg)
        final_name = Path(final_gh).name

        if final_name != base_name:
            warn(f"File đã tồn tại → đổi thành {C.YELLOW}{final_name}{C.RESET}")

        info(f"Đang đẩy {final_gh}...")
        try:
            gh_url = push_to_github(final_gh, code, cfg)
            ok(f"GitHub: {C.CYAN}{gh_url}{C.RESET}")
            results.append({"num": num, "file": final_name, "status": "OK", "url": gh_url})
        except Exception as e:
            err(f"Lỗi GitHub: {e}")
            results.append({"num": num, "file": local_path.name, "status": "GITHUB_ERROR"})

        progress_bar(i+1, total, f"Bài {num} xong")

    # ── Tóm tắt ──
    print("\n")
    sep("═")
    print(f"\n  {C.BOLD}KẾT QUẢ TỔNG KẾT{C.RESET}")
    sep()
    for r in results:
        if r["status"] == "OK":
            print(f"  {C.GREEN}✓{C.RESET}  Bài {r['num']}  →  {r['file']}  →  {C.DIM}{r.get('url','')[:60]}{C.RESET}")
        elif r["status"] == "LOCAL_ONLY":
            print(f"  {C.YELLOW}→{C.RESET}  Bài {r['num']}  →  {r['file']}  {C.DIM}(chỉ local){C.RESET}")
        else:
            print(f"  {C.RED}✗{C.RESET}  Bài {r['num']}  →  {r['file']}  {C.RED}[{r['status']}]{C.RESET}")

    ok_count = sum(1 for r in results if r["status"] == "OK")
    lo_count = sum(1 for r in results if r["status"] == "LOCAL_ONLY")
    er_count = sum(1 for r in results if "ERROR" in r["status"])
    sep()
    print(f"  {C.GREEN}✓ GitHub: {ok_count}{C.RESET}  |  {C.YELLOW}Local: {lo_count}{C.RESET}  |  {C.RED}Lỗi: {er_count}{C.RESET}  |  Tổng: {total}")
    print(f"\n  Thư mục local: {C.CYAN}{OUTPUT_DIR}{C.RESET}")
    print()

# ══════════════════════════════════════════
#  CẤU HÌNH WIZARD
# ══════════════════════════════════════════
def setup_config(cfg: dict) -> dict:
    clear()
    header()
    print(f"  {C.BOLD}CẤU HÌNH API KEYS & GITHUB{C.RESET}")
    sep()
    print(f"  {C.DIM}Bỏ trống để giữ nguyên giá trị hiện tại{C.RESET}\n")

    fields = [
        ("GEMINI_API_KEY", "Gemini API Key", "aistudio.google.com/app/apikey", True),
        ("GITHUB_TOKEN",   "GitHub Token",   "github.com/settings/tokens → tick 'repo'", True),
        ("GITHUB_USER",    "GitHub Username","", False),
        ("GITHUB_REPO",    "GitHub Repo",    "Tên repo (không cần URL đầy đủ)", False),
        ("GITHUB_BRANCH",  "Branch",         "Mặc định: main", False),
        ("OUTPUT_FOLDER",  "Thư mục GitHub", "Thư mục lưu file trong repo", False),
    ]

    for key, label, hint, is_secret in fields:
        current = cfg.get(key, "")
        display = ("*" * min(len(current), 12) + "...") if is_secret and current else (current or C.DIM + "(trống)" + C.RESET)
        if hint:
            dim(f"{hint}")
        val = input(f"  {C.BOLD}{label}{C.RESET} [{display}]: ").strip()
        if val:
            cfg[key] = val
        print()

    save_config(cfg)
    ok("Đã lưu cấu hình vào .env")
    return cfg

# ══════════════════════════════════════════
#  KIỂM TRA KẾT NỐI
# ══════════════════════════════════════════
def check_connections(cfg: dict):
    print()
    print(f"  {C.BOLD}KIỂM TRA KẾT NỐI{C.RESET}")
    sep()

    # Gemini
    info("Kiểm tra Gemini API...")
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={cfg['GEMINI_API_KEY']}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            ok(f"Gemini API hoạt động ✓")
        else:
            err(f"Gemini: HTTP {r.status_code} — {r.json().get('error',{}).get('message','?')}")
    except Exception as e:
        err(f"Gemini: {e}")

    # GitHub
    info("Kiểm tra GitHub repo...")
    try:
        url = f"https://api.github.com/repos/{cfg['GITHUB_USER']}/{cfg['GITHUB_REPO']}"
        r = requests.get(url, headers=gh_headers(cfg["GITHUB_TOKEN"]), timeout=10)
        if r.status_code == 200:
            d = r.json()
            ok(f"GitHub: {d['full_name']} ({d['visibility']}) — branch mặc định: {d['default_branch']}")
        elif r.status_code == 404:
            err(f"GitHub: Repo không tồn tại hoặc token không có quyền truy cập")
        elif r.status_code == 401:
            err(f"GitHub: Token không hợp lệ")
        else:
            err(f"GitHub: HTTP {r.status_code}")
    except Exception as e:
        err(f"GitHub: {e}")

    print()

# ══════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════
def main():
    cfg = load_config()

    while True:
        clear()
        header()
        choice = menu_main(cfg)

        # ── Nhập tay ──
        if choice == "1":
            clear(); header()
            print(f"  {C.BOLD}NHẬP ĐỀ BÀI TỪ BÀN PHÍM{C.RESET}")
            sep()
            raw = input_multiline()
            if not raw.strip():
                warn("Không có nội dung."); input("\n  Enter để tiếp tục..."); continue

            dry = input(f"\n  {C.BOLD}Dry run (không đẩy GitHub)? [y/N]{C.RESET}: ").strip().lower() == "y"
            run_pipeline(raw, cfg, dry_run=dry)
            input(f"  {C.DIM}Enter để quay về menu...{C.RESET}")

        # ── Đọc file ──
        elif choice == "2":
            clear(); header()
            print(f"  {C.BOLD}ĐỌC ĐỀ BÀI TỪ FILE{C.RESET}")
            sep()
            try:
                raw, fpath = input_from_file()
                ok(f"Đọc file: {fpath} ({len(raw)} ký tự)")
            except FileNotFoundError as e:
                err(str(e)); input("\n  Enter để tiếp tục..."); continue
            except Exception as e:
                err(f"Lỗi đọc file: {e}"); input("\n  Enter để tiếp tục..."); continue

            dry = input(f"\n  {C.BOLD}Dry run (không đẩy GitHub)? [y/N]{C.RESET}: ").strip().lower() == "y"
            run_pipeline(raw, cfg, dry_run=dry)
            input(f"  {C.DIM}Enter để quay về menu...{C.RESET}")

        # ── Cấu hình ──
        elif choice == "3":
            cfg = setup_config(cfg)
            input(f"\n  {C.DIM}Enter để quay về menu...{C.RESET}")

        # ── Kiểm tra kết nối ──
        elif choice == "4":
            clear(); header()
            check_connections(cfg)
            input(f"  {C.DIM}Enter để quay về menu...{C.RESET}")

        # ── Thoát ──
        elif choice == "0":
            clear()
            print(f"\n  {C.DIM}Tạm biệt!{C.RESET}\n")
            sys.exit(0)

        else:
            warn("Lựa chọn không hợp lệ.")
            time.sleep(0.8)


if __name__ == "__main__":
    main()
