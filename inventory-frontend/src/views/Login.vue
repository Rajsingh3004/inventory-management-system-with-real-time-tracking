<template>
  <div class="login">
    <div class="login-box">
      <h2>Inventory Login</h2>
      <form @submit.prevent="handleLogin">
        <input v-model="email" type="email" placeholder="Email" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit" class="btn-primary">Login</button>
      </form>
      
      <p class="toggle-text">
        New here? <router-link to="/register">Create an account</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const router = useRouter();

const handleLogin = async () => {
  try {
    const formData = new URLSearchParams();
    formData.append('username', email.value);
    formData.append('password', password.value);

    const res = await api.post('/login', formData);
    
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('role', res.data.role); // Backend case check karein (role or Role)
    localStorage.setItem('name', res.data.name);

    router.push('/dashboard');
  } catch (err) {
    alert("Login Fail: " + (err.response?.data?.detail || "Error"));
  }
};
</script>
