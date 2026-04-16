#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 演示集成在提取流程中的遮挡攻击功能
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from blind_watermark import WaterMark

os.chdir(os.path.dirname(__file__))

print("=" * 60)
print("演示：在提取水印流程中集成遮挡攻击功能")
print("=" * 60)
print()

# 第一步：嵌入水印
print("第一步：嵌入水印")
bwm = WaterMark(password_img=1, password_wm=1)
bwm.read_img('pic/ori_img.jpeg')
wm = '@guofei9987 开源万岁！'
bwm.read_wm(wm, mode='str')
bwm.embed('output/embedded.png')

len_wm = len(bwm.wm_bit)
print('水印长度:', len_wm)
print()

# 第二步：不使用攻击，直接提取水印
print("第二步：不使用攻击，直接提取水印")
bwm1 = WaterMark(password_img=1, password_wm=1)
wm_extract = bwm1.extract('output/embedded.png', wm_shape=len_wm, mode='str', attack=False)
print("提取结果：", wm_extract)
print("提取成功:", wm == wm_extract)
print()

# 第三步：使用默认参数的遮挡攻击后提取水印
print("第三步：使用默认参数的遮挡攻击后提取水印")
print("(默认：3个遮挡块，每个块占比0.1)")
bwm2 = WaterMark(password_img=1, password_wm=1)
wm_extract = bwm2.extract('output/embedded.png', wm_shape=len_wm, mode='str', attack=True)
print("提取结果：", wm_extract)
print("提取成功:", wm == wm_extract)
print()

# 第四步：使用自定义参数的遮挡攻击后提取水印
print("第四步：使用自定义参数的遮挡攻击后提取水印")
print("(5个遮挡块，每个块占比0.15)")
bwm3 = WaterMark(password_img=1, password_wm=1)
wm_extract = bwm3.extract('output/embedded.png', wm_shape=len_wm, mode='str',
                          attack=True, attack_ratio=0.15, attack_n=5)
print("提取结果：", wm_extract)
print("提取成功:", wm == wm_extract)
print()

# 第五步：更强的遮挡攻击后提取水印
print("第五步：更强的遮挡攻击后提取水印")
print("(10个遮挡块，每个块占比0.2)")
bwm4 = WaterMark(password_img=1, password_wm=1)
wm_extract = bwm4.extract('output/embedded.png', wm_shape=len_wm, mode='str',
                          attack=True, attack_ratio=0.2, attack_n=10)
print("提取结果：", wm_extract)
print("提取成功:", wm == wm_extract)
print()

print("=" * 60)
print("演示完成！")
print("=" * 60)
print()
print("使用说明：")
print("  - 在 extract() 方法中添加 attack=True 参数即可启用遮挡攻击")
print("  - attack_ratio: 每个遮挡块占图像的比例（默认：0.1）")
print("  - attack_n: 遮挡块的数量（默认：3）")
print()
