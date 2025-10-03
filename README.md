# ListMan v1 Manual

## NAME
**ListMan** — a multi-threaded wordlist manager for cybersecurity students and penetration testers.

## SYNOPSIS
```
python listman.py [OPTIONS]
```

## DESCRIPTION
**ListMan** is a Python-based tool to unify multiple password or username wordlists into a single master list. It is designed to save time when working with multiple files from sources like `rockyou.txt`, `SecLists`, or custom wordlists.

**Features include**:

- Multi-threaded processing to speed up reading large files
- Logging of processed files to avoid reprocessing
- Pause and resume support for long-running operations
- Skip already logged files
- Optional compression (`gzip` or `bz2`) to save disk space
- CLI options to create, add, or manage wordlists
- Random-colored ASCII hacker-style banner

**Author**: CySec Don  
**Email**: cysecdon@proton.me  
**Version**: 1.0  
**License**: MIT

## HELP / SYNTAX
To view all available commands and syntax, use:
```
python listman.py --help
```

**Common commands supported:**

| Command | Description |
|---------|-------------|
| `--create [FILES]` | Create a new master wordlist from the specified files |
| `--create-folder [FOLDERS]` | Create a master wordlist from all `.txt` files in the folder(s) |
| `--add [FILES]` | Add files to an existing master wordlist |
| `--add-folder [FOLDERS]` | Add all `.txt` files from folder(s) to an existing master |
| `--threads N` | Number of threads to use (default: 4) |
| `--log` | Enable logging of processed files |
| `--log-file [FILE]` | Specify a custom log file name (default: listman.log) |
| `--skip-logged` | Skip files already logged in previous runs |
| `--resume` | Resume from last paused state |
| `--compress gzip/bz2` | Compress master wordlist |
| `--version` | Show version information |
| `--about` | Show about banner with description |

## USAGE

### 1. Show program version
```
python listman.py --version
```

### 2. Show About Banner
```
python listman.py --about
```

### 3. Create a new master wordlist from files
```
python listman.py --create file1.txt file2.txt --threads 4 --log --compress gzip
```

### 4. Create a new master wordlist from a folder
```
python listman.py --create-folder ./wordlists --threads 8 --compress bz2
```

### 5. Add new wordlists to an existing master
```
python listman.py --add newfile.txt --log --skip-logged
```

### 6. Resume a paused operation
```
python listman.py --create-folder ./bigwordlists --resume
```

### 7. Compression options
```
--compress gzip
--compress bz2
```

### 8. Logging and skip-logged
```
--log
--log-file customlog.log
--skip-logged
```

### 9. Threads
```
--threads 8
```

### 10. Pause & Resume
- Press Ctrl+C to pause and save state
- Resume using `--resume`

## FILES
- `master_wordlist.txt` — unified master wordlist
- `listman.log` — log of processed files
- `resume_state.json` — saved state for resuming

## EXAMPLES
1. **Basic create**:
```
python listman.py --create rockyou.txt common.txt
```

2. **Create from folder, 8 threads, compressed gzip**:
```
python listman.py --create-folder ./SecLists --threads 8 --compress gzip --log
```

3. **Add new files to existing master**:
```
python listman.py --add new_passwords.txt --log --skip-logged
```

4. **Resume after interruption**:
```
python listman.py --resume
```

5. **Show version or banner**:
```
python listman.py --version
python listman.py --about
```

## NOTES
- Ensures no duplicate entries in the master list
- Works with plain text, gzip, and bz2 compressed files
- Random colored ASCII banner
- Safe pause/resume for large datasets

## AUTHOR
**CySec Don**  
Email: `cysecdon@proton.me`

## LICENSE
**MIT License**

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

