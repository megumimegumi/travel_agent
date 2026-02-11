<template>
  <div class="auth-page">
    <div class="auth-card fade-in-up">
      <h2 class="auth-title">👋 欢迎回来</h2>
      <form @submit.prevent="handleLogin" novalidate>
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="form.username" 
            class="styled-input" 
            :class="{ 'input-error': errors.username }" 
            required 
            placeholder="请输入用户名" 
            @input="errors.username = ''"
          />
          <span class="field-error" v-if="errors.username">{{ errors.username }}</span>
        </div>
        <div class="form-group">
          <label>密码</label>
          <input 
            type="password" 
            v-model="form.password" 
            class="styled-input" 
            :class="{ 'input-error': errors.password }" 
            required 
            placeholder="请输入密码" 
            @input="errors.password = ''"
          />
          <span class="field-error" v-if="errors.password">{{ errors.password }}</span>
        </div>
        <div v-if="globalError" class="error-text">
            {{ globalError }}
        </div>
        <button type="submit" class="action-btn" :disabled="loading">
          {{ loading ? '登录中...' : '立即登录' }}
        </button>
      </form>
      <div class="auth-footer">
        <router-link to="/register">注册账号</router-link>
        <span class="divider">|</span>
        <router-link to="/forgot-password">忘记密码?</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const form = reactive({ username: '', password: '' });
const errors = reactive({ username: '', password: '' });
const globalError = ref('');

const handleLogin = async () => {
    // Basic validation
    let hasError = false;
    errors.username = '';
    errors.password = '';
    globalError.value = '';

    if (!form.username) {
        errors.username = '请输入用户名';
        hasError = true;
    }
    if (!form.password) {
        errors.password = '请输入密码';
        hasError = true;
    }

    if (hasError) return;

    loading.value = true;
    try {
        const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(form)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || '登录失败');
        
        // Save user info
        localStorage.setItem('user', JSON.stringify(data));
        
        // Notify app
        window.dispatchEvent(new Event('user-login'));
        
        router.push('/');
    } catch (e) {
        if (e.message === 'Incorrect password') {
            errors.password = '密码错误';
        } else if (e.message === 'User not found') {
             errors.username = '没有该用户';
        } else {
            globalError.value = e.message;
        }
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: 80vh; }
.auth-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); width: 100%; max-width: 380px; border: 1px solid rgba(255,255,255,0.8); }
.auth-title { text-align: center; margin-bottom: 30px; font-size: 1.8rem; color: #2d3436; font-weight: 700; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; color: #636e72; font-weight: 600; font-size: 0.95rem; }
.styled-input { width: 100%; padding: 12px; border: 2px solid #dfe6e9; border-radius: 10px; font-size: 1rem; transition: all 0.3s; box-sizing: border-box; background: #fdfdfd; }
.styled-input:focus { border-color: #6c5ce7; outline: none; background: white; box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1); }
.action-btn { width: 100%; padding: 14px; background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); color: white; border: none; border-radius: 12px; font-size: 1.1rem; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; font-weight: bold; margin-top: 10px; }
.action-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3); }
.action-btn:disabled { opacity: 0.7; cursor: wait; transform: none; box-shadow: none; }
.auth-footer { margin-top: 25px; text-align: center; color: #b2bec3; font-size: 0.9em; }
.auth-footer a { color: #636e72; text-decoration: none; font-weight: 500; margin: 0 8px; transition: color 0.2s; }
.auth-footer a:hover { color: #6c5ce7; }
.divider { color: #dfe6e9; }
.fade-in-up { animation: fadeInUp 0.5s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

/* Error styles */
.input-error { border-color: #ff7675 !important; background: #fff0f0; }
.field-error { color: #d63031; font-size: 0.85rem; margin-top: 5px; display: block; text-align: left; }
.error-text { color: #d63031; font-size: 0.9em; margin-bottom: 20px; text-align: center; font-weight: 500; animation: shake 0.4s ease-in-out; }
@keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-5px); } 75% { transform: translateX(5px); } }
</style>