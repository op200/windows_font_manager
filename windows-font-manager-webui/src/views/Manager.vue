<script setup lang="ts">
import { Delete24Regular } from '@vicons/fluent'
import {
  NButton,
  NDataTable,
  NDescriptions,
  NDescriptionsItem,
  NDrawer,
  NDrawerContent,
  NFlex,
  NIcon,
  NInput,
  NList,
  NListItem,
  NModal,
  NSpace,
  NSpin,
  NTabPane,
  NTabs,
  NTag,
  NText,
  NTooltip,
} from 'naive-ui'
import type { RowData } from 'naive-ui/es/data-table/src/interface'
import { storeToRefs } from 'pinia'
import { computed, h, onMounted, ref, watch } from 'vue'

import { useMainStore, type FontData } from '@/stores/mainStore'
import { useSettingStore } from '@/stores/settingStore'
import { log } from '@/utils/log'

const { ws, font_dict, font_dict_selected, search_text, show_text } = storeToRefs(useMainStore())
const { show_text_size } = storeToRefs(useSettingStore())

const show_text_replaced = computed(() => show_text.value.replace(/(?<!\\)\\n/g, '\n'))

const duplicate_family_same_path = computed<Set<string>>(() => {
  if (font_dict_selected.value === undefined || !(font_dict_selected.value in font_dict.value))
    return new Set()

  const all_family = font_dict.value[font_dict_selected.value]
    ?.map(data => data.familys.map(fam => `${fam}/${data.font_type}`))
    .flat()

  if (all_family === undefined) return new Set()

  return new Set(all_family.filter((x, i) => all_family.indexOf(x) !== i))
})
const duplicate_family = computed<Set<string>>(() => {
  const all_family = Object.values(font_dict.value)
    .flat()
    .map(data => data.familys.map(fam => `${fam}/${data.font_type}`))
    .flat()

  return new Set(all_family.filter((x, i) => all_family.indexOf(x) !== i))
})

const nvg = navigator
const wd = window
const global_ctrl_state = ref(false)
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Control') global_ctrl_state.value = true
}
const handleKeyUp = (e: KeyboardEvent) => {
  if (e.key === 'Control') global_ctrl_state.value = false
}
window.addEventListener('keydown', handleKeyDown)
window.addEventListener('keyup', handleKeyUp)
window.addEventListener('focus', () => {
  global_ctrl_state.value = false
})

const TAB_HEIGHT = 'calc(100vh - 4rem - 3px - 168px)'

const checked_row_keys_dict = ref<Record<string, number[]>>({})
const checked_row_data_dict = ref<Record<string, FontData[]>>({})

const show_tab_add_modal = ref(false)
const tab_add_modal_input = ref<string>()

const show_del_fonts_modal = ref(false)
const is_close_tab_before_del_fonts = ref(false)
const will_del_fonts = ref<string[]>([])

const filted_value = ref<FontData[] | undefined>(undefined)
async function refresh_search_text() {
  if (!(search_text && font_dict_selected.value)) {
    filted_value.value = undefined
    return
  }

  filted_value.value = font_dict.value[font_dict_selected.value]?.filter(v => {
    const regex = new RegExp(search_text.value)
    if (regex.test(v.filename)) return true
    for (const family of v.familys) if (regex.test(family)) return true
  })
}
async function refresh_url_fonts() {
  const resp = await fetch('/gv/WIN_FONT_PATHS')
  const WIN_FONT_PATHS = (await resp.json()) as string[]

  Object.entries(font_dict.value)
    .filter(([key]) => !WIN_FONT_PATHS.includes(key))
    .flatMap(([, fonts]) => fonts)
    .forEach(font_data => {
      const pathname = font_data.pathname.replaceAll('\\', '/')
      font_data.familys.forEach(fam => {
        document.fonts.add(new FontFace(fam, `url('/font/${pathname}')`))
      })
    })
}
watch(search_text, refresh_search_text)
watch(font_dict_selected, refresh_search_text)
watch(
  font_dict,
  () => {
    refresh_search_text()
    checked_row_keys_dict.value = {}
    checked_row_data_dict.value = {}
    refresh_url_fonts()
  },
  { deep: false },
)
onMounted(() => {
  refresh_search_text()
  refresh_url_fonts()
})

interface Font_info_res {
  pathname: string
  familys: string[]
  font_type: 'Regular' | 'Bold' | 'Italic' | 'Bold_Italic'
  created: number
  modified: number
  revision: number
  version?: string
  is_variable: boolean
  units_per_em: number
  glyph_count: number
  cmap_len: number
  copyright_notice?: string
  unique_id?: string
  full_name?: string
  PostScript_name?: string
  trademark?: string
  manufacturer?: string
  designer?: string
}

function rowProps(rowData: RowData, rowIndex: number) {
  return {
    style: 'cursor: pointer;',
    onClick: async () => {
      if (drawer_show.value === true) {
        log.warn('Can not open multiple drawers')
        return
      }
      drawer_data.value = undefined
      drawer_show.value = true
      const pathname = rowData.pathname as string
      const req = await fetch('/font_info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pathname: pathname }),
      })
      drawer_data.value = (await req.json()) as Font_info_res
    },
  }
}

const drawer_show = ref<boolean>(false)
const drawer_data = ref<Font_info_res | undefined>(undefined)
</script>

<template>
  <div class="one-height" style="padding: 1rem; height: calc(100% - 2rem)">
    <!-- add dirs -->
    <n-modal
      v-model:show="show_tab_add_modal"
      :mask-closable="false"
      preset="dialog"
      negative-text="Cancel"
      positive-text="OK"
      :show-icon="false"
      title="Add directories"
      @positive-click="
        () => {
          if (!tab_add_modal_input) return
          const paths = tab_add_modal_input?.split('\n').filter(v => v.length)
          ws.send(JSON.stringify({ add_dirs: paths }))
          log.debug('@add_dirs', tab_add_modal_input, paths)
          tab_add_modal_input = ''
        }
      "
      @negative-click="
        () => {
          tab_add_modal_input = ''
        }
      "
    >
      <n-space vertical>
        <n-input
          v-model:value="tab_add_modal_input"
          type="textarea"
          placeholder="One directory per line"
        />
      </n-space>
    </n-modal>

    <!-- del fonts -->
    <n-modal
      v-model:show="show_del_fonts_modal"
      :mask-closable="false"
      preset="dialog"
      negative-text="Cancel"
      positive-text="OK"
      :show-icon="false"
      :title="`Delete ${will_del_fonts.length} font${will_del_fonts.length ? 's' : ''}${is_close_tab_before_del_fonts ? ' after closing tab' : ''}`"
      @positive-click="
        () => {
          font_dict = {}
          ws.send(
            JSON.stringify({
              wait_ms: is_close_tab_before_del_fonts ? 5000 : 1000,
              del_fonts: will_del_fonts,
            }),
          )
          if (is_close_tab_before_del_fonts) wd.close()
          is_close_tab_before_del_fonts = false
        }
      "
      :on-after-leave="() => (global_ctrl_state = false)"
      style="width: 40vw"
    >
      <n-space vertical>
        <n-space>
          <n-button
            @click="
              () => {
                show_del_fonts_modal = false
                nvg.clipboard.writeText(will_del_fonts.map(v => `del \u0022${v}\u0022`).join('\n'))
              }
            "
          >
            Copy delete CMD
          </n-button>
        </n-space>
        <n-list bordered style="height: 24em; overflow-y: auto">
          <n-list-item v-for="(v, i) in will_del_fonts">
            <n-flex style="align-items: center">
              <n-tag
                size="small"
                :style="{
                  width: `${will_del_fonts.length.toString().length}em`,
                  justifyContent: 'center',
                }"
                >{{ i + 1 }}</n-tag
              >
              <span>{{ v }}</span>
            </n-flex>
          </n-list-item>
        </n-list>
      </n-space>
    </n-modal>

    <n-tabs
      v-model:value="font_dict_selected"
      type="card"
      tab-style="min-width: 80px;"
      class="one-height"
      closable
      @close="
        (name: string | number) => {
          ws.send(
            JSON.stringify({
              pop_dirs: [name],
            }),
          )
          log.debug('@close', name)
        }
      "
      addable
      @add="
        () => {
          show_tab_add_modal = true
        }
      "
    >
      <n-tab-pane
        v-for="(val, key) in font_dict"
        :key="key"
        :tab="key"
        :name="key"
        class="one-height"
        style="display: grid; padding-top: 0"
      >
        <n-flex justify="space-between" style="margin: 0.8rem 0; align-items: center">
          <n-flex style="align-items: center; gap: 1rem">
            <strong style="font-size: 1rem">{{ key }}</strong>
            <strong style="display: inline-flex; gap: 0.5ch">
              <span v-if="checked_row_keys_dict[key]?.length">{{
                `${checked_row_keys_dict[key].length} /`
              }}</span>
              <span>{{ (filted_value || val).length }}</span>
              <span v-if="val.length !== (filted_value || val).length">{{
                `/ ${val.length}`
              }}</span>
              <span>Font{{ (filted_value || val).length > 1 ? 's' : '' }}</span>
            </strong>
          </n-flex>
          <n-space>
            <n-button
              :tertiary="!global_ctrl_state"
              :secondary="global_ctrl_state"
              circle
              type="error"
              @click="
                () => {
                  will_del_fonts = checked_row_data_dict[key]?.map(v => v.pathname) || []
                  show_del_fonts_modal = true
                  is_close_tab_before_del_fonts = false
                }
              "
              @click.ctrl.exact="is_close_tab_before_del_fonts = true"
            >
              <template #icon>
                <n-icon>
                  <Delete24Regular />
                </n-icon>
              </template>
            </n-button>
            <n-input
              clearable
              v-model:value="search_text"
              type="text"
              placeholder="Search"
              style="font-family: serif; min-width: 25em"
            />
            <n-input
              clearable
              v-model:value="show_text"
              type="text"
              placeholder="Show"
              style="font-family: serif; min-width: 25em"
            />
          </n-space>
        </n-flex>
        <n-data-table
          :columns="[
            {
              type: 'selection',
            },
            {
              title: '#',
              key: '#',
              width: `calc(${(filted_value || val).length.toString().length} * var(--n-font-size) + var(--n-td-padding) * 2)`,
            },
            {
              title: 'Path',
              key: 'path',
              width: `max(10em, min(40em, calc(${Math.max(...(filted_value || val).map(font_data => font_data.filename.length))} * var(--n-font-size))))`,
              resizable: true,
              sorter: (row1: FontData, row2: FontData) =>
                row1.pathname.localeCompare(row2.pathname, 'zh-CN', {
                  sensitivity: 'base', // 中文按拼音排序
                }),
              render(rowData: FontData) {
                return h(
                  NTooltip,
                  { trigger: 'hover' },
                  {
                    default: () => rowData.pathname,
                    trigger: () =>
                      h(
                        NButton,
                        {
                          focusable: false,
                          style: {
                            'white-space': 'normal',
                            'min-height': 'var(--n-height)',
                            height: 'auto',
                            'max-height': 'fit-content',
                            'padding-top': '0.4em',
                            'padding-bottom': '0.4em',
                          },
                          onClick: (e: MouseEvent) => {
                            e.stopPropagation()
                            nvg.clipboard.writeText(rowData.pathname)
                          },
                        },
                        {
                          default: () => rowData.filename,
                        },
                      ),
                  },
                )
              },
            },
            {
              title: 'Familys',
              key: 'familys',
              resizable: true,
              sorter: (row1: FontData, row2: FontData) => {
                const a = row1.familys,
                  b = row2.familys

                // 先按数组长度排序
                if (a.length !== b.length) {
                  return a.length - b.length
                }

                // 长度相同，按第一个元素排序
                const aFirst = a[0] || ''
                const bFirst = b[0] || ''
                return aFirst.localeCompare(bFirst, 'zh-CN', {
                  sensitivity: 'base', // 中文按拼音排序
                })
              },
              render(rowData: FontData) {
                return h(
                  NFlex,
                  {
                    style: { gap: '0.2rem' },
                  },
                  {
                    default: () =>
                      rowData.familys.map(tagKey => {
                        return h(
                          NButton,
                          {
                            ghost: true,
                            type: duplicate_family_same_path.has(`${tagKey}/${rowData.font_type}`)
                              ? 'error'
                              : duplicate_family.has(`${tagKey}/${rowData.font_type}`)
                                ? 'warning'
                                : 'default',
                            size: 'tiny',
                            style: { 'white-space': 'normal' },
                            onClick: (e: MouseEvent) => {
                              e.stopPropagation()
                              nvg.clipboard.writeText(tagKey)
                            },
                          },
                          {
                            default: () => tagKey,
                          },
                        )
                      }),
                  },
                )
              },
            },
            {
              title: 'Font type',
              key: 'font_type',
              width: `calc(${'Font type'.length}em)`,
              resizable: false,
              sorter: (row1: FontData, row2: FontData) => {
                const a = row1.font_type_val,
                  b = row2.font_type_val
                const aNum = (a[0] ? 2 : 0) + (a[1] ? 1 : 0) // true,true=3; true,false=2; false,true=1; false,false=0
                const bNum = (b[0] ? 2 : 0) + (b[1] ? 1 : 0)
                return bNum - aNum // 降序排列（true多的在前）
              },
            },
            {
              title: 'Show',
              key: 'show',
              render(rowData: FontData) {
                return h(
                  'span',
                  {
                    style: {
                      'font-size': `${show_text_size}rem`,
                      'font-family': [...rowData.familys, 'BackFont'].reduce(
                        (pre, cur) => `${pre}, '${cur}'`,
                      ),
                      'font-weight': rowData.font_type_val[0] ? 'bold' : 'normal',
                      'font-style': rowData.font_type_val[1] ? 'italic' : 'normal',
                      'white-space': 'break-spaces',
                    },
                  },
                  show_text_replaced,
                )
              },
            },
          ]"
          :data="
            (filted_value || val).map((v, i) => {
              return { index: i, '#': i + 1, ...v }
            })
          "
          :row-key="rowData => rowData.index"
          :checked-row-keys="checked_row_keys_dict[key] || []"
          @update:checked-row-keys="
            (
              keys: Array<string | number>,
              rows: object[],
              meta: {
                row: object | undefined
                action: 'check' | 'uncheck' | 'checkAll' | 'uncheckAll'
              },
            ) => {
              checked_row_keys_dict[key] = keys as number[]
              checked_row_data_dict[key] = rows as FontData[]
              log.debug('@update:checked-row-keys', checked_row_keys_dict, checked_row_data_dict)
            }
          "
          :row-props="rowProps"
          :max-height="TAB_HEIGHT"
          :min-height="TAB_HEIGHT"
          :virtual-scroll="true"
          class="one-height"
        />
      </n-tab-pane>
    </n-tabs>
  </div>
  <n-drawer v-model:show="drawer_show" :width="'50%'">
    <n-drawer-content>
      <div
        v-if="drawer_data === undefined"
        style="
          display: flex;
          width: 100%;
          height: 100%;
          align-items: center;
          justify-content: center;
        "
      >
        <n-spin size="large" />
      </div>
      <n-descriptions
        v-else
        bordered
        :column="2"
        label-placement="left"
        :title="drawer_data.pathname"
        :label-style="{
          'white-space': 'nowrap',
        }"
      >
        <n-descriptions-item label="Created">{{
          new Intl.DateTimeFormat(undefined, {
            dateStyle: 'medium',
            timeStyle: 'medium',
          }).format(new Date((drawer_data.created - 2082844800) * 1000))
        }}</n-descriptions-item>
        <n-descriptions-item label="Modified">{{
          new Intl.DateTimeFormat(undefined, {
            dateStyle: 'medium',
            timeStyle: 'medium',
          }).format(new Date((drawer_data.modified - 2082844800) * 1000))
        }}</n-descriptions-item>
        <n-descriptions-item label="Revision">{{ drawer_data.revision }}</n-descriptions-item>
        <n-descriptions-item label="Version">{{ drawer_data.version }}</n-descriptions-item>
        <n-descriptions-item label="Variable"
          ><n-text :type="drawer_data.is_variable ? 'success' : 'error'">{{
            drawer_data.is_variable ? 'YES' : 'NO'
          }}</n-text></n-descriptions-item
        >
        <n-descriptions-item label="units/em">{{ drawer_data.units_per_em }}</n-descriptions-item>
        <n-descriptions-item label="Glyph">{{ drawer_data.glyph_count }}</n-descriptions-item>
        <n-descriptions-item label="CMap">{{ drawer_data.cmap_len }}</n-descriptions-item>
        <n-descriptions-item label="Copyright notice" :span="2">{{
          drawer_data.copyright_notice
        }}</n-descriptions-item>
        <n-descriptions-item label="Unique ID">{{ drawer_data.unique_id }}</n-descriptions-item>
        <n-descriptions-item label="Full name">{{ drawer_data.full_name }}</n-descriptions-item>
        <n-descriptions-item label="PostScript name">{{
          drawer_data.PostScript_name
        }}</n-descriptions-item>
        <n-descriptions-item label="Trademark">{{ drawer_data.trademark }}</n-descriptions-item>
        <n-descriptions-item label="Manufacturer">{{
          drawer_data.manufacturer
        }}</n-descriptions-item>
        <n-descriptions-item label="Designer">{{ drawer_data.designer }}</n-descriptions-item>
      </n-descriptions>
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.one-height {
  position: relative;
  height: 100%;
  overflow: hidden;
}
</style>
