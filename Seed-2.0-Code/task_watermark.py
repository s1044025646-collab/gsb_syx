#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blind_watermark import WaterMark
import cv2

print("=== 开始水印嵌入与提取任务 ===")

# 1. 嵌入水印
print("\n1. 嵌入水印")
bwm_embed = WaterMark(password_wm=123, password_img=456)
bwm_embed.read_img(filename='examples/pic/ori_img.jpeg')
wm_content = "test"
bwm_embed.read_wm(wm_content, mode='str')
embedded_img = bwm_embed.embed('examples/output/task_embedded.png')
len_wm = len(bwm_embed.wm_bit)
print(f"水印嵌入完成！")
print(f"嵌入内容: {wm_content}")
print(f"水印长度: {len_wm}")
print(f"嵌入图片: examples/output/task_embedded.png")

# 2. 直接提取（不攻击）
print("\n2. 直接提取水印（不攻击）")
bwm_extract1 = WaterMark(password_wm=123, password_img=456)
wm_extracted_normal = bwm_extract1.extract(
    'examples/output/task_embedded.png',
    wm_shape=len_wm,
    mode='str'
)
print(f"直接提取结果: {wm_extracted_normal}")

# 3. 应用遮挡攻击后提取
print("\n3. 应用遮挡攻击后提取水印")
bwm_extract2 = WaterMark(password_wm=123, password_img=456)
wm_extracted_attacked = bwm_extract2.extract(
    'examples/output/task_embedded.png',
    wm_shape=len_wm,
    mode='str',
    apply_attack=True,
    attack_type='shelter',
    attack_params={'ratio': 0.1, 'n': 3},
    attacked_output_file='examples/output/task_attacked_image.png'
)
print(f"遮挡攻击后提取结果: {wm_extracted_attacked}")
print(f"攻击后图片: examples/output/task_attacked_image.png")

print("\n=== 任务完成 ===")
