<template>
  <div class="login-wrapper">
    <div v-if="showIntro" class="video-intro">
      <div class="intro-content">
        <h1 class="main-title">INVENTORY <br> MANAGEMENT <br> SYSTEM</h1>
        <div class="divider"></div>
        <p class="sub-title">WITH REAL-TIME TRACKING</p>
      </div>

      <video autoplay muted @ended="showIntro = false" class="intro-video">
        <source src="../assets/mixkit-animation-of-futuristic-devices-99786-full-hd.mp4" type="video/mp4">
      </video>
      
      <button class="skip-btn" @click="showIntro = false">Skip Intro</button>
    </div>

    <div v-else class="login-box animate-fade">
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

const showIntro = ref(true);
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
    localStorage.setItem('role', res.data.role);
    localStorage.setItem('name', res.data.name);
    router.push('/dashboard');
  } catch (err) {
    alert("Login Fail: " + (err.response?.data?.detail || "Error"));
  }
};
</script>

<style scoped>
.login-wrapper { 
  height: 100vh; 
  display: flex; 
  justify-content: center; 
  align-items: center; 
  /* --- Background Image Settings --- */
  background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
              url('C:\Users\meenu\OneDrive\Documents\projects\inventory management system project\inventory-frontend\src\automated-inventory-management-system-wallpaper_987764-40035.avif'); /* Apni image ka path yaha dalein */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  /* ---------------------------------- */
  overflow: hidden; 
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Login Box ko thoda aur sundar banane ke liye Glassmorphism effect */
.login-box {
  background: rgba(255, 255, 255, 0.1); /* Halka transparent white */
  backdrop-filter: blur(15px); /* Background dhundhla karne ke liye */
  padding: 40px;
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
  color: white;
  width: 100%;
  max-width: 400px;
}
/* Intro Video Styling */
.video-intro { 
  position: fixed; 
  top: 0; 
  left: 0; 
  width: 100%; 
  height: 100%; 
  z-index: 1000; 
  background: black; 
  display: flex;
  align-items: center; /* वर्टिकली सेंटर */
}

.intro-video { 
  position: absolute;
  top: 0;
  left: 0;
  width: 100%; 
  height: 100%; 
  object-fit: cover; 
  z-index: -1; /* वीडियो को पीछे भेज दिया */
}

/* Text on Left Side */
.intro-content {
  margin-left: 60px; /* लेफ्ट से गैप */
  z-index: 1001;
  color: white;
  max-width: 800px;
}

.main-title {
  font-size: 5rem; /* बहुत बड़ा टेक्स्ट */
  font-weight: 900;
  line-height: 0.9;
  margin: 0;
  letter-spacing: -2px;
  text-transform: uppercase;
  background: linear-gradient(to right, #fff, #888);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: slideIn 1s ease-out forwards;
  
}

.divider {
  width: 100px;
  height: 4px;
  background: #00d4ff; /* निऑन लाइन */
  margin: 20px 0;
  animation: grow 1.5s ease-out forwards;
}

.sub-title {
  font-size: 1.5rem;
  letter-spacing: 8px;
  font-weight: 300;
  color: #00d4ff;
  animation: fadeIn 2s ease-in forwards;
}

/* Animations */
@keyframes slideIn {
  from { opacity: 0; transform: translateX(-50px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes grow {
  from { width: 0; }
  to { width: 100px; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.skip-btn { 
  position: absolute; 
  bottom: 30px; 
  right: 30px; 
  padding: 10px 20px; 
  background: rgba(255,255,255,0.1); 
  color: white; 
  border: 1px solid rgba(255,255,255,0.3); 
  border-radius: 30px; 
  cursor: pointer; 
  backdrop-filter: blur(5px);
}

.skip-btn:hover {
  background: white;
  color: black;
}

/* Login Box Fade */
.animate-fade { animation: fadeIn 1s ease-in; }
.intro-content {
  margin-left: auto;
  margin-right: 100px;
  z-index: 1001;
  color: white;
  max-width: 800px;
  text-align: right; 
}

.divider {
  width: 100px;
  height: 4px;
  background: #00d4ff;
  margin: 20px 0 20px auto; 
  animation: grow 1.5s ease-out forwards;
}
</style>