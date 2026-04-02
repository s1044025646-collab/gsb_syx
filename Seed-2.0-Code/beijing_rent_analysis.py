import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import os
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="北京租房数据分析系统",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #2c3e50;
    }
    h2 {
        color: #34495e;
    }
    </style>
    """, unsafe_allow_html=True)

# 标题
st.title("🏠 北京租房数据分析系统")
st.markdown("---")

@st.cache_data
def load_and_process_data():
    """
    数据预处理与工程函数：
    1. 自动扫描并合并所有 CSV 文件
    2. 处理 GBK/UTF-8 编码兼容
    3. 删除全空行
    4. 清洗价格和面积数据
    5. 提取地铁距离
    6. 计算每平米月租金
    """
    data_dir = Path("RentFromDanke")
    all_files = list(data_dir.glob("*.csv"))
    
    if not all_files:
        st.error("未找到任何 CSV 文件！")
        return None
    
    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file, encoding='gbk')
            except Exception as e:
                st.warning(f"无法读取文件 {file}: {e}")
                continue
        
        # 删除全空行
        df = df.dropna(how='all')
        dfs.append(df)
    
    if not dfs:
        st.error("没有成功读取任何数据文件！")
        return None
    
    # 合并所有数据
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # 清洗价格数据：提取数字，去除"元"等字符
    def clean_price(x):
        if pd.isna(x):
            return np.nan
        x = str(x)
        match = re.search(r'\d+\.?\d*', x)
        return float(match.group()) if match else np.nan
    
    combined_df['价格'] = combined_df['价格'].apply(clean_price)
    
    # 清洗面积数据：提取数字，去除"平米"等字符
    def clean_area(x):
        if pd.isna(x):
            return np.nan
        x = str(x)
        match = re.search(r'\d+\.?\d*', x)
        return float(match.group()) if match else np.nan
    
    combined_df['面积'] = combined_df['面积'].apply(clean_area)
    
    # 从地铁字段提取数字距离
    def extract_subway_distance(x):
        if pd.isna(x):
            return np.nan
        x = str(x)
        match = re.search(r'(\d+)米', x)
        return float(match.group(1)) if match else np.nan
    
    combined_df['地铁距离'] = combined_df['地铁'].apply(extract_subway_distance)
    
    # 计算每平米月租金
    combined_df['每平米月租金'] = combined_df['价格'] / combined_df['面积']
    
    # 删除价格或面积为空的行
    combined_df = combined_df.dropna(subset=['价格', '面积'])
    
    return combined_df

# 加载数据
data_load_state = st.text('正在加载数据...')
df = load_and_process_data()
data_load_state.text('')

if df is None:
    st.stop()

# 侧边栏：交互式筛选控制
st.sidebar.header("🔍 数据筛选")

# 位置1多选框
locations = sorted(df['位置1'].dropna().unique())
selected_locations = st.sidebar.multiselect(
    "选择行政区",
    options=locations,
    default=locations
)

# 价格范围滑动条
min_price = int(df['价格'].min())
max_price = int(df['价格'].max())
price_range = st.sidebar.slider(
    "价格范围（元）",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price)
)

# 面积范围滑动条
min_area = int(df['面积'].min())
max_area = int(df['面积'].max())
area_range = st.sidebar.slider(
    "面积范围（平米）",
    min_value=min_area,
    max_value=max_area,
    value=(min_area, max_area)
)

# 根据筛选条件过滤数据
filtered_df = df[
    (df['位置1'].isin(selected_locations)) &
    (df['价格'] >= price_range[0]) &
    (df['价格'] <= price_range[1]) &
    (df['面积'] >= area_range[0]) &
    (df['面积'] <= area_range[1])
]

# 顶部：关键指标展示
st.header("📊 关键指标")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_houses = len(filtered_df)
    st.metric("房源总数", f"{total_houses:,}")

with col2:
    avg_price_per_sqm = filtered_df['每平米月租金'].mean()
    st.metric("平均单价", f"{avg_price_per_sqm:.2f} 元/㎡")

with col3:
    avg_area = filtered_df['面积'].mean()
    st.metric("平均面积", f"{avg_area:.2f} ㎡")

with col4:
    # 地铁房占比（地铁距离 < 1000米的房源）
    subway_houses = filtered_df[filtered_df['地铁距离'] < 1000]
    subway_ratio = len(subway_houses) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
    st.metric("地铁房占比", f"{subway_ratio:.1f}%")

st.markdown("---")

# 使用 tabs 分为两个板块
tab1, tab2 = st.tabs(["市场宏观趋势", "区域对比"])

with tab1:
    st.header("市场宏观趋势")
    
    # 任务 A：面积与价格的散点图
    st.subheader("🏷️ 面积与价格关系")
    fig_scatter = px.scatter(
        filtered_df,
        x='面积',
        y='价格',
        color='位置1',
        size='每平米月租金',
        title='房源面积与价格散点图',
        labels={'面积': '面积（㎡）', '价格': '价格（元）', '位置1': '行政区'},
        hover_data=['小区', '位置2', '户型'],
        size_max=30
    )
    fig_scatter.update_layout(
        height=600,
        xaxis_title='面积（㎡）',
        yaxis_title='价格（元）'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # 任务 B：租金单价随地铁距离变化的趋势图
    st.subheader("🚇 租金单价与地铁距离")
    subway_df = filtered_df.dropna(subset=['地铁距离'])
    if len(subway_df) > 0:
        fig_subway = px.scatter(
            subway_df,
            x='地铁距离',
            y='每平米月租金',
            color='位置1',
            title='租金单价随地铁距离变化趋势',
            labels={'地铁距离': '地铁距离（米）', '每平米月租金': '单价（元/㎡）'},
            trendline='ols',
            trendline_scope='overall'
        )
        fig_subway.update_layout(height=500)
        st.plotly_chart(fig_subway, use_container_width=True)
    else:
        st.warning("暂无地铁距离数据")

with tab2:
    st.header("区域对比")
    
    # 任务 C：各行政区租金单价的箱线图
    st.subheader("📦 各行政区租金单价分布")
    fig_box = px.box(
        filtered_df,
        x='位置1',
        y='每平米月租金',
        color='位置1',
        title='各行政区租金单价箱线图',
        labels={'位置1': '行政区', '每平米月租金': '单价（元/㎡）'}
    )
    fig_box.update_layout(height=500)
    st.plotly_chart(fig_box, use_container_width=True)
    
    # 任务 D：平均单价最高的 Top 10 商圈（位置2）
    st.subheader("🏪 Top 10 高单价商圈")
    top_districts = filtered_df.groupby('位置2')['每平米月租金'].mean().sort_values(ascending=False).head(10)
    fig_bar = px.bar(
        x=top_districts.values,
        y=top_districts.index,
        orientation='h',
        title='平均单价最高的 Top 10 商圈',
        labels={'x': '平均单价（元/㎡）', 'y': '商圈'},
        color=top_districts.values,
        color_continuous_scale='Reds'
    )
    fig_bar.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 底部：数据预览和导出
st.header("📋 数据预览与导出")

# 显示前 100 条数据
st.subheader("前 100 条数据预览")
st.dataframe(filtered_df.head(100), use_container_width=True)

# 导出按钮
st.subheader("导出数据")
csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="📥 下载完整数据 CSV",
    data=csv,
    file_name='beijing_rent_processed.csv',
    mime='text/csv'
)

# 页脚
st.markdown("---")
st.markdown("💡 提示：使用侧边栏筛选器可以实时更新图表和数据")
