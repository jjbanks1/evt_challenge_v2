# evt_challenge_v2

**Prequesite Install:**

pip install -r requirements.txt


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


**Create CSV Output:**

python jpg2location.py testfiles/file?.jpg testfiles/subdir/flooding.jpg testfiles/sunrset_philippines.jpg > out.csv


**Run Unit Tests:**

python jpg2locationtest.py



