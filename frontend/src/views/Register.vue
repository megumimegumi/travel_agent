<template>
  <div class="auth-page">
    <div class="auth-card fade-in-up">
      <h2 class="auth-title">✨ 创建新账号</h2>
      <form @submit.prevent="handleRegister" novalidate>
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="form.username" 
            class="styled-input" 
            :class="{ 'input-error': errors.username }"
            placeholder="设置用户名" 
            @input="errors.username = ''"
          />
          <span class="field-error" v-if="errors.username">{{ errors.username }}</span>
        </div>
        
        <div class="form-group">
          <label>电子邮箱</label>
          <input 
            type="email" 
            v-model="form.email" 
            class="styled-input" 
            :class="{ 'input-error': errors.email }"
            placeholder="用于找回密码" 
            @input="errors.email = ''"
          />
          <span class="field-error" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <div class="form-group relative">
          <label>密码</label>
          <input 
            type="password" 
            v-model="form.password" 
            class="styled-input" 
            :class="{ 'input-error': errors.password }"
            placeholder="设置安全密码" 
            @focus="showPasswordTooltip = true"
            @blur="showPasswordTooltip = false"
            @input="errors.password = ''"
          />
          <div class="tooltip" v-if="showPasswordTooltip">
             8-16位字符，包含字母和数字
          </div>
          <span class="field-error" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label>确认密码</label>
          <input 
            type="password" 
            v-model="form.confirmPassword" 
            class="styled-input" 
            :class="{ 'input-error': errors.confirmPassword }"
            placeholder="再次输入密码" 
            @input="errors.confirmPassword = ''"
          />
          <span class="field-error" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</span>
        </div>

        <div v-if="globalError" class="global-error">{{ globalError }}</div>

        <button type="submit" class="action-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册并登录' }}
        </button>
      </form>
      <div class="auth-footer">
        <span>已有账号?</span>
        <router-link to="/login">直接登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' });
const errors = reactive({ username: '', email: '', password: '', confirmPassword: '' });
const globalError = ref('');
const showPasswordTooltip = ref(false);

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\W_]{8,16}$/;

const validate = () => {
    let isValid = true;
    errors.username = '';
    errors.email = '';
    errors.password = '';
    errors.confirmPassword = '';
    globalError.value = '';

    if (!form.username) {
        errors.username = '请输入用户名';
        isValid = false;
    }

    if (!form.email) {
        errors.email = '请输入电子邮箱';
        isValid = false;
    } else if (!emailRegex.test(form.email)) {
        errors.email = '邮箱格式不正确';
        isValid = false;
    }

    if (!form.password) {
        errors.password = '请输入密码';
        isValid = false;
    } else if (!passwordRegex.test(form.password)) {
        errors.password = '密码格式不符合要求';
        isValid = false;
    }

    if (form.password !== form.confirmPassword) {
        errors.confirmPassword = '两次输入的密码不一致';
        isValid = false;
    }

    return isValid;
};

const handleRegister = async () => {
    if (!validate()) return;

    loading.value = true;
    try {
        const { confirmPassword, ...registerData } = form; // Exclude confirmPassword
        
        // Register
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(registerData)
        });

        let data;
        const contentType = res.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            data = await res.json();
        } else {
            const text = await res.text();
            throw new Error(text.includes('Internal Server Error') ? '服务器内部错误，请稍后重试' : text);
        }

        if (!res.ok) throw new Error(data.detail || '注册失败');
        
        // Auto Login
        const loginRes = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username: form.username, password: form.password })
        });
        const loginData = await loginRes.json();
        if (!loginRes.ok) throw new Error('注册成功但自动登录失败，请手动登录');

        localStorage.setItem('user', JSON.stringify(loginData));
        window.dispatchEvent(new Event('user-login'));
        router.push('/');
        
    } catch (e) {
        globalError.value = e.message;
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.auth-page { display: flex; align-items: center; justify-content: center; min-height: 80vh; }
.auth-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); width: 100%; max-width: 380px; border: 1px solid rgba(255,255,255,0.8); position: relative; }
.auth-title { text-align: center; margin-bottom: 30px; font-size: 1.8rem; color: #2d3436; font-weight: 700; }
.form-group { margin-bottom: 20px; position: relative; }
.form-group label { display: block; margin-bottom: 8px; color: #636e72; font-weight: 600; font-size: 0.95rem; }
.styled-input { width: 100%; padding: 12px; border: 2px solid #dfe6e9; border-radius: 10px; font-size: 1rem; transition: all 0.3s; box-sizing: border-box; background: #fdfdfd; }
.styled-input:focus { border-color: #6c5ce7; outline: none; background: white; box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1); }
.input-error { border-color: #ff7675 !important; background: #fff0f0; }
.field-error { color: #d63031; font-size: 0.8rem; margin-top: 5px; display: block; }
.global-error { color: #d63031; font-size: 0.9em; margin-bottom: 15px; text-align: center; font-weight: 500; }
.action-btn { width: 100%; padding: 14px; background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%); color: white; border: none; border-radius: 12px; font-size: 1.1rem; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; font-weight: bold; margin-top: 10px; }
.action-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3); }
.action-btn:disabled { opacity: 0.7; cursor: wait; transform: none; box-shadow: none; }
.auth-footer { margin-top: 25px; text-align: center; color: #b2bec3; font-size: 0.9em; }
.auth-footer a { color: #6c5ce7; text-decoration: none; font-weight: 500; margin: 0 5px; transition: color 0.2s; }
.auth-footer a:hover { color: #a29bfe; }
.tooltip { 
    position: absolute; 
    background: rgba(45, 52, 54, 0.95); 
    color: white; 
    padding: 10px 14px; 
    border-radius: 8px; 
    font-size: 0.85rem; 
    top: 105%; 
    left: 0; 
    z-index: 10; 
    width: 100%; 
    box-sizing: border-box; 
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.1);
    animation: fadeInTooltip 0.2s ease-out;
    text-align: left;
    line-height: 1.4;
}
.tooltip::after { 
    content: ''; 
    position: absolute; 
    bottom: 100%; 
    left: 20px; 
    border-width: 6px; 
    border-style: solid; 
    border-color: transparent transparent rgba(45, 52, 54, 0.95) transparent; 
}
@keyframes fadeInTooltip { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
.fade-in-up { animation: fadeInUp 0.5s ease-out; }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>