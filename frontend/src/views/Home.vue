<template>
  <div class="home-page-container">
  <div class="home-page">
    <div class="hero-section fade-in">
      <h1 class="hero-title"><span class="emoji-icon">🌍</span> AI 智能旅行助手</h1>
      <p class="hero-subtitle">探索世界，智享旅程 —— 您的专属私人旅行定制专家</p>
      
      <div class="feature-cards">
        <div class="card hover-float" @click="$router.push('/planner')">
          <div class="icon">✈️</div>
          <h3>智能规划</h3>
          <p>只需几秒，为您生成包含交通、住宿、景点的完整行程单。</p>
          <span class="link-text">开始规划 &rarr;</span>
        </div>
        
        <div class="card hover-float" @click="$router.push('/recommend')">
          <div class="icon">🎲</div>
          <h3>灵感推荐</h3>
          <p>不知道去哪玩？告诉我们您的偏好，为您匹配最佳目的地。</p>
          <span class="link-text">获取灵感 &rarr;</span>
        </div>
        
        <div class="card hover-float" @click="$router.push('/my-itineraries')">
          <div class="icon">📂</div>
          <h3>我的行程</h3>
          <p>随时查看、管理您保存的行程，记录每一次美好的出发。</p>
          <span class="link-text">查看记录 &rarr;</span>
        </div>
      </div>
    </div>
    
    <div class="showcase-section slide-up">
      <h2 class="section-title">为何选择我们？</h2>
      <div class="benefits-grid">
        <div class="benefit-item hover-float">
          <span class="badg">💡</span>
          <h4>深度定制</h4>
          <p>基于 DeepSeek 大模型，结合实时天气与交通信息，打造可行性极高的方案。</p>
        </div>
        <div class="benefit-item hover-float">
          <span class="badg">⚡</span>
          <h4>突发如意</h4>
          <p>遇到航班延误或恶劣天气？一键重组行程，让旅途无忧。</p>
        </div>
        <div class="benefit-item hover-float">
          <span class="badg">🖼️</span>
          <h4>沉浸体验</h4>
          <p>丰富的景点图文介绍与交互式地图，出行前即可身临其境。</p>
        </div>
      </div>
    </div>

    <!-- New Module: Hot Destinations Carousel -->
    <div class="hot-section slide-up" style="animation-delay: 0.2s;">
        <h2 class="section-title">🔥 当季热门目的地</h2>
        <div class="carousel-container">
            <div class="carousel-track" :style="trackStyle">
                <div v-for="(dest, idx) in extendedDestinations" :key="idx" 
                     class="hot-card hover-float" 
                     @click="goToDest(dest.name)">
                    <div class="hot-img" :style="{ backgroundColor: dest.color }">{{ dest.icon }}</div>
                    <div class="hot-info">
                        <h4>{{ dest.title }}</h4>
                        <p>{{ dest.desc }}</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- New Module: User Reviews Pagination -->
    <div class="review-section slide-up" style="animation-delay: 0.4s;">
        <h2 class="section-title">💬 用户原声</h2>
        <div class="review-display">
             <transition name="fade-slide" mode="out-in">
                <div :key="activeReviewIndex" class="reviews-row-active">
                    <div v-for="review in visibleReviews" :key="review.user" class="review-card hover-float">
                        <p class="review-text">{{ review.text }}</p>
                        <div class="review-user">—— {{ review.user }}</div>
                    </div>
                </div>
            </transition>
        </div>
    </div>

  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

// Mock Data - Expanded to 20 items
const destinations = [
    { name: '大理', title: '大理 · 苍山洱海', desc: '风花雪月，浪漫治愈', icon: '🏞️', color: '#a29bfe' },
    { name: '成都', title: '成都 · 熊猫基地', desc: '天府之国，热辣滚烫', icon: '🐼', color: '#ff7675' },
    { name: '厦门', title: '厦门 · 鼓浪屿', desc: '文艺海岛，慢享时光', icon: '🌊', color: '#74b9ff' },
    { name: '西安', title: '西安 · 大唐不夜城', desc: '梦回长安，一眼千年', icon: '🏯', color: '#fdcb6e' },
    { name: '三亚', title: '三亚 · 亚龙湾', desc: '阳光沙滩，椰林树影', icon: '🌴', color: '#00b894' },
    { name: '北京', title: '北京 · 故宫博物院', desc: '红墙黄瓦，帝王气象', icon: '🏛️', color: '#e17055' },
    { name: '杭州', title: '杭州 · 西湖', desc: '水光潋滟，山色空蒙', icon: '🛶', color: '#0984e3' },
    { name: '重庆', title: '重庆 · 洪崖洞', desc: '8D魔幻，赛博朋克', icon: '🌶️', color: '#d63031' },
    { name: '桂林', title: '桂林 · 漓江', desc: '山水甲天下', icon: '⛰️', color: '#00cec9' },
    { name: '拉萨', title: '拉萨 · 布达拉宫', desc: '日光之城，信仰之地', icon: '🙏', color: '#6c5ce7' },
    // Added 10 more
    { name: '青岛', title: '青岛 · 栈桥', desc: '红瓦绿树，碧海蓝天', icon: '🍺', color: '#74b9ff' },
    { name: '苏州', title: '苏州 · 园林', desc: '江南园林，甲天下', icon: '🎋', color: '#55efc4' },
    { name: '南京', title: '南京 · 夫子庙', desc: '六朝古都，秦淮人家', icon: '🏮', color: '#fab1a0' },
    { name: '敦煌', title: '敦煌 · 莫高窟', desc: '大漠孤烟，丝路明珠', icon: '🏜️', color: '#e17055' },
    { name: '长沙', title: '长沙 · 茶颜悦色', desc: '星城魅力，快乐大本营', icon: '🍜', color: '#ff7675' },
    { name: '哈尔滨', title: '哈尔滨 · 冰雪大世界', desc: '东方莫斯科，冰城夏都', icon: '❄️', color: '#81ecec' },
    { name: '昆明', title: '昆明 · 滇池', desc: '春城花都，四季如春', icon: '💐', color: '#a29bfe' },
    { name: '乌鲁木齐', title: '乌鲁木齐 · 天山天池', desc: '西域风情，瓜果飘香', icon: '🍇', color: '#6c5ce7' },
    { name: '张家界', title: '张家界 · 天门山', desc: '阿凡达仙境，奇峰三千', icon: '⛰️', color: '#00b894' },
    { name: '上海', title: '上海 · 外滩', desc: '魔都风情，十里洋场', icon: '🏙️', color: '#0984e3' }
];

const reviews = [
    { text: '"突发暴雨那次真的帮了大忙，AI立刻帮我改成了博物馆行程！"', user: '旅游达人 @小美' },
    { text: '"行程规划非常详细，连交通耗时和预算都算得很准。"', user: '摄影师 @阿杰' },
    { text: '"带爸妈出去玩最怕累，AI规划的节奏刚刚好。"', user: '孝顺的 @Lily' },
    { text: '"原来不知道去哪玩，推荐功能帮我发现了宝藏小城。"', user: '探索者 @Tom' },
    { text: '"界面太好看了，操作也很流畅，爱了爱了！"', user: '设计师 @Vivi' },
    { text: '"避雷指南很有用，帮我省了不少冤枉钱。"', user: '学生党 @小明' },
    { text: '"比以前找攻略快多了，几分钟就搞定了一周的行程。"', user: '忙碌的 @HR' },
    { text: '"美食推荐很地道，没有踩雷，好评！"', user: '吃货 @大胃王' },
    { text: '"喜欢这个突发状况模拟，很有安全感。"', user: '谨慎的 @Anna' },
    { text: '"地图交互很直观，可以直接看到景点位置。"', user: '路痴 @小红' },
    // Added 10 more
    { text: '"第一次带孩子出国玩，多亏了这款应用，行程安排得很合理。"', user: '辣妈 @Sarah' },
    { text: '"推荐的小众景点真的绝了，完全避开了人挤人。"', user: '独行侠 @Jack' },
    { text: '"预算控制功能很棒，每一笔钱都花在刀刃上。"', user: '精打细算的 @Alice' },
    { text: '"交通方案对比很清晰，选了最省时的方案。"', user: '效率控 @Bob' },
    { text: '"住宿推荐的民宿很有特色，老板也很热情。"', user: '民宿控 @Cathy' },
    { text: '"行程可以随时调整，太适合这种随性的人了。"', user: '自由的 @David' },
    { text: '"界面简洁大方，没有广告干扰，体验很好。"', user: '极简主义 @Emily' },
    { text: '"智能打包清单提醒了我带变压器，救命啊！"', user: '健忘的 @Frank' },
    { text: '"语音助手识别很精准，通过对话就能修改行程。"', user: '科技迷 @Grace' },
    { text: '"已经推荐给身边所有朋友了，出国游必备神器！"', user: '热心肠的 @Helen' }
];

// Continuous Marquee Logic
const extendedDestinations = computed(() => [...destinations, ...destinations]);

// Review Logic: Show 2 items, rotate every 5 seconds
const activeReviewIndex = ref(0);
const visibleReviews = computed(() => {
    // Current index and next index. Handle modulo for safe wrapping.
    const i1 = activeReviewIndex.value % reviews.length;
    const i2 = (activeReviewIndex.value + 1) % reviews.length;
    return [reviews[i1], reviews[i2]];
});

let reviewInterval = null;
onMounted(() => {
    reviewInterval = setInterval(() => {
        // Move forward by 2 steps
        activeReviewIndex.value = (activeReviewIndex.value + 2) % reviews.length;
    }, 5000); // 5 seconds display
});

onUnmounted(() => {
    if (reviewInterval) clearInterval(reviewInterval);
});

const goToDest = (name) => {
    router.push({ path: '/planner', query: { destination: name } });
};

</script>

<style scoped>
/* BACKGROUND COLOR HERE: */
.home-page-container {
    background: #f7f4f4; 
    /* Edit this line to change background color */
    background: linear-gradient(120deg, #d4ece8 0%, #11e6d4 100%);
    width: 100%;
    min-height: 100vh;
}
.home-page {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.hero-section { margin-bottom: 60px; }
.hero-title {
  font-size: 3.5rem;
  margin-bottom: 15px;
  /* Removed hover-float here */
  background: linear-gradient(135deg, #6c5ce7 0%, #00cec9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: default;
  display: inline-block;
  padding-bottom: 5px;
}
/* Ensure emoji is visible */
.emoji-icon {
    -webkit-text-fill-color: initial !important; 
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    display: inline-block;
    margin-right: 15px;
}
.hero-subtitle {
  font-size: 1.25rem;
  color: #636e72;
  margin-bottom: 50px;
  font-weight: 300;
}

/* Feature Cards */
.feature-cards { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; }
.card {
  background: white;
  padding: 30px;
  border-radius: 20px;
  width: 280px;
  /* Softer shadow */
  box-shadow: 0 10px 25px rgba(163, 177, 198, 0.15); 
  border: 1px solid rgba(255,255,255,0.6);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex; flex-direction: column; align-items: center;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 6px; background: #dfe6e9; }
.card:nth-child(1)::before { background: #6c5ce7; }
.card:nth-child(2)::before { background: #00cec9; }
.card:nth-child(3)::before { background: #fdcb6e; }
.icon { font-size: 3rem; margin-bottom: 20px; }
.card h3 { margin: 0 0 10px 0; color: #2d3436; font-size: 1.3rem; }
.card p { color: #888; font-size: 0.95rem; line-height: 1.6; margin-bottom: 25px; }
.link-text { margin-top: auto; font-weight: bold; color: #6c5ce7; transition: margin-left 0.2s; }
.card:hover .link-text { margin-left: 10px; }
.card:nth-child(2) .link-text { color: #00b894; }
.card:nth-child(3) .link-text { color: #e17055; }

/* Showcase Section */
.showcase-section {
    padding: 50px 40px;
    background: rgba(255, 255, 255, 0.7); /* translucent */
    border-radius: 24px;
    margin-bottom: 60px;
    /* Blend better */
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}
.section-title { font-size: 2.2rem; color: #2d3436; margin-bottom: 40px; /* Removed hover-float */ }
.benefits-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 30px; }
.benefit-item {
    text-align: left; padding: 25px;
    background: white; border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.02);
}
.badg { font-size: 2.5rem; display: block; margin-bottom: 15px; }
.benefit-item h4 { font-size: 1.2rem; margin: 0 0 10px 0; color: #2c3e50; }
.benefit-item p { color: #7f8c8d; line-height: 1.6; margin: 0; }

/* Animations */
.hover-float { transition: transform 0.3s, box-shadow 0.3s; }
.hover-float:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
.fade-in { animation: fadeIn 0.8s ease-out; }
.slide-up { animation: slideUp 0.8s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Carousel Styles - CSS Only Marquee */
.hot-section { margin-top: 60px; margin-bottom: 60px; overflow: hidden; position: relative; }
.carousel-container {
    width: 100%;
    overflow: hidden; 
    padding: 20px 0;
    /* Mask for fade out effect at edges */
    mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
    -webkit-mask-image: linear-gradient(to right, transparent, black 10%, black 90%, transparent);
}
.carousel-track {
    display: flex;
    gap: 20px;
    width: max-content; 
    padding: 0 20px;
    /* Translate half of the total width (since we duplicated) */
    animation: scroll 100s linear infinite; 
}
.carousel-track:hover {
    animation-play-state: paused;
}

/* 
   We have 20 items. Duplicated = 40.
   Width of one item + gap = 220 + 20 = 240px.
   Total width of original set = 20 * 240 = 4800px.
*/
@keyframes scroll {
    0% { transform: translateX(0); }
    100% { transform: translateX(-4800px); } /* Exact width of original 20 items */
}

.hot-card {
    width: 220px; flex-shrink: 0;
    background: white; border-radius: 16px; overflow: hidden;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06); cursor: pointer; text-align: left;
    border: 1px solid rgba(0,0,0,0.03);
}
.hot-img { height: 130px; display: flex; justify-content: center; align-items: center; font-size: 3.5rem; color: white; }
.hot-info { padding: 18px; }
.hot-info h4 { margin: 0 0 6px 0; color: #2d3436; font-size: 1.1rem; }
.hot-info p { margin: 0; color: #b2bec3; font-size: 0.85rem; }

/* Review Section - Pagination Style */
.review-section { margin-bottom: 60px; overflow: hidden; position: relative; }

.review-display {
    min-height: 250px; /* Reserve space to prevent layout shift */
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    width: 100%;
}

.reviews-row-active { 
    display: flex; 
    gap: 30px; 
    justify-content: center; 
    width: 100%;
    position: relative; /* Context for absolute leaving items */
}

.review-card {
    background: white; padding: 30px; border-radius: 18px;
    width: 350px; /* Slightly wider */
    box-shadow: 0 8px 25px rgba(0,0,0,0.05); text-align: left; position: relative;
    border: 1px solid rgba(0,0,0,0.02);
}
.review-card::before { content: '“'; position: absolute; top: 15px; left: 20px; font-size: 4rem; color: #f1f2f6; font-family: serif; z-index: 0; }
.review-text { font-style: italic; color: #555; position: relative; z-index: 1; margin-bottom: 20px; line-height: 1.6; font-size: 0.95rem; }
.review-user { font-weight: bold; color: #6c5ce7; text-align: right; font-size: 0.9rem; position: relative; z-index: 1; }

/* Transition Styles */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px); /* Slide in from bottom */
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px); /* Slide out to top */
}

.home-page-container {
    background: #fdfdfd; /* Fallback */
    /* Soft gradient background */
    background: linear-gradient(120deg, #fdfbfb 0%, #a8ecd6 100%);
    width: 100%;
    min-height: 100vh;
}
.home-page {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.hero-section { margin-bottom: 60px; }
.hero-title {
  font-size: 3.5rem;
  margin-bottom: 15px;
  /* Removed hover-float here */
  background: linear-gradient(135deg, #6c5ce7 0%, #00cec9 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: default;
  display: inline-block;
  padding-bottom: 5px;
}
/* Ensure emoji is visible */
.emoji-icon {
    -webkit-text-fill-color: initial !important; 
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    display: inline-block;
    margin-right: 15px;
}
.hero-subtitle {
  font-size: 1.25rem;
  color: #636e72;
  margin-bottom: 50px;
  font-weight: 300;
}

/* Feature Cards */
.feature-cards { display: flex; justify-content: center; gap: 30px; flex-wrap: wrap; }
.card {
  background: white;
  padding: 30px;
  border-radius: 20px;
  width: 280px;
  /* Softer shadow */
  box-shadow: 0 10px 25px rgba(163, 177, 198, 0.15); 
  border: 1px solid rgba(255,255,255,0.6);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  display: flex; flex-direction: column; align-items: center;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 6px; background: #dfe6e9; }
.card:nth-child(1)::before { background: #6c5ce7; }
.card:nth-child(2)::before { background: #00cec9; }
.card:nth-child(3)::before { background: #fdcb6e; }
.icon { font-size: 3rem; margin-bottom: 20px; }
.card h3 { margin: 0 0 10px 0; color: #2d3436; font-size: 1.3rem; }
.card p { color: #888; font-size: 0.95rem; line-height: 1.6; margin-bottom: 25px; }
.link-text { margin-top: auto; font-weight: bold; color: #6c5ce7; transition: margin-left 0.2s; }
.card:hover .link-text { margin-left: 10px; }
.card:nth-child(2) .link-text { color: #00b894; }
.card:nth-child(3) .link-text { color: #e17055; }

/* Showcase Section */
.showcase-section {
    padding: 50px 40px;
    background: rgba(255, 255, 255, 0.7); /* translucent */
    border-radius: 24px;
    margin-bottom: 60px;
    /* Blend better */
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}
.section-title { font-size: 2.2rem; color: #2d3436; margin-bottom: 40px; /* Removed hover-float */ }
.benefits-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 30px; }
.benefit-item {
    text-align: left; padding: 25px;
    background: white; border-radius: 16px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.02);
}
.badg { font-size: 2.5rem; display: block; margin-bottom: 15px; }
.benefit-item h4 { font-size: 1.2rem; margin: 0 0 10px 0; color: #2c3e50; }
.benefit-item p { color: #7f8c8d; line-height: 1.6; margin: 0; }

/* Animations */
.hover-float { transition: transform 0.3s, box-shadow 0.3s; }
.hover-float:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
.fade-in { animation: fadeIn 0.8s ease-out; }
.slide-up { animation: slideUp 0.8s ease-out; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Carousel Styles */
.hot-section { margin-top: 60px; margin-bottom: 60px; overflow: hidden; }
.carousel-container {
    width: 100%;
    overflow: hidden; /* Hide scrollbar */
    padding: 20px 0; /* Space for shadows */
}
.carousel-track {
    display: flex;
    gap: 20px;
    /* Width will be dynamic based on items */
    width: max-content; 
    padding: 0 20px;
}
.hot-card {
    width: 220px; flex-shrink: 0;
    background: white; border-radius: 16px; overflow: hidden;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06); cursor: pointer; text-align: left;
    border: 1px solid rgba(0,0,0,0.03);
}
.hot-img { height: 130px; display: flex; justify-content: center; align-items: center; font-size: 3.5rem; color: white; }
.hot-info { padding: 18px; }
.hot-info h4 { margin: 0 0 6px 0; color: #2d3436; font-size: 1.1rem; }
.hot-info p { margin: 0; color: #b2bec3; font-size: 0.85rem; }

/* Review Section */
.review-section { margin-bottom: 60px; overflow: hidden; }
.reviews-track { gap: 30px; }
.review-card {
    background: white; padding: 30px; border-radius: 18px;
    width: 300px; flex-shrink: 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.05); text-align: left; position: relative;
    border: 1px solid rgba(0,0,0,0.02);
}
.review-card::before { content: '“'; position: absolute; top: 15px; left: 20px; font-size: 4rem; color: #f1f2f6; font-family: serif; z-index: 0; }
.review-text { font-style: italic; color: #555; position: relative; z-index: 1; margin-bottom: 20px; line-height: 1.6; font-size: 0.95rem; }
.review-user { font-weight: bold; color: #6c5ce7; text-align: right; font-size: 0.9rem; position: relative; z-index: 1; }

</style>
