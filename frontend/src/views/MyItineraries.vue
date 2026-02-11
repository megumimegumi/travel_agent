<template>
  <div class="list-page fade-in-up">
    <h2>📂 我的行程历史</h2>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else-if="list.length === 0" class="empty">
      暂无保存的行程，去 <router-link to="/planner">创建一个</router-link>？
    </div>
    
    <div v-else class="grid">
      <div v-for="item in list" :key="item.id" class="card">
        <div class="card-header">
           <span class="dest">{{ item.destination }}</span>
           <span class="date">{{ item.created_at ? item.created_at.split('T')[0] : '' }}</span>
        </div>
        <div class="card-body">
          <p>📅 出发: {{ item.start_date || '未定' }} ({{ item.days }}天)</p>
          <p>💰 预算: ¥{{ item.total_cost }}</p>
        </div>
        <div class="card-footer">
          <button @click="toggleFavorite(item)" :class="['fav-btn', { active: item.is_favorite }]">
            {{ item.is_favorite ? '❤️ 已收藏' : '🤍 收藏' }}
          </button>
          <button @click="deleteItem(item.id)" class="del-btn">🗑️ 删除</button>
          <button @click="viewDetail(item)" class="view-btn">查看详情</button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <Transition name="fade">
      <div v-if="showDetailModal && selectedItinerary" class="modal-overlay" @click.self="showDetailModal = false">
        <div class="detail-card">
          <div class="modal-header">
            <h3>📝 {{ selectedItinerary.destination }} 行程详情</h3>
            <button class="close-btn" @click="showDetailModal = false">×</button>
          </div>
          
          <div class="modal-content">
             <div class="meta-info">
                <span>🗓️ {{ selectedItinerary.start_date }}出发</span>
                <span>📅 {{ selectedItinerary.days }}天</span>
                <span>💰 预估费用 ¥{{ selectedItinerary.total_cost }}</span>
             </div>
             
             <!-- Render Daily Plans -->
             <div class="timeline">
               <div v-for="day in selectedItinerary.content_json.daily_plans" :key="day.day" class="day-container">
                  <div class="day-header">Day {{ day.day }} | {{ day.theme }}</div>
                  
                  <div v-for="(act, idx) in day.activities" :key="idx" class="activity-item">
                     <div class="time">{{ act.time }}</div>
                     <div class="act-details">
                        <div class="act-title">{{ act.activity }}</div>
                        <div class="act-desc">{{ act.description }}</div>
                        <div class="act-loc" v-if="act.location">📍 {{ act.location }}</div>
                     </div>
                  </div>
               </div>
             </div>
          </div>
          
          <div class="modal-footer">
             <button class="action-btn" @click="editPlan(selectedItinerary)">✏️ 编辑/重新规划</button>
             <button class="close-btn-text" @click="showDetailModal = false">关闭</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const list = ref([]);
const loading = ref(true);

const showDetailModal = ref(false);
const selectedItinerary = ref(null);

const getUser = () => {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
};

const fetchList = async () => {
  const user = getUser();
  if (!user || !user.user_id) {
      loading.value = false;
      return; 
  }
  
  try {
    const res = await fetch(`/api/itineraries/${user.user_id}`);
    list.value = await res.json();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const viewDetail = (item) => {
  selectedItinerary.value = item;
  showDetailModal.value = true;
};

const editPlan = (item) => {
  // Navigate to planner with this plan as preset? 
  // For now, just go to planner with destination.
  // Ideally, we should support loading existing plan.
  router.push({ path: '/planner', query: { destination: item.destination } });
};

const toggleFavorite = async (item) => {
  const newStatus = !item.is_favorite;
  const action = newStatus ? 'favorite' : 'unfavorite';
  
  await fetch(`/api/itineraries/${item.id}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ itinerary_id: item.id, action })
  });
  
  item.is_favorite = newStatus;
};

const deleteItem = async (id) => {
  if (!confirm('确定删除吗？')) return;
  await fetch(`/api/itineraries/${id}/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ itinerary_id: id, action: 'delete' })
  });
  list.value = list.value.filter(i => i.id !== id);
};

onMounted(fetchList);
</script>

<style scoped>
/* Page & Card Styles */
.list-page { max-width: 1000px; margin: 0 auto; padding: 20px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
.card { background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s; }
.card:hover { transform: translateY(-3px); }
.card-header { background: linear-gradient(135deg, #66a6ff, #89f7fe); color: white; padding: 15px; display: flex; justify-content: space-between; align-items: center; }
.dest { font-size: 1.2em; font-weight: bold; }
.date { font-size: 0.8em; opacity: 0.9; }
.card-body { padding: 15px; flex: 1; color: #555; }
.card-footer { padding: 10px 15px; border-top: 1px solid #eee; display: flex; justify-content: space-between; background: #fdfdfd; }
button { border: none; background: none; cursor: pointer; font-size: 0.9em; padding: 6px 12px; border-radius: 4px; transition: background 0.2s; }
.fav-btn:hover { background: #ffeaa7; }
.fav-btn.active { color: #e55039; }
.del-btn { color: #b2bec3; }
.del-btn:hover { color: #e55039; background: #ffeaa7; }
.view-btn { color: #0984e3; background: #dfe6e9; font-weight: 500; }
.view-btn:hover { background: #74b9ff; color: white; }

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; animation: fadeIn 0.3s; }
.detail-card { background: white; width: 600px; max-width: 95%; max-height: 90vh; border-radius: 12px; display: flex; flex-direction: column; box-shadow: 0 10px 25px rgba(0,0,0,0.2); animation: slideUp 0.3s; }
.modal-header { padding: 15px 20px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; color: #2d3436; }
.close-btn { font-size: 1.5rem; color: #b2bec3; }

.modal-content { overflow-y: auto; padding: 20px; flex: 1; }
.meta-info { display: flex; gap: 15px; background: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 20px; font-size: 0.9em; color: #636e72; }

/* Timeline Styles */
.day-container { margin-bottom: 20px; }
.day-header { font-weight: bold; color: #0984e3; margin-bottom: 10px; border-left: 4px solid #74b9ff; padding-left: 10px; font-size: 1.1em; }
.activity-item { display: flex; margin-bottom: 12px; padding-left: 15px; position: relative; }
.activity-item::before { content: ''; position: absolute; left: 0; top: 6px; width: 6px; height: 6px; background: #dfe6e9; border-radius: 50%; }
.time { width: 60px; font-size: 0.85em; color: #999; flex-shrink: 0; }
.act-title { font-weight: 600; color: #2d3436; }
.act-desc { font-size: 0.9em; color: #636e72; margin-top: 2px; }
.act-loc { font-size: 0.8em; color: #00cec9; margin-top: 2px; }

.modal-footer { padding: 15px; border-top: 1px solid #eee; text-align: right; }
.action-btn { background: #0984e3; color: white; margin-right: 10px; font-weight: bold; }
.close-btn-text { background: #eee; color: #666; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

.fade-in-up { animation: slideUp 0.6s ease-out; }
</style>
