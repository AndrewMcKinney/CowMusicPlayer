start:
	python cow_music/cow_music.py

format: 
	python formatting_helper/formatting_helper.py

install:
	python -m pip install -r py_requirements.txt

clean:
	del /f music_storage.json
	RD /S /Q "music_files"