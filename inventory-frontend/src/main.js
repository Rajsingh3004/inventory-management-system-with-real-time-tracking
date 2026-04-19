
import { createApp } from 'vue'
import App from './App.vue'      // Check karein file ka 'A' capital hai ya nahi
import router from './router'    // src/router/index.js ko load karega
import './style.css'            // Default Vite styling (optional)

const app = createApp(App)

app.use(router)                  // Router ko activate kiya
app.mount('#app')                // index.html ki 'app' id se joda