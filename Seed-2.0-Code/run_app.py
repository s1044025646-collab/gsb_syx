import os
import sys
import subprocess

# 设置环境变量禁用统计收集和交互式提示
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'

# 启动 Streamlit 应用，重定向标准输入来跳过交互式提示
proc = subprocess.Popen(
    [sys.executable, '-m', 'streamlit', 'run',
     'beijing_rent_analysis.py',
     '--server.port', '8883'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# 发送一个空输入来跳过电子邮件提示
proc.stdin.write('\n')
proc.stdin.flush()

# 读取输出
while True:
    line = proc.stdout.readline()
    if not line:
        break
    print(line, end='')
    if 'Local URL:' in line:
        break

