from skimage.filters import gaussian
from moviepy.editor import VideoFileClip

def blur(image):
    """ Returns a blurred (radius=2 pixels) version of the image """
    return gaussian(image.astype(float), sigma=10)

clip = VideoFileClip("test2.mov")
clip_blurred = clip.fl_image( blur )
clip_blurred.write_videofile("blurred_video.mov")