#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cv2
import os

from blind_watermark import WaterMark

os.chdir(os.path.dirname(__file__))

# 1. 嵌入水印
print("=== 开始嵌入水印 ===")
bwm = WaterMark(password_wm=1, password_img=1)
# 读取原图
bwm.read_img(filename='pic/ori_img.jpeg')
# 读取水印
bwm.read_wm('pic/watermark.png')
# 打上盲水印
embedded_img = bwm.embed('output/embedded_for_attack.png')
wm_shape = cv2.imread('pic/watermark.png', flags=cv2.IMREAD_GRAYSCALE).shape
print(f"水印嵌入完成，水印形状: {wm_shape}")

# 2. 直接提取水印（不攻击）
print("\n=== 直接提取水印（不攻击） ===")
bwm1 = WaterMark(password_wm=1, password_img=1)
wm_extracted_normal = bwm1.extract(
    'output/embedded_for_attack.png',
    wm_shape=wm_shape,
    out_wm_name='output/wm_extracted_normal.png',
    mode='img'
)
print("直接提取完成，结果已保存到 output/wm_extracted_normal.png")

# 3. 应用遮挡攻击后提取水印
print("\n=== 应用遮挡攻击后提取水印 ===")
bwm2 = WaterMark(password_wm=1, password_img=1)
wm_extracted_attacked = bwm2.extract(
    'output/embedded_for_attack.png',
    wm_shape=wm_shape,
    out_wm_name='output/wm_extracted_attacked.png',
    mode='img',
    apply_attack=True,
    attack_type='shelter',
    attack_params={'ratio': 0.1, 'n': 3},
    attacked_output_file='output/attacked_image.png'
)
print("遮挡攻击后提取完成！")
print("- 攻击后的图片: output/attacked_image.png")
print("- 提取的水印: output/wm_extracted_attacked.png")

# 4. 使用文本水印测试
print("\n=== 文本水印测试 ===")
bwm_text = WaterMark(password_wm=123, password_img=456)
bwm_text.read_img('pic/ori_img.jpeg')
text_wm = "这是一个测试水印！测试遮挡攻击功能！"
bwm_text.read_wm(text_wm, mode='str')
embedded_text_img = bwm_text.embed('output/embedded_text_for_attack.png')
len_wm = len(bwm_text.wm_bit)

# 直接提取文本
bwm_text1 = WaterMark(password_wm=123, password_img=456)
text_extracted_normal = bwm_text1.extract(
    'output/embedded_text_for_attack.png',
    wm_shape=len_wm,
    mode='str'
)
print(f"直接提取的文本: {text_extracted_normal}")

# 遮挡攻击后提取文本
bwm_text2 = WaterMark(password_wm=123, password_img=456)
text_extracted_attacked = bwm_text2.extract(
    'output/embedded_text_for_attack.png',
    wm_shape=len_wm,
    mode='str',
    apply_attack=True,
    attack_type='shelter',
    attack_params={'ratio': 0.08, 'n': 5},
    attacked_output_file='output/attacked_text_image.png'
)
print(f"遮挡攻击后提取的文本: {text_extracted_attacked}")

print("\n=== 所有测试完成 ===")
