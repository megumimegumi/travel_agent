<template>
  <div class="planner-page fade-in-up">
    <div class="sidebar">
      <h2>🛠️ 行程定制</h2>
      
      <div class="form-group">
        <label>目的地</label>
        <input v-model="form.destination" placeholder="例如：厦门" />
      </div>
      <div class="form-group">
        <label>出发地</label>
        <input v-model="form.origin" placeholder="例如：上海" />
      </div>
      <div class="form-group">
        <label>出发日期</label>
        <input type="date" v-model="form.start_date" />
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>天数</label>
          <input type="number" v-model.number="form.days" min="1" max="14" />
        </div>
        <div class="form-group">
          <label>预算(元)</label>
          <input type="number" v-model.number="form.budget" step="100" />
        </div>
      </div>

      <div class="form-group">
        <label>同行关系</label>
        <select v-model="form.travelers_relation">
          <option>独自一人</option>
          <option>情侣/夫妻</option>
          <option>朋友</option>
          <option>家庭</option>
        </select>
      </div>
      <div class="form-group">
        <label>人数</label>
        <input type="number" v-model.number="form.travelers_count" min="1" />
      </div>

      <div class="form-group">
        <label>体力水平</label>
        <select v-model="form.fitness_level">
          <option value="铁人三项">铁人三项</option>
          <option value="精力充沛">精力充沛</option>
          <option value="普通人">普通人</option>
          <option value="容易累">容易累</option>
        </select>
      </div>
      <div class="form-group">
        <label>旅行节奏</label>
        <select v-model="form.pace">
          <option value="悠闲放松">悠闲放松</option>
          <option value="适中">适中</option>
          <option value="紧凑充实">紧凑充实</option>
          <option value="特种兵打卡">特种兵打卡</option>
        </select>
      </div>

      <div class="form-group">
        <label>住宿偏好</label>
        <select v-model="form.accommodation_preference">
          <option>经济型 (¥100-300)</option>
          <option>舒适型 (¥300-600)</option>
          <option>高档型 (¥600-1000)</option>
          <option>豪华型 (¥1000-2000)</option>
          <option>奢华型 (¥2000+)</option>
        </select>
      </div>

       <div class="form-group">
        <label>兴趣偏好 (多选, 逗号分隔)</label>
        <input v-model="interestsInput" placeholder="美食, 摄影, 古迹..." />
      </div>

       <div class="form-group">
        <label>额外要求 (选填)</label>
        <textarea v-model="form.extra_requirements" rows="2" placeholder="例如：必须要去迪士尼，或者想避开人流..." class="text-area-input"></textarea>
      </div>

      <button @click="generatePlan" :disabled="loading" class="generate-btn">
        {{ loading ? '🚀 AI 规划中...' : '生成行程' }}
      </button>
    </div>

    <!-- Right Side Content -->
    <div class="content-area">
      <Transition name="fade" mode="out-in">
        <div v-if="!itinerary && !loading" class="placeholder key-1">
            <div class="placeholder-content">
                <div class="art-logo">
                    <svg viewBox="0 0 200 200" width="200" height="200" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="100" cy="100" r="80" fill="#e3f2fd" />
                        <path d="M60 100 Q100 60 140 100 T180 100" stroke="#90caf9" stroke-width="4" fill="none" />
                        <text x="100" y="115" text-anchor="middle" font-size="24" fill="#1e88e5">✈️</text>
                        <circle cx="140" cy="50" r="10" fill="#ffe082" />
                    </svg>
                </div>
                <h3>👈 开始您的旅程</h3>
                <p>在左侧填写信息，让 AI 为您定制完美行程</p>
            </div>
        </div>
      
        <div v-else-if="loading" class="loading-state key-2">
            <div class="spinner"></div>
            <div class="thinking-logs">
                <p v-for="(log, idx) in thinkingLogs" :key="idx" class="log-item">{{ log }}</p>
            </div>
        </div>

        <div v-else-if="itinerary" class="result-container key-3">
            <div class="header-card">
            <h2>📍 {{ itinerary.request.destination }} · {{ itinerary.request.days }}日智能规划</h2>
            <div class="meta-info">
                <span>💰 预算: ¥{{ itinerary.total_cost_estimate }}</span>
                <span>🗓️ {{ itinerary.request.start_date }}</span>
            </div>
            <div class="actions">
                <button @click="saveItinerary" class="save-btn">💾 保存</button>
                <button @click="showSimInput = !showSimInput" class="sim-btn">⚡ 应对突发</button>
            </div>
            </div>

            <!-- Simulation Input & Result -->
            <Transition name="slide-down">
                <div v-if="showSimInput" class="sim-card">
                    <h3>🌩️ 模拟行程突发状况</h3>
                    <div class="sim-input-group">
                        <input v-model="simEventDesc" placeholder="例如：突然下大暴雨，或者航班延误了..." />
                        <button @click="simulatePlan" :disabled="simulating">
                            {{ simulating ? '正在调整...' : '开始调整' }}
                        </button>
                    </div>

                    <!-- Inline Result Display -->
                    <div v-if="showSimChanges" class="sim-results-inline">
                        <div class="sim-header-inline">
                            <h4>⚡ 调整报告</h4>
                            <button class="close-btn-text" @click="showSimChanges = false; showSimInput = false;">确认并关闭</button>
                        </div>
                        <p class="sim-intro">AI 已根据突发情况为您重组行程，变动如下：</p>
                        <div class="change-list">
                            <div v-for="(change, idx) in simulationChanges" :key="idx" :class="['change-item', change.type]">
                                <div class="change-icon">
                                    <span v-if="change.type === 'modify'">🔄</span>
                                    <span v-if="change.type === 'cancel'">⛔</span>
                                    <span v-if="change.type === 'add'">✨</span>
                                    <span v-if="change.type === 'info'">ℹ️</span>
                                </div>
                                <div class="change-content">
                                    <strong>Day {{ change.day }}</strong>
                                    <span>{{ change.text }}</span>
                                    <div v-if="change.details" class="change-detail">{{ change.details }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </Transition>

            <div class="days-container">
            <div v-for="day in itinerary.daily_plans" :key="day.day" class="day-card">
                <div class="day-header">
                <h3>Day {{ day.day }} | {{ day.theme }}</h3>
                <span class="weather-badge">🌤️ {{ day.weather_summary }}</span>
                </div>
                <div class="activities">
                <div v-for="(act, idx) in day.activities" :key="idx" class="activity-item">
                    <div class="time-col">
                        <span class="time">{{ act.time }}</span>
                        <div class="line"></div>
                    </div>
                    <div class="details-card">
                        <div class="act-header">
                            <strong>{{ act.activity }}</strong>
                            <span class="check" @click="toggleDetail(act)">
                                {{ act.showDetail ? '🔽 收起详情' : '🔍 查看详情' }}
                            </span>
                        </div>
                        <p class="desc">{{ act.description }}</p>
                        <p class="meta">📍 {{ act.location }} <span v-if="act.transport_suggestion">| 🚗 {{ act.transport_suggestion }}</span></p>
                        
                        <!-- Scenic Info Injection -->
                        <Transition name="slide-down">
                        <div v-if="act.showDetail && act.scenic_info" class="scenic-gallery">
                            <div class="scenic-tags" v-if="act.scenic_info.level">
                                <span class="tag">{{ act.scenic_info.level }}</span>
                                <span class="tag price">{{ act.scenic_info.price }}</span>
                            </div>
                            <div class="scenic-intro" v-if="act.scenic_info.content">
                                <p>{{ act.scenic_info.content }}</p>
                            </div>
                            <!-- Images -->
                            <div class="img-scroll" v-if="act.scenic_info.photos && act.scenic_info.photos.length">
                                <img v-for="(url, pidx) in act.scenic_info.photos" :key="pidx" :src="url" @click="enlargeImage(url)" />
                            </div>
                            <!-- Static Map -->
                            <div class="static-map" v-if="act.scenic_info.static_map">
                                <img :src="act.scenic_info.static_map" @click="enlargeImage(act.scenic_info.static_map)" alt="Map" />
                            </div>
                        </div>
                        </Transition>
                    </div>
                </div>
                </div>
            </div>
            </div>
            
            <!-- 准备清单 & Tips -->
            <div class="extra-modules-grid">
            <div v-if="itinerary.preparation_list" class="module-card">
                <h3>🧳 行前准备</h3>
                <div class="prep-list">
                <div v-for="(items, category) in itinerary.preparation_list" :key="category" class="prep-item">
                    <strong>{{ category }}</strong>: {{ items.join(', ') }}
                </div>
                </div>
            </div>
            <div v-if="itinerary.special_tips" class="module-card">
                <h3>🚦 避坑指南</h3>
                <div v-for="(tips, type) in itinerary.special_tips" :key="type" class="prep-item">
                <p><strong>{{ type }}</strong>: {{ tips.join('; ') }}</p>
                </div>
            </div>
            </div>

        </div>
      </Transition>
    </div>

    <!-- Image Modal -->
    <Transition name="modal-fade">
        <div v-if="zoomedImage" class="modal-overlay" @click="zoomedImage = null">
            <img :src="zoomedImage" class="modal-img" />
        </div>
    </Transition>

    <!-- Toast Notification -->
    <Transition name="toast-fade">
        <div v-if="showToast" class="toast-notification">
            <span class="toast-icon">✅</span>
            <span class="toast-message">{{ toastMessage }}</span>
        </div>
    </Transition>

  </div>
</template>

<style scoped>
/* Toast Styles */
.toast-notification {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.85);
    color: white;
    padding: 20px 40px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    z-index: 3000;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px;
    backdrop-filter: blur(5px);
    width: 250px;
    text-align: center;
}

.toast-icon {
    font-size: 3rem;
    display: block;
    animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-message {
    font-size: 1.1rem;
    font-weight: 500;
}

.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.4s ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translate(-50%, -40%); }

@keyframes popIn {
    0% { transform: scale(0.5); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

/* Sim Inline Styles */
.sim-results-inline {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #eee;
    animation: fadeIn 0.4s ease;
}
.sim-header-inline { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.sim-header-inline h4 { margin: 0; color: #2d3436; font-size: 1.1em; }
.close-btn-text { background: none; border: none; color: #0984e3; cursor: pointer; font-size: 0.9em; }
.sim-intro { font-size: 0.9em; color: #666; margin-bottom: 10px; }

.change-list { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; }
.change-item { display: flex; gap: 8px; padding: 10px; border-radius: 6px; background: #f8f9fa; border-left: 3px solid #ddd; font-size: 0.9em; }
.change-item.modify { border-color: #74b9ff; background: #eaf4ff; }
.change-item.cancel { border-color: #ff7675; background: #ffeae9; }
.change-item.add { border-color: #55efc4; background: #eafffa; }
.change-icon { font-size: 1.1em; }
.change-content strong { display: block; margin-bottom: 2px; color: #2d3436; }
.change-detail { font-size: 0.85em; color: #636e72; margin-top: 2px; font-family: monospace; }

/* Animation Keyframes */
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const loading = ref(false);
const itinerary = ref(null);
const interestsInput = ref(''); // Cleared default
const zoomedImage = ref(null);
const thinkingLogs = ref([]);

const form = ref({
  destination: '厦门',
  origin: '上海',
  start_date: new Date().toISOString().split('T')[0],
  days: 2,
  budget: 3000,
  travelers_count: 1,
  travelers_relation: '独自一人',
  fitness_level: '普通人',
  pace: '适中',
  accommodation_preference: '舒适型 (¥300-600)',
  extra_requirements: '',
  interests: []
});

const showSimInput = ref(false);
const simEventDesc = ref('');
const simulating = ref(false);

const showToast = ref(false);
const toastMessage = ref('');

onMounted(() => {
  const q = route.query;
  if (q.destination) form.value.destination = q.destination;
  if (q.origin) form.value.origin = q.origin;
  if (q.days) form.value.days = parseInt(q.days);
  if (q.budget) form.value.budget = parseInt(q.budget);
  if (q.relation) form.value.travelers_relation = q.relation;
  if (q.fitness) form.value.fitness_level = q.fitness.split(' ')[0]; // Extract "普通人" from "普通人 (xxx)"
  if (q.start_date) form.value.start_date = q.start_date;
});

// Helper to fetch images
const enrichItinerary = async (planData) => {
    // Flatten activities to find scenic spots
    // We only enhance activities that likely have scenic spots (not meals/transport if possible, but simplest is all)
    if (!planData || !planData.daily_plans) return;

    for (const day of planData.daily_plans) {
        for (const act of day.activities) {
            // Lazy simple check: if location is specific
            if (act.location && act.location.length > 1 && !act.location.includes("酒店")) {
                fetchScenicInfo(act);
            }
        }
    }
};

const fetchScenicInfo = async (activity) => {
    try {
        const city = itinerary.value.request.destination;
        const res = await fetch(`/api/tools/scenic_info?keyword=${encodeURIComponent(activity.location)}&city=${encodeURIComponent(city)}`);
        const data = await res.json();
        if (data && !data.error) {
            // Vue 3 reactivity: we can just assign property
            activity.scenic_info = data;
        }
    } catch (e) {
        console.warn("Failed to fetch info for", activity.location);
    }
};

const enlargeImage = (url) => {
    zoomedImage.value = url;
};

const toggleDetail = (act) => {
    act.showDetail = !act.showDetail;
    if (act.showDetail && !act.scenic_info) {
        fetchScenicInfo(act);
    }
};

const simulateThinking = () => {
    thinkingLogs.value = [];
    const steps = [
        "🤔 正在理解您的旅行需求...",
        "🌤️ 正在查询目的地天气与交通...",
        "🏨 正在筛选符合您偏好的住宿...",
        "🗺️ 正在规划最佳游玩路线...",
        "✨ 正在生成个性化避坑指南..."
    ];
    let i = 0;
    const interval = setInterval(() => {
        if (i < steps.length) {
            thinkingLogs.value.push(steps[i]);
            i++;
        } else {
            clearInterval(interval);
        }
    }, 800);
    return interval;
};

const generatePlan = async () => {
  loading.value = true;
  itinerary.value = null;
  const thinkingInterval = simulateThinking();
  
  // Parse interests
  form.value.interests = interestsInput.value.split(',').map(s => s.trim()).filter(s => s);
  
  try {
    const response = await fetch('/api/plan/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    });
    
    if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Server Error (${response.status}): ${errText}`);
    }
    
    const data = await response.json();
    clearInterval(thinkingInterval);
    itinerary.value = data;
    
    // Start enriching in background
    enrichItinerary(data);
    
  } catch (error) {
    alert('规划生成失败: ' + error.message);
  } finally {
    loading.value = false;
    clearInterval(thinkingInterval);
  }
};

const showSimChanges = ref(false);
const simulationChanges = ref([]);

const compareItineraries = (oldPlan, newPlan) => {
    const changes = [];
    if (!oldPlan || !newPlan) return ["行程已整体重置"];
    
    const daysOld = oldPlan.daily_plans || [];
    const daysNew = newPlan.daily_plans || [];
    
    const maxDays = Math.max(daysOld.length, daysNew.length);
    
    for (let i = 0; i < maxDays; i++) {
        const dayNum = i + 1;
        if (i >= daysNew.length) {
            changes.push({ day: dayNum, type: 'cancel', text: `取消了第 ${dayNum} 天由于不可抗力无法进行的行程` });
            continue;
        }
        if (i >= daysOld.length) {
             changes.push({ day: dayNum, type: 'add', text: `新增了第 ${dayNum} 天的行程安排` });
             continue;
        }

        const dOld = daysOld[i];
        const dNew = daysNew[i];
        
        // Detailed comparison
        let removedActs = [];
        let addedActs = [];
        let modifiedActs = [];

        // Simple check by title string
        const oldTitles = dOld.activities.map(a => a.activity);
        const newTitles = dNew.activities.map(a => a.activity);
        
        // Find Removed
        dOld.activities.forEach(oldA => {
            if (!newTitles.includes(oldA.activity)) removedActs.push(oldA);
        });
        
        // Find Added
        dNew.activities.forEach(newA => {
            if (!oldTitles.includes(newA.activity)) addedActs.push(newA);
        });
        
        // Try to match removed -> added as Replacement
        // Heuristic: If we have 1 removed and 1 added, likely a replacement. 
        // Or if 'removed' location is same type (Indoor/Outdoor checks are hard here without data).
        // We will just sequentially pair them if counts match or close.
        
        let processedRemoved = [];
        
        if (removedActs.length > 0 && addedActs.length > 0) {
            // Pair them up
            const pairCount = Math.min(removedActs.length, addedActs.length);
            for(let k=0; k<pairCount; k++) {
                const rem = removedActs[k];
                const add = addedActs[k];
                processedRemoved.push(rem.activity);
                
                // Construct reason if available
                let reason = "受突发状况影响";
                if(simEventDesc.value.includes("雨") || simEventDesc.value.includes("雪")) reason = "因天气原因";
                if(simEventDesc.value.includes("延误") || simEventDesc.value.includes("交通")) reason = "因交通变故";
                
                changes.push({
                    day: dayNum,
                    type: 'modify',
                    text: `第 ${dayNum} 天行程变更`,
                    details: `原计划前往 "${rem.activity}" ${reason}改为前往 "${add.activity}"`
                });
            }
            // Logic to handle leftovers would go here
        } 
        else if (removedActs.length > 0) {
             removedActs.forEach(rem => {
                 changes.push({
                     day: dayNum, 
                     type: 'cancel',
                     text: `第 ${dayNum} 天取消了 "${rem.activity}"`
                 });
             });
        }
        else if (addedActs.length > 0) {
             addedActs.forEach(add => {
                 changes.push({
                     day: dayNum, 
                     type: 'add',
                     text: `第 ${dayNum} 天新增了 "${add.activity}"`
                 });
             });
        }
        
        // Theme changes
        if (dOld.theme !== dNew.theme) {
                 changes.push({ 
                    day: dayNum, 
                    type: 'modify', 
                    text: `第 ${dayNum} 天主题调整: "${dOld.theme}" -> "${dNew.theme}"`
                });
        }
    }
    
    if (changes.length === 0) changes.push({ day: 0, type: 'info', text: '行程整体无重大变动，仅做微调' });
    return changes;
};

const simulatePlan = async () => {
    if (!simEventDesc.value) return;
    simulating.value = true;
    try {
        // Keep a copy of old
        const oldPlan = JSON.parse(JSON.stringify(itinerary.value));
        
        const response = await fetch('/api/plan/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                itinerary: itinerary.value,
                event_description: simEventDesc.value,
                current_request: form.value
            })
        });
        if (!response.ok) {
            const errText = await response.text();
            throw new Error(`Simulation failed: ${response.status} ${errText}`);
        }
        const data = await response.json();
        
        let newPlan = null;
        if (data.new_itinerary) {
            newPlan = data.new_itinerary;
        } else if (data.updated_plan) {
            newPlan = data.updated_plan;
        }
        
        if (newPlan) {
            itinerary.value = newPlan;
            simulationChanges.value = compareItineraries(oldPlan, newPlan);
            showSimChanges.value = true; // Show modal
            
            // Enrich the new plan with images/info
            enrichItinerary(newPlan);
        }
        
        simEventDesc.value = '';
        showSimInput.value = false;
        
    } catch (e) {
        console.error(e);
        alert('模拟调整失败: ' + e.message);
    } finally {
        simulating.value = false;
    }
};

const saveItinerary = async () => {
  if (!itinerary.value) return;
  
  // Get logged-in user
  const u = localStorage.getItem('user');
  let user = null;
  if(u) {
      try { user = JSON.parse(u); } catch(e) {}
  }
  
  if (!user || !user.user_id) {
      alert('请先登录才能保存行程！');
      return;
  }

  try {
    const response = await fetch('/api/itineraries/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: user.user_id, // Use actual user ID
        itinerary_data: itinerary.value
      })
    });
    if (response.ok) {
      toastMessage.value = '行程已保存到\n“我的行程”';
      showToast.value = true;
      setTimeout(() => {
          showToast.value = false;
      }, 2000);
    } else {
       throw new Error('Server returned ' + response.status);
    }
  } catch (e) {
    alert('保存失败: ' + e);
  }
};
</script>


<style scoped>
/* Page Layout */
.planner-page {
  display: flex;
  height: calc(100vh - 60px); /* 60px is approx nav height */
  width: 100vw;
  overflow: hidden;
  background-color: #fdfcf8;
}

.sidebar {
  width: 320px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #ffffff 0%, #f7f9fc 100%);
  padding: 24px;
  border-right: 1px solid #eaeaea;
  overflow-y: auto;
  box-shadow: 2px 0 10px rgba(0,0,0,0.02);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.sidebar h2 {
    font-size: 1.2rem;
    color: #333;
    margin-bottom: 10px;
    font-weight: 600;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 0; /* Remove padding to be full flush */
  background: #fdfcf8;
  position: relative;
}

/* Animations */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-down-enter-active, .slide-down-leave-active { transition: all 0.4s ease; max-height: 200px; opacity: 1; }
.slide-down-enter-from, .slide-down-leave-to { max-height: 0; opacity: 0; overflow: hidden; }

/* Form Elements */
.form-group label { display: block; font-size: 0.85em; color: #7f8c8d; margin-bottom: 6px; font-weight: 500; }
.form-group input, .form-group select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  transition: all 0.3s;
  font-size: 0.95em;
  box-sizing: border-box; /* Fix width overflow */
}
.form-group input:focus, .form-group select:focus, .text-area-input:focus {
  border-color: #a18cd1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(161, 140, 209, 0.1);
}
.text-area-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  transition: all 0.3s;
  font-size: 0.95em;
  box-sizing: border-box;
  font-family: inherit;
  resize: vertical;
}

.form-row { display: flex; gap: 12px; }
.form-row .form-group { flex: 1; }

.generate-btn {
  width: 100%; margin-top: 20px; padding: 14px;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
  color: white; border: none; border-radius: 12px;
  font-weight: 600; font-size: 1rem; cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 15px rgba(161, 140, 209, 0.4);
}
.generate-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(161, 140, 209, 0.5); }
.generate-btn:disabled { opacity: 0.7; cursor: wait; }

/* Result Layout */
.placeholder, .loading-state {
    display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
    padding-top: 5vh; /* Moved up significantly */
    height: 100%; color: #95a5a6;
}
.art-logo { margin-bottom: 20px; animation: float 6s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }

.placeholder-content { text-align: center; }
.placeholder-content h3 { font-size: 1.5rem; color: #34495e; margin: 10px 0; }
.thinking-logs { margin-top: 20px; text-align: left; }
.log-item { background: #f0f2f5; padding: 8px 15px; border-radius: 20px; margin-bottom: 8px; font-size: 0.9em; animation: fadeIn 0.5s ease; color: #555; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

.key-1 { background: #fdfcf8; } /* Ensures bg color during transition */
.key-2 { background: #fdfcf8; }

.result-container {
  max-width: 1000px; /* Limit width for reading ease, but allow centering */
  margin: 0 auto;
  padding: 40px;
}

.header-card {
  background: white; padding: 30px; border-radius: 16px; 
  box-shadow: 0 10px 30px rgba(0,0,0,0.03); margin-bottom: 30px;
  border: 1px solid #f0f0f0;
  position: relative; overflow: hidden;
}
.header-card::before {
    content: ''; position: absolute; top:0; left:0; width: 6px; height: 100%;
    background: linear-gradient(to bottom, #a18cd1, #fbc2eb);
}

.header-card h2 { margin: 0 0 15px 0; color: #2c3e50; font-size: 1.8rem; }
.meta-info { display: flex; gap: 20px; color: #666; font-size: 1rem; }
.meta-info span { background: #f8f9fa; padding: 6px 12px; border-radius: 6px; }

.actions { margin-top: 20px; display: flex; gap: 12px; }
.save-btn, .sim-btn {
    border:none; padding: 10px 20px; border-radius: 8px; cursor: pointer;
    font-weight: 600; transition: filter 0.2s;
}
.save-btn { background: #e0f7fa; color: #00838f; }
.sim-btn { background: #fff3e0; color: #ef6c00; }
.save-btn:hover, .sim-btn:hover { filter: brightness(0.95); }

/* Simulation Card */
.sim-card {
    background: #fff8f8; border: 1px solid #ffebee; border-radius: 12px;
    padding: 20px; margin-bottom: 30px;
}
.sim-card h3 { margin: 0 0 10px 0; color: #c62828; font-size: 1.1em; }
.sim-input-group { display: flex; gap: 10px; }
.sim-input-group input { flex: 1; padding: 10px; border: 1px solid #ffcdd2; border-radius: 6px; }
.sim-input-group button { background: #ef5350; color: white; border: none; padding: 0 24px; border-radius: 6px; cursor: pointer; font-weight: bold;}

/* Days & Activities */
.day-card { 
    background: white; margin-bottom: 30px; border-radius: 16px; 
    padding: 0; 
    box-shadow: 0 4px 20px rgba(0,0,0,0.02); 
    border: 1px solid #f5f5f5;
    overflow: hidden;
}

.day-header { 
    background: #fbfbfb;
    padding: 20px 30px; border-bottom: 1px solid #eee; 
    display: flex; justify-content: space-between; align-items: center; 
}
.day-header h3 { margin: 0; color: #34495e; font-size: 1.2rem; }
.weather-badge { background: white; padding: 6px 12px; border-radius: 20px; font-size: 0.9em; box-shadow: 0 2px 5px rgba(0,0,0,0.05); color: #f39c12; }

.activities { padding: 30px; }
.activity-item { display: flex; gap: 20px; margin-bottom: 30px; position: relative; }
.activity-item:last-child { margin-bottom: 0; }

.time-col { width: 60px; display: flex; flex-direction: column; align-items: center; flex-shrink: 0; }
.time-col .time { font-weight: bold; color: #3498db; font-size: 0.9em; margin-bottom: 5px; }
.time-col .line { width: 2px; flex: 1; background: #eef2f6; border-radius: 1px; }

.details-card { flex: 1; background: #fff; }
.act-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
.act-header strong { font-size: 1.1em; color: #2c3e50; }
.check { cursor: pointer; font-size: 0.8em; color: #95a5a6; }
.check:hover { color: #3498db; }

.desc { color: #576574; line-height: 1.6; margin: 5px 0 10px 0; font-size: 0.95em; }
.meta { font-size: 0.85em; color: #95a5a6; display: flex; gap: 10px; align-items: center; }

/* Scenic Gallery */
.scenic-gallery { margin-top: 15px; padding-top: 15px; border-top: 1px dashed #eee; }
.scenic-tags { margin-bottom: 10px; }
.tag { display: inline-block; padding: 2px 8px; background: #f0f2f5; color: #666; border-radius: 4px; font-size: 0.8em; margin-right: 8px; }
.tag.price { background: #fff3e0; color: #e67e22; }

.img-scroll { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 5px; scrollbar-width: thin; }
.img-scroll img { height: 100px; border-radius: 8px; cursor: zoom-in; object-fit: cover; transition: transform 0.2s; }
.img-scroll img:hover { transform: scale(1.05); }

.static-map { margin-top: 10px; border-radius: 8px; overflow: hidden; border: 1px solid #eee; }
.static-map img { width: 100%; height: 150px; object-fit: cover; display: block; cursor: zoom-in;}

/* Extra Modules */
.extra-modules-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 30px; }
.module-card { background: white; padding: 25px; border-radius: 16px; border: 1px solid #f5f5f5; box-shadow: 0 5px 15px rgba(0,0,0,0.02); }
.module-card h3 { margin-top: 0; color: #34495e; border-bottom: 2px solid #a18cd1; display: inline-block; padding-bottom: 5px; margin-bottom: 15px; }
.prep-item { margin-bottom: 8px; font-size: 0.95em; color: #555; }

/* Image Modal */
.modal-overlay { 
    position: fixed; top:0; left:0; width: 100vw; height: 100vh; 
    background: rgba(0,0,0,0.95); z-index: 2000; 
    display: flex; justify-content: center; align-items: center; 
    cursor: zoom-out; backdrop-filter: blur(5px); 
}
.modal-img { 
    width: 100vw; 
    height: 100vh; 
    object-fit: contain;
    border-radius: 0;
    box-shadow: none;
}

.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.4s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .modal-img { animation: zoomInFull 0.4s cubic-bezier(0.165, 0.84, 0.44, 1); }
.modal-fade-leave-active .modal-img { animation: zoomOutFull 0.3s ease; }

@keyframes zoomInFull { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes zoomOutFull { from { transform: scale(1); opacity: 1; } to { transform: scale(0.95); opacity: 0; } }

@keyframes zoomInFull { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
@keyframes zoomOutFull { from { transform: scale(1); opacity: 1; } to { transform: scale(0.95); opacity: 0; } }

.loading-state { text-align: center; color: #666; width: 100%; }
.spinner { 
  width: 40px; height: 40px; border: 4px solid #f3f3f3; border-top: 4px solid #a18cd1; 
  border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px auto; 
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Page Transition */
.fade-in-up { animation: fadeInUp 0.6s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
