import numpy as np


def bbox_to_list(bbox):
    return [bbox.p0, bbox.p1, bbox.p2, bbox.p3]


def build_mask_text(value: str, mask_char: str, count: int):
    masked = ""
    masked_count = 0

    for ch in value:
        if ch.isalnum() and masked_count < count:
            masked += mask_char
            masked_count += 1
        else:
            masked += ch

    return masked

def compute_masked_value(value: str, config, mask_type: str) -> str:
    result = list(value)

    if mask_type == "FULL":
        return "".join(
            config.maskChar if ch.isalnum() else ch
            for ch in value
        )

    if config.maskFirst > 0:
        count = 0
        for i, ch in enumerate(result):
            if ch.isalnum() and count < config.maskFirst:
                result[i] = config.maskChar
                count += 1

    if config.maskLast > 0:
        count = 0
        for i in range(len(result) - 1, -1, -1):
            if result[i].isalnum() and count < config.maskLast:
                result[i] = config.maskChar
                count += 1

    return "".join(result)
