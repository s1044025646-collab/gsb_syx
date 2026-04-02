from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# 数据仅读取同级目录下的 RentFromDanke 文件夹（不含应用代码）
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

    # 删除全空行（例如整行都是空/NaN）
    df_all = df_all.dropna(how="all")

    # 类型转换
    for col in ["价格", "面积"]:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce")

    # 特征工程：提取距地铁距离（米）
    if "地铁" in df_all.columns:
        s = df_all["地铁"].astype("string")
        # 兼容如：地铁：距2号线...积水潭站1300米 / ...站 650米
        df_all["距地铁距离(米)"] = (
            s.str.extract(r"(\d+)\s*米", expand=False).astype("float")
        )
    else:
        df_all["距地铁距离(米)"] = np.nan

    # 计算单价（元/㎡）
    if {"价格", "面积"}.issubset(df_all.columns):
        df_all["租金单价(元/㎡)"] = df_all["价格"] / df_all["面积"]
        df_all.loc[df_all["面积"] <= 0, "租金单价(元/㎡)"] = np.nan
    else:
        df_all["租金单价(元/㎡)"] = np.nan

    return df_all


def main() -> None:
    st.set_page_config(page_title="北京租房数据探索", layout="wide")
    st.title("北京租房数据探索（Danke）")

    df = load_data(DATA_DIR)

    with st.sidebar:
        st.header("筛选")

        if "位置1" in df.columns:
            options = sorted([x for x in df["位置1"].dropna().unique().tolist() if str(x) != ""])
        else:
            options = []

        selected_loc1 = st.multiselect("位置1（多选）", options=options, default=options)

        price_min = float(np.nanmin(df["价格"])) if "价格" in df.columns else 0.0
        price_max = float(np.nanmax(df["价格"])) if "价格" in df.columns else 0.0
        if not np.isfinite(price_min):
            price_min = 0.0
        if not np.isfinite(price_max):
            price_max = price_min

        selected_price = st.slider(
            "价格范围",
            min_value=float(price_min),
            max_value=float(price_max),
            value=(float(price_min), float(price_max)),
            step=10.0 if price_max - price_min >= 10 else 1.0,
        )

    dff = df.copy()
    if selected_loc1 and "位置1" in dff.columns:
        dff = dff[dff["位置1"].isin(selected_loc1)]
    if "价格" in dff.columns:
        dff = dff[dff["价格"].between(selected_price[0], selected_price[1], inclusive="both")]

    # 顶部指标
    c1, c2, c3 = st.columns([1, 1, 2])
    avg_unit = float(np.nanmean(dff["租金单价(元/㎡)"])) if "租金单价(元/㎡)" in dff.columns else np.nan
    total_cnt = int(len(dff))

    c1.metric("平均单价（元/㎡）", "—" if not np.isfinite(avg_unit) else f"{avg_unit:.1f}")
    c2.metric("房源总数", f"{total_cnt:,}")
    c3.caption(f"数据文件数：{dff['数据文件'].nunique() if '数据文件' in dff.columns else '—'}")

    tab1, tab2, tab3 = st.tabs(["图表", "数据表", "字段概览"])

    with tab1:
        left, right = st.columns(2, gap="large")

        with left:
            st.subheader("面积-价格散点图（按位置1着色）")
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

        with right:
            st.subheader("租金单价随地铁距离变化趋势")
            trend_df = dff.dropna(subset=["距地铁距离(米)", "租金单价(元/㎡)"]).copy()
            if len(trend_df) == 0:
                st.info("当前筛选条件下，没有足够的地铁距离数据可绘制趋势图。")
            else:
                # 过滤极端异常值，避免趋势线被少量离群点拉偏
                q1 = trend_df["租金单价(元/㎡)"].quantile(0.01)
                q99 = trend_df["租金单价(元/㎡)"].quantile(0.99)
                trend_df = trend_df[trend_df["租金单价(元/㎡)"].between(q1, q99)]

                pts = (
                    alt.Chart(trend_df)
                    .mark_circle(size=35, opacity=0.25)
                    .encode(
                        x=alt.X("距地铁距离(米):Q", title="距地铁距离（米）"),
                        y=alt.Y("租金单价(元/㎡):Q", title="租金单价（元/㎡）"),
                        tooltip=[c for c in ["租金单价(元/㎡)", "距地铁距离(米)", "价格", "面积", "位置1", "位置2", "小区"] if c in trend_df.columns],
                    )
                )
                loess = (
                    alt.Chart(trend_df)
                    .transform_loess("距地铁距离(米)", "租金单价(元/㎡)", bandwidth=0.3)
                    .mark_line(color="#F58518", size=3)
                    .encode(
                        x="距地铁距离(米):Q",
                        y="租金单价(元/㎡):Q",
                    )
                )
                st.altair_chart((pts + loess).interactive(), use_container_width=True)

    with tab2:
        st.subheader("筛选后的数据（可滚动查看）")
        st.dataframe(dff, use_container_width=True, height=520)

    with tab3:
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
