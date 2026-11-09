import { createPinia } from 'pinia'
import { createApp } from 'vue'

import '@/assets/fonts.css'

import App from './App.vue'
import { i18n } from './i18n.ts'
import router from './router'

createApp(App) //
  .use(i18n)
  .use(createPinia())
  .use(router)
  .mount('#app')
