import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="ICT碳足迹",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'total' not in st.session_state:
    st.session_state.total = 0
if 'saving' not in st.session_state:
    st.session_state.saving = 0

# ==================== 用户友好的侧边栏参数 ====================
with st.sidebar:
    st.header("⚙️ 参数设置")
    st.info("💡 根据您的实际情况选择，系统会自动计算碳排放量")

    with st.expander("📱 设备参数", expanded=False):
        phone_brand = st.selectbox(
            "手机品牌",
            ["苹果 iPhone", "三星 Galaxy", "华为", "小米", "OPPO/VIVO", "其他品牌"],
            index=0,
            help="不同品牌的生产工艺和供应链碳强度不同"
        )
        # 修正：根据碳信托数据，智能手机平均碳足迹约60-120kg CO₂
        phone_carbon_map = {
            "苹果 iPhone": 75,      # iPhone 14 Pro约70-80kg
            "三星 Galaxy": 68,       # Galaxy S23约65-70kg
            "华为": 65,              # 旗舰机型约60-70kg
            "小米": 55,              # 约50-60kg
            "OPPO/VIVO": 52,         # 约50-55kg
            "其他品牌": 58           # 行业平均值
        }

        estimated_phone_carbon = phone_carbon_map[phone_brand]
        st.caption(f"估算生产碳排放: **{estimated_phone_carbon} kg CO₂**")
        st.caption("_数据参考：碳信托、苹果环境报告、三星可持续发展报告_")

    with st.expander("📺 视频服务", expanded=False):
        video_platform = st.selectbox(
            "常用视频平台",
            ["YouTube/Netflix", "哔哩哔哩/爱奇艺", "抖音/快手", "视频会议(Teams/Zoom)"],
            index=0,
            help="不同平台的服务器能效和能源结构不同"
        )
        video_quality = st.radio(
            "常用视频质量",
            ["480p（标清）", "720p（高清）", "1080p（全高清）", "4K（超高清）"],
            index=1
        )

        # 修正：根据IEA数据，视频流媒体平均0.03-0.08 kg CO₂/小时
        platform_factor = {
            "YouTube/Netflix": 1.0,      # 全球平均
            "哔哩哔哩/爱奇艺": 1.1,      # 中国电力碳强度较高
            "抖音/快手": 0.6,            # 短视频，传输量小
            "视频会议(Teams/Zoom)": 0.4   # 优化传输，能耗较低
        }
        # 修正：根据网飞研究，画质对带宽和能耗影响非线性
        quality_factor = {
            "480p（标清）": 0.15,        # 约0.3GB/小时
            "720p（高清）": 0.4,         # 约0.7GB/小时
            "1080p（全高清）": 1.0,      # 约1.5GB/小时（基准）
            "4K（超高清）": 2.5          # 约3-7GB/小时
        }

        base_intensity = 0.055  # 基准：0.055 kg CO₂/小时（基于平均电网强度）
        video_intensity = base_intensity * platform_factor[video_platform] * quality_factor[video_quality]

        st.caption(f"视频流媒体强度: **{video_intensity:.3f} kg CO₂/小时**")
        st.caption("_数据参考：IEA、Carbon Brief、网飞可持续发展报告_")

    with st.expander("📺 视频会议", expanded=False):
        meeting_quality = st.select_slider(
            "视频会议质量",
            options=["音频优先", "平衡模式", "高清视频"],
            value="平衡模式"
        )
        meeting_factor = {"音频优先": 0.2, "平衡模式": 0.5, "高清视频": 0.8}
        meeting_intensity = 0.022 * meeting_factor[meeting_quality]  # 基准0.022 kg/h
        st.caption(f"视频会议强度: **{meeting_intensity:.3f} kg CO₂/小时**")

    with st.expander("✈️ 旅行替代", expanded=False):
        travel_type = st.selectbox(
            "被替代的出行方式",
            ["国内航班", "国际航班", "高铁", "自驾车", "公共交通"],
            index=0
        )
        travel_distance = st.radio(
            "典型旅行距离",
            ["短途 (<500km)", "中途 (500-1000km)", "长途 (1000-3000km)", "国际 (>3000km)"],
            index=1
        )

        # 修正：根据IPCC、DEFRA排放因子数据库（每人公里CO₂当量）
        travel_factor_map = {
            "国内航班": {  # 国内短途航班效率较低
                "短途 (<500km)": 0.275,
                "中途 (500-1000km)": 0.195,
                "长途 (1000-3000km)": 0.170,
                "国际 (>3000km)": 0.155
            },
            "国际航班": {  # 长途国际航班效率较高
                "短途 (<500km)": 0.25,
                "中途 (500-1000km)": 0.18,
                "长途 (1000-3000km)": 0.155,
                "国际 (>3000km)": 0.142  # 宽体机长途效率高
            },
            "高铁": {  # 电气化高铁，与电网碳强度相关
                "短途 (<500km)": 0.027,
                "中途 (500-1000km)": 0.025,
                "长途 (1000-3000km)": 0.024,
                "国际 (>3000km)": 0.024
            },
            "自驾车": {  # 假设汽油车，1.5L排量，单人
                "短途 (<500km)": 0.185,
                "中途 (500-1000km)": 0.175,
                "长途 (1000-3000km)": 0.165,
                "国际 (>3000km)": 0.165
            },
            "公共交通": {  # 城际大巴/火车
                "短途 (<500km)": 0.032,
                "中途 (500-1000km)": 0.030,
                "长途 (1000-3000km)": 0.028,
                "国际 (>3000km)": 0.026
            }
        }
        distance_map = {
            "短途 (<500km)": 300,
            "中途 (500-1000km)": 750,
            "长途 (1000-3000km)": 2000,
            "国际 (>3000km)": 5000
        }

        flight_factor = travel_factor_map[travel_type][travel_distance]
        typical_distance = distance_map[travel_distance]

        st.caption(f"{travel_type}排放因子: **{flight_factor:.3f} kg CO₂/公里·人**")
        st.caption(f"典型距离: **{typical_distance} 公里**")
        st.caption("_数据参考：IPCC、DEFRA、IEA交通报告_")

    with st.expander("⚡ 能源结构", expanded=False):
        region = st.selectbox(
            "您所在地区",
            ["欧洲（高绿电）", "美国（中等）", "中国（中等偏上）", "印度（高煤电）", "其他"],
            index=2
        )

        # 修正：基于IEA 2023年电网碳强度数据（kg CO₂/kWh）
        region_factor = {
            "欧洲（高绿电）": 0.23,      # 欧盟平均：约230g/kWh
            "美国（中等）": 0.37,        # 美国平均：约370g/kWh
            "中国（中等偏上）": 0.52,    # 中国平均：约520g/kWh
            "印度（高煤电）": 0.72,      # 印度平均：约720g/kWh
            "其他": 0.45                 # 全球平均：约450g/kWh
        }

        electricity_carbon = region_factor[region]

        green_data_center = st.checkbox(
            "选择使用绿色数据中心服务",
            value=False,
            help="如AWS、Google Cloud的可再生能源区域，可降低60-80%碳排放"
        )

        if green_data_center:
            electricity_carbon *= 0.35  # 使用100%可再生能源的数据中心

        st.caption(f"电力碳强度: **{electricity_carbon:.2f} kg CO₂/kWh**")
        st.caption("_数据参考：IEA 2023年电力报告、各国电网数据_")

    with st.expander("🔧 高级设置", expanded=False):
        st.warning("以下为直接碳排放参数设置，仅供专家参考")

        override_mode = st.checkbox("手动覆盖计算参数")

        if override_mode:
            video_intensity = st.slider(
                "视频流媒体强度 (kg CO₂/小时)",
                min_value=0.05, max_value=0.3, value=video_intensity, step=0.01
            )

            meeting_intensity = st.slider(
                "视频会议强度 (kg CO₂/小时)",
                min_value=0.02, max_value=0.1, value=meeting_intensity, step=0.01
            )

            estimated_phone_carbon = st.slider(
                "手机生产碳排放 (kg CO₂)",
                min_value=20, max_value=100, value=estimated_phone_carbon, step=1  # 去掉小数点
            )

            flight_factor = st.slider(
                "旅行排放因子 (kg CO₂/公里)",
                min_value=0.15, max_value=0.35, value=flight_factor, step=0.01
            )

    # 参数摘要卡片
    st.markdown("---")
    st.markdown("### 📊 计算参数摘要")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("设备生产排放", f"{estimated_phone_carbon} kg")
        st.metric("视频流媒体强度", f"{video_intensity:.3f} kg/h")

    with col2:
        st.metric("旅行排放因子", f"{flight_factor:.2f} kg/km")
        st.metric("电力碳强度", f"{electricity_carbon:.2f}")

    st.markdown("---")


# ==================== 碳足迹计算 ====================
st.title("ICT产业碳足迹可视化评估")
st.markdown("全球变化与人类活动 - 期末项目")

col1, col2 = st.columns(2)
with col1:
    st.header("🔴 作为排放源")

    st.subheader("你的数字习惯")
    video = st.slider("每天视频流媒体（小时）", 0.0, 12.0, 2.0, 0.5)
    meetings = st.slider("每周视频会议（小时）", 0.0, 10.0, 3.0, 0.5)
    phone_years = st.selectbox("手机换机周期", [1, 2, 3, 4, 5], index=1)

    if st.button("计算我的碳足迹"):
        video_carbon = video * video_intensity * 365
        meeting_carbon = meetings * meeting_intensity * 52
        phone_carbon = estimated_phone_carbon / phone_years

        st.session_state.total = video_carbon + meeting_carbon + phone_carbon

        st.success(f"""
        **你的年数字碳足迹：{st.session_state.total:.1f} kg CO₂**
        构成分析：
        - 视频流媒体：{video_carbon:.1f} kg
        - 视频会议：{meeting_carbon:.1f} kg
        - 设备生产：{phone_carbon:.1f} kg
        """)

with col2:
    st.header("🟢 作为减排工具")

    st.subheader("视频会议替代差旅")
    km = st.slider("替代的距离（公里/年）", 100, 5000, 1000, 100)

    if st.button("计算减排潜力"):
        # 使用侧边栏参数
        flight_carbon = km * flight_factor
        meeting_carbon = meetings * meeting_intensity * 52
        st.session_state.saving = flight_carbon - meeting_carbon

        st.info(f"""
        **减排量：{st.session_state.saving:.1f} kg CO₂**

        对比分析（基于当前参数设置）：
        - ✈️ 旅行排放：{flight_carbon:.1f} kg ({flight_factor} kg/公里 × {km}公里)
        - 💻 视频会议排放：{meeting_carbon:.1f} kg ({meeting_intensity} kg/小时 x 每年视频会议时长)
        - ✅ 净减排：{st.session_state.saving:.1f} kg
        """)

# ==================== 对比图表 ====================
st.markdown("---")
st.header("双重角色对比")

# 创建两列，左边放说明，右边放图表
col_text, col_chart = st.columns([1, 1.5])

with col_text:
    st.markdown(f"""
    ### 📈 基于当前参数的对比

    **当前参数设置**：
    - 视频流媒体：{video_intensity:.3f} kg CO₂/小时
    - 视频会议：{meeting_intensity} kg CO₂/小时  
    - 旅行排放：{flight_factor} kg CO₂/公里

    **计算方法**：\\
    个人碳足迹 = 使用强度 × 时间 × 参数 \\
    减排潜力 = 传统方式排放 - ICT方式排放

    > 💡 **参数敏感性**：
    > 这些参数基于行业平均值，
    > 实际值会因地区、技术、能源结构而异
    > 可以在侧边栏调整探索不同情景
    """)

with col_chart:
    # 更小的图表
    fig, ax = plt.subplots(figsize=(6, 3))

    categories = ['Digital Footprint', 'Reduction Potential']
    values = [st.session_state.total, st.session_state.saving]

    if st.session_state.total > 0 or st.session_state.saving > 0:
        # 自动调整数值范围，确保对比明显
        if st.session_state.saving > 10 * st.session_state.total:
            # 如果减排远大于排放，调整显示比例
            values = [st.session_state.total, st.session_state.saving / 10]
            categories = ['Digital Footprint', 'Reduction Potential (÷10)']
        elif st.session_state.total > 10 * st.session_state.saving:
            values = [st.session_state.total, st.session_state.saving * 10]
            categories = ['Digital Footprint', 'Reduction Potential (×10)']

        colors = ['#ff6b6b', '#51cf66']
        bars = ax.bar(categories, values, color=colors)

        ax.set_ylabel('kg CO₂', fontsize=10)
        ax.set_title('ICT: Emissions vs. Reduction', fontsize=12, fontweight='bold')

        # 数值标签
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 5,
                    f'{value:.1f} kg', ha='center', va='bottom', fontsize=9)

        # 设置y轴
        max_val = max(values) if max(values) > 0 else 100
        ax.set_ylim(0, max_val * 1.2)
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)

        # 紧凑布局
        plt.tight_layout()

        # 禁用宽度自适应，保持原始尺寸
        st.pyplot(fig, use_container_width=False)
    else:
        st.info("👆 请先计算碳足迹和减排潜力")

# ==================== 情景模拟与敏感性分析（合并版）====================
st.markdown("---")
st.header("情景模拟与敏感性分析")

# 第一部分：预设情景模拟
st.subheader("📋 预设减排情景")
st.write("探索不同技术路径和政策选择的减排效果")

# 创建选项卡，让用户在预设情景和自定义调整之间切换
tab1, tab2, tab3 = st.tabs(["🚀 技术优化情景", "📱 设备生命周期优化", "🎯 自定义参数调整"])

with tab1:
    # 技术优化情景
    st.markdown("#### 绿色ICT技术推广")

    tech_col1, tech_col2 = st.columns(2)

    with tech_col1:
        # 绿色数据中心情景
        st.markdown("**🔋 数据中心绿电化**")
        green_power_ratio = st.slider(
            "数据中心绿电比例 (%)",
            0, 100, 50, 10,
            key="green_power_ratio"
        )

        # 计算影响
        if st.session_state.total > 0 and green_power_ratio > 0:
            # 假设视频相关活动的碳足迹减少比例与绿电比例成正比
            video_contribution = video * video_intensity * 365
            meeting_contribution = meetings * meeting_intensity * 52
            tech_reduction = (video_contribution + meeting_contribution) * (green_power_ratio / 100)

            st.metric(
                "碳足迹减少",
                f"{tech_reduction:.1f} kg",
                delta=f"-{tech_reduction / st.session_state.total * 100:.1f}%",
                delta_color="normal"
            )

    with tech_col2:
        # 视频压缩技术改进
        st.markdown("**🎬 高效视频编码技术**")
        compression_improvement = st.slider(
            "视频数据压缩率提升 (%)",
            0, 50, 20, 5,
            key="compression_improvement"
        )

        if st.session_state.total > 0 and compression_improvement > 0:
            video_data_reduction = compression_improvement / 100
            compression_reduction = video * video_intensity * 365 * video_data_reduction

            st.metric(
                "碳足迹减少",
                f"{compression_reduction:.1f} kg",
                delta=f"-{compression_reduction / st.session_state.total * 100:.1f}%",
                delta_color="normal"
            )

with tab2:
    # 设备生命周期优化
    st.markdown("#### 延长设备使用周期")

    lifecycle_col1, lifecycle_col2 = st.columns(2)

    with lifecycle_col1:
        st.markdown("**📱 手机使用年限延长**")
        current_phone_years = st.select_slider(
            "当前使用年限",
            options=[1, 2, 3, 4, 5],
            value=phone_years,
            key="current_phone_years"
        )

        target_phone_years = st.select_slider(
            "目标使用年限",
            options=[2, 3, 4, 5, 6],
            value=min(phone_years + 1, 6),
            key="target_phone_years"
        )

        if current_phone_years < target_phone_years:
            current_annual = estimated_phone_carbon / current_phone_years
            target_annual = estimated_phone_carbon / target_phone_years
            reduction = current_annual - target_annual

            st.metric(
                "年减排量",
                f"{reduction:.1f} kg",
                delta=f"-{reduction / current_annual * 100:.1f}%",
                delta_color="normal"
            )

    with lifecycle_col2:
        st.markdown("**💻 设备共享与云化**")
        device_sharing = st.slider(
            "设备利用率提升 (%)",
            0, 100, 50, 10,
            help="通过设备共享、云计算替代本地计算"
        )

        if st.session_state.total > 0 and device_sharing > 0:
            # 假设设备碳排放部分可以通过云化减少
            device_contribution = estimated_phone_carbon / phone_years
            sharing_reduction = device_contribution * (device_sharing / 100) * 0.5  # 系数调整

            st.metric(
                "年减排量",
                f"{sharing_reduction:.1f} kg",
                delta=f"-{sharing_reduction / device_contribution * 100:.1f}%",
                delta_color="normal"
            )

with tab3:
    # 自定义参数调整与敏感性分析
    st.markdown("#### 🎛️ 自定义参数调整")
    st.write("手动调整参数，观察对结果的影响")

    # 动态调整滑块
    adj_col1, adj_col2, adj_col3 = st.columns(3)

    with adj_col1:
        # 视频流媒体强度调整
        st.markdown("**📺 视频流媒体强度**")
        video_adjustment = st.slider(
            "调整比例 (±%)",
            -50, 50, 0, 5,
            key="video_adjustment"
        )

        if st.session_state.total > 0:
            adjusted_video_intensity = video_intensity * (1 + video_adjustment / 100)
            original_video_part = video * video_intensity * 365
            adjusted_video_part = video * adjusted_video_intensity * 365
            video_change = adjusted_video_part - original_video_part
            video_change_percent = (video_change / st.session_state.total) * 100

            st.metric(
                "影响",
                f"{video_change:+.1f} kg",
                delta=f"{video_change_percent:+.1f}%",
                delta_color="inverse" if video_change > 0 else "normal"
            )

    with adj_col2:
        # 手机碳排放调整
        st.markdown("**📱 手机生产碳排放**")
        phone_adjustment = st.slider(
            "调整比例 (±%)",
            -50, 50, 0, 5,
            key="phone_adjustment"
        )

        if st.session_state.total > 0:
            adjusted_phone_carbon = estimated_phone_carbon * (1 + phone_adjustment / 100)
            original_phone_part = estimated_phone_carbon / phone_years
            adjusted_phone_part = adjusted_phone_carbon / phone_years
            phone_change = adjusted_phone_part - original_phone_part
            phone_change_percent = (phone_change / st.session_state.total) * 100

            st.metric(
                "影响",
                f"{phone_change:+.1f} kg",
                delta=f"{phone_change_percent:+.1f}%",
                delta_color="inverse" if phone_change > 0 else "normal"
            )

    with adj_col3:
        # 飞机排放因子调整
        st.markdown("**✈️ 旅行排放因子**")
        flight_adjustment = st.slider(
            "调整比例 (±%)",
            -50, 50, 0, 5,
            key="flight_adjustment"
        )

        if st.session_state.saving > 0:
            adjusted_flight_factor = flight_factor * (1 + flight_adjustment / 100)
            original_flight_emission = km * flight_factor
            adjusted_flight_emission = km * adjusted_flight_factor
            flight_change = adjusted_flight_emission - original_flight_emission
            flight_change_percent = (
                                                flight_change / original_flight_emission) * 100 if original_flight_emission > 0 else 0

            st.metric(
                "对减排影响",
                f"{flight_change:+.1f} kg",
                delta=f"{flight_change_percent:+.1f}%",
                delta_color="inverse" if flight_change > 0 else "normal"
            )

# 第二部分：敏感性分析图表
st.markdown("---")
st.subheader("📊 参数敏感性分析")

if st.session_state.total > 0:
    # 计算每个参数变化10%对结果的影响
    sensitivity_data = []

    # 定义参数及其对总碳足迹的贡献计算方法
    param_contributions = {
        "视频流媒体": {
            "value": video_intensity,
            "contribution": video * video_intensity * 365,
            "unit": "kg/小时"
        },
        "视频会议": {
            "value": meeting_intensity,
            "contribution": meetings * meeting_intensity * 52,
            "unit": "kg/小时"
        },
        "手机生产": {
            "value": estimated_phone_carbon,
            "contribution": estimated_phone_carbon / phone_years,
            "unit": "kg"
        }
    }

    # 计算敏感性
    for param_name, param_info in param_contributions.items():
        if param_info["contribution"] > 0:
            # 参数增加10%的影响
            change_10_percent = param_info["contribution"] * 0.1
            sensitivity_percent = (change_10_percent / st.session_state.total) * 100

            sensitivity_data.append({
                "参数": param_name,
                "敏感性": abs(sensitivity_percent),
                "变化方向": "+" if sensitivity_percent > 0 else "-",
                "贡献占比": (param_info["contribution"] / st.session_state.total) * 100
            })

    if sensitivity_data:
        # 按敏感性排序
        sensitivity_data.sort(key=lambda x: x["敏感性"], reverse=True)

        # 创建水平条形图
        fig_sens, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        # 左侧：敏感性条形图
        # 修改这里：将参数名称改为英文缩写
        param_names = []
        for d in sensitivity_data:
            if d["参数"] == "视频流媒体":
                param_names.append("Video Streaming")
            elif d["参数"] == "视频会议":
                param_names.append("Video Conferencing")
            elif d["参数"] == "手机生产":
                param_names.append("Phone Production")
            else:
                param_names.append(d["参数"])  # 其他情况保留原名

        sensitivities = [d["敏感性"] for d in sensitivity_data]

        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'][:len(param_names)]
        bars1 = ax1.barh(param_names, sensitivities, color=colors)

        # 修改这里：图表标签改为英文
        ax1.set_xlabel('Impact Change (%)')
        ax1.set_title('Sensitivity Ranking')
        ax1.set_xlim(0, max(sensitivities) * 1.2)

        # 在条形上添加数值
        for bar, value in zip(bars1, sensitivities):
            width = bar.get_width()
            ax1.text(width + 0.2, bar.get_y() + bar.get_height() / 2,
                     f'{value:.1f}%', va='center', ha='left')

        # 右侧：贡献占比饼图
        # 修改这里：饼图标签也使用英文
        labels = []
        for d in sensitivity_data:
            if d["参数"] == "视频流媒体":
                labels.append("Video Streaming")
            elif d["参数"] == "视频会议":
                labels.append("Video Conferencing")
            elif d["参数"] == "手机生产":
                labels.append("Phone Production")
            else:
                labels.append(d["参数"])

        sizes = [d["贡献占比"] for d in sensitivity_data]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1'][:len(labels)]

        # 如果有其他贡献，添加"其他"类别
        total_covered = sum(sizes)
        if total_covered < 100:
            labels.append("Other")
            sizes.append(100 - total_covered)
            colors.append('#95A5A6')

        # 修改这里：饼图标题改为英文
        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                startangle=90, textprops={'fontsize': 10})
        ax2.set_title('Footprint Composition')

        plt.tight_layout()
        st.pyplot(fig_sens)

        # 分析结论
        most_sensitive = sensitivity_data[0]
        st.info(f"""
        **分析结论**：

        1. **最敏感参数**：**{most_sensitive['参数']}**
           - 该参数变化10%会导致总碳足迹变化 **{most_sensitive['敏感性']:.1f}%**
           - 在总碳足迹中占比 **{most_sensitive['贡献占比']:.1f}%**

        2. **政策启示**：
           - 针对{most_sensitive['参数']}采取措施，减排效果最显著
           - 提高该参数的准确性对评估结果至关重要

        3. **个人行动建议**：
           - 关注最敏感参数对应的生活习惯
           - 通过调整这些习惯，实现最高效的碳减排
        """)
    else:
        st.info("请先计算您的碳足迹，以查看敏感性分析")
else:
    st.info("👆 请先计算碳足迹，以启用情景模拟与敏感性分析功能")

# ==================== 课程总结 ====================
st.markdown("---")
with st.expander("📚 数据来源与假设", expanded=True):
    st.markdown("""
    **数据来源参考：**
    1. **手机碳排放**：基于Apple环境报告、华为可持续发展报告等
    2. **视频流媒体**：IEA数据中心能耗报告，考虑PUE=1.5
    3. **航空排放**：ICAO碳计算器，考虑平均载客率
    4. **区域电力**：IEA各国电力结构数据2023

    **主要假设：**
    - 视频流媒体基准：1080p画质，数据中心PUE=1.5
    - 手机生产碳排放包括原材料、制造、运输
    - 航空排放包括CO2和非CO2温室气体
    - 电力碳排放因子基于2023年平均值

    **不确定性说明：**
    本工具使用简化模型，计算结果为估算值，
    实际碳排放因具体设备、使用习惯、电网实时状况而异。
    """)
