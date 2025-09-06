#!/usr/bin/env python3
"""
ListMan v1
----------
Author : CySec Don
Email  : cysecdon@proton.me
Version: 1.0

Description:
    ListMan is a Wordlist Manager that unifies multiple password lists
    into a single master wordlist.
"""

import argparse
import os
import glob
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import signal
import sys
import json
import gzip
import bz2
from colorama import init, Fore, Style
import random

# Initialize colorama
init(autoreset=True)

__program__ = "ListMan"
__author__ = "CySec Don"
__email__ = "cysecdon@proton.me"
__version__ = "1.0"
__license__ = "MIT License"

MASTER_FILE = "master_wordlist.txt"
LOG_FILE = "listman.log"
RESUME_FILE = "resume_state.json"

should_exit = False

# Available colors for random rotation
COLORS = [Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.RED]

# -------------------- Signal Handler --------------------
def signal_handler(sig, frame):
    global should_exit
    print("\n[!] Pause requested. Saving state...")
    should_exit = True

signal.signal(signal.SIGINT, signal_handler)

# -------------------- Banner & Logo --------------------
def ascii_logo():
    """Return colored ASCII logo with random color"""
    color = random.choice(COLORS)
    logo = f"""
{color}{Style.BRIGHT}██╗     ██╗███████╗████████╗███╗   ███╗ █████╗ ███╗   ██╗
{color}{Style.BRIGHT}██║     ██║██╔════╝╚══██╔══╝████╗ ████║██╔══██╗████╗  ██║
{color}{Style.BRIGHT}██║     ██║███████╗   ██║   ██╔████╔██║███████║██╔██╗ ██║
{color}{Style.BRIGHT}██║     ██║╚════██║   ██║   ██║╚██╔╝██║██╔══██║██║╚██╗██║
{color}{Style.BRIGHT}███████╗██║███████║   ██║   ██║ ╚═╝ ██║██║  ██║██║ ╚████║
{color}{Style.BRIGHT}╚══════╝╚═╝╚══════╝   ╚═╝   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
"""
    return logo

def banner():
    """Return the full about banner"""
    return f"""{ascii_logo()}
{Fore.CYAN}{Style.BRIGHT}{__program__} v{__version__}{Style.RESET_ALL}
Author : {__author__}
Email  : {__email__}
License: {__license__}

{Fore.YELLOW}Description:{Style.RESET_ALL}
    ListMan unifies multiple wordlists into a single master wordlist.
    It supports multi-threading, logging, pause/resume, and compression.

{Fore.YELLOW}Basic Usage:{Style.RESET_ALL}
    Create new master wordlist from files:
        python listman.py --create file1.txt file2.txt --threads 8

    Create from folder of .txt wordlists:
        python listman.py --create-folder /path/to/lists --compress gzip

    Add new lists to existing master:
        python listman.py --add newlist.txt --log --skip-logged

    Resume after interruption:
        python listman.py --create-folder ./lists --resume

    Show version:
        python listman.py --version

    Show this banner:
        python listman.py --about
"""

# -------------------- Logging & Resume --------------------
def log_action(log_path, action, path, word_count):
    with open(log_path, "a") as logfile:
        logfile.write(f"{datetime.now().isoformat()} | {action:<6} | {path} | {word_count} words\n")

def load_logged_files(log_path):
    if not log_path or not os.path.exists(log_path):
        return set()
    logged = set()
    with open(log_path, "r") as logfile:
        for line in logfile:
            parts = line.strip().split("|")
            if len(parts) >= 3:
                path = parts[2].strip()
                logged.add(path)
    return logged

def save_resume_state(pending_files):
    with open(RESUME_FILE, "w") as f:
        json.dump(pending_files, f)
    print(f"[+] Saved resume state with {len(pending_files)} pending files.")

def load_resume_state():
    if os.path.exists(RESUME_FILE):
        with open(RESUME_FILE, "r") as f:
            return json.load(f)
    return None

# -------------------- Word Collection --------------------
def collect_words_from_file(path, log_path=None, action=None):
    global should_exit
    words = set()
    try:
        with open(path, "r", errors="ignore") as infile:
            total = sum(1 for _ in infile)
        with open(path, "r", errors="ignore") as infile:
            for line in tqdm(infile, total=total, desc=f"Processing {os.path.basename(path)}", leave=False):
                if should_exit:
                    break
                word = line.strip()
                if word:
                    words.add(word)
        if log_path and action and not should_exit:
            log_action(log_path, action, path, len(words))
    except Exception as e:
        print(f"[-] Error reading {path}: {e}")
    return words

def collect_words_from_inputs(files, folders, threads, log_path=None, action=None, skip_logged=False, resume=False):
    all_files = []

    if files:
        for f in files:
            if os.path.isfile(f):
                all_files.append(f)
            else:
                print(f"[-] File not found: {f}")

    if folders:
        for folder in folders:
            if os.path.isdir(folder):
                all_files.extend(glob.glob(os.path.join(folder, "*.txt")))
            else:
                print(f"[-] Folder not found: {folder}")

    if not all_files:
        return set()

    if skip_logged and log_path:
        logged = load_logged_files(log_path)
        all_files = [f for f in all_files if f not in logged]
        print(f"[+] Skipping {len(logged)} already logged files. {len(all_files)} left.")

    if resume:
        pending = load_resume_state()
        if pending:
            print(f"[+] Resuming from saved state with {len(pending)} files...")
            all_files = pending

    words = set()
    print(f"[+] Processing {len(all_files)} file(s) with {threads} thread(s)...")
    remaining = list(all_files)

    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(collect_words_from_file, f, log_path, action): f for f in all_files}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Merging results"):
                if should_exit:
                    break
                words |= future.result()
    except KeyboardInterrupt:
        pass

    if should_exit:
        unfinished = [f for f in remaining if f not in load_logged_files(log_path)]
        save_resume_state(unfinished)
        sys.exit(0)

    if os.path.exists(RESUME_FILE):
        os.remove(RESUME_FILE)

    return words

# -------------------- Save Master --------------------
def save_master(words, compress=None):
    if compress == "gzip":
        out_file = MASTER_FILE + ".gz"
        print(f"[+] Saving compressed master wordlist (gzip) with {len(words)} entries...")
        with gzip.open(out_file, "wt") as outfile:
            for word in tqdm(sorted(words), desc="Writing master"):
                outfile.write(word + "\n")
    elif compress == "bz2":
        out_file = MASTER_FILE + ".bz2"
        print(f"[+] Saving compressed master wordlist (bz2) with {len(words)} entries...")
        with bz2.open(out_file, "wt") as outfile:
            for word in tqdm(sorted(words), desc="Writing master"):
                outfile.write(word + "\n")
    else:
        out_file = MASTER_FILE
        print(f"[+] Saving master wordlist with {len(words)} entries...")
        with open(out_file, "w") as outfile:
            for word in tqdm(sorted(words), desc="Writing master"):
                outfile.write(word + "\n")
    print(f"[+] Done: {out_file}")

# -------------------- Create / Add --------------------
def create_master(files, folders, threads, log_path, skip_logged, resume, compress):
    words = collect_words_from_inputs(files, folders, threads, log_path, "CREATE", skip_logged, resume)
    save_master(words, compress)

def add_to_master(files, folders, threads, log_path, skip_logged, resume, compress):
    if not any(os.path.exists(f) for f in [MASTER_FILE, MASTER_FILE + ".gz", MASTER_FILE + ".bz2"]):
        print("[-] No master wordlist found. Use --create first.")
        return

    existing = set()
    if os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "r", errors="ignore") as infile:
            existing = set(line.strip() for line in infile if line.strip())
    elif os.path.exists(MASTER_FILE + ".gz"):
        with gzip.open(MASTER_FILE + ".gz", "rt") as infile:
            existing = set(line.strip() for line in infile if line.strip())
    elif os.path.exists(MASTER_FILE + ".bz2"):
        with bz2.open(MASTER_FILE + ".bz2", "rt") as infile:
            existing = set(line.strip() for line in infile if line.strip())

    print(f"[+] Loaded {len(existing)} entries from existing master")
    words = existing | collect_words_from_inputs(files, folders, threads, log_path, "ADD", skip_logged, resume)
    save_master(words, compress)

# -------------------- Main --------------------
def main():
    parser = argparse.ArgumentParser(description="ListMan - unify multiple wordlists into one master list")
    parser.add_argument("--create", nargs="*", help="Create new master wordlist from files")
    parser.add_argument("--add", nargs="*", help="Add new wordlists to existing master")
    parser.add_argument("--create-folder", nargs="*", help="Create new master from folders containing .txt files")
    parser.add_argument("--add-folder", nargs="*", help="Add new folders of .txt files to existing master")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to use (default: 4)")
    parser.add_argument("--log", action="store_true", help="Enable logging of processed files")
    parser.add_argument("--log-file", default=LOG_FILE, help="Path to log file (default: listman.log)")
    parser.add_argument("--skip-logged", action="store_true", help="Skip files already in log")
    parser.add_argument("--resume", action="store_true", help="Resume from last interrupted state")
    parser.add_argument("--compress", choices=["gzip", "bz2"], help="Compress the master list (gzip or bz2)")
    parser.add_argument("--version", action="store_true", help="Show version info and exit")
    parser.add_argument("--about", action="store_true", help="Show about banner and exit")

    args = parser.parse_args()

    if args.version:
        print(f"{__program__} v{__version__} by {__author__} <{__email__}>")
        sys.exit(0)

    if args.about:
        print(banner())
        sys.exit(0)

    log_path = args.log_file if args.log else None

    if args.create or args.create_folder:
        create_master(args.create, args.create_folder, args.threads, log_path, args.skip_logged, args.resume, args.compress)
    elif args.add or args.add_folder:
        add_to_master(args.add, args.add_folder, args.threads, log_path, args.skip_logged, args.resume, args.compress)
    else:
        print("[-] No action specified. Use --create / --add or --*-folder.")

if __name__ == "__main__":
    main()
