import { createApp } from 'vue'
import App from './App.vue'      
import router from './router'    
// Check if style.css exists, if not, comment this line
import './style.css'            

const app = createApp(App)

app.use(router)                  
app.mount('#app')