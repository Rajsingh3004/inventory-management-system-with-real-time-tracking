<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h2>Register</h2>
      <form @submit.prevent="handleRegister">
        <input v-model="user.name" type="text" placeholder="Full Name" required />
        <input v-model="user.email" type="email" placeholder="Email" required />
        <input v-model="user.password" type="password" placeholder="Password" required />
        <select v-model="user.role">
          <option value="user">User</option>
        </select>
        <button type="submit" class="btn-secondary">Register</button>
      </form>
      <p class="toggle-text">
        Already registered? <router-link to="/">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { useRouter } from 'vue-router';

const router = useRouter();
const user = ref({ name: '', email: '', password: '', role: 'user' });

const handleRegister = async () => {
  try {
    await api.post('/register', user.value);
    alert("Success! Please Login.");
    router.push('/');
  } catch (err) { alert("Fail: " + err.response.data.detail); }
};
</script>

<style scoped>
.auth-wrapper { display: flex; justify-content: center; align-items: center; height: 100vh; background: #1a1a2e; }
.auth-card { background: #16213e; padding: 40px; border-radius: 12px; width: 350px; text-align: center; color: white; }
input, select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 5px; border: none; background: #0f3460; color: white; }
.btn-secondary { width: 100%; padding: 12px; background: #e94560; border: none; cursor: pointer; color: white; font-weight: bold; }
.toggle-text { margin-top: 20px; color: #ccc; }
</style>