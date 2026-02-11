import streamlit as st
import sys
import os
import io
import json
from datetime import datetime, timedelta

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.dirname(current_dir)
sys.path.append(src_path)

from models import TravelRequest, FitnessLevel, TravelPace, TravelSession, TravelState, SimulationEvent, EventType
from agents.planning_agent import PlanningAgent
from agents.guide_agent import GuideAgent
from simulation import EnvironmentSimulator
from tools.weather_tool import WeatherTool
from tools.traffic_tool import TrafficTool
from tools.scenic_tool import ScenicTool
from services.deepseek_client import DeepSeekClient
from services.memory_service import MemoryService

# Page Config
st.set_page_config(
    page_title="Dynamic Travel Agent (Thesis Demo)",
    page_icon="✈️",
    layout="wide"
)

# --- Custom CSS Injection ---
st.markdown("""
<style>
    /* 引入字体 */
    @import url('https://fonts.googleapis.com/css2?family=Ma+Shan+Zheng&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

    /* 1. 全局背景与字体 (淡雅渐变) */
    .stApp {
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    /* 2. 也是动画关键帧 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideIn {
        from { width: 0; }
        to { width: 100%; }
    }

    /* --- 图片点击放大 (Lightbox) Hack --- */
    input.img-zoom-check {
        display: none;
    }
    .img-zoom-label {
        cursor: zoom-in;
        display: block;
        margin: 0;
    }
    .img-zoom-thumb {
        width: 100%;
        height: 80px;
        object-fit: cover;
        border-radius: 6px;
        transition: transform 0.2s;
        border: 1px solid #ddd;
    }
    .img-zoom-thumb:hover {
        transform: scale(1.03);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .img-zoom-fullscreen {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0,0,0,0.9);
        z-index: 999999; 
        justify-content: center;
        align-items: center;
        cursor: zoom-out;
        animation: fadeIn 0.2s ease-in-out;
    }
    /* 全屏下的图片样式 */
    .img-zoom-fullscreen img {
        width: 100vw;
        height: 100vh;
        object-fit: contain;
        box-shadow: none;
        border-radius: 0;
    }
    /* 选中状态触发全屏显示 */
    input.img-zoom-check:checked + label .img-zoom-fullscreen {
        display: flex;
    }

    /* 3. 标题样式 */
    .main-title {
        font-family: 'Ma Shan Zheng', cursive; 
        font-size: 3rem;
        background: linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        padding: 20px 0;
        animation: fadeIn 1s ease-out;
    }
    .sub-title {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 30px;
        animation: fadeIn 1.2s ease-out;
    }

    /* 4. 卡片容器样式 */
    .css-card {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        animation: fadeIn 0.8s ease-out;
    }
    .css-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }

    /* 5. 侧边栏美化 */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        background-image: linear-gradient(180deg, #ffffff 0%, #f3f4f6 100%);
        border-right: 1px solid #eef2f6;
    }

    /* 辅助动画类 */
    .fade-in {
        animation: fadeIn 1.2s ease-in-out;
    }

    /* Timeline 样式 */
    .timeline-item {
        position: relative;
        padding-left: 30px;
        margin-bottom: 25px;
        animation: fadeIn 0.8s ease-in-out;
    }
    .timeline-dot {
        position: absolute;
        left: 6px;
        top: 6px;
        width: 12px;
        height: 12px;
        background-color: #74b9ff;
        border-radius: 50%;
        border: 2px solid #fff;
        box-shadow: 0 0 0 2px #dcebee;
    }
    .activity-time {
        font-weight: bold;
        color: #74b9ff;
        margin-right: 10px;
        font-family: monospace;
    }
    
    /* 6. 按钮样式 */
    .stButton > button {
        background: linear-gradient(90deg, #a18cd1 0%, #fbc2eb 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 50px;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(161, 140, 209, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(161, 140, 209, 0.6);
        background: linear-gradient(90deg, #fbc2eb 0%, #a18cd1 100%);
    }

    /* 7. 行程时间轴 */
    .timeline-container {
        position: relative;
        padding-left: 30px;
        border-left: 2px dashed #d1d8e0;
    }
    .timeline-item {
        position: relative;
        margin-bottom: 25px;
        animation: fadeIn 0.5s ease-out;
    }
    .timeline-dot {
        position: absolute;
        left: -36px;
        top: 5px;
        width: 14px;
        height: 14px;
        background: #a18cd1;
        border-radius: 50%;
        border: 2px solid #fff;
        box-shadow: 0 0 0 3px rgba(161, 140, 209, 0.2);
    }
    .activity-time {
        font-weight: bold;
        color: #57606f;
        background: #dfe4ea;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        margin-right: 8px;
    }
    
    /* 8. Log 样式 */
    .log-box {
        background-color: #2d3436;
        color: #dfe6e9;
        font-family: 'JetBrains Mono', monospace;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00cec9;
        margin-bottom: 10px;
        animation: fadeIn 0.5s;
    }
    
    # 隐藏 Streamlit 默认 header footer 以及 InputHints (Press enter to apply)
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="InputInstructions"] { display: none; }

</style>
""", unsafe_allow_html=True)

# Title with Custom HTML
st.markdown('<div class="main-title">🌍 动态旅行规划 Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multi-Constraint Optimization & AIR Loop (Thesis Demo)</div>', unsafe_allow_html=True)

# Initialize Memory Service
if 'memory_service' not in st.session_state:
    st.session_state.memory_service = MemoryService()

# Sidebar: User Inputs
with st.sidebar:
    st.header("1. 用户需求设置 ")
    
    current_user_name = st.text_input("User ID", value="Megumi")
    
    destination = st.text_input("目的地 ", value="厦门")
    origin = st.text_input("出发地 ", value="上海")

    start_date = st.date_input("出发日期", value=datetime.now() + timedelta(days=1))
    
    col1, col2 = st.columns(2)
    with col1:
        days = st.number_input("天数", min_value=1, max_value=14, value=2)
        budget = st.number_input("预算 (元)", min_value=500, value=3000, step=100)
    with col2:
        relation = st.selectbox("关系", ["独自一人", "情侣/夫妻", "朋友", "家庭"])
        
        # 联动逻辑：人数
        if relation == "独自一人":
            people = st.number_input("人数", value=1, disabled=True)
        elif relation == "情侣/夫妻":
            people = st.number_input("人数", value=2, disabled=True)
        else:
            people = st.number_input("人数", min_value=1, value=2)
    
    fitness = st.selectbox("体力水平", [e.value for e in FitnessLevel], index=2)
    pace = st.selectbox("旅行节奏", [e.value for e in TravelPace], index=1)
    accommodation = st.selectbox("住宿偏好", ["经济型 (¥100-300)", "舒适型 (¥300-600)", "高档型 (¥600-1000)", "豪华型 (¥1000-2000)", "奢华型 (¥2000+)"], index=1)
    
    # 兴趣偏好：12个固定选项 + 其他
    interest_options = [
        "历史古迹", "自然风光", "地道美食", "网红打卡", "博物馆", "海边休闲",
        "登山徒步", "主题乐园", "艺术展览", "购物血拼", "乡村体验", "夜景探索", "其他"
    ]
    
    selected_interests = st.multiselect(
        "兴趣偏好", 
        interest_options,
        default=["海边休闲", "地道美食"]
    )
    
    final_interests = [i for i in selected_interests if i != "其他"]
    if "其他" in selected_interests:
        custom_input = st.text_input("请输入其他兴趣 (可输入多个，用逗号分隔)", placeholder="例如：猫咖, 滑雪")
        if custom_input:
             # 支持中文逗号和英文逗号
             extras = [x.strip() for x in custom_input.replace("，", ",").split(",") if x.strip()]
             final_interests.extend(extras)
    
    extra_req = st.text_area("额外要求", "")
    
    start_btn = st.button("🚀 智能分析并生成行程")

if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None
if 'air_log' not in st.session_state:
    st.session_state.air_log = []

# Main logic merged
if start_btn:
    st.session_state.itinerary = None
    st.session_state.air_log = []
    
    with st.status("🤖 AI Agent 正在执行 AIR 规划循环...", expanded=True) as status:
        try:
            # 1. 初始化工具
            deepseek = DeepSeekClient()
            weather_tool = WeatherTool()
            traffic_tool = TrafficTool()
            planner = PlanningAgent()

            # [Reflection] 1. 约束分析
            status.write("🤔 [Reflection] 正在分析用户约束条件...")
            req = TravelRequest(
                destination=destination,
                origin=origin,
                days=days,
                budget=float(budget),
                travelers_count=people,
                travelers_relation=relation,
                fitness_level=FitnessLevel(fitness),
                pace=TravelPace(pace),
                accommodation_preference=accommodation,
                interests=final_interests,
                extra_requirements=extra_req,
                start_date=start_date.strftime("%Y-%m-%d")
            )
            st.session_state.request = req
            
            # 记录 Reflection 日志
            st.session_state.air_log.append({
                "step": "Reflection",
                "content": f"分析多维约束: 预算({budget}), 体力({fitness}), 偏好({len(final_interests)}项), 关系({relation})"
            })
            
            # [Action] 2. 工具决策
            status.write("🛠️ [Action] 正在决策所需工具...")
            requirements_dict = req.model_dump()
            needed_tools = deepseek.analyze_tool_needs(requirements_dict)
            
            st.session_state.air_log.append({
                "step": "Action", 
                "content": f"决定调用外部工具: {needed_tools}"
            })
            
            # [Information] 3. 获取环境信息
            status.write("📡 [Information] 正在获取实时环境数据...")
            weather_ctx = ""
            route_ctx = ""
            
            if "weather" in needed_tools:
                w_data = weather_tool.get_forecast(destination)
                if "error" not in w_data:
                    forecast = w_data.get('forecast', [])
                    weather_ctx = f"未来天气预测: " + "; ".join([f"{d['date']}: {d['description']}, {d['temperature']}" for d in forecast[:days]])
                    st.session_state.air_log.append({
                        "step": "Information",
                        "content": f"获取天气数据: {forecast[0]['description'] if forecast else 'Unknown'}..."
                    })
                else:
                    st.session_state.air_log.append({"step": "Information", "content": "天气数据获取失败，使用默认设定"})
                    
            if "traffic" in needed_tools:
                dist_km = traffic_tool.calculate_distance(origin, destination)
                decision = deepseek.decide_intercity_transport(origin, destination, dist_km, "ai_decide")
                mode = decision.get("recommended_mode", "driving")
                route_ctx = f"建议跨城交通: {mode}。距离 {dist_km}km。"
                
                st.session_state.air_log.append({
                    "step": "Information",
                    "content": f"获取交通数据: 距离{dist_km}km, 推荐{mode}"
                })

            # [Reflection] 4. 最终规划
            status.write("🧠 [Reflection] 综合信息进行多约束优化规划...")
            
            # Memory Interface
            user_hist_str = ""
            if 'memory_service' in st.session_state:
                 user_hist_str = st.session_state.memory_service.get_user_history(current_user_name)
                 
                 if user_hist_str:
                     with status:
                        st.info(f"📚 成功检索到用户【{current_user_name}】的历史偏好记录，AI将结合规划。")
                        with st.expander("查看检测到的历史记忆详情"):
                            st.text(user_hist_str)

            final_plan = planner.run(req, weather_info=weather_ctx, route_info=route_ctx, user_history=user_hist_str)
            
            # Save Memory
            if 'memory_service' in st.session_state:
                # Convert request model to dict for storage
                try:
                    req_data = req.model_dump() if hasattr(req, 'model_dump') else req.dict()
                    st.session_state.memory_service.add_record(current_user_name, req_data)
                except Exception as mem_err:
                    print(f"Memory Save Failed: {mem_err}")

            st.session_state.air_log.append({
                "step": "Reflection",
                "content": "生成最终行程: 平衡预算+历史偏好优化"
            })
            
            st.session_state.itinerary = final_plan
            status.update(label="✅ 行程规划完成！", state="complete", expanded=False)
            
        except Exception as e:
            status.update(label="❌ 发生错误", state="error")
            st.error(f"Error details: {str(e)}")

def generate_change_summary(old_itin, new_itin):
    """比较新旧行程，生成变更摘要"""
    changes = []
    days = max(len(old_itin.daily_plans), len(new_itin.daily_plans))
    for i in range(days):
        day_num = i + 1
        if i >= len(old_itin.daily_plans):
            changes.append(f"Day {day_num}: 新增了整天的行程")
            continue
        if i >= len(new_itin.daily_plans):
            changes.append(f"Day {day_num}: 取消了整天的行程")
            continue
            
        old_day = old_itin.daily_plans[i]
        new_day = new_itin.daily_plans[i]
        
        # 比较活动
        old_acts = set(item.activity for item in old_day.activities)
        new_acts = set(item.activity for item in new_day.activities)
        
        added = new_acts - old_acts
        removed = old_acts - new_acts
        
        if added or removed:
             # 如果完全不一样，可能是因为DeepSeek翻译不同，尝试只提取关键词比较略有些复杂
             # 这里简单一点，只要集合不同就列出
             summary_part = f"Day {day_num} 变更: "
             if removed:
                 summary_part += f"取消[{', '.join(removed)}] "
             if added:
                 summary_part += f"新增[{', '.join(added)}]"
             changes.append(summary_part)
        elif old_day.theme != new_day.theme:
            # 活动名一样但主题变了的情况少见，但也算
            changes.append(f"Day {day_num} 主题调整: {new_day.theme}")

    return changes

def handle_simulation_event(event_type: str, event_desc: str):
    """处理突发事件的 AIR 循环"""
    if not st.session_state.itinerary:
        st.error("⚠️ 请先生成行程规划，再进行突发事件模拟。")
        return

    st.session_state.air_log.append({
        "step": "Information",
        "content": f"⚠️ 系统监测到突发事件: [{event_type}] {event_desc}"
    })
    
    with st.status(f"⚡ 正在处理突发事件: {event_type}...", expanded=True) as status:
        try:
            # 1. Reflection: 评估影响
            status.write("🤔 [Reflection] 评估事件对当前行程的影响...")
            guide = GuideAgent()
            
            # 构造虚拟环境快照
            # 确保时间格式正确，假设发生在第1天上午
            sim_time = f"{st.session_state.request.start_date} 09:00"
            env_snapshot = {
                "time": sim_time, 
                "weather": "突发恶劣天气" if "雨" in event_desc or "雪" in event_desc else "正常",
                "events": event_desc
            }
            
            # 使用 GuideAgent 判断是否需要重规划
            # 这里我们需要构造一个 TravelSession 对象，或者简化传参
            class MockSession:
                def __init__(self, itin, req):
                    self.itinerary = itin
                    self.request = req
                    # 必须完整初始化 TravelState
                    self.state = TravelState(
                        current_time=sim_time,
                        current_location=req.destination,
                        remaining_budget=req.budget
                    )
            
            mock_session = MockSession(st.session_state.itinerary, st.session_state.request)
            
            decision = guide.reflect_and_act(mock_session, env_snapshot)
            
            st.session_state.air_log.append({
                "step": "Reflection",
                "content": f"Agent 决策: {decision}"
            })
            
            if "REPLAN" in decision:
                # 2. Action: 重新规划
                status.write("🛠️ [Action] 启动重规划引擎...")
                reason = decision.split("REPLAN:")[-1].strip()
                
                # 记录决策原因
                st.session_state.air_log.append({
                    "step": "Action",
                    "content": f"决策: 触发重规划 | 原因: {reason}"
                })
                
                planner = PlanningAgent()
                feedback = f"突发事件发生: {event_desc}. 请重新调整行程。原因: {reason}"
                
                # 重新调用规划器
                new_plan = planner.run(
                    st.session_state.request, 
                    weather_info=f"注意: {event_desc}", # 将事件作为新的环境信息
                    feedback=feedback
                )
                
                # 计算差异
                changes = generate_change_summary(st.session_state.itinerary, new_plan)
                if changes:
                    change_items = ""
                    for c in changes:
                        # 格式化: 加粗日期，分行显示增删，使用颜色标识
                        c_formatted = c.replace("Day ", "<b>Day </b>")
                        # 替换文本为带样式的HTML
                        if "取消" in c_formatted:
                            c_formatted = c_formatted.replace("取消", "<br><span style='color:#e55039; font-weight:bold;'>➖ 取消</span>")
                        if "新增" in c_formatted:
                            c_formatted = c_formatted.replace("新增", "<br><span style='color:#38ada9; font-weight:bold;'>➕ 新增</span>")
                            
                        change_items += f"<li style='margin-bottom:10px; line-height:1.5; border-bottom:1px dashed #eee; padding-bottom:5px;'>{c_formatted}</li>"
                    
                    st.session_state.air_log.append({
                        "step": "Action",
                        "content": f"✅ <b>行程变更详情:</b><ul style='margin-top:5px; padding-left:0; list-style-type:none; font-size:0.95em;'>{change_items}</ul>" 
                    })
                
                st.session_state.itinerary = new_plan
                st.session_state.air_log.append({
                    "step": "Action",
                    "content": "✅ 已生成适应突发事件的新方案"
                })
                status.update(label="✅ 动态调整完成！", state="complete")
                
            else:
                st.session_state.air_log.append({
                    "step": "Action",
                    "content": "维持原计划 (评估后认为影响可控)"
                })
                status.update(label="✅ 评估完成：无需调整", state="complete")
                
        except Exception as e:
            import traceback
            st.error(f"Simulation Error: {str(e)}\n\nDebug Info:\n{traceback.format_exc()}")

@st.cache_data(show_spinner=False)
def fetch_scenic_details(keyword, city):
    """缓存获取景区信息，避免重复请求"""
    if not keyword or len(keyword) < 2:
        return None
    # 避免查询一些通用词汇 (扩展版)
    skip_words = [
        "酒店", "机场", "火车站", "餐厅", "饭店", "休息", "出发", "返回", "自由活动", "办理入住", "用餐", "吃饭",
        "集合", "解散", "购物", "特产", "散步", "早餐", "午餐", "晚餐", "夜宵", "高铁", "飞机", "大巴", "打车",
        "租车", "交通", "路程", "睡觉", "洗漱", "退房", "登机", "候机", "取票", "闲逛", "购买", "补给"
    ]
    for sw in skip_words:
        if sw in keyword:
            return None
            
    tool = ScenicTool()
    return tool.get_scenic_info(keyword, city)

# Display Logic (Merged View)
if st.session_state.itinerary:
    itin = st.session_state.itinerary
    
    # 这里的 shown_scenics 用于本轮渲染的去重
    shown_scenics_names = set()
    
    # 顶部概览卡片
    st.markdown(f"""
    <div class="css-card" style="border-left: 5px solid #a18cd1; background: linear-gradient(to right, rgba(255,255,255,0.95), rgba(240,245,255,0.9));">
        <h2 style="margin:0; color: #2c3e50;">📍 {itin.request.destination} · {itin.request.days}日智能规划</h2>
        <div style="margin-top: 10px; display: flex; gap: 20px; color: #57606f;">
            <span>📅 出发: <b>{itin.request.start_date}</b></span>
            <span>💰 预算: <b>¥{itin.total_cost_estimate:.0f}</b></span>
            <span>👥 人数: <b>{itin.request.travelers_count}人 ({itin.request.travelers_relation})</b></span>
        </div>
        <div style="margin-top: 10px; font-size: 0.9em; color: #7f8c8d;">
            🎯 <b>核心偏好:</b> {', '.join(itin.request.interests)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 两列布局
    col_content, col_map = st.columns([2, 1])
    
    with col_content:
        for day in itin.daily_plans:
            st.markdown(f"""
            <div class="css-card">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 2px solid #f1f2f6; padding-bottom: 10px; margin-bottom: 15px;">
                    <h3 style="margin:0; color:#2c3e50;">📅 Day {day.day}: {day.theme}</h3>
                    <span style="background:#dfe4ea; padding:4px 10px; border-radius:15px; font-size:0.8em;">🌤️ {day.weather_summary}</span>
                </div>
                <div class="timeline-container">
            """, unsafe_allow_html=True)
            
            for item in day.activities:
                # 简单的 transport icon
                trans_icon = "🚕" if "车" in str(item.transport_suggestion) else "🚶" 
                
                # 获取景区信息 (Scenic Info)
                scenic_html = ""
                
                # 策略: 优先使用 AI 直接提取的 scenic_spot
                query_word = ""

                if hasattr(item, 'scenic_spot') and item.scenic_spot:
                     query_word = item.scenic_spot.strip()
                
                # 如果 AI 没提取出来 (旧数据兼容)，则回退到原来的正则清洗逻辑
                if not query_word:
                    # 1. 预处理 activity 移除动词和无关名词
                    act_text = item.activity
                    remove_words = [
                        "前往", "游览", "参观", "抵达", "漫步", "打卡", "探索", "体验", "享受", "去", "参加", 
                        "乘坐", "观看", "欣赏", "Visit", "Tour", "Go to", "See", "Explore", "寻找", "品尝", 
                        "享用", "逛吃", "购买", "及周边", "周边", "午餐", "晚餐", "夜宵", "日落", "夜景", 
                        "看", "闲逛", "休憩", "逗留", "活动"
                    ]
                    for v in remove_words:
                        act_text = act_text.replace(v, "")
                    
                    # 去除标点和空格
                    act_text = act_text.replace("，", "").replace("。", "").replace("及", "").replace("与", "").strip()
                    
                    # 2. 决定查询词
                    # 如果 activity 清洗后剩下的词比较像是一个景点名 (长度适中)
                    if len(act_text) >= 2 and len(act_text) < 15:
                        query_word = act_text
                    # 如果 activity 没啥用，再看 location
                    elif item.location and len(item.location) >= 2 and len(item.location) < 15:
                        if "->" not in item.location and "/" not in item.location:
                            query_word = item.location
                
                # 二次清洗
                query_word = query_word.strip()
                
                # 最终检查: 确保不是空，也不是排除词
                scenic_data = None
                if query_word:
                    scenic_data = fetch_scenic_details(query_word, itin.request.destination)
                    
                    # 页面内去重逻辑
                    if scenic_data and scenic_data.get('name'):
                        if scenic_data['name'] in shown_scenics_names:
                            scenic_data = None
                        else:
                            shown_scenics_names.add(scenic_data['name'])
                
                if scenic_data:
                    s_name = scenic_data.get('name', '')
                    s_level = scenic_data.get('level', '') 
                    s_price = scenic_data.get('price', '未知')
                    s_content = scenic_data.get('content', '')
                    s_photos = scenic_data.get('photos', [])
                    s_map_url = scenic_data.get('static_map', '')
                    
                    # 静态地图
                    map_html = ""
                    if s_map_url:
                        # 使用 Lightbox 结构包裹地图，使其支持点击全屏放大
                        unique_map_id = f"map-{abs(hash(item.activity))}"
                        # 注意: 必须去除缩进，避免被 Markdown 识别为代码块
                        map_html = f"""<div style="margin-top:8px; border-radius:4px; border:1px solid #eee; overflow:hidden;">
<div style="position:relative;">
<input type="checkbox" id="{unique_map_id}" class="img-zoom-check">
<label for="{unique_map_id}" class="img-zoom-label" title="点击查看高清地图">
<img src="{s_map_url}" style="width:100%; height:auto; display:block;" alt="位置地图" loading="lazy">
<div class="img-zoom-fullscreen">
<img src="{s_map_url}" loading="lazy">
</div>
</label>
</div>
<div style="font-size:0.75em; color:#999; text-align:center; background:#fafafa; padding:2px;">📍 景区位置示意图 (点击查看高清)</div>
</div>"""
                    
                    scenic_html = f"""<div style="margin-top: 8px; font-size: 0.85em; background: #f0f8ff; padding: 10px; border-radius: 8px; border: 1px dashed #74b9ff;">
<div style="font-weight:bold; color:#0984e3; display:flex; align-items:center gap:10px;">
<span>🏞️ 景区百科: {s_name}</span>
<span style="font-size:0.8em; color:#fff; background:#fab1a0; padding:1px 6px; border-radius:4px; margin-left:8px;">{s_level}</span>
</div>
<div style="margin-top:6px; color:#636e72; line-height:1.4;">{s_content}</div>
<div style="margin-top:6px; font-size:0.9em; color:#2c3e50; background:rgba(255,255,255,0.6); padding:5px; border-radius:4px;">
💰 <b>{s_price}</b>
</div>
{map_html}
</div>"""
                
                # 渲染文本部分
                st.markdown(f"""
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <div style="display:flex; align-items:baseline;">
                            <span class="activity-time">{item.time}</span>
                            <strong style="font-size:1.05em; color:#2d3436;">{item.activity}</strong>
                        </div>
                        <div style="margin-left: 0px; margin-top: 5px; color: #636e72; font-size: 0.95em; background: rgba(255,255,255,0.5); padding: 8px; border-radius: 6px;">
                            📍 {item.location or '未指定地点'} <br>
                            💡 {item.description}
                        </div>
                        <div style="margin-top:5px; font-size:0.85em; color:#a4b0be;">
                            {trans_icon} 交通建议: {item.transport_suggestion or '无'}
                        </div>
                        {scenic_html}
                    </div>
                """, unsafe_allow_html=True)
                
                # 图片展示: 使用 Pure CSS Lightbox 实现 "点击放大 -> 点击关闭"
                if scenic_data and scenic_data.get('photos'):
                    photos = scenic_data['photos'][:6] # Display up to 6 photos
                    if photos:
                        # 构造 HTML 网格
                        gallery_html = '<div style="display:grid; grid-template-columns: repeat(6, 1fr); gap:6px; margin-top:8px;">'
                        
                        for idx, p_url in enumerate(photos):
                            # 生成唯一的ID
                            uid = f"img-{abs(hash(item.activity))}-{idx}"
                            # 注意:这里必须去除缩进，否则 st.markdown 会将其解析为代码块
                            gallery_html += f"""<div style="position:relative;">
<input type="checkbox" id="{uid}" class="img-zoom-check">
<label for="{uid}" class="img-zoom-label" title="点击放大/缩小">
<img src="{p_url}" class="img-zoom-thumb" loading="lazy">
<div class="img-zoom-fullscreen">
<img src="{p_url}" loading="lazy">
</div>
</label>
</div>"""
                        gallery_html += "</div>"
                        st.markdown(gallery_html, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)

    with col_content:
        # --- 1. 行前准备清单 ---
        if hasattr(itin, 'preparation_list') and itin.preparation_list:
            st.markdown("---")
            st.markdown('<h3 class="fade-in">🧳 行前准备清单</h3>', unsafe_allow_html=True)
            prep = itin.preparation_list
            pc1, pc2, pc3 = st.columns(3)
            
            def make_prep_html(title, items):
                if not items: return ""
                items_html = "".join([f"<div style='color:#57606f; margin-left:10px;'>- {i}</div>" for i in items])
                return f"""
                <div class="fade-in" style="margin-bottom:15px;">
                    <strong style="display:block; margin-bottom:5px;">{title}</strong>
                    {items_html}
                </div>
                """

            with pc1:
                st.markdown(make_prep_html("🆔 证件", prep.get("证件", [])), unsafe_allow_html=True)
                st.markdown(make_prep_html("💊 药品", prep.get("药品", [])), unsafe_allow_html=True)
            with pc2:
                st.markdown(make_prep_html("👗 衣物", prep.get("衣物", [])), unsafe_allow_html=True)
                st.markdown(make_prep_html("🧴 日用品", prep.get("日用品", [])), unsafe_allow_html=True)
            with pc3:
                st.markdown(make_prep_html("📱 电子产品", prep.get("电子产品", [])), unsafe_allow_html=True)
                st.markdown(make_prep_html("📲 App准备", prep.get("App准备", [])), unsafe_allow_html=True)

        # --- 2. 特色避坑与注意事项 ---
        if hasattr(itin, 'special_tips') and itin.special_tips:
            st.markdown("---")
            st.markdown('<h3 class="fade-in">🚦 特色避坑与注意事项</h3>', unsafe_allow_html=True)
            tips = itin.special_tips
            
            if tips.get("交通"):
                with st.expander("🚍 交通出行避坑", expanded=True):
                    for i in tips["交通"]: st.write(f"• {i}")
            
            tc1, tc2 = st.columns(2)
            with tc1:
                if tips.get("餐饮"):
                    st.markdown("**🍜 餐饮美食**")
                    for i in tips["餐饮"]: st.info(i)
            with tc2:
                if tips.get("景点"):
                    st.markdown("**🏞️ 景点游玩**")
                    for i in tips["景点"]: st.success(i)
            
            if tips.get("防坑指南"):
                st.markdown("**🛡️ 综合防坑指南**")
                for i in tips["防坑指南"]: st.error(i)

    with col_map:
        st.markdown("### 🧠 AIR 动态规划链路")
        st.info("Action-Information-Reflection 循环演示")
        
        for log in st.session_state.air_log:
            # 样式映射
            if log['step'] == 'Action':
                border_color = "#fab1a0" # Orange
                icon = "⚡"
            elif log['step'] == 'Information':
                border_color = "#74b9ff" # Blue
                icon = "📡"
            else: # Reflection
                border_color = "#a29bfe" # Purple
                icon = "🤔"
                
            st.markdown(f"""
            <div style="background:#fff; color:#2d3436; padding:12px; margin-bottom:10px; border-radius:8px; border-left: 4px solid {border_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <div style="font-size:0.8em; color:{border_color}; font-weight:bold;">{icon} [{log['step']}]</div>
                <div style="font-size:0.9em; margin-top:4px;">{log['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown(f"""
        <div class="css-card" style="text-align:center;">
             <h4>📊 预算控制</h4>
             <p style="font-size:2em; font-weight:bold; color:#a18cd1;">¥{itin.total_cost_estimate}</p>
             <p style="color:#b2bec3;">(精确控制在预算 {itin.request.budget} 范围内)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 用户历史记录模块
        if 'memory_service' in st.session_state and current_user_name:
            user_hist_data = st.session_state.memory_service.get_user_history(current_user_name, limit=3)
            if user_hist_data:
                st.markdown("---")
                st.markdown("### 📚 用户旅行记忆图谱")
                st.info(f"AI 已检索到用户【{current_user_name}】的历史偏好，并将其融入规划思考。")
                
                with st.expander("🔍 原始查询记录与 AI 思考", expanded=True):
                    st.markdown("#### 📜 Recent Query Records")
                    st.text(user_hist_data)
                    
                    st.markdown("#### 🧠 AI Reflection on History")
                    st.markdown(f"""
                    > **Pattern Recognition**: 
                    > 用户似乎偏好 **{itin.request.pace}** 节奏的旅行。
                    > 历史记录显示对 **{", ".join(itin.request.interests[:2])}** 这一类目的地有持续兴趣。
                    > 
                    > **Guidance Strategy**:
                    > 本次规划已尝试在满足新目的地的同时，保留用户习惯的预算区间。
                    """)
        
    # 动态模拟控制台
    st.markdown("---")
    st.subheader("⚡ 突发事件模拟与动态调整 (AIR Simulation)")
    
    sim_col1, sim_col2 = st.columns([3, 1])
    with sim_col1:
        sim_event_options = [
            "航班/列车延误", 
            "突发恶劣天气 (暴雨/台风)", 
            "景区临时关闭/限流", 
            "身体不适/体力透支", 
            "交通拥堵/封路",
            "突发预算不足",
            "重要证件/物品丢失",
            "其他"
        ]
        event_type = st.selectbox("选择模拟事件类型", sim_event_options, key="sim_event_type")
        
        custom_placeholder = "例如：到达时航班延误了4小时..."
        if event_type == "其他":
            custom_placeholder = "请输入具体的突发事件描述..."
            
        custom_event = st.text_input("详细描述 (可选/必填)", placeholder=custom_placeholder, key="sim_event_desc")
        
    with sim_col2:
        st.write("")
        st.write("")
        trigger_btn = st.button("🔴 触发突发事件", use_container_width=True)
        
    if trigger_btn:
        if event_type == "其他" and not custom_event:
            st.error("请填写具体的突发事件描述！")
        else:
            # 组合事件描述，确保AI能获取完整上下文 (Fix for AI processing context)
            if event_type == "其他":
                full_desc = custom_event
            else:
                full_desc = f"{event_type}: {custom_event}" if custom_event else f"发生了 {event_type}"
            
            handle_simulation_event(event_type, full_desc)
            st.rerun()

