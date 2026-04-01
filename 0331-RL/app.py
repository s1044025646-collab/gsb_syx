# -*- coding: utf-8 -*-
"""
北京租房数据分析Streamlit应用
功能：数据自动化整合、预处理、交互式筛选、深度可视化分析
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="北京租房数据分析平台",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 样式优化 ====================
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .main-header {
        text-align: center;
        color: #2c3e50;
        padding: 20px 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 数据加载与预处理 ====================
@st.cache_data
def load_and_process_data():
    """
    加载并预处理所有CSV数据
    使用@st.cache_data缓存提高性能
    """
    data_dir = Path("RentFromDanke")
    all_data = []
    
    # 扫描并读取所有CSV文件
    csv_files = sorted(data_dir.glob("*.csv"))
    
    for csv_file in csv_files:
        # 处理编码兼容问题，先尝试UTF-8，失败则使用GBK
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
        except:
            df = pd.read_csv(csv_file, encoding='gbk')
        
        # 删除全空行
        df = df.dropna(how='all')
        all_data.append(df)
    
    # 合并所有数据
    df = pd.concat(all_data, ignore_index=True)
    
    # ==================== 数据清洗 ====================
    
    # 清洗价格字段：去除非数字字符，转换为浮点数
    def clean_price(price):
        if pd.isna(price):
            return np.nan
        price_str = str(price)
        # 提取所有数字
        nums = re.findall(r'\d+\.?\d*', price_str)
        return float(nums[0]) if nums else np.nan
    
    df['价格'] = df['价格'].apply(clean_price)
    
    # 清洗面积字段：去除非数字字符，转换为浮点数
    def clean_area(area):
        if pd.isna(area):
            return np.nan
        area_str = str(area)
        nums = re.findall(r'\d+\.?\d*', area_str)
        return float(nums[0]) if nums else np.nan
    
    df['面积'] = df['面积'].apply(clean_area)
    
    # 从地铁字段提取距离（米）
    def extract_subway_distance(subway_str):
        if pd.isna(subway_str):
            return np.nan
        subway_str = str(subway_str)
        # 提取距离数字（匹配"米"前面的数字）
        match = re.search(r'(\d+)\s*米', subway_str)
        return float(match.group(1)) if match else np.nan
    
    df['地铁距离'] = df['地铁'].apply(extract_subway_distance)
    
    # 计算核心指标：每平米月租金
    df['每平米月租金'] = df['价格'] / df['面积']
    
    # 移除异常值
    df = df[df['价格'] > 0]
    df = df[df['面积'] > 0]
    df = df[df['每平米月租金'] > 0]
    
    return df


# ==================== 主程序开始 ====================
def main():
    # 标题
    st.markdown('<h1 class="main-header">🏠 北京租房数据深度分析平台</h1>', unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner('正在加载并预处理数据...'):
        df = load_and_process_data()
    
    # ==================== 侧边栏筛选控制 ====================
    st.sidebar.title("🔍 筛选条件")
    
    # 位置1多选框（默认全选）
    all_locations = sorted(df['位置1'].dropna().unique().tolist())
    selected_locations = st.sidebar.multiselect(
        "选择行政区",
        options=all_locations,
        default=all_locations,
        help="可以同时选择多个行政区进行对比分析"
    )
    
    # 价格范围滑动条
    min_price = int(df['价格'].min())
    max_price = int(df['价格'].max())
    price_range = st.sidebar.slider(
        "价格范围（元/月）",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=100
    )
    
    # 面积范围滑动条
    min_area = int(df['面积'].min())
    max_area = int(df['面积'].max())
    area_range = st.sidebar.slider(
        "面积范围（平米）",
        min_value=min_area,
        max_value=max_area,
        value=(min_area, max_area),
        step=1
    )
    
    # 应用筛选条件
    filtered_df = df[
        (df['位置1'].isin(selected_locations)) &
        (df['价格'] >= price_range[0]) &
        (df['价格'] <= price_range[1]) &
        (df['面积'] >= area_range[0]) &
        (df['面积'] <= area_range[1])
    ].copy()
    
    # ==================== 顶部关键指标 ====================
    st.markdown("### 📊 核心指标概览")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_count = len(filtered_df)
        st.metric(
            label="🏘️ 房源总数",
            value=f"{total_count:,}",
            delta=""
        )
    
    with col2:
        avg_price = filtered_df['每平米月租金'].mean()
        st.metric(
            label="💰 平均单价",
            value=f"{avg_price:.1f} 元/㎡",
            delta=""
        )
    
    with col3:
        avg_area = filtered_df['面积'].mean()
        st.metric(
            label="📐 平均面积",
            value=f"{avg_area:.1f} ㎡",
            delta=""
        )
    
    with col4:
        # 地铁房定义：地铁距离<=1000米
        subway_count = filtered_df[filtered_df['地铁距离'] <= 1000].shape[0]
        subway_ratio = (subway_count / total_count) * 100 if total_count > 0 else 0
        st.metric(
            label="🚇 地铁房占比",
            value=f"{subway_ratio:.1f}%",
            delta=""
        )
    
    st.divider()
    
    # ==================== 可视化标签页 ====================
    tab1, tab2 = st.tabs(["📈 市场宏观趋势", "🗺️ 区域对比分析"])
    
    # ========== 标签页1：市场宏观趋势 ==========
    with tab1:
        st.markdown("#### 任务A：面积与价格关系散点图")
        st.markdown("颜色映射行政区，点大小代表单价高低")
        
        # 采样数据避免渲染过慢
        plot_df = filtered_df.sample(min(5000, len(filtered_df)), random_state=42)
        
        fig_scatter = px.scatter(
            plot_df,
            x='面积',
            y='价格',
            color='位置1',
            size='每平米月租金',
            size_max=30,
            opacity=0.7,
            hover_data=['小区', '位置2', '户型', '地铁距离'],
            title='房源面积与价格分布关系',
            labels={
                '面积': '面积（㎡）',
                '价格': '月租金（元）',
                '位置1': '行政区'
            },
            height=600
        )
        fig_scatter.update_layout(showlegend=True)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.divider()
        
        # 任务B：租金单价随地铁距离变化趋势
        st.markdown("#### 任务B：租金单价随地铁距离变化趋势")
        st.markdown("带趋势拟合线，展示地铁对租金的影响")
        
        # 过滤掉地铁距离为空的数据
        subway_df = filtered_df.dropna(subset=['地铁距离']).copy()
        subway_df = subway_df[subway_df['地铁距离'] <= 5000]
        
        if len(subway_df) > 0:
            # 按距离分组计算平均值
            subway_df['距离分组'] = pd.cut(
                subway_df['地铁距离'],
                bins=range(0, 5001, 250),
                labels=[f"{i}-{i+250}" for i in range(0, 5000, 250)]
            )
            
            distance_avg = subway_df.groupby('距离分组')['每平米月租金'].mean().reset_index()
            distance_avg = distance_avg.dropna()
            
            fig_trend = go.Figure()
            
            # 添加散点
            fig_trend.add_trace(
                go.Scatter(
                    x=subway_df['地铁距离'],
                    y=subway_df['每平米月租金'],
                    mode='markers',
                    name='单个房源',
                    marker=dict(color='rgba(100, 149, 237, 0.3)', size=5),
                    hovertext=subway_df['小区']
                )
            )
            
            # 添加趋势线（多项式拟合）
            z = np.polyfit(subway_df['地铁距离'], subway_df['每平米月租金'], 2)
            p = np.poly1d(z)
            x_trend = np.linspace(subway_df['地铁距离'].min(), subway_df['地铁距离'].max(), 100)
            
            fig_trend.add_trace(
                go.Scatter(
                    x=x_trend,
                    y=p(x_trend),
                    mode='lines',
                    name='趋势拟合线',
                    line=dict(color='red', width=3)
                )
            )
            
            fig_trend.update_layout(
                title='租金单价随地铁距离变化趋势',
                xaxis_title='地铁距离（米）',
                yaxis_title='每平米月租金（元）',
                height=500,
                hovermode='closest'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 添加说明
            st.info("💡 **观察结论**：总体上，距离地铁越近，租金单价越高，呈现明显的负相关关系。距离地铁1000米内溢价效应尤其显著。")
        else:
            st.warning("暂无有效的地铁距离数据")
    
    # ========== 标签页2：区域对比分析 ==========
    with tab2:
        st.markdown("#### 任务C：各行政区租金单价箱线图")
        st.markdown("用于识别价格分布区间和异常值")
        
        fig_box = px.box(
            filtered_df,
            x='位置1',
            y='每平米月租金',
            color='位置1',
            title='各行政区每平米月租金分布对比',
            labels={
                '位置1': '行政区',
                '每平米月租金': '每平米月租金（元）'
            },
            height=550
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        
        st.divider()
        
        # 任务D：平均单价最高的Top 10商圈
        st.markdown("#### 任务D：平均单价最高的Top 10商圈")
        st.markdown("横向柱状图展示商圈租金水平排名")
        
        # 计算各商圈平均单价，过滤样本量过小的商圈
        location2_stats = filtered_df.groupby('位置2').agg({
            '每平米月租金': 'mean',
            '编号': 'count'
        }).reset_index()
        location2_stats = location2_stats[location2_stats['编号'] >= 5]
        
        top10_location2 = location2_stats.nlargest(10, '每平米月租金').sort_values('每平米月租金', ascending=True)
        
        fig_bar = px.bar(
            top10_location2,
            x='每平米月租金',
            y='位置2',
            orientation='h',
            color='每平米月租金',
            color_continuous_scale='Reds',
            title='平均单价最高的Top 10商圈',
            labels={
                '每平米月租金': '平均每平米月租金（元）',
                '位置2': '商圈'
            },
            height=550,
            text='每平米月租金'
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_bar.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    
    # ==================== 数据预览与导出 ====================
    st.markdown("### 📋 数据预览与导出")
    
    # 展示前100条数据
    st.markdown(f"#### 处理后的数据预览（共 {len(filtered_df):,} 条，显示前100条）")
    display_columns = ['位置1', '位置2', '小区', '户型', '价格', '面积', '每平米月租金', '地铁距离', '地铁']
    st.dataframe(
        filtered_df[display_columns].head(100),
        use_container_width=True,
        height=400
    )
    
    # 下载按钮
    csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载完整处理后数据（CSV）",
        data=csv,
        file_name="北京租房数据_清洗后.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # 页脚
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d;">
        <p>🏠 北京租房数据分析平台 | 数据来源：蛋壳公寓公开数据</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
