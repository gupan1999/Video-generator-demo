#!/usr/bin/env python
# coding: utf-8
import numpy as np

'''
def random_colors(N):
    np.random.seed(1)
    colors = [tuple(255 * np.random.rand(3)) for _ in range(N)]
    return colors


def apply_custom_mask(image, mask, color, mode='inner', alpha=0.5):

    for n, c in enumerate(color):
        if mode == 'inner':
            image[:, :, n] = np.where(
                mask == 1,
                image[:, :, n] * (1 - alpha) + alpha * c,
                image[:, :, n]
            )
        else:
            image[:, :, n] = np.where(
                mask == 1,
                image[:, :, n],
                image[:, :, n] * (1 - alpha) + alpha * c
            )

    return image
    
def show(image, boxes, masks, colors=None):
n_instances = boxes.shape[0]
if not n_instances:
    print('NO INSTANCES TO DISPLAY')

colors = colors or [(0,0, 0)]*n_instances

for i in range(n_instances):

    if not np.any(boxes[i]):
        continue

    # y1, x1, y2, x2 = boxes[i]
    # label = names[ids[i]]
    color = colors[i]
    # score = scores[i] if scores is not None else None
    # caption = '{} {:.2f}'.format(label, score) if score else label
    mask = masks[i, :, :]
    image = apply_custom_mask(image, mask, color,mode='outer',alpha=1)
    # image = apply_mask(image, mask, color)
    # image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 1)
    # image = cv2.putText(
    #     image, caption, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2
    # )

return image

'''


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


# 需要的目标以外置黑色
def custom_show(image, masks):

    alpha = 1
    if not len(masks):
        for i in range(3):
            image[:, :, i] = image[:, :, i] * (1-alpha) + alpha * 0
        return image
    final_mask = masks[0]
    for i in range(1, masks.shape[0]):
        final_mask = np.bitwise_or(final_mask, masks[i])
    for j in range(3):
        image[:, :, j] = np.where(
            final_mask == 1,
            image[:, :, j],
            image[:, :, j] * (1 - alpha) + alpha * 0
        )
    return image

def custom_show1(image, masks):
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



