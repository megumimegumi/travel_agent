
<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const isPlanner = computed(() => route.path === '/planner');
const isHome = computed(() => route.path === '/');

const user = ref(null);

const checkUser = () => {
    const u = localStorage.getItem('user');
    if (u) {
        try {
            user.value = JSON.parse(u);
        } catch(e) { user.value = null; }
    } else {
        user.value = null;
    }
};

const logout = () => {
    localStorage.removeItem('user');
    user.value = null;
    router.push('/login');
};

onMounted(() => {
    checkUser();
    window.addEventListener('user-login', checkUser);
});
</script>

<template>
  <div class="app-container">
    <nav class="navbar">
      <div class="logo">🌍 Travel Agent</div>
      <div class="nav-links">
        <router-link to="/">首页</router-link>
        <router-link to="/planner">行程规划</router-link>
        <router-link to="/recommend">目的地推荐</router-link>
        <router-link to="/my-itineraries">我的行程</router-link>
        <router-link to="/favorites">我的收藏</router-link>
      </div>
      <div class="user-info" v-if="user">
        <div class="user-dropdown-container">
            <span class="user-welcome">👋 {{ user.username }}</span>
            <div class="dropdown-menu">
                <router-link to="/my-itineraries" class="dropdown-item">📂 我的行程</router-link>
                <router-link to="/favorites" class="dropdown-item">❤️ 我的收藏</router-link>
                <div class="divider-horizontal"></div>
                <div @click="logout" class="dropdown-item">🔄 切换用户</div>
                <div @click="logout" class="dropdown-item danger">🚪 退出登录</div>
            </div>
        </div>
      </div>
      <div class="user-info" v-else>
        <router-link to="/login" class="login-btn-nav">登录</router-link>
      </div>
    </nav>
    
    <div :class="['main-content', { 'full-width': isPlanner || isHome }]">
      <router-view></router-view>
    </div>
  </div>
</template>

<style>
.app-container {
  font-family: 'Noto Sans SC', sans-serif;
  min-height: 100vh;
  background: #fdfbfb;
  display: flex;
  flex-direction: column;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 60px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  flex-shrink: 0;
  z-index: 100;
  position: sticky;
  top: 0;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  background: linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: transform 0.3s ease;
  cursor: default;
}

.logo:hover {
  transform: translateY(-2px);
}

.user-dropdown-container {
    position: relative;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
}

.user-dropdown-container:hover {
    background-color: #e3f2fd; /* Light blue background */
    transform: translateY(-2px); /* Upward animation */
}

.dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    width: 160px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    opacity: 0;
    visibility: hidden;
    transform: translateY(10px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    padding: 8px 0;
    overflow: hidden;
    margin-top: 5px;
}

.user-dropdown-container:hover .dropdown-menu {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.dropdown-item {
    padding: 10px 16px;
    color: #2d3436;
    font-size: 0.95rem;
    cursor: pointer;
    display: block;
    text-decoration: none;
    transition: background-color 0.2s;
}

.dropdown-item:hover {
    background-color: #f5f6fa;
    color: #6c5ce7;
}

.dropdown-item.danger:hover {
    color: #d63031;
    background-color: #fff0f0;
}

.divider-horizontal {
    height: 1px;
    background-color: #eee;
    margin: 4px 0;
}

.nav-links a {
  margin: 0 15px;
  text-decoration: none;
  color: #2c3e50;
  font-weight: 500;
  padding: 5px 0;
  transition: all 0.3s ease;
}

.nav-links a:hover {
  transform: translateY(-3px);
  color: #74b9ff;
}

.nav-links a.router-link-active {
  color: #66a6ff;
  border-bottom: 2px solid #66a6ff;
}

.main-content {
  padding: 0;
  max-width: none;
  width: 100%;
  box-sizing: border-box;
  flex: 1;
}

.main-content.container-limit {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

/* User Info Styles */
.user-welcome { font-weight: 600; color: #2d3436; font-size: 0.95rem; }
.logout-btn { 
    margin-left: 10px; padding: 5px 15px; border: 1px solid #dfe6e9; background: white; 
    border-radius: 20px; color: #636e72; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;
}
.logout-btn:hover { border-color: #ff7675; color: #ff7675; }

.login-btn-nav {
    text-decoration: none; background: #6c5ce7; color: white !important; 
    padding: 8px 20px; border-radius: 20px; font-size: 0.9rem; font-weight: bold;
    box-shadow: 0 4px 10px rgba(108, 92, 231, 0.3); transition: all 0.2s;
}
.login-btn-nav:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(108, 92, 231, 0.4); }
</style>
