from pathlib import Path
import time
import io

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "RentFromDanke"


@st.cache_data(show_spinner=False)
def load_data(data_dir: Path) -> pd.DataFrame:
    csv_paths = sorted(data_dir.glob("bj_danke_*.csv"))
    if not csv_paths:
        raise FileNotFoundError(f"未在目录中找到数据文件: {data_dir}")

    dfs: list[pd.DataFrame] = []
    for p in csv_paths:
        df = pd.read_csv(p)
        df["数据文件"] = p.name
        dfs.append(df)

    df_all = pd.concat(dfs, ignore_index=True)
    df_all = df_all.dropna(how="all")

    for col in ["价格", "面积"]:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce")

    if "地铁" in df_all.columns:
        s = df_all["地铁"].astype("string")
        df_all["距地铁距离(米)"] = (
            s.str.extract(r"(\d+)\s*米", expand=False).astype("float")
        )
    else:
        df_all["距地铁距离(米)"] = np.nan

    if {"价格", "面积"}.issubset(df_all.columns):
        df_all["租金单价(元/㎡)"] = df_all["价格"] / df_all["面积"]
        df_all.loc[df_all["面积"] <= 0, "租金单价(元/㎡)"] = np.nan
    else:
        df_all["租金单价(元/㎡)"] = np.nan

    return df_all


def init_session_state(df: pd.DataFrame) -> None:
    if "filters_initialized" not in st.session_state:
        st.session_state.filters_initialized = True
        st.session_state.reset_filters = False


def get_safe_minmax(series: pd.Series) -> tuple[float, float]:
    valid = series.dropna()
    if len(valid) == 0:
        return (0.0, 0.0)
    return (float(valid.min()), float(valid.max()))


def filter_dataframe(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    dff = df.copy()

    if filters.get("selected_loc1") and "位置1" in dff.columns:
        dff = dff[dff["位置1"].isin(filters["selected_loc1"])]

    if filters.get("selected_loc2") and "位置2" in dff.columns:
        dff = dff[dff["位置2"].isin(filters["selected_loc2"])]

    if filters.get("selected_huxing") and "户型" in dff.columns:
        dff = dff[dff["户型"].isin(filters["selected_huxing"])]

    if "selected_price" in filters and "价格" in dff.columns:
        dff = dff[dff["价格"].between(filters["selected_price"][0], filters["selected_price"][1], inclusive="both")]

    if "selected_area" in filters and "面积" in dff.columns:
        dff = dff[dff["面积"].between(filters["selected_area"][0], filters["selected_area"][1], inclusive="both")]

    if "selected_subway" in filters and "距地铁距离(米)" in dff.columns:
        dff = dff[dff["距地铁距离(米)"].between(filters["selected_subway"][0], filters["selected_subway"][1], inclusive="both")]

    if filters.get("keyword_xiaoqu") and "小区" in dff.columns:
        dff = dff[dff["小区"].astype("string").str.contains(filters["keyword_xiaoqu"], case=False, na=False)]

    if filters.get("selected_files") and "数据文件" in dff.columns:
        dff = dff[dff["数据文件"].isin(filters["selected_files"])]

    return dff


def to_csv_download(df: pd.DataFrame) -> str:
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    return output.getvalue()


def get_top_bottom(df: pd.DataFrame, n: int, price_col: str = "价格") -> tuple[pd.DataFrame, pd.DataFrame]:
    valid = df.dropna(subset=[price_col])
    if len(valid) == 0:
        return pd.DataFrame(), pd.DataFrame()
    top = valid.nlargest(n, price_col)
    bottom = valid.nsmallest(n, price_col)
    return top, bottom


def parse_floor(floor_str):
    if pd.isna(floor_str):
        return None, None
    s = str(floor_str)
    current = None
    total = None
    if "/" in s:
        parts = s.split("/")
        if len(parts) >= 2:
            try:
                current = float(parts[0])
                total = float(parts[1])
            except:
                pass
    return current, total


def main() -> None:
    st.set_page_config(page_title="北京租房数据探索", layout="wide")
    st.title("北京租房数据探索（Danke）")

    df = load_data(DATA_DIR)
    init_session_state(df)

    if st.session_state.reset_filters:
        st.session_state.reset_filters = False
        st.rerun()

    with st.sidebar:
        st.header("筛选条件")

        loc1_options = sorted([x for x in df["位置1"].dropna().unique().tolist() if str(x) != ""]) if "位置1" in df.columns else []
        selected_loc1 = st.multiselect("位置1（多选）", options=loc1_options, default=loc1_options, key="loc1_filter")

        temp_df_for_loc2 = df[df["位置1"].isin(selected_loc1)] if selected_loc1 and "位置1" in df.columns else df
        loc2_options = sorted([x for x in temp_df_for_loc2["位置2"].dropna().unique().tolist() if str(x) != ""]) if "位置2" in df.columns else []
        selected_loc2 = st.multiselect("位置2（多选）", options=loc2_options, default=loc2_options, key="loc2_filter")

        huxing_options = sorted([x for x in df["户型"].dropna().unique().tolist() if str(x) != ""]) if "户型" in df.columns else []
        selected_huxing = st.multiselect("户型（多选）", options=huxing_options, default=huxing_options, key="huxing_filter")

        price_min, price_max = get_safe_minmax(df["价格"]) if "价格" in df.columns else (0, 10000)
        selected_price = st.slider(
            "价格范围",
            min_value=price_min,
            max_value=price_max,
            value=(price_min, price_max),
            step=10.0 if price_max - price_min >= 10 else 1.0,
            key="price_filter"
        )

        area_min, area_max = get_safe_minmax(df["面积"]) if "面积" in df.columns else (0, 200)
        selected_area = st.slider(
            "面积范围（㎡）",
            min_value=area_min,
            max_value=area_max,
            value=(area_min, area_max),
            step=1.0 if area_max - area_min >= 1 else 0.5,
            key="area_filter"
        )

        subway_min, subway_max = get_safe_minmax(df["距地铁距离(米)"]) if "距地铁距离(米)" in df.columns else (0, 5000)
        selected_subway = st.slider(
            "距地铁距离（米）",
            min_value=subway_min,
            max_value=subway_max,
            value=(subway_min, subway_max),
            step=50.0 if subway_max - subway_min >= 50 else 10.0,
            key="subway_filter"
        )

        keyword_xiaoqu = st.text_input("小区关键词搜索", "", key="xiaoqu_keyword")

        file_options = sorted(df["数据文件"].unique().tolist()) if "数据文件" in df.columns else []
        selected_files = st.multiselect("数据文件", options=file_options, default=file_options, key="file_filter")

        st.divider()
        
        if st.button("重置筛选", type="primary", use_container_width=True):
            st.session_state.reset_filters = True
            st.rerun()

    filters = {
        "selected_loc1": selected_loc1,
        "selected_loc2": selected_loc2,
        "selected_huxing": selected_huxing,
        "selected_price": selected_price,
        "selected_area": selected_area,
        "selected_subway": selected_subway,
        "keyword_xiaoqu": keyword_xiaoqu,
        "selected_files": selected_files,
    }

    dff = filter_dataframe(df, filters)

    c1, c2, c3, c4, c5 = st.columns(5)
    avg_price = float(np.nanmean(dff["价格"])) if "价格" in dff.columns else np.nan
    median_price = float(np.nanmedian(dff["价格"])) if "价格" in dff.columns else np.nan
    avg_unit = float(np.nanmean(dff["租金单价(元/㎡)"])) if "租金单价(元/㎡)" in dff.columns else np.nan
    median_unit = float(np.nanmedian(dff["租金单价(元/㎡)"])) if "租金单价(元/㎡)" in dff.columns else np.nan
    total_cnt = int(len(dff))

    c1.metric("平均月租（元）", "—" if not np.isfinite(avg_price) else f"{avg_price:.0f}")
    c2.metric("中位数月租（元）", "—" if not np.isfinite(median_price) else f"{median_price:.0f}")
    c3.metric("平均单价（元/㎡）", "—" if not np.isfinite(avg_unit) else f"{avg_unit:.1f}")
    c4.metric("中位数单价（元/㎡）", "—" if not np.isfinite(median_unit) else f"{median_unit:.1f}")
    c5.metric("房源总数", f"{total_cnt:,}")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["总览", "图表", "对比分析", "原始数据", "统计相关", "字段质量"])

    with tab1:
        st.subheader("关键房源展示")
        n_top_bottom = st.number_input("展示最贵/最便宜房源数量", min_value=1, max_value=20, value=5)
        top_df, bottom_df = get_top_bottom(dff, n_top_bottom)
        
        cols = [c for c in ["价格", "面积", "位置1", "位置2", "小区", "户型", "地铁", "编号"] if c in dff.columns]
        
        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown("**🏠 最贵房源**")
            if len(top_df) > 0:
                st.dataframe(top_df[cols], use_container_width=True)
            else:
                st.info("无数据")
        with col_right:
            st.markdown("**🏘️ 最便宜房源**")
            if len(bottom_df) > 0:
                st.dataframe(bottom_df[cols], use_container_width=True)
            else:
                st.info("无数据")

        st.divider()
        st.subheader("自动洞察")
        insights = []
        if len(dff) == 0:
            insights.append("当前筛选条件下无数据。")
        else:
            insights.append(f"当前样本量共 {len(dff)} 套房源。")
            
            if "位置1" in dff.columns and len(dff["位置1"].dropna()) > 0:
                loc1_counts = dff["位置1"].value_counts()
                if len(loc1_counts) > 0:
                    insights.append(f"房源最多的区域是 {loc1_counts.index[0]}，共 {loc1_counts.iloc[0]} 套。")
            
            if "租金单价(元/㎡)" in dff.columns and len(dff["租金单价(元/㎡)"].dropna()) > 0:
                try:
                    avg_by_loc1 = dff.groupby("位置1")["租金单价(元/㎡)"].mean().sort_values(ascending=False)
                    if len(avg_by_loc1) > 0:
                        insights.append(f"单价最高的区域是 {avg_by_loc1.index[0]}，平均单价 {avg_by_loc1.iloc[0]:.1f} 元/㎡。")
                except:
                    pass
            
            if "距地铁距离(米)" in dff.columns and len(dff["距地铁距离(米)"].dropna()) > 0:
                within_500 = (dff["距地铁距离(米)"] <= 500).sum()
                total_with_subway = dff["距地铁距离(米)"].notna().sum()
                if total_with_subway > 0:
                    ratio = within_500 / total_with_subway * 100
                    insights.append(f"距地铁500米内的房源占比 {ratio:.1f}%（共 {within_500} 套）。")

        for insight in insights:
            st.markdown(f"💡 {insight}")

    with tab2:
        st.info("💡 说明：由于Streamlit与Altair的刷选机制限制，当前图表支持框选查看子集，如需应用到全局筛选，请使用侧边栏筛选条件。")
        
        left1, right1 = st.columns(2)
        left2, right2 = st.columns(2)
        left3, right3 = st.columns(2)

        with left1:
            st.subheader("面积-价格散点图")
            base_scatter = dff.dropna(subset=["面积", "价格"])
            if len(base_scatter) > 0:
                color_col = "位置1" if "位置1" in base_scatter.columns else None
                scatter = (
                    alt.Chart(base_scatter)
                    .mark_circle(size=50, opacity=0.6)
                    .encode(
                        x=alt.X("面积:Q", title="面积（㎡）"),
                        y=alt.Y("价格:Q", title="价格（元/月）"),
                        tooltip=[c for c in ["价格", "面积", "位置1", "位置2", "小区", "地铁", "编号"] if c in base_scatter.columns],
                        color=alt.Color(f"{color_col}:N", title="位置1") if color_col else alt.value("#4C78A8"),
                    )
                )
                st.altair_chart(scatter.interactive(), use_container_width=True)
            else:
                st.info("无数据")

        with right1:
            st.subheader("月租直方图")
            price_hist_data = dff.dropna(subset=["价格"])
            if len(price_hist_data) > 0:
                bins = st.slider("分箱数", min_value=5, max_value=50, value=20, key="price_bins")
                use_log = st.checkbox("对数横轴", key="price_log")
                if use_log:
                    price_hist = (
                        alt.Chart(price_hist_data)
                        .mark_bar()
                        .encode(
                            x=alt.X("价格:Q", bin=alt.Bin(maxbins=bins), scale=alt.Scale(type="log")),
                            y=alt.Y("count()", title="套数")
                        )
                    )
                else:
                    price_hist = (
                        alt.Chart(price_hist_data)
                        .mark_bar()
                        .encode(
                            x=alt.X("价格:Q", bin=alt.Bin(maxbins=bins)),
                            y=alt.Y("count()", title="套数")
                        )
                    )
                st.altair_chart(price_hist, use_container_width=True)
            else:
                st.info("无数据")

        with left2:
            st.subheader("面积直方图")
            area_hist_data = dff.dropna(subset=["面积"])
            if len(area_hist_data) > 0:
                bins_area = st.slider("分箱数", min_value=5, max_value=50, value=20, key="area_bins")
                area_hist = (
                    alt.Chart(area_hist_data)
                    .mark_bar()
                    .encode(
                        x=alt.X("面积:Q", title="面积（㎡）", bin=alt.Bin(maxbins=bins_area)),
                        y=alt.Y("count()", title="套数")
                    )
                )
                st.altair_chart(area_hist, use_container_width=True)
            else:
                st.info("无数据")

        with right2:
            st.subheader("户型套数")
            huxing_data = dff.dropna(subset=["户型"])
            if len(huxing_data) > 0 and "户型" in dff.columns:
                chart_type = st.radio("图表类型", ["条形图", "饼图"], key="huxing_chart", horizontal=True)
                huxing_counts = huxing_data["户型"].value_counts().reset_index()
                huxing_counts.columns = ["户型", "套数"]
                if chart_type == "条形图":
                    huxing_chart = (
                        alt.Chart(huxing_counts)
                        .mark_bar()
                        .encode(
                            x=alt.X("套数:Q", title="套数"),
                            y=alt.Y("户型:N", title="户型", sort="-x")
                        )
                    )
                else:
                    huxing_chart = (
                        alt.Chart(huxing_counts)
                        .mark_arc()
                        .encode(
                            theta=alt.Theta("套数:Q"),
                            color=alt.Color("户型:N")
                        )
                    )
                st.altair_chart(huxing_chart, use_container_width=True)
            else:
                st.info("无数据")

        with left3:
            st.subheader("箱线图")
            box_data = dff.dropna(subset=["位置1", "价格", "租金单价(元/㎡)"])
            if len(box_data) > 0 and "位置1" in dff.columns:
                box_metric = st.selectbox("选择指标", ["价格", "租金单价(元/㎡)"], key="box_metric")
                box_chart = (
                    alt.Chart(box_data)
                    .mark_boxplot()
                    .encode(
                        x=alt.X("位置1:N", title="位置1"),
                        y=alt.Y(f"{box_metric}:Q", title=box_metric)
                    )
                )
                st.altair_chart(box_chart, use_container_width=True)
            else:
                st.info("无数据")

        with right3:
            st.subheader("距地铁距离分段平均单价")
            subway_data = dff.dropna(subset=["距地铁距离(米)", "租金单价(元/㎡)"])
            if len(subway_data) > 0:
                bins_subway = subway_data.copy()
                bins_subway["距离段"] = pd.cut(
                    bins_subway["距地铁距离(米)"],
                    bins=[0, 500, 1000, 2000, 3000, float("inf")],
                    labels=["0-500米", "500-1000米", "1000-2000米", "2000-3000米", "3000米以上"]
                )
                subway_avg = bins_subway.groupby("距离段")["租金单价(元/㎡)"].mean().reset_index()
                subway_chart = (
                    alt.Chart(subway_avg)
                    .mark_bar()
                    .encode(
                        x=alt.X("距离段:N", title="距离段", sort=None),
                        y=alt.Y("租金单价(元/㎡):Q", title="平均单价（元/㎡）")
                    )
                )
                st.altair_chart(subway_chart, use_container_width=True)
            else:
                st.info("无数据")

        if "楼层" in dff.columns:
            st.divider()
            st.subheader("楼层与单价关系")
            floor_data = dff.dropna(subset=["楼层", "租金单价(元/㎡)"])
            if len(floor_data) > 0:
                try:
                    floor_data["当前层"], floor_data["总层"] = zip(*floor_data["楼层"].apply(parse_floor))
                    floor_data = floor_data.dropna(subset=["当前层", "总层"])
                    if len(floor_data) > 0:
                        floor_chart = (
                            alt.Chart(floor_data)
                            .mark_circle()
                            .encode(
                                x=alt.X("当前层:Q", title="当前层"),
                                y=alt.Y("租金单价(元/㎡):Q", title="租金单价（元/㎡）")
                            )
                        )
                        st.altair_chart(floor_chart, use_container_width=True)
                    else:
                        st.info("无法解析楼层数据")
                except:
                    st.info("无法解析楼层数据")
            else:
                st.info("无数据")

    with tab3:
        st.subheader("位置一对比分析")
        if "位置1" in dff.columns and len(dff["位置1"].dropna()) > 0:
            compare_metric = st.selectbox("对比指标", ["套数", "均价", "单价均值", "单价中位数"], key="compare_metric")
            
            if compare_metric == "套数":
                compare_df = dff["位置1"].value_counts().reset_index()
                compare_df.columns = ["位置1", "数值"]
            elif compare_metric == "均价":
                compare_df = dff.groupby("位置1")["价格"].mean().reset_index()
                compare_df.columns = ["位置1", "数值"]
            elif compare_metric == "单价均值":
                compare_df = dff.groupby("位置1")["租金单价(元/㎡)"].mean().reset_index()
                compare_df.columns = ["位置1", "数值"]
            else:
                compare_df = dff.groupby("位置1")["租金单价(元/㎡)"].median().reset_index()
                compare_df.columns = ["位置1", "数值"]

            col_compare1, col_compare2 = st.columns([1, 1])
            with col_compare1:
                st.dataframe(compare_df, use_container_width=True)
            with col_compare2:
                compare_chart = (
                    alt.Chart(compare_df)
                    .mark_bar()
                    .encode(
                        x=alt.X("数值:Q", title=compare_metric),
                        y=alt.Y("位置1:N", title="位置1", sort="-x")
                    )
                )
                st.altair_chart(compare_chart, use_container_width=True)
        else:
            st.info("无位置1数据")

        st.divider()
        st.subheader("位置一×户型交叉热力图")
        if "位置1" in dff.columns and "户型" in dff.columns:
            cross_data = dff.dropna(subset=["位置1", "户型"])
            if len(cross_data) > 0:
                cross_metric = st.selectbox("热力图指标", ["套数", "平均单价"], key="cross_metric")
                if cross_metric == "套数":
                    cross_df = cross_data.groupby(["位置1", "户型"]).size().reset_index(name="数值")
                else:
                    cross_df = cross_data.groupby(["位置1", "户型"])["租金单价(元/㎡)"].mean().reset_index(name="数值")
                
                if len(cross_df) > 0 and len(cross_df["位置1"].unique()) * len(cross_df["户型"].unique()) * 0.2 <= len(cross_df):
                    heatmap = (
                        alt.Chart(cross_df)
                        .mark_rect()
                        .encode(
                            x=alt.X("户型:N", title="户型"),
                            y=alt.Y("位置1:N", title="位置1"),
                            color=alt.Color("数值:Q", title=cross_metric)
                        )
                    )
                    st.altair_chart(heatmap, use_container_width=True)
                else:
                    st.info("数据过于稀疏，暂不展示")
            else:
                st.info("无数据")
        else:
            st.info("缺少位置1或户型字段")

    with tab4:
        st.subheader("筛选后的数据")
        
        csv = to_csv_download(dff)
        st.download_button(
            label="📥 下载 CSV",
            data=csv,
            file_name="rent_data.csv",
            mime="text/csv",
        )
        
        if len(dff.columns) > 0:
            default_cols = [c for c in ["价格", "面积", "位置1", "位置2", "小区", "户型", "地铁", "楼层", "编号", "数据文件"] if c in dff.columns]
            available_cols = dff.columns.tolist()
            selected_cols = st.multiselect("选择显示列", available_cols, default=default_cols if default_cols else available_cols)
            
            st.dataframe(dff[selected_cols] if selected_cols else dff, use_container_width=True, height=600)
        else:
            st.dataframe(dff, use_container_width=True, height=600)

    with tab5:
        st.subheader("数值列相关系数")
        numeric_cols = dff.select_dtypes(include=[np.number]).columns.tolist()
        relevant_cols = [c for c in ["价格", "面积", "距地铁距离(米)", "租金单价(元/㎡)"] if c in numeric_cols]
        
        if len(relevant_cols) >= 2:
            corr_df = dff[relevant_cols].corr()
            corr_long = corr_df.stack().reset_index()
            corr_long.columns = ["变量1", "变量2", "相关系数"]
            
            col_corr1, col_corr2 = st.columns([1, 1])
            with col_corr1:
                st.dataframe(corr_df, use_container_width=True)
            with col_corr2:
                corr_heatmap = (
                    alt.Chart(corr_long)
                    .mark_rect()
                    .encode(
                        x=alt.X("变量1:N", title=""),
                        y=alt.Y("变量2:N", title=""),
                        color=alt.Color("相关系数:Q", scale=alt.Scale(domain=[-1, 1], scheme="redblue"))
                    )
                )
                st.altair_chart(corr_heatmap, use_container_width=True)
        else:
            st.info("数值列不足，无法计算相关系数")

    with tab6:
        st.subheader("字段与缺失值概览")
        info_df = pd.DataFrame(
            {
                "字段": dff.columns,
                "非空数": [int(dff[c].notna().sum()) for c in dff.columns],
                "缺失数": [int(dff[c].isna().sum()) for c in dff.columns],
                "缺失率": [float(dff[c].isna().mean()) for c in dff.columns],
                "dtype": [str(dff[c].dtype) for c in dff.columns],
            }
        ).sort_values("缺失率", ascending=False)
        st.dataframe(info_df, use_container_width=True, height=500)

        high_missing = info_df[info_df["缺失率"] > 0.5]
        if len(high_missing) > 0:
            st.divider()
            st.warning("⚠️ 高缺失率字段提醒：")
            for _, row in high_missing.iterrows():
                st.markdown(f"- **{row['字段']}**: 缺失率 {row['缺失率']:.1%}")

        st.divider()
        st.subheader("重复房源检测")
        duplicate_cols = []
        if "编号" in dff.columns:
            duplicate_by_id = dff.duplicated(subset=["编号"], keep=False)
            if duplicate_by_id.sum() > 0:
                duplicate_cols.append("编号")
                st.info(f"发现 {duplicate_by_id.sum()} 条可能重复房源（同编号）")
        
        if all(c in dff.columns for c in ["小区", "面积", "价格"]):
            duplicate_by_combo = dff.duplicated(subset=["小区", "面积", "价格"], keep=False)
            if duplicate_by_combo.sum() > 0:
                duplicate_cols.append("小区+面积+价格")
                st.info(f"发现 {duplicate_by_combo.sum()} 条可能重复房源（同小区同面积同价格）")
        
        if not duplicate_cols:
            st.success("未发现明显重复房源")


if __name__ == "__main__":
    main()
