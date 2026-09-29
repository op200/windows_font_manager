import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingStore = defineStore('setting', () => {
  const is_debug = ref(false)

  const show_text_size = ref(1.4)

  return { is_debug, show_text_size }
})
