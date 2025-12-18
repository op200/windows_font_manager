import { log } from '@/utils/log'
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const ws_url = '/ws'

export interface BackInfo {
  version: string
  latest_release_ver: string
}
export interface FontData {
  pathname: string
  filename: string
  familys: string[]
  font_type: 'Regular' | 'Bold' | 'Italic' | 'Bold_Italic'
  font_type_val: [boolean, boolean]
}

export const useMainStore = defineStore('main', () => {
  const is_connect = ref(true)

  const ws = ref(new WebSocket(ws_url))
  function reconnect_ws(is_first: boolean) {
    if (!is_first)
      log.info("reconnect ws")

    ws.value = new WebSocket(ws_url)

    ws.value.onerror = (event: Event) => {
      log.error("@ws:error", event)
    }
    ws.value.onopen = (event: Event) => {
      log.debug("@ws:open", event)
      is_connect.value = true

      ws.value.send(JSON.stringify({
        'get_fonts': '',
      }))
    }
    ws.value.onclose = (event: CloseEvent) => {
      log.debug("@ws:close", event)
      is_connect.value = false
      reconnect_ws(false)
    }
    ws.value.onmessage = (event: MessageEvent) => {
      const data = event.data as string
      const data_json = JSON.parse(data)
      log.debug("@ws:msg", event, data_json, data.length)
      if ('fonts' in data_json && data_json.fonts !== null)
        font_dict.value = data_json.fonts || {}
      if ('info' in data_json)
        back_info.value = data_json.info
    }
  }
  reconnect_ws(true)

  const back_info = ref<BackInfo>()
  const font_dict = ref<Record<string, FontData[]>>({})

  const font_dict_selected = ref<string | undefined>()
  watch(font_dict, () => {
    if (font_dict_selected.value === undefined || !(font_dict_selected.value in font_dict.value)) {
      font_dict_selected.value = Object.keys(font_dict.value)[0]
    }
  })

  const show_text = ref('中文。0.123abDE,ff')

  return { ws, is_connect, back_info, font_dict, font_dict_selected, show_text }
})
