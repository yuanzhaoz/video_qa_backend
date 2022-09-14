### Start the backend

Start the backend of the video QA engine by setting up flask 
```
export FLASK_APP=video_qa_flask.py
export FLASK_ENV=development
flask run
```

Create a directory `checkpoints` and store the available vqa models. The current version mainly deals with models from this [paper](https://github.com/antoyang/just-ask).

Store available video(mp4) files inside `video_qa_frontend/src/assets` for the backend to extract the list of available videos to show.
