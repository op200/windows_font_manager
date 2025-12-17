import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingStore = defineStore('setting', () => {
    const is_debug = ref(false)

    return { is_debug }
})
