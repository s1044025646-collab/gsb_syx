from pathlib import Path
import hashlib

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


def get_data_dir_hash(data_dir: Path) -> str:
    csv_paths = sorted(data_dir.glob("bj_danke_*.csv"))
    hash_str = ""
    for p in csv_paths:
        mtime = p.stat().st_mtime
        hash_str += f"{p.name}:{mtime};"
    return hashlib.md5(hash_str.encode()).hexdigest()[:12]


DATA_DIR = Path(__file__).resolve().parent.parent / "RentFromDanke"
DATA_HASH = get_data_dir_hash(DATA_DIR)


@st.cache_data(show_spinner=False)
def load_data(data_dir: Path, cache_buster: str) -> pd.DataFrame:
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

    if "楼层" in df_all.columns:
        s = df_all["楼层"].astype("string")
        df_all["当前楼层"] = s.str.extract(r"(\d+)", expand=False).astype("float")
        df_all["总楼层"] = s.str.extract(r"共(\d+)层", expand=False).astype("float")

    df_all["_row_id"] = df_all.index.astype(str)
    return df_all


def reset_filters() -> None:
    st.session_state.selected_loc1 = []
    st.session_state.selected_loc2 = []
    st.session_state.selected_house_type = []
    st.session_state.selected_data_files = []
    st.session_state.price_range = st.session_state.default_price_range
    st.session_state.area_range = st.session_state.default_area_range
    st.session_state.subway_range = st.session_state.default_subway_range
    st.session_state.community_keyword = ""
    st.session_state.selection_active = False
    st.session_state.selected_row_ids = []


def init_session_state(df: pd.DataFrame) -> None:
    if "initialized" not in st.session_state:
        price_min = float(np.nanmin(df["价格"])) if "价格" in df.columns else 0.0
        price_max = float(np.nanmax(df["价格"])) if "价格" in df.columns else 0.0
        area_min = float(np.nanmin(df["面积"])) if "面积" in df.columns else 0.0
        area_max = float(np.nanmax(df["面积"])) if "面积" in df.columns else 0.0
        subway_min = float(np.nanmin(df["距地铁距离(米)"])) if "距地铁距离(米)" in df.columns else 0.0
        subway_max = float(np.nanmax(df["距地铁距离(米)"])) if "距地铁距离(米)" in df.columns else 5000.0

        st.session_state.default_price_range = (
            float(price_min) if np.isfinite(price_min) else 0.0,
            float(price_max) if np.isfinite(price_max) else 10000.0,
        )
        st.session_state.default_area_range = (
            float(area_min) if np.isfinite(area_min) else 0.0,
            float(area_max) if np.isfinite(area_max) else 200.0,
        )
        st.session_state.default_subway_range = (
            float(subway_min) if np.isfinite(subway_min) else 0.0,
            float(subway_max) if np.isfinite(subway_max) else 5000.0,
        )
        st.session_state.selected_loc1 = []
        st.session_state.selected_loc2 = []
        st.session_state.selected_house_type = []
        st.session_state.selected_data_files = []
        st.session_state.price_range = st.session_state.default_price_range
        st.session_state.area_range = st.session_state.default_area_range
        st.session_state.subway_range = st.session_state.default_subway_range
        st.session_state.community_keyword = ""
        st.session_state.selection_active = False
        st.session_state.selected_row_ids = []
        st.session_state.initialized = True


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    dff = df.copy()

    if st.session_state.selection_active and st.session_state.selected_row_ids:
        dff = dff[dff["_row_id"].isin(st.session_state.selected_row_ids)]
    else:
        if st.session_state.selected_loc1 and "位置1" in dff.columns:
            dff = dff[dff["位置1"].isin(st.session_state.selected_loc1)]

        if st.session_state.selected_loc2 and "位置2" in dff.columns:
            dff = dff[dff["位置2"].isin(st.session_state.selected_loc2)]

        if st.session_state.selected_house_type and "户型" in dff.columns:
            dff = dff[dff["户型"].isin(st.session_state.selected_house_type)]

        if st.session_state.selected_data_files and "数据文件" in dff.columns:
            dff = dff[dff["数据文件"].isin(st.session_state.selected_data_files)]

        if "价格" in dff.columns:
            dff = dff[dff["价格"].between(st.session_state.price_range[0], st.session_state.price_range[1], inclusive="both")]

        if "面积" in dff.columns:
            dff = dff[dff["面积"].between(st.session_state.area_range[0], st.session_state.area_range[1], inclusive="both")]

        if "距地铁距离(米)" in dff.columns:
            dff = dff[dff["距地铁距离(米)"].between(st.session_state.subway_range[0], st.session_state.subway_range[1], inclusive="both")]

        if st.session_state.community_keyword and "小区" in dff.columns:
            dff = dff[dff["小区"].astype("string").str.contains(st.session_state.community_keyword, case=False, na=False)]

    return dff


def safe_nanmean(series: pd.Series) -> float:
    val = np.nanmean(series)
    return val if np.isfinite(val) else np.nan


def safe_nanmedian(series: pd.Series) -> float:
    val = np.nanmedian(series)
    return val if np.isfinite(val) else np.nan


def format_metric(val: float, fmt: str = ".1f") -> str:
    if not np.isfinite(val):
        return "—"
    return f"{val:{fmt}}"


def generate_insights(dff: pd.DataFrame) -> list[str]:
    insights = []
    n = len(dff)
    if n == 0:
        return ["当前筛选条件下无数据。"]

    insights.append(f"当前样本量：{n:,} 套房源")

    if "位置1" in dff.columns and dff["位置1"].notna().any():
        loc1_stats = dff.groupby("位置1")["租金单价(元/㎡)"].agg(["median", "count"]).dropna()
        if len(loc1_stats) > 0:
            highest_loc = loc1_stats["median"].idxmax()
            highest_price = loc1_stats.loc[highest_loc, "median"]
            insights.append(f"单价最高的区域：{highest_loc}，中位数 {format_metric(highest_price)} 元/㎡")

    if "距地铁距离(米)" in dff.columns:
        within_500m = (dff["距地铁距离(米)"] <= 500).sum()
        ratio = within_500m / n * 100
        insights.append(f"距地铁 500 米内房源占比：{within_500m:,} 套 ({ratio:.1f}%)")

    if "户型" in dff.columns and dff["户型"].notna().any():
        top_type = dff["户型"].value_counts().idxmax()
        top_count = dff["户型"].value_counts().max()
        insights.append(f"最常见户型：{top_type}，共 {top_count:,} 套")

    return insights


def check_data_quality(df: pd.DataFrame) -> list[str]:
    warnings = []
    missing_rates = df.isna().mean()
    high_missing = missing_rates[missing_rates > 0.5]
    for col, rate in high_missing.items():
        warnings.append(f"⚠️ 字段「{col}」缺失率较高：{rate:.1%}")

    dup_keys = ["编号"] if "编号" in df.columns else ["小区", "面积", "价格"]
    if all(k in df.columns for k in dup_keys):
        dups = df.duplicated(subset=dup_keys, keep=False).sum()
        if dups > 0:
            warnings.append(f"🔍 发现 {dups:,} 条疑似重复房源（基于 {','.join(dup_keys)} 判断）")

    return warnings


def get_corr_heatmap(df: pd.DataFrame, cols: list[str]):
    valid_cols = [c for c in cols if c in df.columns and df[c].dtype in [np.float64, np.int64]]
    if len(valid_cols) < 2:
        return None
    corr = df[valid_cols].corr().stack().reset_index(name="correlation")
    corr.columns = ["x", "y", "correlation"]

    chart = alt.Chart(corr).mark_rect().encode(
        x=alt.X("x:N", title=""),
        y=alt.Y("y:N", title=""),
        color=alt.Color("correlation:Q", title="相关系数", scale=alt.Scale(scheme="redblue", domain=[-1, 1])),
        tooltip=["x", "y", alt.Tooltip("correlation:Q", format=".2f")]
    ).properties(title="数值字段相关系数热力图")

    text = chart.mark_text(baseline="middle").encode(
        text=alt.Text("correlation:Q", format=".2f"),
        color=alt.condition(
            alt.datum.correlation > 0.5,
            alt.value("white"),
            alt.value("black")
        )
    )
    return chart + text


def main() -> None:
    st.set_page_config(page_title="北京租房数据探索", layout="wide")
    st.title("北京租房数据探索（Danke）")

    df = load_data(DATA_DIR, DATA_HASH)
    init_session_state(df)

    with st.sidebar:
        st.header("筛选条件")

        loc1_options = sorted([x for x in df["位置1"].dropna().unique().tolist() if str(x) != ""]) if "位置1" in df.columns else []
        selected_loc1 = st.multiselect("位置1", options=loc1_options, default=st.session_state.selected_loc1)

        if selected_loc1 and "位置2" in df.columns:
            loc2_options = sorted([x for x in df[df["位置1"].isin(selected_loc1)]["位置2"].dropna().unique().tolist() if str(x) != ""])
        elif "位置2" in df.columns:
            loc2_options = sorted([x for x in df["位置2"].dropna().unique().tolist() if str(x) != ""])
        else:
            loc2_options = []
        selected_loc2 = st.multiselect("位置2（随位置1更新）", options=loc2_options, default=st.session_state.selected_loc2)

        house_type_options = sorted([x for x in df["户型"].dropna().unique().tolist() if str(x) != ""]) if "户型" in df.columns else []
        selected_house_type = st.multiselect("户型", options=house_type_options, default=st.session_state.selected_house_type)

        data_file_options = sorted(df["数据文件"].dropna().unique().tolist()) if "数据文件" in df.columns else []
        selected_data_files = st.multiselect("数据文件", options=data_file_options, default=st.session_state.selected_data_files)

        st.session_state.price_range = st.slider(
            "价格范围（元/月）",
            min_value=st.session_state.default_price_range[0],
            max_value=st.session_state.default_price_range[1],
            value=st.session_state.price_range,
            step=50.0,
        )

        st.session_state.area_range = st.slider(
            "面积范围（㎡）",
            min_value=st.session_state.default_area_range[0],
            max_value=st.session_state.default_area_range[1],
            value=st.session_state.area_range,
            step=1.0,
        )

        st.session_state.subway_range = st.slider(
            "距地铁距离（米）",
            min_value=st.session_state.default_subway_range[0],
            max_value=st.session_state.default_subway_range[1],
            value=st.session_state.subway_range,
            step=50.0,
        )

        community_keyword = st.text_input("小区关键词搜索", value=st.session_state.community_keyword)

        st.button("🔄 一键重置所有筛选", on_click=reset_filters, use_container_width=True)

        st.session_state.selected_loc1 = selected_loc1
        st.session_state.selected_loc2 = selected_loc2
        st.session_state.selected_house_type = selected_house_type
        st.session_state.selected_data_files = selected_data_files
        st.session_state.community_keyword = community_keyword

        if st.session_state.selection_active:
            st.info("📌 当前正在使用图表框选的子集，侧边栏筛选暂不生效")
            if st.button("清除图表选择", use_container_width=True):
                st.session_state.selection_active = False
                st.session_state.selected_row_ids = []
                st.rerun()

    dff = filter_dataframe(df)

    st.subheader("核心指标")
    c1, c2, c3, c4, c5 = st.columns(5)
    avg_unit = safe_nanmean(dff["租金单价(元/㎡)"])
    median_price = safe_nanmedian(dff["价格"])
    median_unit = safe_nanmedian(dff["租金单价(元/㎡)"])
    total_cnt = int(len(dff))

    c1.metric("平均单价（元/㎡）", format_metric(avg_unit))
    c2.metric("中位数月租（元）", format_metric(median_price, ".0f"))
    c3.metric("中位数单价（元/㎡）", format_metric(median_unit))
    c4.metric("房源总数", f"{total_cnt:,}")
    c5.metric("数据文件数", dff["数据文件"].nunique() if "数据文件" in dff.columns else "—")

    tab_overview, tab_charts, tab_compare, tab_table, tab_stats, tab_quality = st.tabs(
        ["📊 总览", "📈 图表", "🆚 区域对比", "📋 数据表", "🔢 统计", "✅ 数据质量"]
    )

    with tab_overview:
        st.subheader("💡 数据洞察")
        insights = generate_insights(dff)
        for insight in insights:
            st.write(f"- {insight}")

        st.subheader("🔝 价格极值展示")
        col1, col2 = st.columns([1, 5])
        with col1:
            top_n = st.number_input("显示条数 N", min_value=1, max_value=20, value=5)

        display_cols = [c for c in ["价格", "面积", "租金单价(元/㎡)", "位置1", "位置2", "小区", "户型"] if c in dff.columns]
        if len(dff) > 0 and "价格" in dff.columns:
            most_expensive = dff.nlargest(top_n, "价格")[display_cols]
            cheapest = dff.nsmallest(top_n, "价格")[display_cols]

            left, right = st.columns(2)
            with left:
                st.caption(f"💰 最贵的 {top_n} 套")
                st.dataframe(most_expensive, use_container_width=True, hide_index=True)
            with right:
                st.caption(f"💸 最便宜的 {top_n} 套")
                st.dataframe(cheapest, use_container_width=True, hide_index=True)

        st.subheader("📍 面积-价格散点图")
        base = dff.dropna(subset=["面积", "价格"])
        color_col = "位置1" if "位置1" in base.columns else None

        scatter = (
            alt.Chart(base)
            .mark_circle(size=50, opacity=0.6)
            .encode(
                x=alt.X("面积:Q", title="面积（㎡）"),
                y=alt.Y("价格:Q", title="价格（元/月）"),
                tooltip=[c for c in ["价格", "面积", "位置1", "位置2", "小区", "地铁", "编号"] if c in base.columns],
                color=alt.Color(f"{color_col}:N", title="位置1") if color_col else alt.value("#4C78A8"),
            )
            .interactive()
        )
        st.altair_chart(scatter, use_container_width=True)

        st.caption("💡 图表子集筛选：通过下方面积/价格区间精确选择")
        col1, col2 = st.columns(2)
        with col1:
            sel_area_min = st.number_input("筛选最小面积", min_value=0.0, max_value=200.0, value=float(base["面积"].min()))
            sel_price_min = st.number_input("筛选最小价格", min_value=0.0, max_value=20000.0, value=float(base["价格"].min()))
        with col2:
            sel_area_max = st.number_input("筛选最大面积", min_value=0.0, max_value=200.0, value=float(base["面积"].max()))
            sel_price_max = st.number_input("筛选最大价格", min_value=0.0, max_value=20000.0, value=float(base["价格"].max()))

        if st.button("🔍 应用此区间作为全局筛选", type="primary"):
            subset = base[
                (base["面积"].between(sel_area_min, sel_area_max)) &
                (base["价格"].between(sel_price_min, sel_price_max))
            ]
            if len(subset) > 0:
                st.session_state.selected_row_ids = subset["_row_id"].tolist()
                st.session_state.selection_active = True
                st.success(f"✅ 已选中 {len(subset)} 个数据点，全页按此子集重算")
                st.rerun()
            else:
                st.warning("此区间内无数据")

    with tab_charts:
        left, right = st.columns(2)

        with left:
            st.subheader("月租分布直方图")
            bins = st.slider("分箱数", min_value=5, max_value=50, value=20, key="rent_bins")
            if "价格" in dff.columns and dff["价格"].notna().any():
                use_log = st.checkbox("对数横轴", key="rent_log")
                hist = alt.Chart(dff.dropna(subset=["价格"])).mark_bar().encode(
                    x=alt.X("价格:Q", bin=alt.Bin(maxbins=bins), title="月租（元）", scale=alt.Scale(type="log") if use_log else alt.Scale()),
                    y=alt.Y("count()", title="套数"),
                    tooltip=[alt.Tooltip("价格:Q", bin=True, title="月租区间"), "count()"]
                )
                st.altair_chart(hist, use_container_width=True)

        with right:
            st.subheader("面积分布直方图")
            if "面积" in dff.columns and dff["面积"].notna().any():
                hist = alt.Chart(dff.dropna(subset=["面积"])).mark_bar().encode(
                    x=alt.X("面积:Q", bin=alt.Bin(maxbins=20), title="面积（㎡）"),
                    y=alt.Y("count()", title="套数"),
                    tooltip=[alt.Tooltip("面积:Q", bin=True, title="面积区间"), "count()"]
                )
                st.altair_chart(hist, use_container_width=True)

        left, right = st.columns(2)

        with left:
            st.subheader("户型分布")
            if "户型" in dff.columns and dff["户型"].notna().any():
                chart_type = st.radio("图表类型", ["条形图", "饼图"], horizontal=True)
                type_counts = dff["户型"].value_counts().reset_index()
                type_counts.columns = ["户型", "套数"]
                if chart_type == "条形图":
                    bar = alt.Chart(type_counts).mark_bar().encode(
                        x=alt.X("套数:Q", title="套数"),
                        y=alt.Y("户型:N", title="户型", sort="-x"),
                        tooltip=["户型", "套数"]
                    )
                    st.altair_chart(bar, use_container_width=True)
                else:
                    pie = alt.Chart(type_counts).mark_arc().encode(
                        theta="套数:Q",
                        color="户型:N",
                        tooltip=["户型", "套数"]
                    )
                    st.altair_chart(pie, use_container_width=True)

        with right:
            st.subheader("区域箱线图")
            box_metric = st.selectbox("选择指标", ["租金单价(元/㎡)", "价格"], key="box_metric")
            if "位置1" in dff.columns and box_metric in dff.columns:
                box_df = dff.dropna(subset=["位置1", box_metric])
                if len(box_df) > 0:
                    box = alt.Chart(box_df).mark_boxplot().encode(
                        x=alt.X("位置1:N", title=""),
                        y=alt.Y(f"{box_metric}:Q", title=box_metric),
                        color="位置1:N"
                    )
                    st.altair_chart(box, use_container_width=True)

        left, right = st.columns(2)

        with left:
            st.subheader("距地铁距离分段均价")
            if "距地铁距离(米)" in dff.columns and dff["距地铁距离(米)"].notna().any():
                bins = [0, 500, 1000, 1500, 2000, 3000, 99999]
                labels = ["0-500米", "500-1000米", "1000-1500米", "1500-2000米", "2000-3000米", "3000米以上"]
                subway_df = dff.dropna(subset=["距地铁距离(米)", "租金单价(元/㎡)"]).copy()
                subway_df["距离分段"] = pd.cut(subway_df["距地铁距离(米)"], bins=bins, labels=labels)
                subway_avg = subway_df.groupby("距离分段", observed=False)["租金单价(元/㎡)"].median().reset_index()
                bar = alt.Chart(subway_avg).mark_bar().encode(
                    x=alt.X("距离分段:N", title="距地铁距离", sort=labels),
                    y=alt.Y("租金单价(元/㎡):Q", title="中位数单价（元/㎡）"),
                    tooltip=["距离分段", alt.Tooltip("租金单价(元/㎡):Q", format=".1f")]
                )
                st.altair_chart(bar, use_container_width=True)

        with right:
            st.subheader("楼层与单价关系")
            floor_cols = ["当前楼层", "总楼层", "楼层"]
            has_floor = any(c in dff.columns for c in floor_cols) and dff["租金单价(元/㎡)"].notna().any()
            if has_floor:
                floor_col = "当前楼层" if "当前楼层" in dff.columns else "楼层"
                if floor_col == "当前楼层":
                    floor_df = dff.dropna(subset=["当前楼层", "租金单价(元/㎡)"])
                    if len(floor_df) > 0:
                        scatter = alt.Chart(floor_df).mark_circle(opacity=0.5).encode(
                            x=alt.X("当前楼层:Q", title="楼层"),
                            y=alt.Y("租金单价(元/㎡):Q", title="单价（元/㎡）"),
                            tooltip=["当前楼层", "租金单价(元/㎡)"]
                        )
                        st.altair_chart(scatter, use_container_width=True)
                else:
                    st.info("楼层字段解析信息不足，跳过绘图")
            else:
                st.info("暂无楼层数据")

        st.subheader("相关分析")
        corr_cols = ["价格", "面积", "租金单价(元/㎡)", "距地铁距离(米)", "当前楼层"]
        corr_chart = get_corr_heatmap(dff, corr_cols)
        if corr_chart:
            st.altair_chart(corr_chart, use_container_width=True)
        else:
            st.info("有效数值字段不足，无法计算相关性")

        st.subheader("位置-户型交叉热力图")
        if "位置1" in dff.columns and "户型" in dff.columns:
            cross_df = dff.groupby(["位置1", "户型"], observed=False).size().reset_index(name="套数")
            cross_df = cross_df[cross_df["套数"] >= 3]
            if len(cross_df) > 5:
                heatmap = alt.Chart(cross_df).mark_rect().encode(
                    x="位置1:N",
                    y="户型:N",
                    color="套数:Q",
                    tooltip=["位置1", "户型", "套数"]
                )
                st.altair_chart(heatmap, use_container_width=True)
            else:
                st.info("交叉单元格数据过于稀疏，跳过热力图")

    with tab_compare:
        st.subheader("区域指标对比")
        if "位置1" in dff.columns:
            agg_method = st.radio("聚合方式", ["均值", "中位数"], horizontal=True)
            agg_func = "mean" if agg_method == "均值" else "median"

            compare_df = dff.groupby("位置1", observed=False).agg({
                "价格": agg_func,
                "租金单价(元/㎡)": agg_func,
                "面积": "count"
            }).reset_index()
            compare_df.columns = ["位置1", "平均月租", "平均单价", "套数"]
            compare_df = compare_df.sort_values("套数", ascending=False)

            left, right = st.columns(2)
            with left:
                st.dataframe(compare_df.round(1), use_container_width=True, hide_index=True)
            with right:
                metric = st.selectbox("对比指标", ["套数", "平均月租", "平均单价"])
                bar = alt.Chart(compare_df).mark_bar().encode(
                    x=alt.X(f"{metric}:Q", title=metric),
                    y=alt.Y("位置1:N", title="", sort="-x"),
                    tooltip=["位置1", metric]
                )
                st.altair_chart(bar, use_container_width=True)

    with tab_table:
        st.subheader("筛选后的数据")

        if len(dff) > 0:
            csv = dff.drop(columns=["_row_id"]).to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下载 CSV（UTF-8 with BOM）",
                data=csv,
                file_name="租房筛选结果.csv",
                mime="text/csv",
            )

            hide_cols = st.multiselect("隐藏列（可选）", options=[c for c in dff.columns if c != "_row_id"])
            show_cols = [c for c in dff.columns if c not in hide_cols and c != "_row_id"]
            st.dataframe(
                dff[show_cols],
                use_container_width=True,
                height=600,
                hide_index=True,
                column_config={
                    "价格": st.column_config.NumberColumn("价格", format="%d"),
                    "面积": st.column_config.NumberColumn("面积", format="%.1f"),
                    "租金单价(元/㎡)": st.column_config.NumberColumn("单价", format="%.1f"),
                }
            )

    with tab_stats:
        st.subheader("描述性统计")
        num_cols = dff.select_dtypes(include=[np.number]).columns.drop(["_row_id"], errors="ignore").tolist()
        if num_cols:
            stats_df = dff[num_cols].describe().T.round(2)
            st.dataframe(stats_df, use_container_width=True)

    with tab_quality:
        st.subheader("字段与缺失值概览")
        info_df = pd.DataFrame(
            {
                "字段": [c for c in dff.columns if c != "_row_id"],
                "非空数": [int(dff[c].notna().sum()) for c in dff.columns if c != "_row_id"],
                "缺失数": [int(dff[c].isna().sum()) for c in dff.columns if c != "_row_id"],
                "缺失率": [float(dff[c].isna().mean()) for c in dff.columns if c != "_row_id"],
                "dtype": [str(dff[c].dtype) for c in dff.columns if c != "_row_id"],
            }
        ).sort_values("缺失率", ascending=False)
        st.dataframe(info_df, use_container_width=True, height=400)

        warnings = check_data_quality(dff)
        if warnings:
            st.subheader("⚠️ 数据质量提醒")
            for w in warnings:
                st.write(w)

    with st.expander("📝 关于双向联动的实现说明"):
        st.markdown("""
        **当前实现的联动方案（兼容 Streamlit 1.30）：**

        1. 在「总览」标签页观察面积-价格散点图的分布
        2. 通过下方的面积/价格数值输入框，输入要筛选的区间范围
        3. 点击「应用此区间作为全局筛选」按钮
        4. 此时侧边栏会显示「正在使用图表框选的子集」，所有图表、指标、表格都会按选中的子集计算
        5. 点击侧边栏的「清除图表选择」或「一键重置所有筛选」可返回正常筛选模式

        **技术说明：**
        由于 Streamlit 1.30 版本不支持 Altair 图表原生刷选事件回调，
        本方案采用区间数值映射到离散筛选的折中方案，通过 `st.session_state`
        显式维护选择状态并规定优先级：
        - 图表选择子集优先于侧边栏筛选
        - 重置操作会同时清除两种状态
        """)


if __name__ == "__main__":
    main()
