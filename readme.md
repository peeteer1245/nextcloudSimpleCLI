# nextcloudSimpleCLI

# setup

```bash
pip install -r requirements.txt

cp config.json.example config.json

nano config.json
```

# running

```bash
python3 main.py very_big_file.zip /destination_folder
```

or

```bash
python3 main.py --server https://example.com --user John --password Doe very_big_file.zip /destination_folder
```

or

```bash
python3 main.py -lH /example_folder  # list contents of folders
```

Usage:

```bash
usage: main.py [-h] [-l] [-H] [-c CONFIG] [-s SERVER] [-u USER] [-p PASSWORD] [source_files ...] destination

positional arguments:
  source_files          source files / folders
  destination           destination folder

options:
  -h, --help            show this help message and exit
  -l                    list Nextcloud directory contents
  -H, --human-readable  print sizes like 1K 234M 2G etc.
  -c CONFIG, --config CONFIG
                        config file containing login credentials
  -s SERVER, --server SERVER
                        url of nextcloud server
  -u USER, --user USER  login username
  -p PASSWORD, --password PASSWORD
                        login password
```