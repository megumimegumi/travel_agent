<template>
  <div class="recommendation-page">
    <h2 class="page-title"><span class="emoji">🎯</span> <span class="gradient-text">智能目的地推荐</span></h2>
    
    <div class="input-section fade-in-up">
      <div class="section-header">
        <h3>告诉AI您的旅行设想</h3>
        <p class="sub-text">完善以下信息，AI 将为您精准匹配最佳目的地</p>
      </div>
      
      <!-- Row 1: Basic Info -->
      <div class="form-row">
        <div class="form-group half">
           <label>🛫 出发地 <span class="required-star">*</span></label>
           <input 
             ref="originInput" 
             v-model="form.origin" 
             placeholder="例如：北京" 
             :class="['styled-input', { 'input-error': errors.origin }]" 
           />
           <span v-if="errors.origin" class="error-msg">请告诉我们从哪里出发</span>
        </div>
        <div class="form-group half">
           <label>📅 计划出发月份</label>
           <select v-model="form.month" class="styled-select">
              <option v-for="m in 12" :key="m" :value="m + '月'">{{ m }}月</option>
              <option value="随时">随时出发</option>
           </select>
        </div>
      </div>
      
      <!-- Row 2: Constraints -->
      <div class="form-row">
        <div class="form-group half">
           <label>⏳ 旅行天数 <span class="required-star">*</span></label>
           <input 
             ref="daysInput" 
             type="number" 
             v-model.number="form.days" 
             min="1" max="30" 
             :class="['styled-input', { 'input-error': errors.days }]" 
           />
           <span v-if="errors.days" class="error-msg">请填写有效的旅行天数</span>
        </div>
         <div class="form-group half">
           <label>💰 预算范围 (元) <span class="required-star">*</span></label>
           <input 
             ref="budgetInput"
             type="number" 
             v-model.number="form.budget" 
             step="500" 
             :class="['styled-input', { 'input-error': errors.budget }]"
            />
            <span v-if="errors.budget" class="error-msg">请填写您的预算范围</span>
        </div>
      </div>

      <!-- Row 3: Companions -->
      <div class="form-row">
        <div class="form-group half">
           <label>👥 同行关系</label>
           <select v-model="form.relation" class="styled-select">
              <option>独自一人</option>
              <option>情侣/夫妻</option>
              <option>朋友结伴</option>
              <option>家庭亲子</option>
              <option>带父母</option>
           </select>
        </div>
        <div class="form-group half">
           <label>🔢 同行人数</label>
           <input type="number" v-model.number="form.people_count" min="1" class="styled-input" />
        </div>
      </div>

       <!-- Row 4: Physical -->
      <div class="form-row">
        <div class="form-group half">
           <label>💪 体力水平</label>
           <select v-model="form.fitness" class="styled-select">
              <option>铁人三项 (极其充沛)</option>
              <option>精力充沛 (能走两万步)</option>
              <option>普通人 (正常行走)</option>
              <option>容易累 (少走路)</option>
              <option>养老模式 (几乎不走)</option>
           </select>
        </div>
        <div class="form-group half">
           <label>🐢 旅行节奏</label>
           <select v-model="form.pace" class="styled-select">
              <option>特种兵 (高强度打卡)</option>
              <option>紧凑 (充实)</option>
              <option>适中 (劳逸结合)</option>
              <option>慢悠悠 (睡到自然醒)</option>
           </select>
        </div>
      </div>

      <!-- Interest & Preference -->
      <div class="form-group">
        <label>🏞️ 目的地倾向 (选填)</label>
        <input v-model="form.destination_pref" placeholder="例如：想去海边，或者是著名的历史古都..." class="styled-input" />
      </div>

      <div class="form-group">
        <label>🏷️ 兴趣爱好 (可多选)</label>
        <div class="tags-input-area">
          <span 
            v-for="tag in commonInterests" 
            :key="tag" 
            @click="toggleInterest(tag)"
            :class="['check-tag', { active: form.interests.includes(tag) }]"
          >
            {{ tag }}
          </span>
        </div>
        
        <Transition name="slide-fade">
          <div v-if="form.interests.includes('其他')" class="custom-interest-input">
            <input 
              v-model="customInterest" 
              placeholder="✨ 请告诉 AI 您独特的兴趣爱好..." 
              :class="['styled-input', 'custom-input-field', { 'input-error': errors.customInterest }]" 
              ref="customInterestInput"
            />
            <span v-if="errors.customInterest" class="error-msg">请填写您的具体兴趣</span>
          </div>
        </Transition>
      </div>
      
      <div class="form-group">
        <label>✍️ 额外要求 (选填)</label>
        <textarea v-model="form.extra_requirements" rows="2" class="styled-textarea" placeholder="例如：必须要有地铁，或者希望避开人流高峰..."></textarea>
      </div>
      
      <button @click="getRecommendations" :disabled="loading" class="action-btn hover-float">
        {{ loading ? '🌌 正在调用全网数据分析中...' : '🚀 生成推荐城市' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state fade-in-up">
        <div class="spinner"></div>
        <div class="thinking-logs">
            <p v-for="(log, idx) in thinkingLogs" :key="idx" class="log-item">{{ log }}</p>
        </div>
    </div>

    <!-- Results -->
    <div v-if="!loading && results.length > 0" class="results-container fade-in-up">
      <h3 class="results-title">✨ 为您精心挑选的最佳目的地</h3>
      <div class="results-grid">
        <div v-for="(item, index) in results" :key="index" class="dest-card hover-float">
          <div class="card-header">
              <div class="rank">#{{ index + 1 }}</div>
              <h3>{{ item.city }}</h3>
          </div>
          <div class="tags">
            <span class="season-tag">📅 {{ item.suitable_season }}</span>
            <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <p class="reason">{{ item.reason }}</p>
          <button @click="goToPlan(item.city)" class="plan-btn">🗓️ 去规划行程</button>
        </div>
      </div>
    </div>

    <div v-if="!loading && hasSearched && results.length === 0" class="no-results fade-in-up">
        <p>😕 抱歉，AI 似乎在神游，没有生成结果。请稍后重试。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const results = ref([]);
const thinkingLogs = ref([]);
const hasSearched = ref(false);
const customInterest = ref('');
const customInterestInput = ref(null);
const originInput = ref(null);
const daysInput = ref(null);
const budgetInput = ref(null);

const errors = reactive({
    origin: false,
    days: false,
    budget: false,
    customInterest: false
});

const commonInterests = [
    '自然风光', '人文历史', '地道美食', '海岛度假', '爬山徒步', 
    '博物馆', '亲子乐园', '网红打卡', '乡村田园', '极限运动', 
    '摄影', '购物', '温泉养生', '古镇探访', '艺术展览', 
    '主题乐园', '自驾探索', '露营野餐', '滑雪体验', '朝圣祈福', 
    '其他'
];

const form = reactive({
    origin: '',
    month: new Date().getMonth() + 1 + '月',
    days: 5,
    budget: 5000,
    relation: '独自一人',
    people_count: 1,
    fitness: '普通人 (正常行走)',
    pace: '适中 (劳逸结合)',
    destination_pref: '',
    interests: [],
    extra_requirements: ''
});

const toggleInterest = (tag) => {
    if (form.interests.includes(tag)) {
        form.interests = form.interests.filter(t => t !== tag);
    } else {
        form.interests.push(tag);
    }
};

const simulateThinking = () => {
    thinkingLogs.value = [];
    const steps = [
        "🤔 正在解析您的详细旅行画像...",
        "🛫 分析出发地与交通便利度...",
        "📅 筛选当季最适宜的目的地...",
        "💰 正在计算预算与消费水平匹配度...",
        "🔍 在数据库中检索符合兴趣的城市...",
        "✨ 正在生成最终的推荐方案..."
    ];
    let i = 0;
    thinkingLogs.value.push(steps[0]);
    i++;
    
    const interval = setInterval(() => {
        if (i < steps.length) {
            thinkingLogs.value.push(steps[i]);
            i++;
        }
    }, 1500);
    return interval;
};

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => errors[key] = false);
  
  let firstError = null;

  if (!form.origin.trim()) {
      errors.origin = true;
      if (!firstError) firstError = originInput;
  }
  if (!form.days || form.days <= 0) {
      errors.days = true;
      if (!firstError) firstError = daysInput;
  }
  if (!form.budget || form.budget <= 0) {
      errors.budget = true;
      if (!firstError) firstError = budgetInput;
  }
  if (form.interests.includes('其他') && !customInterest.value.trim()) {
      errors.customInterest = true;
      if (!firstError) firstError = customInterestInput;
  }

  if (firstError && firstError.value) {
      firstError.value.scrollIntoView({ behavior: 'smooth', block: 'center' });
      firstError.value.focus();
      return false;
  }
  return true;
};

const getRecommendations = async () => {
  if (!validateForm()) return;

  loading.value = true;
  hasSearched.value = true;
  results.value = [];
  const thinkingInterval = simulateThinking();
  
  try {
    // Handle custom interest
    let finalInterests = [...form.interests];
    if (finalInterests.includes('其他')) {
        finalInterests = finalInterests.filter(t => t !== '其他');
        if (customInterest.value.trim()) {
            finalInterests.push(customInterest.value.trim());
        }
    }

    // Construct rich requirement string
    const reqText = `
      【基础信息】
      从 ${form.origin || '待定'} 出发，计划 ${form.month} 出行，游玩 ${form.days} 天。
      预算约 ${form.budget} 元。
      
      【同行与状态】
      ${form.people_count}人 (${form.relation})。
      体力: ${form.fitness}。节奏: ${form.pace}。
      
      【偏好设置】
      目的地倾向: ${form.destination_pref || '无特殊倾向'}
      兴趣标签: ${finalInterests.join(', ') || '综合体验'}
      
      【额外要求】
      ${form.extra_requirements}
    `.trim();

    const response = await fetch('/api/recommend/destinations', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        user_profile: { 
            origin: form.origin,
            interests: finalInterests 
        },
        requirements: reqText
      })
    });
    
    if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`);
    }
    
    const data = await response.json();
    if (Array.isArray(data)) {
        results.value = data;
    } else {
        throw new Error('格式错误');
    }
    
  } catch (e) {
    alert('推荐生成失败: ' + e.message);
  } finally {
    loading.value = false;
    clearInterval(thinkingInterval);
  }
};

const goToPlan = (city) => {
  router.push({ 
      path: '/planner', 
      query: { 
          destination: city,
          origin: form.origin,
          days: form.days,
          budget: form.budget,
          relation: form.relation,
          fitness: form.fitness, // We can actually pass more params to planner to pre-fill
          start_date: new Date().toISOString().split('T')[0] // Default to today as planner needs exact date
      }
  });
};
</script>

<style scoped>
.recommendation-page { max-width: 1000px; margin: 0 auto; padding: 30px 20px; }
.page-title { text-align: center; margin-bottom: 30px; font-size: 2.2rem; font-weight: 800; }
.gradient-text { background: linear-gradient(to right, #6a11cb 0%, #2575fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.emoji { margin-right: 8px; vertical-align: bottom; }

.input-section { 
    background: white; padding: 40px; border-radius: 20px; 
    box-shadow: 0 15px 35px rgba(0,0,0,0.08); 
    border: 1px solid rgba(255,255,255,0.8);
    position: relative;
    overflow: hidden;
}
.input-section::before {
    content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 6px;
    background: linear-gradient(to right, #6c5ce7, #00cec9);
}

.section-header { margin-bottom: 30px; text-align: center; }
.section-header h3 { margin: 0; color: #2d3436; font-size: 1.5rem; }
.sub-text { color: #636e72; margin-top: 8px; font-size: 1rem; }

.form-row { display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }
.half { flex: 1; min-width: 200px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #2d3436; font-size: 0.95rem; }

/* Styled Inputs */
.styled-input, .styled-select, .styled-textarea {
    width: 100%; padding: 14px; border: 2px solid #dfe6e9; border-radius: 10px;
    font-size: 1rem; transition: all 0.3s;
    background: #f9f9f9; box-sizing: border-box;
    font-family: inherit;
}
.styled-input:focus, .styled-select:focus, .styled-textarea:focus { border-color: #74b9ff; outline: none; background: white; box-shadow: 0 0 0 4px rgba(116, 185, 255, 0.1); }

/* Tags */
.tags-input-area { display: flex; flex-wrap: wrap; gap: 10px; }
.check-tag {
    padding: 8px 16px; background: #f1f2f6; border-radius: 20px; color: #57606f; cursor: pointer;
    transition: all 0.2s; border: 1px solid transparent; user-select: none; font-size: 0.95rem;
}
.check-tag:hover { background: #dfe4ea; }
.check-tag.active { background: #6c5ce7; color: white; border-color: #5f27cd; font-weight: 600; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(108, 92, 231, 0.3); }

/* Custom Interest Input Animation */
.custom-interest-input { margin-top: 15px; width: 100%; }
.custom-input-field { 
    border-color: #a29bfe; background: #f8f7ff; 
    box-shadow: 0 4px 10px rgba(108, 92, 231, 0.1);
}
.custom-input-field:focus { border-color: #6c5ce7; background: white; }

/* Validation Styles */
.required-star { color: #ff7675; margin-left: 4px; font-weight: bold; }
.input-error { border-color: #ff7675 !important; background-color: #fff0f0 !important; animation: shake 0.4s ease-in-out; }
.error-msg { color: #ff7675; font-size: 0.85rem; margin-top: 5px; display: block; }
@keyframes shake { 0%, 100% { transform: translateX(0); } 20%, 60% { transform: translateX(-5px); } 40%, 80% { transform: translateX(5px); } }

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.4s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { transform: translateY(-10px); opacity: 0; }

.action-btn { 
    width: 100%; background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); 
    color: white; border: none; padding: 18px; border-radius: 12px; 
    font-size: 1.2rem; font-weight: bold; cursor: pointer; margin-top: 10px;
    box-shadow: 0 8px 20px rgba(108, 92, 231, 0.3);
    transition: all 0.3s;
}
.action-btn:hover { transform: translateY(-2px); box-shadow: 0 12px 25px rgba(108, 92, 231, 0.4); }
.action-btn:disabled { opacity: 0.8; cursor: wait; filter: grayscale(0.5); transform: none; box-shadow: none; }

/* Loading */
.loading-state { text-align: center; color: #666; width: 100%; margin: 40px 0; min-height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.spinner { 
  width: 50px; height: 50px; border: 5px solid #f3f3f3; border-top: 5px solid #6c5ce7; 
  border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 25px auto; 
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.thinking-logs { margin-top: 20px; text-align: center; max-width: 500px; margin: 20px auto; width: 100%; }
.log-item { background: #eef2f7; padding: 12px 20px; border-radius: 30px; margin-bottom: 10px; font-size: 1rem; animation: fadeIn 0.5s ease; color: #4b6584; display: inline-block; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }

/* Results */
.results-container { margin-top: 50px; }
.results-title { text-align: center; font-size: 1.8rem; color: #2d3436; margin-bottom: 30px; }
.results-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 25px; } /* Cards grid for result items */

.dest-card { 
    background: white; padding: 25px; border-radius: 16px; 
    box-shadow: 0 10px 30px rgba(0,0,0,0.06); 
    border: 1px solid rgba(0,0,0,0.03);
    display: flex; flex-direction: column;
    position: relative;
    overflow: hidden;
}
.rank { 
    position: absolute; top: -10px; right: -10px; width: 60px; height: 60px; 
    background: #f1f2f6; border-radius: 50%; color: #b2bec3; 
    display: flex; align-items: flex-end; justify-content: flex-start; 
    padding: 10px; font-size: 1.5rem; font-weight: 900; opacity: 0.3; pointer-events: none;
}
.dest-card:nth-child(1) .rank, .dest-card:nth-child(2) .rank, .dest-card:nth-child(3) .rank {
    background: #ffeaa7; color: #fdcb6e; opacity: 0.8;
}

.card-header h3 { margin: 0 0 10px 0; font-size: 1.5rem; color: #2d3436; position: relative; z-index: 1; }

.tags { margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 6px; }
.tag { background: #f0f2f5; padding: 4px 10px; border-radius: 6px; color: #636e72; font-size: 0.8em; }
.season-tag { background: #ffeaa7; color: #d35400; padding: 4px 10px; border-radius: 6px; font-size: 0.8em; font-weight: bold; }

.reason { color: #636e72; line-height: 1.6; font-size: 0.95rem; flex: 1; margin-bottom: 20px; text-align: justify; }

.plan-btn { 
    width: 100%;
    background: white; border: 2px solid #0984e3; color: #0984e3; 
    padding: 10px; border-radius: 10px; font-weight: 700; cursor: pointer; transition: all 0.3s;
}
.plan-btn:hover { background: #0984e3; color: white; box-shadow: 0 5px 15px rgba(9, 132, 227, 0.3); }

/* Animations */
.fade-in-up { animation: fadeInUp 0.5s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.hover-float { transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s; }
.hover-float:hover { transform: translateY(-8px); box-shadow: 0 20px 40px rgba(0,0,0,0.12); z-index: 10; }
</style>
