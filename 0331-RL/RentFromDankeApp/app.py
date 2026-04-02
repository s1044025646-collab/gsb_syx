from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "RentFromDanke"


def get_data_hash(data_dir: Path) -> float:
    csv_paths = sorted(data_dir.glob("bj_danke_*.csv"))
    return max(p.stat().st_mtime for p in csv_paths) if csv_paths else 0.0


@st.cache_data(show_spinner=False)
def load_data(data_dir: Path, _hash: float) -> pd.DataFrame:
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
        df_all["当前楼层"] = s.str.extract(r"^(\d+)/", expand=False).astype("float")
        df_all["总楼层"] = s.str.extract(r"/(\d+)层", expand=False).astype("float")

    return df_all


def init_session_state() -> None:
    if "selection_active" not in st.session_state:
        st.session_state.selection_active = False
    if "selected_indices" not in st.session_state:
        st.session_state.selected_indices = set()
    if "reset_trigger" not in st.session_state:
        st.session_state.reset_trigger = 0


def reset_filters() -> None:
    st.session_state.selection_active = False
    st.session_state.selected_indices = set()
    st.session_state.reset_trigger += 1


def main() -> None:
    st.set_page_config(page_title="北京租房数据探索", layout="wide")
    init_session_state()

    data_hash = get_data_hash(DATA_DIR)
    df = load_data(DATA_DIR, data_hash)

    st.title("北京租房数据探索（Danke）")

    with st.sidebar:
        st.header("筛选")

        trigger = st.session_state.reset_trigger

        if "位置1" in df.columns:
            loc1_options = sorted([x for x in df["位置1"].dropna().unique().tolist() if str(x) != ""])
        else:
            loc1_options = []

        selected_loc1 = st.multiselect("位置1（多选）", options=loc1_options, default=loc1_options, key=f"loc1_{trigger}")

        if "位置2" in df.columns:
            if selected_loc1:
                loc2_df = df[df["位置1"].isin(selected_loc1)]
            else:
                loc2_df = df
            loc2_options = sorted([x for x in loc2_df["位置2"].dropna().unique().tolist() if str(x) != ""])
        else:
            loc2_options = []

        selected_loc2 = st.multiselect("位置2（多选）", options=loc2_options, default=loc2_options, key=f"loc2_{trigger}")

        if "户型" in df.columns:
            layout_options = sorted([x for x in df["户型"].dropna().unique().tolist() if str(x) != ""])
        else:
            layout_options = []

        selected_layout = st.multiselect("户型（多选）", options=layout_options, default=layout_options, key=f"layout_{trigger}")

        if "数据文件" in df.columns:
            file_options = sorted([x for x in df["数据文件"].dropna().unique().tolist() if str(x) != ""])
        else:
            file_options = []

        selected_files = st.multiselect("数据文件（多选）", options=file_options, default=file_options, key=f"files_{trigger}")

        st.divider()

        area_min = float(np.nanmin(df["面积"])) if "面积" in df.columns else 0.0
        area_max = float(np.nanmax(df["面积"])) if "面积" in df.columns else 0.0
        if not np.isfinite(area_min):
            area_min = 0.0
        if not np.isfinite(area_max):
            area_max = area_min

        selected_area = st.slider(
            "面积范围（㎡）",
            min_value=float(area_min),
            max_value=float(area_max),
            value=(float(area_min), float(area_max)),
            step=1.0,
            key=f"area_{trigger}",
        )

        price_min = float(np.nanmin(df["价格"])) if "价格" in df.columns else 0.0
        price_max = float(np.nanmax(df["价格"])) if "价格" in df.columns else 0.0
        if not np.isfinite(price_min):
            price_min = 0.0
        if not np.isfinite(price_max):
            price_max = price_min

        selected_price = st.slider(
            "价格范围（元/月）",
            min_value=float(price_min),
            max_value=float(price_max),
            value=(float(price_min), float(price_max)),
            step=10.0 if price_max - price_min >= 10 else 1.0,
            key=f"price_{trigger}",
        )

        subway_min = float(np.nanmin(df["距地铁距离(米)"])) if "距地铁距离(米)" in df.columns else 0.0
        subway_max = float(np.nanmax(df["距地铁距离(米)"])) if "距地铁距离(米)" in df.columns else 5000.0
        if not np.isfinite(subway_min):
            subway_min = 0.0
        if not np.isfinite(subway_max):
            subway_max = subway_min

        selected_subway = st.slider(
            "距地铁距离（米）",
            min_value=float(subway_min),
            max_value=float(subway_max),
            value=(float(subway_min), float(subway_max)),
            step=50.0,
            key=f"subway_{trigger}",
        )

        st.divider()

        keyword = st.text_input("小区关键词搜索", "", key=f"keyword_{trigger}")

        st.divider()

        if st.button("🔄 重置所有筛选", use_container_width=True):
            reset_filters()
            st.rerun()

    dff = df.copy()

    if selected_loc1 and "位置1" in dff.columns:
        dff = dff[dff["位置1"].isin(selected_loc1)]
    if selected_loc2 and "位置2" in dff.columns:
        dff = dff[dff["位置2"].isin(selected_loc2)]
    if selected_layout and "户型" in dff.columns:
        dff = dff[dff["户型"].isin(selected_layout)]
    if selected_files and "数据文件" in dff.columns:
        dff = dff[dff["数据文件"].isin(selected_files)]
    if "面积" in dff.columns:
        dff = dff[dff["面积"].between(selected_area[0], selected_area[1], inclusive="both")]
    if "价格" in dff.columns:
        dff = dff[dff["价格"].between(selected_price[0], selected_price[1], inclusive="both")]
    if "距地铁距离(米)" in dff.columns:
        dff = dff[dff["距地铁距离(米)"].between(selected_subway[0], selected_subway[1], inclusive="both")]
    if keyword and "小区" in dff.columns:
        dff = dff[dff["小区"].astype("string").str.contains(keyword, case=False, na=False)]

    if st.session_state.selection_active and st.session_state.selected_indices:
        dff = dff.loc[dff.index.isin(st.session_state.selected_indices)]

    tab_overview, tab_charts, tab_compare, tab_data, tab_quality = st.tabs(
        ["📊 总览", "📈 图表", "🔍 对比分析", "📋 数据表", "⚙️ 数据质量"]
    )

    with tab_overview:
        st.subheader("核心指标")

        c1, c2, c3, c4, c5 = st.columns(5)

        avg_unit = float(np.nanmean(dff["租金单价(元/㎡)"])) if "租金单价(元/㎡)" in dff.columns else np.nan
        med_unit = float(np.nanmedian(dff["租金单价(元/㎡)"])) if "租金单价(元/㎡)" in dff.columns else np.nan
        med_price = float(np.nanmedian(dff["价格"])) if "价格" in dff.columns else np.nan
        total_cnt = int(len(dff))

        c1.metric("平均单价（元/㎡）", "—" if not np.isfinite(avg_unit) else f"{avg_unit:.1f}")
        c2.metric("中位数单价（元/㎡）", "—" if not np.isfinite(med_unit) else f"{med_unit:.1f}")
        c3.metric("中位数月租（元/月）", "—" if not np.isfinite(med_price) else f"{med_price:.0f}")
        c4.metric("房源总数", f"{total_cnt:,}")
        c5.caption(f"数据文件数：{dff['数据文件'].nunique() if '数据文件' in dff.columns else '—'}")

        st.divider()

        col_left, col_right = st.columns([1, 1])

        with col_left:
            n_show = st.number_input("展示条数", min_value=1, max_value=20, value=5, step=1)
            st.subheader(f"🏆 最贵的 {n_show} 条房源")
            if "价格" in dff.columns and len(dff) > 0:
                top_expensive = dff.nlargest(n_show, "价格")[["价格", "面积", "位置1", "位置2", "小区", "户型"]].reset_index(drop=True)
                top_expensive.index = top_expensive.index + 1
                st.dataframe(top_expensive, use_container_width=True)
            else:
                st.info("无有效数据")

        with col_right:
            st.subheader(f"💰 最便宜的 {n_show} 条房源")
            if "价格" in dff.columns and len(dff) > 0:
                top_cheapest = dff.nsmallest(n_show, "价格")[["价格", "面积", "位置1", "位置2", "小区", "户型"]].reset_index(drop=True)
                top_cheapest.index = top_cheapest.index + 1
                st.dataframe(top_cheapest, use_container_width=True)
            else:
                st.info("无有效数据")

        st.divider()
        st.subheader("💡 数据洞察")

        if len(dff) == 0:
            st.warning("当前筛选条件下没有数据")
        else:
            insights = []
            insights.append(f"当前筛选下共有 **{len(dff)}** 套房源")

            if "位置1" in dff.columns and dff["位置1"].nunique() > 0:
                loc1_price = dff.groupby("位置1")["租金单价(元/㎡)"].median().dropna()
                if len(loc1_price) > 0:
                    highest_loc = loc1_price.idxmax()
                    highest_price = loc1_price.max()
                    insights.append(f"单价最高的行政区是 **{highest_loc}**，中位数单价 **{highest_price:.1f} 元/㎡**")

            if "距地铁距离(米)" in dff.columns:
                within_500 = (dff["距地铁距离(米)"] <= 500).sum()
                ratio = within_500 / len(dff) * 100
                insights.append(f"距地铁500米内的房源占比 **{ratio:.1f}%**（共{within_500}套）")

            for insight in insights:
                st.write(f"• {insight}")

            high_missing_cols = []
            for col in dff.columns:
                missing_rate = dff[col].isna().mean()
                if missing_rate > 0.3:
                    high_missing_cols.append(f"{col}（缺失率{missing_rate:.1%}）")

            if high_missing_cols:
                st.warning(f"⚠️ 以下字段缺失率较高：{', '.join(high_missing_cols)}")

            if "编号" in dff.columns:
                dup_count = dff["编号"].duplicated().sum()
                if dup_count > 0:
                    st.warning(f"⚠️ 发现 {dup_count} 条重复编号的房源，请留意")

    with tab_charts:
        st.info("💡 说明：在散点图或直方图上框选可作为额外筛选条件应用到全页，从侧边栏点「重置」可清除选择")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("月租分布直方图")
            base = dff.dropna(subset=["价格"])
            if len(base) > 0:
                bins = st.slider("分箱数", min_value=5, max_value=50, value=20, key="price_bins")
                use_log = st.toggle("对数横轴", False, key="price_log")
                hist_price = (
                    alt.Chart(base)
                    .mark_bar()
                    .encode(
                        x=alt.X("价格:Q", bin=alt.Bin(maxbins=bins), title="价格（元/月）", scale=alt.Scale(type="log" if use_log else "linear")),
                        y=alt.Y("count()", title="房源套数"),
                        tooltip=["count()"],
                    )
                    .interactive()
                )
                st.altair_chart(hist_price, use_container_width=True)
            else:
                st.info("无有效数据")

        with col2:
            st.subheader("面积分布直方图")
            base = dff.dropna(subset=["面积"])
            if len(base) > 0:
                bins = st.slider("分箱数", min_value=5, max_value=50, value=20, key="area_bins")
                hist_area = (
                    alt.Chart(base)
                    .mark_bar()
                    .encode(
                        x=alt.X("面积:Q", bin=alt.Bin(maxbins=bins), title="面积（㎡）"),
                        y=alt.Y("count()", title="房源套数"),
                        tooltip=["count()"],
                    )
                    .interactive()
                )
                st.altair_chart(hist_area, use_container_width=True)
            else:
                st.info("无有效数据")

        st.divider()

        col3, col4 = st.columns(2)

        with col3:
            st.subheader("户型套数分布")
            if "户型" in dff.columns and dff["户型"].nunique() > 0:
                chart_type = st.radio("图表类型", ["条形图", "饼图"], horizontal=True, key="layout_chart")
                layout_data = dff["户型"].value_counts().reset_index()
                layout_data.columns = ["户型", "套数"]

                if chart_type == "条形图":
                    chart_layout = (
                        alt.Chart(layout_data)
                        .mark_bar()
                        .encode(
                            x=alt.X("套数:Q", title="套数"),
                            y=alt.Y("户型:N", title="户型", sort="-x"),
                            tooltip=["户型", "套数"],
                        )
                        .interactive()
                    )
                else:
                    chart_layout = (
                        alt.Chart(layout_data)
                        .mark_arc()
                        .encode(
                            theta=alt.Theta("套数:Q"),
                            color=alt.Color("户型:N", legend=alt.Legend(title="户型")),
                            tooltip=["户型", "套数"],
                        )
                    )
                st.altair_chart(chart_layout, use_container_width=True)
            else:
                st.info("无有效数据")

        with col4:
            st.subheader("按位置1的箱线图")
            if {"位置1", "价格", "租金单价(元/㎡)"}.issubset(dff.columns) and dff["位置1"].nunique() > 1:
                box_metric = st.selectbox("选择指标", ["月租", "单价"], key="box_metric")
                metric_col = "价格" if box_metric == "月租" else "租金单价(元/㎡)"
                box_data = dff.dropna(subset=["位置1", metric_col])

                box_chart = (
                    alt.Chart(box_data)
                    .mark_boxplot()
                    .encode(
                        x=alt.X("位置1:N", title="行政区"),
                        y=alt.Y(f"{metric_col}:Q", title=box_metric),
                        color=alt.Color("位置1:N", legend=None),
                    )
                    .interactive()
                )
                st.altair_chart(box_chart, use_container_width=True)
            else:
                st.info("无足够数据")

        st.divider()

        col5, col6 = st.columns(2)

        with col5:
            st.subheader("距地铁距离分段均价")
            if "距地铁距离(米)" in dff.columns and dff["距地铁距离(米)"].notna().sum() > 0:
                bins = [0, 500, 1000, 1500, 2000, 3000, 10000]
                labels = ["0-500米", "500-1000米", "1000-1500米", "1500-2000米", "2000-3000米", "3000米以上"]
                subway_df = dff.dropna(subset=["距地铁距离(米)", "租金单价(元/㎡)"]).copy()
                subway_df["距离分段"] = pd.cut(subway_df["距地铁距离(米)"], bins=bins, labels=labels)
                subway_agg = subway_df.groupby("距离分段", observed=False)["租金单价(元/㎡)"].mean().reset_index()
                subway_agg.columns = ["距离分段", "平均单价"]

                subway_chart = (
                    alt.Chart(subway_agg)
                    .mark_bar()
                    .encode(
                        x=alt.X("距离分段:N", title="距地铁距离"),
                        y=alt.Y("平均单价:Q", title="平均单价（元/㎡）"),
                        tooltip=["距离分段", "平均单价"],
                    )
                    .interactive()
                )
                st.altair_chart(subway_chart, use_container_width=True)
            else:
                st.info("无有效数据")

        with col6:
            st.subheader("楼层与单价关系")
            if {"当前楼层", "租金单价(元/㎡)"}.issubset(dff.columns) and dff["当前楼层"].notna().sum() > 10:
                floor_df = dff.dropna(subset=["当前楼层", "租金单价(元/㎡)"]).copy()
                floor_chart = (
                    alt.Chart(floor_df)
                    .mark_circle(size=40, opacity=0.5)
                    .encode(
                        x=alt.X("当前楼层:Q", title="当前楼层"),
                        y=alt.Y("租金单价(元/㎡):Q", title="租金单价（元/㎡）"),
                        tooltip=["当前楼层", "租金单价(元/㎡)", "小区"],
                    )
                    .interactive()
                )
                st.altair_chart(floor_chart, use_container_width=True)
            else:
                st.info("无足够楼层数据")

        st.divider()

        col7, col8 = st.columns(2)

        with col7:
            st.subheader("数值列相关系数")
            numeric_cols = ["价格", "面积", "距地铁距离(米)", "租金单价(元/㎡)"]
            numeric_cols = [c for c in numeric_cols if c in dff.columns]
            if len(numeric_cols) >= 2:
                corr_df = dff[numeric_cols].corr().stack().reset_index()
                corr_df.columns = ["变量1", "变量2", "相关系数"]

                corr_heatmap = (
                    alt.Chart(corr_df)
                    .mark_rect()
                    .encode(
                        x=alt.X("变量1:N", title=""),
                        y=alt.Y("变量2:N", title=""),
                        color=alt.Color("相关系数:Q", scale=alt.Scale(scheme="redblue", domain=[-1, 1])),
                        tooltip=["变量1", "变量2", "相关系数"],
                    )
                )
                st.altair_chart(corr_heatmap, use_container_width=True)
            else:
                st.info("无足够数值列")

        with col8:
            st.subheader("位置1×户型 均价热力图")
            if {"位置1", "户型", "租金单价(元/㎡)"}.issubset(dff.columns):
                cross_df = dff.groupby(["位置1", "户型"], observed=False)["租金单价(元/㎡)"].median().reset_index()
                cross_df = cross_df.dropna()

                if len(cross_df) > 5:
                    cross_heatmap = (
                        alt.Chart(cross_df)
                        .mark_rect()
                        .encode(
                            x=alt.X("户型:N", title=""),
                            y=alt.Y("位置1:N", title=""),
                            color=alt.Color("租金单价(元/㎡):Q", title="中位数单价", scale=alt.Scale(scheme="viridis")),
                            tooltip=["位置1", "户型", "租金单价(元/㎡)"],
                        )
                    )
                    st.altair_chart(cross_heatmap, use_container_width=True)
                else:
                    st.info("交叉数据较稀疏")
            else:
                st.info("无有效数据")

        st.divider()
        st.subheader("面积-价格散点图")
        base = dff.dropna(subset=["面积", "价格"])
        if len(base) > 0:
            color_col = "位置1" if "位置1" in base.columns else None

            col_left, col_right = st.columns([3, 1])
            with col_right:
                st.caption("💡 图表筛选设置")
                area_min_chart = st.slider(
                    "筛选面积最小值",
                    min_value=float(base["面积"].min()),
                    max_value=float(base["面积"].max()),
                    value=float(base["面积"].min()),
                    step=1.0,
                )
                area_max_chart = st.slider(
                    "筛选面积最大值",
                    min_value=float(base["面积"].min()),
                    max_value=float(base["面积"].max()),
                    value=float(base["面积"].max()),
                    step=1.0,
                )
                price_min_chart = st.slider(
                    "筛选价格最小值",
                    min_value=float(base["价格"].min()),
                    max_value=float(base["价格"].max()),
                    value=float(base["价格"].min()),
                    step=10.0,
                )
                price_max_chart = st.slider(
                    "筛选价格最大值",
                    min_value=float(base["价格"].min()),
                    max_value=float(base["价格"].max()),
                    value=float(base["价格"].max()),
                    step=10.0,
                )
                if st.button("✅ 应用范围作为筛选", use_container_width=True):
                    selected = base[
                        base["面积"].between(area_min_chart, area_max_chart) &
                        base["价格"].between(price_min_chart, price_max_chart)
                    ].index
                    st.session_state.selection_active = True
                    st.session_state.selected_indices = set(selected)
                    st.rerun()

            with col_left:
                scatter = (
                    alt.Chart(base)
                    .mark_circle(size=50, opacity=0.6)
                    .encode(
                        x=alt.X("面积:Q", title="面积（㎡）"),
                        y=alt.Y("价格:Q", title="价格（元/月）"),
                        tooltip=[c for c in ["价格", "面积", "位置1", "位置2", "小区", "地铁", "编号"] if c in base.columns],
                        color=alt.Color(f"{color_col}:N", title="位置1") if color_col else alt.value("#4C78A8"),
                    )
                )
                st.altair_chart(scatter, use_container_width=True)

            st.caption("⚠️ 说明：由于 Altair 原生框选与 Streamlit 状态同步限制，采用右侧滑块实现图表范围筛选，保证全页数据一致性")
        else:
            st.info("无有效数据")

    with tab_compare:
        st.subheader("按位置1对比分析")
        if "位置1" in dff.columns and dff["位置1"].nunique() > 1:
            compare_metric = st.selectbox("选择对比指标", ["套数", "均价", "单价均值", "单价中位数"], key="compare_metric")

            agg_funcs = {
                "套数": ("编号", np.count_nonzero),
                "均价": ("价格", np.nanmean),
                "单价均值": ("租金单价(元/㎡)", np.nanmean),
                "单价中位数": ("租金单价(元/㎡)", np.nanmedian),
            }

            col, func = agg_funcs[compare_metric]
            compare_df = dff.groupby("位置1", observed=False).apply(lambda x: func(x[col])).reset_index()
            compare_df.columns = ["位置1", compare_metric]
            compare_df = compare_df.sort_values(compare_metric, ascending=False)

            col_chart, col_table = st.columns([2, 1])

            with col_chart:
                bar_chart = (
                    alt.Chart(compare_df)
                    .mark_bar()
                    .encode(
                        x=alt.X(f"{compare_metric}:Q", title=compare_metric),
                        y=alt.Y("位置1:N", title="行政区", sort="-x"),
                        tooltip=["位置1", compare_metric],
                    )
                    .interactive()
                )
                st.altair_chart(bar_chart, use_container_width=True)

            with col_table:
                st.dataframe(compare_df.set_index("位置1"), use_container_width=True)
        else:
            st.info("需要至少2个位置1的数据才能对比")

    with tab_data:
        st.subheader("筛选后的数据")

        col_export, col_cols = st.columns([1, 3])
        with col_export:
            csv = dff.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下载 CSV",
                data=csv,
                file_name="租房数据筛选结果.csv",
                mime="text/csv",
            )

        st.dataframe(
            dff,
            use_container_width=True,
            height=600,
            column_config={},
            hide_index=False,
        )

    with tab_quality:
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
        st.dataframe(info_df, use_container_width=True, height=520)


if __name__ == "__main__":
    main()
