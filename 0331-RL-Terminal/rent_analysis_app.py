import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
import os
import glob
from io import StringIO

st.set_page_config(
    page_title="北京租房数据分析平台",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def hide_streamlit_style():
    hide_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        }
        h1, h2, h3 {
            color: #1f2937;
            font-weight: 600;
        }
        .metric-card {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #3b82f6;
        }
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

hide_streamlit_style()

@st.cache_data(show_spinner="正在加载并处理数据...")
def load_and_process_data():
    """
    数据加载与预处理主函数
    使用 @st.cache_data 缓存加速，避免重复计算
    """
    all_files = glob.glob(os.path.join("RentFromDanke", "*.csv"))
    
    df_list = []
    for file in all_files:
        for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
            try:
                df = pd.read_csv(file, encoding=encoding, low_memory=False)
                break
            except UnicodeDecodeError:
                continue
        df_list.append(df)
    
    df = pd.concat(df_list, ignore_index=True)
    
    df = df.dropna(how='all')
    
    def clean_numeric(value, unit_pattern):
        if pd.isna(value):
            return np.nan
        value_str = str(value)
        value_str = re.sub(unit_pattern, '', value_str)
        value_str = re.sub(r'[^\d.]', '', value_str)
        try:
            return float(value_str)
        except:
            return np.nan
    
    df['价格'] = df['价格'].apply(lambda x: clean_numeric(x, r'[元元/]'))
    df['面积'] = df['面积'].apply(lambda x: clean_numeric(x, r'[平米㎡平平方米]'))
    
    def extract_subway_distance(metro_text):
        if pd.isna(metro_text):
            return np.nan
        text = str(metro_text)
        match = re.search(r'(\d+)\s*米', text)
        if match:
            return float(match.group(1))
        return np.nan
    
    df['地铁距离'] = df['地铁'].apply(extract_subway_distance)
    
    df = df.dropna(subset=['价格', '面积'])
    df = df[(df['价格'] > 0) & (df['面积'] > 0)]
    df['每平米月租金'] = df['价格'] / df['面积']
    
    df['位置1'] = df['位置1'].fillna('未知')
    df['位置2'] = df['位置2'].fillna('未知')
    
    df = df.reset_index(drop=True)
    
    return df

with st.spinner('正在加载租房数据...'):
    df = load_and_process_data()

st.title("🏠 北京租房数据深度分析平台")
st.markdown("---")

with st.sidebar:
    st.header("🎯 筛选条件")
    st.markdown("---")
    
    all_locations = sorted(df['位置1'].unique().tolist())
    selected_locations = st.multiselect(
        "选择行政区",
        options=all_locations,
        default=all_locations,
        help="可多选，默认显示全部区域"
    )
    
    st.markdown("---")
    
    min_price = int(df['价格'].min())
    max_price = int(df['价格'].max())
    price_range = st.slider(
        "价格范围 (元/月)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=100,
        format="%d元"
    )
    
    st.markdown("---")
    
    min_area = int(df['面积'].min())
    max_area = int(df['面积'].max())
    area_range = st.slider(
        "面积范围 (平米)",
        min_value=min_area,
        max_value=max_area,
        value=(min_area, max_area),
        step=1,
        format="%d㎡"
    )
    
    st.markdown("---")
    st.markdown("### 💡 筛选说明")
    st.info("所有图表将根据筛选条件实时联动更新")

mask = (
    (df['位置1'].isin(selected_locations)) &
    (df['价格'] >= price_range[0]) &
    (df['价格'] <= price_range[1]) &
    (df['面积'] >= area_range[0]) &
    (df['面积'] <= area_range[1])
)
filtered_df = df[mask].copy()

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_count = len(filtered_df)
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">🏘️ 房源总数</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #1f2937;">{total_count:,}</div>
        <div style="font-size: 0.8rem; color: #10b981; margin-top: 0.3rem;">套</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_price = filtered_df['每平米月租金'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">💰 平均单价</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #1f2937;">{avg_price:.1f}</div>
        <div style="font-size: 0.8rem; color: #10b981; margin-top: 0.3rem;">元/㎡/月</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_area = filtered_df['面积'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">📐 平均面积</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #1f2937;">{avg_area:.1f}</div>
        <div style="font-size: 0.8rem; color: #10b981; margin-top: 0.3rem;">㎡</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    subway_count = filtered_df['地铁距离'].notna().sum()
    subway_ratio = (subway_count / total_count * 100) if total_count > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">🚇 地铁房占比</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #1f2937;">{subway_ratio:.1f}%</div>
        <div style="font-size: 0.8rem; color: #10b981; margin-top: 0.3rem;">{subway_count:,} 套</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

tab1, tab2 = st.tabs(["📈 市场宏观趋势", "🗺️ 区域对比分析"])

with tab1:
    st.subheader("任务 A：面积与价格关系散点图")
    
    fig_scatter = px.scatter(
        filtered_df,
        x='面积',
        y='价格',
        color='位置1',
        size='每平米月租金',
        size_max=20,
        opacity=0.7,
        hover_data={
            '位置1': True,
            '位置2': True,
            '小区': True,
            '户型': True,
            '每平米月租金': ':,.1f',
            '地铁距离': True
        },
        labels={
            '面积': '面积 (㎡)',
            '价格': '月租金 (元)',
            '位置1': '行政区',
            '每平米月租金': '单价 (元/㎡)'
        },
        title='房源面积与价格分布关系',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig_scatter.update_layout(
        height=600,
        showlegend=True,
        legend_title_text='行政区',
        title_x=0.5,
        title_font=dict(size=18),
        plot_bgcolor='white',
        hovermode='closest'
    )
    fig_scatter.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0,0,0,0.1)',
        zeroline=False
    )
    fig_scatter.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(0,0,0,0.1)',
        zeroline=False
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    st.subheader("任务 B：租金单价随地铁距离变化趋势")
    
    subway_df = filtered_df.dropna(subset=['地铁距离']).copy()
    subway_df = subway_df[subway_df['地铁距离'] <= 5000]
    
    if len(subway_df) > 0:
        subway_df['距离分组'] = pd.cut(
            subway_df['地铁距离'],
            bins=[0, 500, 1000, 1500, 2000, 3000, 5000],
            labels=['0-500m', '500-1000m', '1000-1500m', '1500-2000m', '2000-3000m', '3000-5000m']
        )
        
        trend_data = subway_df.groupby('距离分组')['每平米月租金'].agg(['mean', 'count']).reset_index()
        trend_data = trend_data.dropna(subset=['mean'])
        
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data['距离分组'],
                y=trend_data['mean'],
                mode='lines+markers',
                name='平均单价',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=12, symbol='circle')
            ),
            secondary_y=False
        )
        
        z = np.polyfit(range(len(trend_data)), trend_data['mean'], 1)
        p = np.poly1d(z)
        
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data['距离分组'],
                y=p(range(len(trend_data))),
                mode='lines',
                name='趋势拟合线',
                line=dict(color='#ef4444', width=2, dash='dash')
            ),
            secondary_y=False
        )
        
        fig_trend.add_trace(
            go.Bar(
                x=trend_data['距离分组'],
                y=trend_data['count'],
                name='房源数量',
                marker_color='#10b981',
                opacity=0.3
            ),
            secondary_y=True
        )
        
        fig_trend.update_layout(
            title='租金单价与地铁距离关系趋势分析',
            title_x=0.5,
            title_font=dict(size=18),
            height=500,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            plot_bgcolor='white',
            hovermode='x unified'
        )
        fig_trend.update_xaxes(title_text='地铁站距离分组')
        fig_trend.update_yaxes(title_text='平均单价 (元/㎡/月)', secondary_y=False, gridcolor='rgba(0,0,0,0.1)')
        fig_trend.update_yaxes(title_text='房源数量 (套)', secondary_y=True, gridcolor='rgba(0,0,0,0.05)')
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        slope = z[0]
        st.info(f"📊 **趋势分析**: 地铁距离每增加500米，平均租金单价变化约 {slope:.2f} 元/㎡")
    else:
        st.warning("当前筛选范围内没有地铁房数据")

with tab2:
    st.subheader("任务 C：各行政区租金单价箱线图")
    
    location_stats = filtered_df.groupby('位置1')['每平米月租金'].mean().sort_values(ascending=False).index
    box_df = filtered_df[filtered_df['位置1'].isin(location_stats)]
    
    fig_box = px.box(
        box_df,
        x='位置1',
        y='每平米月租金',
        color='位置1',
        labels={
            '位置1': '行政区',
            '每平米月租金': '每平米月租金 (元)'
        },
        title='各行政区租金单价分布对比',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig_box.update_layout(
        height=550,
        title_x=0.5,
        title_font=dict(size=18),
        showlegend=False,
        plot_bgcolor='white'
    )
    fig_box.update_xaxes(title_text='行政区')
    fig_box.update_yaxes(
        title_text='每平米月租金 (元)',
        showgrid=True,
        gridcolor='rgba(0,0,0,0.1)',
        zeroline=False
    )
    
    st.plotly_chart(fig_box, use_container_width=True)
    
    with st.expander("📋 箱线图解读说明"):
        st.markdown("""
        - **箱体**: 代表 25%-75% 分位数区间（核心价格区间）
        - **中间横线**: 代表中位数价格
        - **须线**: 代表正常价格范围边界
        - **散点**: 代表异常值（过高或过低的单价）
        """)
    
    st.markdown("---")
    st.subheader("任务 D：平均单价最高的 Top 10 商圈")
    
    biz_data = filtered_df.groupby('位置2').agg({
        '每平米月租金': 'mean',
        '价格': 'count'
    }).reset_index()
    biz_data.columns = ['商圈', '平均单价', '房源数量']
    biz_data = biz_data[biz_data['房源数量'] >= 3]
    top10_biz = biz_data.nlargest(10, '平均单价').sort_values('平均单价', ascending=True)
    
    colors = px.colors.sequential.Viridis[2:12]
    
    fig_bar = go.Figure()
    
    fig_bar.add_trace(
        go.Bar(
            y=top10_biz['商圈'],
            x=top10_biz['平均单价'],
            orientation='h',
            marker=dict(
                color=colors,
                line=dict(width=0)
            ),
            text=top10_biz['平均单价'].round(1),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>单价: %{x:.1f} 元/㎡<br>房源数: %{customdata} 套<extra></extra>',
            customdata=top10_biz['房源数量']
        )
    )
    
    fig_bar.update_layout(
        title='Top 10 商圈平均租金单价排名',
        title_x=0.5,
        title_font=dict(size=18),
        height=500,
        plot_bgcolor='white',
        xaxis=dict(
            title='平均单价 (元/㎡/月)',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)'
        ),
        yaxis=dict(title='')
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("📊 数据预览与导出")

col_preview1, col_preview2 = st.columns([3, 1])

with col_preview1:
    st.markdown(f"#### 处理后数据预览 (前 100 条，共 {len(filtered_df):,} 条记录)")
    
    display_columns = ['位置1', '位置2', '小区', '户型', '价格', '面积', '每平米月租金', '地铁距离']
    st.dataframe(
        filtered_df[display_columns].head(100).style.format({
            '价格': '{:.0f} 元',
            '面积': '{:.1f} ㎡',
            '每平米月租金': '{:.1f} 元/㎡',
            '地铁距离': '{:.0f} 米'
        }),
        use_container_width=True,
        height=400
    )

with col_preview2:
    st.markdown("#### 📥 数据导出")
    
    @st.cache_data
    def convert_df_to_csv(df_export):
        return df_export.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    
    csv_data = convert_df_to_csv(filtered_df)
    
    st.download_button(
        label="📥 下载完整数据 CSV",
        data=csv_data,
        file_name=f"北京租房清洗数据_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
        use_container_width=True,
        type='primary'
    )
    
    st.markdown(f"""
    <div style="background: #f0f9ff; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <div style="font-weight: 600; color: #0369a1; margin-bottom: 0.5rem;">数据概览</div>
        <div style="font-size: 0.9rem; color: #0c4a6e;">
            📋 总记录数: {len(filtered_df):,}<br>
            📍 覆盖行政区: {filtered_df['位置1'].nunique()} 个<br>
            🏙️ 覆盖商圈: {filtered_df['位置2'].nunique()} 个
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("© 2024 北京租房数据分析平台 | 数据来源：蛋壳公寓公开数据")
