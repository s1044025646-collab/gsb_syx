#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from blind_watermark import WaterMark

print("=" * 60)
print("水印嵌入 + 遮挡攻击提取演示")
print("=" * 60)
print()

# 第一步：嵌入水印
print("第一步：嵌入水印 'test'")
bwm = WaterMark(password_img=1, password_wm=1)
bwm.read_img('examples/pic/ori_img.jpeg')
wm = 'test'
bwm.read_wm(wm, mode='str')
output_file = 'examples/output/test_embedded.png'
bwm.embed(output_file)

len_wm = len(bwm.wm_bit)
print('水印已嵌入到:', output_file)
print('水印长度:', len_wm)
print()

# 第二步：不使用攻击提取
print("第二步：不使用攻击提取水印")
bwm1 = WaterMark(password_img=1, password_wm=1)
wm_extract = bwm1.extract(output_file, wm_shape=len_wm, mode='str', attack=False)
print("提取结果：", wm_extract)
print()

# 第三步：使用遮挡攻击提取
print("第三步：使用遮挡攻击提取水印")
print("(3个遮挡块，每个占比0.1)")
bwm2 = WaterMark(password_img=1, password_wm=1)
wm_extract = bwm2.extract(output_file, wm_shape=len_wm, mode='str', attack=True)
print("提取结果：", wm_extract)
print()

print("=" * 60)
print("演示完成！")
print("=" * 60)
