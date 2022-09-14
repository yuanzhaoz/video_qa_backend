import logging
import sys
import random
from dataclasses import asdict
import os

from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS, cross_origin
from utils.videoqa import VQA

import cv2 as cv

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# print(app.instance_path)
# print(app.root_path)

PRETRAINED_howtovqa69m = 'checkpoints/ckpt_pt_howtovqa69m.pth'
PRETRAINED_ivqa = 'checkpoints/ckpt_ft_ivqa.pth'
curr_selected_model = 'howtovqa69m'

vqa_model = VQA(PRETRAINED_howtovqa69m)
# vqa_model_ivqa = VQA(PRETRAINED_ivqa)

@app.post("/video_qa")
def respond():
    print(f'{request.json}')

    start_mins = int(request.json['start_mins'])
    start_secs = int(request.json['start_secs'])
    end_mins = int(request.json['end_mins'])
    end_secs = int(request.json['end_secs'])
    question = request.json['question']
    selected_model = request.json['selected_model']
    video_path = f'/home/SERILOCAL/yuanzhao.z/video_qa_web/video_qa_frontend/src/assets/{request.json["selected_video"]}.mp4'
    global curr_selected_model
    global vqa_model

    if curr_selected_model != selected_model:
        if selected_model == 'howtovqa69m':
            print(f'====== select howtovqa69m =====')
            del vqa_model
            vqa_model =  VQA(PRETRAINED_howtovqa69m)
            # vqa_model.load_pretrained(PRETRAINED_howtovqa69m)
            curr_selected_model = 'howtovqa69m'
            
        elif selected_model == 'ivqa':
            print(f'====== select ivqa =====')
            del vqa_model
            vqa_model =  VQA(PRETRAINED_ivqa)
            # vqa_model.load_pretrained(PRETRAINED_ivqa)
            curr_selected_model = 'ivqa'
            

    print(video_path)
    vidFile = cv.VideoCapture(video_path)
    fps = vidFile.get(cv.CAP_PROP_FPS)

    print(start_mins)
    print(start_secs)
    print(end_mins)
    print(end_secs)
    print(video_path)
    print(fps)
    print(question)
    print(selected_model)

    start_frame = int((start_mins*60+start_secs)*fps)
    end_frame = int((end_mins*60+end_secs)*fps)
    assert start_frame<end_frame
    print(start_frame)
    print(end_frame)
    # video_writer = cv.VideoWriter('selected_clip.avi', 0, fps, (width,height))

    width = 0
    height = 0
    frame_counter = 0
    while vidFile.isOpened():
        ret, frame = vidFile.read()
        if width==0 and height==0:
            video_writer = cv.VideoWriter('selected_clip.avi', 0, fps, (frame.shape[1],frame.shape[0]))
            height = frame.shape[0]
            width = frame.shape[1]
        if start_frame<=frame_counter<end_frame:
            video_writer.write(frame)
        elif frame_counter>=end_frame:
            video_writer.release()
            print('Selected clip saved!')
            break
        frame_counter += 1
    
    response = vqa_model.response('selected_clip.avi', question)
    print(response)
    return {'Answer':response}, 200
    # return render_template('test.html', returned_answer=response[0])  #{'response':response[0]}, 201
    # return {'response':response[0]}, 201

    # return {'answer':f'{random.randint(0, 1000)}Answer'}, 200
    # return {'Answer1':f'{response[0]}', 'Answer2':f'{response[1]}'}, 200

@app.route("/")
def hello():
    return "Hello, World!"

@app.route("/get_video_file_default")
def get_video_file_default():
    return send_file(f'../video_qa_frontend/src/assets/steak.mp4')

@app.route("/get_video_file/<video_id>")
def get_video_file(video_id):
    print(f'../video_qa_frontend/src/assets/{video_id}.mp4')
    return send_file(f'../video_qa_frontend/src/assets/{video_id}.mp4')

# @app.route("/select_model/<model_id>")
# def select_model(model_id):
#     if model_id != selected_model_id:
#         if model_id == 'howtovqa69m':
#             PRETRAINED = 'checkpoints/ckpt_pt_howtovqa69m.pth'
#         elif model_id == 'ivqa':
#             PRETRAINED = 'checkpoints/ckpt_ft_ivqa.pth'
#         vqa_model = VQA(PRETRAINED)

@app.route("/video_list")
def get_video_list():
    rel_path = '../video_qa_frontend/src/assets'
    abs_path = os.path.abspath(rel_path)
    print(abs_path)
    video_list = []
    for file in os.listdir(abs_path):
        if file.endswith(".mp4"):
            # video_list.append(f'{abs_path}/{file}')
            video_list.append(file.split('.')[0])
    print(video_list)
    return {'Videos':video_list}, 200

# if __name__ == "__main__":
    # PRETRAINED_howtovqa69m = 'checkpoints/ckpt_pt_howtovqa69m.pth'
    # PRETRAINED_ivqa = 'checkpoints/ckpt_ft_ivqa.pth'
    # # curr_selected_model = 'howtovqa69m'

    # vqa_model = VQA(PRETRAINED_howtovqa69m)
    # app.run(debug=True, host="0.0.0.0", port=5000)  # noqa}