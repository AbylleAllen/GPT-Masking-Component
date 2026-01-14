import cv2
import numpy as np
from masking.mask_utils import build_mask_text


def maskPartial(image_path, boxes, config, field_value):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not readable")

    total_len = len(field_value)

    if config.maskFirst > 0:
        ratio = config.maskFirst / total_len
        boxes[1][0] = boxes[0][0] + round((boxes[1][0] - boxes[0][0]) * ratio)
        boxes[2][0] = boxes[3][0] + round((boxes[2][0] - boxes[3][0]) * ratio)
        masked_text = build_mask_text(field_value, config.maskChar, config.maskFirst)

    elif config.maskLast > 0:
        ratio = config.maskLast / total_len
        boxes[0][0] = boxes[1][0] - round((boxes[1][0] - boxes[0][0]) * ratio)
        boxes[3][0] = boxes[2][0] - round((boxes[2][0] - boxes[3][0]) * ratio)
        masked_text = build_mask_text(field_value[::-1], config.maskChar, config.maskLast)[::-1]

    pts = np.array(boxes, dtype=np.int32)
    cv2.fillPoly(image, [pts], (255, 255, 255))

    x, y, w, h = cv2.boundingRect(pts)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(1.1, w / (len(masked_text) * 40))
    thickness = max(1, int(font_scale * 2))

    text_size = cv2.getTextSize(masked_text, font, font_scale, thickness)[0]
    text_x = x + (w - text_size[0]) // 2
    text_y = y + (h + text_size[1]) // 2

    cv2.putText(image, masked_text, (text_x, text_y),
                font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

    cv2.imwrite(image_path, image)


def maskFull(image_path, boxes, config, field_value):
    image = cv2.imread(image_path)
    pts = np.array(boxes, dtype=np.int32)

    masked_text = "".join(
        config.maskChar if ch.isalnum() else ch
        for ch in field_value
    )

    cv2.fillPoly(image, [pts], (255, 255, 255))

    x, y, w, h = cv2.boundingRect(pts)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(1.1, w / (len(masked_text) * 40))
    thickness = max(1, int(font_scale * 2))

    text_size = cv2.getTextSize(masked_text, font, font_scale, thickness)[0]
    text_x = x + (w - text_size[0]) // 2
    text_y = y + (h + text_size[1]) // 2

    cv2.putText(image, masked_text, (text_x, text_y),
                font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

    cv2.imwrite(image_path, image)
