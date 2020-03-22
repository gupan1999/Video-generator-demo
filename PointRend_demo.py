import os
import torch
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
import sys; sys.path.append("projects/PointRend")
import point_rend
from visualize import process, custom_show1, custom_show
from moviepy.editor import VideoFileClip, CompositeVideoClip
import time

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

video_name = 'cxk.mp4'
input_path = os.path.join('input/', video_name)
basename = os.path.splitext(video_name)[0]
suffix = os.path.splitext(video_name)[1]


def custom_frame1(frame):
    _frame = frame.copy()
    output = predictor(_frame)
    instances = output['instances'].to('cpu')
    data = {'classes': instances.pred_classes.numpy(), 'boxes': instances.pred_boxes.tensor.numpy(), 'masks':instances.pred_masks.numpy() , 'scores': instances.scores.numpy()}
    data = process(data, target_class=[0])
    result = custom_show1(_frame,  data['masks'])
    return result


def custom_frame(frame):
    _frame = frame.copy()
    output = predictor(_frame)
    instances = output['instances'].to('cpu')
    data = {'classes': instances.pred_classes.numpy(), 'boxes': instances.pred_boxes.tensor.numpy(), 'masks':instances.pred_masks.numpy() , 'scores': instances.scores.numpy()}
    data = process(data, target_class=[0])
    result = custom_show(_frame,  data['masks'])
    return result


video = VideoFileClip(input_path)
mask_clip = video.fl_image(custom_frame1).to_mask().without_audio()
clip = video.set_mask(mask_clip).set_pos("center", "center")
background_clip = VideoFileClip('input/DMT TUNNEL.mp4').without_audio().set_duration(clip.duration)
final_clip = CompositeVideoClip([background_clip, clip])

final_clip.write_videofile(
	f'./output/{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}.mp4',
	fps=30,
	codec='mpeg4',
	bitrate="8000k",
	audio_codec="libmp3lame",
	threads=4,
)


