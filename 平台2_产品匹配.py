# 平台2_产品匹配.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import hashlib
import json
import glob
import os
import warnings

warnings.filterwarnings('ignore')

# ========== 自定义JSON编码器 ==========
class NumpyEncoder(json.JSONEncoder):
    """处理numpy数据类型的JSON编码器"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (pd.Timestamp, datetime.date, datetime.datetime)):
            return str(obj)
        return super().default(obj)

st.set_page_config(
    page_title="平台2：养老金融产品匹配系统 | 营销岗",
    page_icon="🎯",
    layout="wide"
)

# ========== 样式 ==========
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    .platform-header {
        background: linear-gradient(135deg, #2c7a4d, #48bb78);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border: 1px solid #00ff88;
        animation: glow 2s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { box-shadow: 0 20px 40px rgba(72,187,120,0.2); }
        to { box-shadow: 0 20px 60px rgba(72,187,120,0.4); }
    }
    .platform-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(45deg, #00ff88, #00b8ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .role-badge {
        background: #48bb78;
        color: white;
        padding: 8px 20px;
        border-radius: 30px;
        display: inline-block;
        font-weight: 600;
        margin-top: 10px;
        border: 1px solid #00ff88;
    }
    .profile-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(72,187,120,0.3);
        margin: 10px 0;
    }
    .product-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #e2e8f0;
        transition: all 0.3s;
        border-left: 5px solid #48bb78;
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(72,187,120,0.2);
    }
    .match-score {
        font-size: 2rem;
        font-weight: 700;
        color: #48bb78;
    }
    .tag-item {
        display: inline-block;
        padding: 5px 15px;
        margin: 3px;
        background: linear-gradient(45deg, #48bb78, #2c7a4d);
        color: white;
        border-radius: 20px;
        font-size: 0.9rem;
    }
    .insight-box {
        background: linear-gradient(135deg, #f0f9ff, #e6fffa);
        border-left: 5px solid #48bb78;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .compliance-tag {
        background: #fed7d7;
        color: #c53030;
        padding: 3px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .stProgress > div > div > div > div {
        background-color: #48bb78;
    }
</style>
""", unsafe_allow_html=True)

# ========== 产品数据库 ==========
@st.cache_data
def load_product_database():
    """加载产品数据库"""
    products = [
        {
            "产品代码": "P001",
            "产品名称": "养老专属定期",
            "风险等级": "R1",
            "预期收益": "2.75%",
            "期限(天)": 365,
            "起购金额(万)": 1,
            "产品类型": "存款类",
            "特点": "保本保息，适合保守型客户",
            "适合人群": ["银发族", "保守型"],
            "合规限制": {"年龄_max": 100, "风险等级": ["低风险"]}
        },
        {
            "产品代码": "P002",
            "产品名称": "灵活存系列",
            "风险等级": "R1",
            "预期收益": "2.35%",
            "期限(天)": 7,
            "起购金额(万)": 0.1,
            "产品类型": "存款类",
            "特点": "高流动性，随时可取",
            "适合人群": ["高流动性需求", "临时资金"],
            "合规限制": {"年龄_max": 100, "风险等级": ["低风险", "中风险", "高风险"]}
        },
        {
            "产品代码": "P003",
            "产品名称": "稳健养老理财",
            "风险等级": "R2",
            "预期收益": "3.5%-4.2%",
            "期限(天)": 180,
            "起购金额(万)": 5,
            "产品类型": "理财类",
            "特点": "中低风险，主投债券",
            "适合人群": ["稳健型", "中等收入"],
            "合规限制": {"年龄_max": 85, "风险等级": ["低风险", "中风险"]}
        },
        {
            "产品代码": "P004",
            "产品名称": "医疗关爱理财",
            "风险等级": "R2",
            "预期收益": "3.8%-4.5%",
            "期限(天)": 365,
            "起购金额(万)": 5,
            "产品类型": "理财类",
            "特点": "附加医疗增值服务",
            "适合人群": ["高医疗负担", "关注健康"],
            "合规限制": {"年龄_max": 85, "风险等级": ["低风险", "中风险"]}
        },
        {
            "产品代码": "P005",
            "产品名称": "养老目标基金2030",
            "风险等级": "R3",
            "预期收益": "5.0%-7.0%",
            "期限(天)": 1095,
            "起购金额(万)": 1,
            "产品类型": "基金类",
            "特点": "目标日期策略，自动调整",
            "适合人群": ["稳健型", "中长期投资"],
            "合规限制": {"年龄_max": 75, "风险等级": ["中风险", "高风险"]}
        },
        {
            "产品代码": "P006",
            "产品名称": "价值增长精选",
            "风险等级": "R3",
            "预期收益": "6.0%-9.0%",
            "期限(天)": 730,
            "起购金额(万)": 50,
            "产品类型": "基金类",
            "特点": "主动管理，追求超额收益",
            "适合人群": ["进取型", "高资产"],
            "合规限制": {"年龄_max": 70, "风险等级": ["中风险", "高风险"]}
        },
        {
            "产品代码": "P007",
            "产品名称": "科技成长组合",
            "风险等级": "R4",
            "预期收益": "7.0%-12.0%",
            "期限(天)": 1095,
            "起购金额(万)": 100,
            "产品类型": "基金类",
            "特点": "聚焦科技创新主题",
            "适合人群": ["进取型", "高资产", "资深投资者"],
            "合规限制": {"年龄_max": 65, "风险等级": ["高风险"]}
        }
    ]
    return pd.DataFrame(products)

# ========== 数据传递类 ==========
class DataTransfer:
    """数据传递类（读取平台1的画像）"""
    @staticmethod
    def get_latest_profile():
        """获取最新的客户画像文件"""
        profile_files = glob.glob("profile_*.json")
        if not profile_files:
            return None
        latest_file = max(profile_files, key=os.path.getctime)
        try:
            # 修复：明确指定编码为 utf-8
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"读取画像文件失败: {e}")
            return None

    @staticmethod
    def save_proposal(data):
        """保存产品方案"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"proposal_{timestamp}.json"
        # 修复：明确指定编码为 utf-8
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder) # ensure_ascii=False 很关键
        return filename

# ========== 产品匹配引擎 ==========
class ProductMatchingEngine:
    """产品智能匹配引擎"""
    def __init__(self, products_df):
        self.products_df = products_df

    def calculate_match_score(self, product, profile):
        """计算单个产品的匹配得分"""
        score = 50 # 基础分
        reasons = []

        # 1. 风险等级匹配
        risk_map = {
            "低风险": ["R1"],
            "中风险": ["R1", "R2"],
            "高风险": ["R1", "R2", "R3"]
        }
        customer_risk = profile['ml_result']['risk_level']
        allowed_risk = risk_map.get(customer_risk, [])
        if product['风险等级'] in allowed_risk:
            score += 15
            reasons.append("✅ 风险等级匹配")
        else:
            score -= 30
            reasons.append("❌ 风险等级不匹配")

        # 2. 年龄限制
        age = profile['customer_data']['年龄']
        max_age = product['合规限制'].get('年龄_max', 100)
        if age <= max_age:
            score += 10
            reasons.append("✅ 年龄符合要求")
        else:
            score -= 20
            reasons.append("❌ 年龄超限")

        # 3. 起购金额
        asset = profile['customer_data']['可投资资产(万)']
        min_purchase = product['起购金额(万)']
        if asset >= min_purchase:
            score += 10
            reasons.append(f"✅ 起购金额达标 (需{min_purchase}万)")
        else:
            score -= 15
            reasons.append(f"❌ 起购金额不足 (需{min_purchase}万)")

        # 4. 流动性匹配
        big_expense = profile['customer_data']['一年内大额支出']
        if big_expense == '是' and product['期限(天)'] <= 90:
            score += 15
            reasons.append("✅ 满足高流动性需求")
        elif big_expense == '否' and product['期限(天)'] >= 180:
            score += 10
            reasons.append("✅ 适合长期投资")

        # 5. 医疗负担匹配
        medical = profile['customer_data']['医疗支出占比(%)']
        if medical >= 40 and "医疗" in product['特点']:
            score += 15
            reasons.append("✅ 符合医疗负担客户需求")

        # 6. 投资经验匹配
        exp_years = profile['customer_data']['投资经验年限']
        if exp_years >= 10 and product['风险等级'] in ['R3', 'R4']:
            score += 10
            reasons.append("✅ 适合资深投资者")
        elif exp_years < 2 and product['风险等级'] in ['R1']:
            score += 5
            reasons.append("✅ 适合投资新手")

        # 7. 标签匹配
        tags = profile.get('tags', [])
        for tag in tags:
            # 清理标签中的emoji
            clean_tag = tag.replace('👴', '').replace('🎯', '').replace('🏥', '').replace('💰', '').replace('🎓', '').replace('💧', '').replace('⚡', '').replace('⚖️', '').replace('🛡️', '').replace('💊', '').replace('🌱', '').replace('💳', '').replace('👨 👩 👧', '').strip()
            # 检查是否匹配适合人群
            for target_group in product['适合人群']:
                if clean_tag in target_group:
                    score += 5
                    reasons.append(f"✅ 符合标签特征: {tag}")
                    break

        # 标准化得分
        final_score = max(0, min(100, score))
        return final_score, reasons

    def match_products(self, profile, top_n=5):
        """匹配产品并返回前N个"""
        matches = []
        for _, product in self.products_df.iterrows():
            score, reasons = self.calculate_match_score(product, profile)
            matches.append({
                '产品': product.to_dict(),
                '匹配得分': score,
                '匹配理由': reasons
            })

        # 按得分排序
        matches.sort(key=lambda x: x['匹配得分'], reverse=True)
        return matches[:top_n], matches

# ========== 主界面 ==========
def main():
    st.markdown("""
        <div class="platform-header">
            <h1 class="platform-title">🎯 平台2：养老金融产品匹配系统</h1>
            <p style="font-size:1.2rem;">营销岗 · 基于客户画像智能匹配产品</p>
            <div class="role-badge">👤 2号：营销岗</div>
        </div>
    """, unsafe_allow_html=True)

    # 加载产品数据
    products_df = load_product_database()

    # 初始化匹配引擎
    engine = ProductMatchingEngine(products_df)

    # ===== 左侧：接收到的客户画像 =====
    st.markdown("## 📥 接收到的客户画像")

    # 获取最新画像
    profile = DataTransfer.get_latest_profile()
    if profile is None:
        st.warning("⚠️ 暂无客户画像数据，请等待平台1（客服岗）发送")
        # 显示模拟数据按钮
        if st.button("🔄 使用模拟数据进行演示"):
            # 创建模拟画像（王阿姨）
            profile = {
                "customer_id": "CUST1001",
                "customer_data": {
                    "年龄": 72,
                    "性别": "女",
                    "婚姻状态": "丧偶",
                    "子女支持": "无",
                    "月养老金收入": 3500,
                    "可投资资产(万)": 10,
                    "医疗支出占比(%)": 35,
                    "是否有负债": "否",
                    "风险问卷得分": 45,
                    "投资经验年限": 2,
                    "一年内大额支出": "否",
                    "资金锁定期限(年)": 2
                },
                "ml_result": {
                    "risk_level": "中风险",
                    "confidence": 85.5,
                    "probabilities": {
                        "低风险": 15.2,
                        "中风险": 85.5,
                        "高风险": 12.3
                    }
                },
                "cluster": "稳健型中产",
                "tags": ['👴 银发族', '💊 中等医疗负担', '🌱 投资新手'],
                "timestamp": datetime.datetime.now().isoformat()
            }
            # 修复：保存时也使用 UTF-8 编码
            temp_filename = "temp_profile_for_demo.json"
            with open(temp_filename, 'w', encoding='utf-8') as f:
                 json.dump(profile, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)
            
            st.session_state['profile'] = profile
            st.success("✅ 已加载模拟数据（王阿姨）")
            st.rerun()
    else:
        st.session_state['profile'] = profile
        st.success(f"✅ 已加载客户画像 - 接收时间：{profile.get('timestamp', '未知')}")

    # 显示画像内容
    if 'profile' in st.session_state:
        profile = st.session_state['profile']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**👤 客户信息**")
            st.info(f"ID: {profile['customer_id']}\n\n年龄: {profile['customer_data']['年龄']}岁\n\n性别: {profile['customer_data']['性别']}")
        with col2:
            st.markdown("**📊 风险等级**")
            risk = profile['ml_result']['risk_level']
            if risk == '低风险':
                st.success(f"🟢 {risk}")
            elif risk == '中风险':
                st.warning(f"🟡 {risk}")
            else:
                st.error(f"🔴 {risk}")
            st.caption(f"置信度: {profile['ml_result']['confidence']:.1f}%")
        with col3:
            st.markdown("**🏷️ 客户标签**")
            tags = profile.get('tags', [])
            for tag in tags:
                st.markdown(f"- {tag}")
        with col4:
            st.markdown("**💰 资产信息**")
            st.info(f"可投资产: {profile['customer_data']['可投资资产(万)']}万\n\n养老金: {profile['customer_data']['月养老金收入']}元")

    # ===== 右侧：产品匹配 =====
    if 'profile' in st.session_state:
        st.markdown("---")
        st.markdown("## 🔍 AI产品智能匹配")

        profile = st.session_state['profile']

        # 匹配参数调整
        with st.expander("⚙️ 匹配参数调整", expanded=False):
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                risk_preference = st.select_slider(
                    "风险偏好调整",
                    options=['更保守', '标准', '更进取'],
                    value='标准'
                )
            with col_p2:
                top_n = st.slider("推荐产品数量", min_value=3, max_value=10, value=5)

        # 执行匹配
        top_products, all_matches = engine.match_products(profile, top_n=top_n)

        # 显示匹配结果统计
        st.markdown("### 📊 匹配结果概览")
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        with col_stat1:
            st.metric("总产品数", len(products_df))
        with col_stat2:
            matched_count = len([p for p in all_matches if p['匹配得分'] >= 60])
            st.metric("匹配产品数", matched_count)
        with col_stat3:
            avg_score = np.mean([p['匹配得分'] for p in all_matches])
            st.metric("平均匹配度", f"{avg_score:.1f}%")
        with col_stat4:
            best_score = top_products[0]['匹配得分']
            st.metric("最高匹配度", f"{best_score:.1f}%")

        # 显示推荐产品列表
        st.markdown("### 🏆 智能推荐产品")
        selected_products = []
        for i, item in enumerate(top_products, 1):
            product = item['产品']
            score = item['匹配得分']
            reasons = item['匹配理由']

            # 根据得分设置颜色
            if score >= 80:
                score_color = "#00ff88"
                score_text = "极佳匹配"
            elif score >= 60:
                score_color = "#ffaa00"
                score_text = "良好匹配"
            else:
                score_color = "#ff4444"
                score_text = "一般匹配"

            # 构建匹配理由HTML
            reasons_html = ""
            for reason in reasons:
                reasons_html += f"<li>{reason}</li>"

            # 构建适合人群HTML
            suitable_groups = "，".join(product['适合人群'])

            # 产品卡片HTML
            product_html = f"""
                <div class="product-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin:0;">{i}. {product['产品名称']}</h3>
                            <p style="margin:5px 0; color:#718096;">
                                代码: {product['产品代码']} | 风险等级: <strong>{product['风险等级']}</strong> | 预期收益: <strong>{product['预期收益']}</strong> | 期限: <strong>{product['期限(天)']}天</strong>
                            </p>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: {score_color};">
                                {score:.0f}%
                            </div>
                            <div style="font-size: 0.8rem;">{score_text}</div>
                        </div>
                    </div>
                    <div style="margin: 10px 0; padding: 10px; background: #f7fafc; border-radius: 8px;">
                        <p><strong>✨ 产品特点</strong>：{product['特点']}</p>
                        <p><strong>🎯 适合人群</strong>：{suitable_groups}</p>
                    </div>
                    <div style="margin: 10px 0;">
                        <details>
                            <summary style="color: #48bb78; cursor: pointer;">查看匹配理由</summary>
                            <ul style="margin-top: 10px;"> {reasons_html} </ul>
                        </details>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 10px;">
                        <div style="flex:1; padding: 8px; background: #f0f0f0; border-radius: 5px; text-align: center;">
                            <small>起购金额</small><br>
                            <strong>{product['起购金额(万)']}万</strong>
                        </div>
                        <div style="flex:1; padding: 8px; background: #f0f0f0; border-radius: 5px; text-align: center;">
                            <small>产品类型</small><br>
                            <strong>{product['产品类型']}</strong>
                        </div>
                        <div style="flex:1; padding: 8px; background: #f0f0f0; border-radius: 5px; text-align: center;">
                            <small>合规状态</small><br>
                            <span class="compliance-tag">可推荐</span>
                        </div>
                    </div>
                </div>
            """
            st.markdown(product_html, unsafe_allow_html=True)

            # 选择复选框
            if st.checkbox(f"选择 {product['产品名称']} 加入方案", key=f"select_{i}"):
                selected_products.append(product)

        # ===== 生成配置方案 =====
        st.markdown("---")
        st.markdown("## 📋 生成产品配置方案")

        if selected_products:
            st.success(f"✅ 已选择 {len(selected_products)} 个产品")

            # 显示配置预览
            total_asset = profile['customer_data']['可投资资产(万)']
            # 根据风险等级给出配置建议
            risk_level = profile['ml_result']['risk_level']
            if risk_level == "低风险":
                config = {"存款类": 70, "理财类": 25, "基金类": 5}
            elif risk_level == "中风险":
                config = {"存款类": 45, "理财类": 35, "基金类": 20}
            else: # 高风险
                config = {"存款类": 25, "理财类": 35, "基金类": 40}

            # 配置饼图
            fig_config = go.Figure(data=[go.Pie(
                labels=list(config.keys()),
                values=list(config.values()),
                hole=0.4,
                marker_colors=['#48bb78', '#4299e1', '#ed8936']
            )])
            fig_config.update_layout(height=300, title="资产配置建议")
            st.plotly_chart(fig_config, use_container_width=True)

            # 具体配置
            st.markdown("**💰 具体配置金额**")
            config_details = []
            for product in selected_products:
                product_type = product['产品类型']
                if product_type in config:
                    # 计算同类产品数量
                    same_type_count = len([p for p in selected_products if p['产品类型'] == product_type])
                    amount = total_asset * config[product_type] / 100 / same_type_count
                    config_details.append({
                        '产品名称': product['产品名称'],
                        '产品类型': product_type,
                        '建议配置(万)': round(amount, 2),
                        '预期收益': product['预期收益'],
                        '期限(天)': product['期限(天)']
                    })
            config_df = pd.DataFrame(config_details)
            st.dataframe(config_df, use_container_width=True, hide_index=True)

            # 发送按钮
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📤 发送至风控岗审核", use_container_width=True):
                    # 构建方案数据
                    proposal = {
                        'profile': profile,
                        'selected_products': selected_products,
                        'config_details': config_details,
                        'total_asset': total_asset,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'status': '待审核'
                    }
                    filename = DataTransfer.save_proposal(proposal)
                    st.success(f"✅ 已发送至风控岗！文件：{filename}")
                    st.balloons()
            with col_btn2:
                if st.button("🔄 重新选择", use_container_width=True):
                    st.rerun()
        else:
            st.info("👆 请在上方选择要加入方案的产品")

        # ===== 产品对比分析 =====
        with st.expander("📊 产品对比分析", expanded=False):
            # 风险收益散点图
            plot_data = []
            for item in all_matches:
                product = item['产品']
                # 解析预期收益
                return_str = product['预期收益']
                if '-' in return_str:
                    return_value = float(return_str.split('-')[0].replace('%',''))
                else:
                    return_value = float(return_str.replace('%',''))
                plot_data.append({
                    '产品名称': product['产品名称'],
                    '风险等级': product['风险等级'],
                    '预期收益': return_value,
                    '期限(天)': product['期限(天)'],
                    '匹配得分': item['匹配得分']
                })

            plot_df = pd.DataFrame(plot_data)
            fig_scatter = px.scatter(
                plot_df,
                x='期限(天)',
                y='预期收益',
                size='匹配得分',
                color='风险等级',
                hover_name='产品名称',
                title="产品风险收益分布图",
                color_discrete_map={
                    'R1': '#00ff88', 'R2': '#ffaa00', 'R3': '#ff6600', 'R4': '#ff4444'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

if __name__ == "__main__":
    main()