<template>
  <div class="auth-page">
    <div class="auth-card fade-in-up">
      <h2 class="auth-title">🔐 重置密码</h2>
      <form v-if="!submitted" @submit.prevent="handleReset">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="form.username" class="styled-input" required placeholder="您的用户名" />
        </div>
        <div class="form-group">
          <label>注册邮箱</label>
          <input type="email" v-model="form.email" class="styled-input" required placeholder="注册时使用的邮箱" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input type="password" v-model="form.new_password" class="styled-input" required placeholder="设置新密码" />
        </div>
        <button type="submit" class="action-btn" :disabled="loading">
          {{ loading ? '处理中...' : '重置密码' }}
        </button>
      </form>
      
      <div v-else class="success-message">
        <div class="check-icon">✅</div>
        <h3>重置成功!</h3>
        <p>您的密码已更新，请使用新密码登录。</p>
        <button @click="router.push('/login')" class="action-btn">去登录</button>
      </div>

      <div class="auth-footer" v-if="!submitted">
        <router-link to="/login">想起密码了? 去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const submitted = ref(false);
const form = reactive({ username: '', email: '', new_password: '' });

const handleReset = async () => {
    loading.value = true;
    try {
        const res = await fetch('/api/auth/reset-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(form)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || '重置失败，请检查用户名和邮箱是否匹配');
        
        submitted.value = true;
    } catch (e) {
        alert(e.message);
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
.auth-footer a { color: #6c5ce7; text-decoration: none; font-weight: 500; transition: color 0.2s; }
.auth-footer a:hover { color: #a29bfe; }
.success-message { text-align: center; padding: 20px 0; }
.check-icon { font-size: 3rem; margin-bottom: 10px; }
.success-message h3 { color: #2d3436; margin: 10px 0; }
.success-message p { color: #636e72; margin-bottom: 20px; }
.fade-in-up { animation: fadeInUp 0.5s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>