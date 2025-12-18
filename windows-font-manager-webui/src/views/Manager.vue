<script setup lang="ts">
import { useMainStore, type FontData } from '@/stores/mainStore'
import { log } from '@/utils/log'
import { Delete24Regular } from '@vicons/fluent'
import { NButton, NDataTable, NFlex, NIcon, NInput, NList, NListItem, NModal, NSpace, NTabPane, NTabs, NTag, NTooltip } from 'naive-ui'
import { storeToRefs } from 'pinia'
import { h, ref, watch } from 'vue'

const { ws, font_dict, font_dict_selected, show_text } = storeToRefs(useMainStore())

const nvg = navigator

const TAB_HEIGHT = "calc(100vh - 4rem - 3px - 168px)"

const checked_row_keys_dict = ref<Record<string, number[]>>({})
const checked_row_data_dict = ref<Record<string, FontData[]>>({})

const show_tab_add_modal = ref(false)
const tab_add_modal_input = ref<string>()

const show_del_fonts_modal = ref(false)
const will_del_fonts = ref<string[]>([])

const search_text = ref<string>("")
const filted_value = ref<FontData[] | undefined>(undefined)
async function refresh_search_text() {
    if (!(search_text && font_dict_selected.value)) {
        filted_value.value = undefined
        return
    }

    filted_value.value = font_dict.value[font_dict_selected.value]?.filter(v => {
        const regex = new RegExp(search_text.value)
        if (regex.test(v.filename))
            return true
        for (const family of v.familys)
            if (regex.test(family))
                return true
    })
}
watch(search_text, refresh_search_text)
watch(font_dict_selected, refresh_search_text)
watch(font_dict, () => {
    refresh_search_text()
    checked_row_keys_dict.value = {}
    checked_row_data_dict.value = {}
}, { deep: false })

</script>


<template>
    <div class="one-height" style="padding: 1rem;height: calc(100% - 2rem);">
        <!-- add dirs -->
        <n-modal v-model:show="show_tab_add_modal" :mask-closable="false" preset="dialog" negative-text="Cancel"
            positive-text="OK" :show-icon="false" title="Add directories" @positive-click="() => {
                if (!tab_add_modal_input) return;
                const paths = tab_add_modal_input?.split('\n').filter(v => v.length)
                ws.send(JSON.stringify({ 'add_dirs': paths }))
                log.debug('@add_dirs', tab_add_modal_input, paths)
                tab_add_modal_input = ''
            }" @negative-click="() => {
                tab_add_modal_input = ''
            }">
            <n-space vertical>
                <n-input v-model:value="tab_add_modal_input" type="textarea" placeholder="One directory per line" />
            </n-space>
        </n-modal>

        <!-- del fonts -->
        <n-modal v-model:show="show_del_fonts_modal" :mask-closable="false" preset="dialog" negative-text="Cancel"
            positive-text="OK" :show-icon="false"
            :title="`Delete ${will_del_fonts.length} font${will_del_fonts.length ? 's' : ''}`" @positive-click="() => {
                font_dict = {}
                ws.send(JSON.stringify({ del_fonts: will_del_fonts }))
            }">
            <n-list bordered style="height: 24em;overflow-y: auto;">
                <n-list-item v-for="(v, i) in will_del_fonts">
                    <n-flex style="align-items: center;">
                        <n-tag size="small"
                            :style="{ width: `${will_del_fonts.length.toString().length}em`, justifyContent: 'center' }">{{
                                i + 1
                            }}</n-tag>
                        <span>{{ v }}</span>
                    </n-flex>
                </n-list-item>
            </n-list>
        </n-modal>

        <n-tabs v-model:value="font_dict_selected" type="card" tab-style="min-width: 80px;" class="one-height" closable
            @close="(name: string | number) => {
                ws.send(JSON.stringify({
                    'pop_dirs': [name]
                }))
                log.debug('@close', name)
            }" addable @add="() => {
                show_tab_add_modal = true
            }">
            <n-tab-pane v-for="val, key in font_dict" :key="key" :tab="key" :name="key" class="one-height"
                style="display: grid;padding-top: 0;">
                <n-flex justify="space-between" style="margin: 0.8rem 0;align-items: center;">
                    <n-flex style="align-items: center;gap: 1rem;">
                        <strong style="font-size: 1rem;">{{ key }}</strong>
                        <strong style="display: inline-flex;gap: 0.5ch;">
                            <span v-if="checked_row_keys_dict[key]?.length">{{
                                `${checked_row_keys_dict[key].length} /` }}</span>
                            <span>{{
                                (filted_value || val).length }}</span>
                            <span v-if="val.length !== (filted_value || val).length">{{
                                `/ ${val.length}` }}</span>
                            <span>Font{{ (filted_value || val).length > 1 ? 's' : '' }}</span>
                        </strong>
                    </n-flex>
                    <n-space>
                        <n-button tertiary circle type="error" @click="() => {
                            will_del_fonts = checked_row_data_dict[key]?.map(v => v.pathname) || []
                            show_del_fonts_modal = true
                        }">
                            <template #icon>
                                <n-icon>
                                    <Delete24Regular />
                                </n-icon>
                            </template>
                        </n-button>
                        <n-input clearable v-model:value="search_text" type="text" placeholder="Search" />
                        <n-input clearable v-model:value="show_text" type="text" placeholder="Show" />
                    </n-space>
                </n-flex>
                <n-data-table :columns="[
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
                        width: `min(40em, calc(${Math.max(...(filted_value || val).map(font_data => font_data.filename.length))} * var(--n-font-size)))`,
                        resizable: true,
                        sorter: (row1: FontData, row2: FontData) =>
                            row1.pathname.localeCompare(row2.pathname, 'zh-CN', {
                                sensitivity: 'base'  // 中文按拼音排序
                            }),
                        render(rowData: FontData) {
                            return h(
                                NTooltip,
                                { trigger: 'hover' },
                                {
                                    default: () => rowData.pathname,
                                    trigger: () => h(
                                        NButton,
                                        {
                                            focusable: false,
                                            style: {
                                                'white-space': 'normal',
                                                'min-height': 'var(--n-height)',
                                                'height': 'auto',
                                                'max-height': 'fit-content',
                                                'padding-top': '0.4em',
                                                'padding-bottom': '0.4em',
                                            },
                                            onClick: () => {
                                                nvg.clipboard.writeText(rowData.pathname)
                                            },
                                        },
                                        {
                                            default: () => rowData.filename
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
                            const a = row1.familys, b = row2.familys

                            // 先按数组长度排序
                            if (a.length !== b.length) {
                                return a.length - b.length;
                            }

                            // 长度相同，按第一个元素排序
                            const aFirst = a[0] || '';
                            const bFirst = b[0] || '';
                            return aFirst.localeCompare(bFirst, 'zh-CN', {
                                sensitivity: 'base'  // 中文按拼音排序
                            })
                        },
                        render(rowData: FontData) {
                            return h(
                                NFlex,
                                {
                                    style: { gap: '0.2rem' },
                                },
                                {
                                    default: () => rowData.familys.map(tagKey => {
                                        return h(
                                            NButton,
                                            {
                                                size: 'tiny',
                                                style: { 'white-space': 'normal' },
                                                onClick: () => {
                                                    nvg.clipboard.writeText(tagKey)
                                                },
                                            },
                                            {
                                                default: () => tagKey
                                            },
                                        )
                                    })
                                },
                            )
                        }
                    },
                    {
                        title: 'Font type',
                        key: 'font_type',
                        width: `calc(${'Font type'.length}em)`,
                        resizable: false,
                        sorter: (row1: FontData, row2: FontData) => {
                            const a = row1.font_type_val, b = row2.font_type_val
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
                                        'font-size': '1.4rem',
                                        'font-family': rowData.familys,
                                        'font-weight': rowData.font_type_val[0] ? 'bold' : 'normal',
                                        'font-style': rowData.font_type_val[1] ? 'italic' : 'normal',
                                    }
                                },
                                show_text,
                            )
                        }
                    },
                ]" :data="(filted_value || val).map((v, i) => { return { 'index': i, '#': i + 1, ...v } })"
                    :row-key="rowData => rowData.index" :checked-row-keys="checked_row_keys_dict[key] || []"
                    @update:checked-row-keys="(
                        keys: Array<string | number>,
                        rows: object[],
                        meta: { row: object | undefined, action: 'check' | 'uncheck' | 'checkAll' | 'uncheckAll' }
                    ) => {
                        checked_row_keys_dict[key] = keys as number[]
                        checked_row_data_dict[key] = rows as FontData[]
                        log.debug(
                            '@update:checked-row-keys',
                            checked_row_keys_dict,
                            checked_row_data_dict,
                        )
                    }" :max-height="TAB_HEIGHT" :min-height="TAB_HEIGHT" :virtual-scroll="true" class="one-height" />
            </n-tab-pane>
        </n-tabs>

    </div>
</template>

<style scoped>
.one-height {
    position: relative;
    height: 100%;
    overflow: hidden;
}
</style>