import numpy as np
from skimage.filters import gaussian


def random_color():
    return tuple(np.random.randint(0, 255, 3))


# 过滤不需要的类别
def process(data, target_class=None):

    if target_class is not None:
        filter = []
        for i in range(len(data['classes'])):
            if data['classes'][i] in target_class:
                filter.append(i)
        data['classes'] = data['classes'][filter]
        data['masks'] = data['masks'][filter, :, :]
        data['scores'] = data['scores'][filter]
        data['boxes'] = data['boxes'][filter]
    return data


# 需要的目标以外置黑色，否则白色
def custom_show(image, masks):
    alpha = 1
    if not len(masks):
        for i in range(3):
            image[:, :, i] = image[:, :, i] * (1 - alpha) + alpha * 0
        return image
    final_mask = masks[0]
    for i in range(1, masks.shape[0]):
        final_mask = np.bitwise_or(final_mask, masks[i])
    for j in range(3):
        image[:, :, j] = np.where(
            final_mask == 1,
            image[:, :, j] * (1 - alpha) + alpha * 255,
            image[:, :, j] * (1 - alpha) + alpha * 0
        )
    return image


# 抖音特效
def tiktok_effect(frame):
    # 单独抽取去掉红色通道的图像
    gb_channel_frame = frame.copy()
    gb_channel_frame[:, :, 0].fill(0)

    # 单独抽取红色通道图像
    r_channel_frame = frame.copy()
    r_channel_frame[:, :, 1].fill(0)
    r_channel_frame[:, :, 2].fill(0)

    # 错位合并图像，形成抖音效果
    result = frame.copy()
    result[:-5, :-5, :] = r_channel_frame[:-5, :-5, :] + gb_channel_frame[5:, 5:, :]

    return result


# 高斯模糊
def blur(image):
    return gaussian(image.astype(float), sigma=10)

