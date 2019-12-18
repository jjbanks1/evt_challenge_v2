# evt_challenge_v2

## Prequesite Install:

**Linux Install from Commandline**

```bash
sudo apt -y install git python-pip python3
git clone https://github.com/jjbanks1/evt_challenge_v2.git
cd evt_challenge_v2/
pip install -r requirements.txt
```

**Windows Install from Commandline**

```bash
python
```
Click Install Button


## Sample Call:

```bash
python jpg2location.py testfiles/file?.jpg testfiles/subdir/flooding.jpg testfiles/sunrset_philippines.jpg
```

**Results:**

```bash
"testfiles\file1.jpg", 75204
"testfiles\file2.jpg", [NOT_JPEG]
"testfiles\file3.jpg", [NO_GEOCODE]
"testfiles\file4.jpg", [NO_GEOCODE]
"testfiles\file5.jpg", [NO_GEOCODE]
"testfiles/subdir/flooding.jpg", 77060
"testfiles/sunrset_philippines.jpg", 5316
```


**Cleanup:**

```bash
rm location_cache.json
rm *.log
```


## CSV Output:

```bash
python jpg2location.py testfiles/file?.jpg testfiles/subdir/flooding.jpg testfiles/sunrset_philippines.jpg > out.csv
```

Double click in file exporter window

## Run Unit Tests:

```bash
python jpg2locationtest.py
```


