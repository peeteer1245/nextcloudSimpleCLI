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
python3 main.py -lH /  # list contents of folders
```
