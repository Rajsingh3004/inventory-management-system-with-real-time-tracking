import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue';
import Dashboard from '../views/Dashboard.vue';

const routes = [
  { path: '/', component: Login },
  { path: '/register', component: Register },
  { path: '/dashboard',component: Dashboard,
    beforeEnter: (to, from, next) => {
      localStorage.getItem('token') ? next() : next('/');
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;