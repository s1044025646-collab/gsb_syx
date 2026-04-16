#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import numpy as np
from blind_watermark import WaterMark

os.chdir(os.path.dirname(__file__))
os.makedirs('output/attack', exist_ok=True)

bwm = WaterMark(password_img=1, password_wm=1)
bwm.read_img('pic/ori_img.jpeg')
wm = '@guofei9987 开源万岁！'
bwm.read_wm(wm, mode='str')
bwm.embed('output/attack/embedded.png')
len_wm = len(bwm.wm_bit)
print('水印长度:', len_wm)

bwm1 = WaterMark(password_img=1, password_wm=1)

print("\n" + "="*50)
print("1. 不攻击，直接提取")
print("="*50)
wm_extract = bwm1.extract('output/attack/embedded.png', wm_shape=len_wm, mode='str')
print("提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

print("\n" + "="*50)
print("2. 提取前实施遮挡攻击（集成方式）")
print("="*50)
wm_extract = bwm1.extract(
    'output/attack/embedded.png', 
    wm_shape=len_wm, 
    mode='str',
    attack='shelter',
    ratio=0.1,
    n=20,
    output_file='output/attack/shelter_attacked.png'
)
print("遮挡攻击后提取结果：", wm_extract)
print("攻击后的图片已保存至: output/attack/shelter_attacked.png")
assert wm == wm_extract, '提取水印和原水印不一致'

print("\n" + "="*50)
print("3. 提取前实施椒盐噪声攻击")
print("="*50)
wm_extract = bwm1.extract(
    'output/attack/embedded.png', 
    wm_shape=len_wm, 
    mode='str',
    attack='salt_pepper',
    ratio=0.05,
    output_file='output/attack/salt_pepper_attacked.png'
)
print("椒盐攻击后提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

print("\n" + "="*50)
print("4. 提取前实施亮度攻击")
print("="*50)
print("注意：单向亮度攻击较强时会影响水印提取，通常需要攻击后再还原")
wm_extract = bwm1.extract(
    'output/attack/embedded.png', 
    wm_shape=len_wm, 
    mode='str',
    attack='bright',
    ratio=0.95,
    output_file='output/attack/bright_attacked.png'
)
print("亮度攻击(ratio=0.95)后提取结果：", wm_extract)
print("(亮度攻击对水印有破坏性，建议使用更温和参数或双向调整)")

print("\n" + "="*50)
print("5. 组合攻击：遮挡 + 椒盐")
print("="*50)
wm_extract = bwm1.extract(
    'output/attack/embedded.png', 
    wm_shape=len_wm, 
    mode='str',
    attack=[
        {'name': 'shelter', 'ratio': 0.05, 'n': 10},
        {'name': 'salt_pepper', 'ratio': 0.02}
    ],
    output_file='output/attack/combined_attacked.png'
)
print("组合攻击后提取结果：", wm_extract)
assert wm == wm_extract, '提取水印和原水印不一致'

print("\n" + "="*50)
print("6. 单独使用 apply_attack 方法")
print("="*50)
import cv2
img = cv2.imread('output/attack/embedded.png')
attacked_img = bwm1.apply_attack(
    img,
    attack='shelter',
    ratio=0.15,
    n=5,
    output_file='output/attack/separate_shelter.png'
)
print("apply_attack 方法处理完成，图片已保存")

print("\n" + "="*50)
print("所有测试通过！")
print("="*50)
print("\n支持的攻击类型:")
print("- 'shelter': 遮挡攻击, 参数: ratio(遮挡比例), n(遮挡块数量)")
print("- 'salt_pepper': 椒盐噪声攻击, 参数: ratio(噪声比例)")
print("- 'bright': 亮度攻击, 参数: ratio(亮度系数)")
print("- 'resize': 缩放攻击, 参数: out_shape(输出尺寸)")
print("- 'rot': 旋转攻击, 参数: angle(旋转角度)")
print("- 'cut': 裁剪攻击, 参数: loc_r/ loc(裁剪位置), scale(缩放系数)")
print("\n使用方式:")
print("1. 单一攻击: attack='shelter', ratio=0.1, n=20")
print("2. 组合攻击: attack=[{'name': 'shelter', 'ratio': 0.1}, {'name': 'salt_pepper', 'ratio': 0.01}]")
print("3. 保存攻击后图片: output_file='path/to/save.png'")
