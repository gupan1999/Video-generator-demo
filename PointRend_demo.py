import os
import time
import cv2
import torch
import tqdm
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import sys; sys.path.append("projects/PointRend")
import point_rend
from visualize import process_frame

cfg = get_cfg()
# Add PointRend-specific config
point_rend.add_pointrend_config(cfg)
# Load a config from file
cfg.merge_from_file("projects/PointRend/configs/InstanceSegmentation/pointrend_rcnn_R_50_FPN_3x_coco.yaml")
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5  # set threshold for this model
cfg.MODEL.WEIGHTS = "datasets/model_final_3c3198.pkl"
if not torch.cuda.is_available():
    cfg.MODEL.DEVICE = 'cpu'

predictor = DefaultPredictor(cfg)

video_name = '打野影流之主.mp4'
input_path = os.path.join('input/', video_name)
basename = os.path.splitext(video_name)[0]
suffix = os.path.splitext(video_name)[1]

video = cv2.VideoCapture(input_path)
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
frames_per_second = video.get(cv2.CAP_PROP_FPS)
num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

output_video_name = basename + f'{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}' + suffix
output_video = os.path.join('output/', output_video_name)
print(output_video)
output_file = cv2.VideoWriter(filename=output_video, fourcc=cv2.VideoWriter_fourcc(*'DIVX'),
                              fps=float(frames_per_second), frameSize=(width, height), isColor=True,)

data = {'classes': None, 'boxes': None, 'masks': None, 'scores': None}


for vis_frame in tqdm.tqdm(process_frame(video, data, predictor), total=num_frames):
    output_file.write(vis_frame)
video.release()
output_file.release()

