# evt_challenge_v2

**Prequesite Install:**

**--Linux Install from Commandline--**

sudo apt -y install git python-pip python3

git clone https://github.com/jjbanks1/evt_challenge_v2.git

cd evt_challenge_v2/

pip install -r requirements.txt

**--Windows Install from Commandline--**

python

<Click Install Button>


**Sample Call:**

python jpg2location.py testfiles/file?.jpg testfiles/subdir/flooding.jpg testfiles/sunrset_philippines.jpg


**Results:**

"testfiles\file1.jpg", 75204

"testfiles\file2.jpg", [NOT_JPEG]

"testfiles\file3.jpg", [NO_GEOCODE]

"testfiles\file4.jpg", [NO_GEOCODE]

"testfiles\file5.jpg", [NO_GEOCODE]

"testfiles/subdir/flooding.jpg", 77060

"testfiles/sunrset_philippines.jpg", 5316


**Cleanup:**

rm location_cache.json

rm *.log


**CSV Output:**

python jpg2location.py testfiles/file?.jpg testfiles/subdir/flooding.jpg testfiles/sunrset_philippines.jpg > out.csv

<Double click in file exporter window>

**Run Unit Tests:**

python jpg2locationtest.py



