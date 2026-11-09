<script setup lang="ts">
import { TextFontSize24Regular } from '@vicons/fluent'
import {
  NFlex,
  NIcon,
  NIconWrapper,
  NInputGroup,
  NInputGroupLabel,
  NInputNumber,
  NSlider,
  NSpace,
  NSwitch,
} from 'naive-ui'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'

import { useSettingStore } from '@/stores/settingStore'

const { is_debug, show_text_size, ignore_case } = storeToRefs(useSettingStore())

const { t } = useI18n({
  useScope: 'local',
  messages: {
    'zh-CN': {
      'Debug mode': 'Debug 模式',
      'Show text size': '展示文字大小',
      'Ignore Case': '字体管理',
    },
  },
})

const SHOW_TEXT_SIZE_RANGE = [0.1, 5]
</script>

<template>
  <n-space vertical style="gap: 1rem; padding: 1rem">
    <n-switch v-model:value="is_debug">
      <template #checked>{{ t('Debug mode') }}</template>
      <template #unchecked>{{ t('Debug mode') }}</template>
    </n-switch>

    <n-flex :wrap="false" :align="'center'">
      <n-input-group style="width: fit-content">
        <n-input-group-label>{{ t('Show text size') }}</n-input-group-label>
        <n-input-number v-model:value="show_text_size" :step="0.1" />
        <n-input-group-label>rem</n-input-group-label>
      </n-input-group>
      <n-slider
        v-model:value="show_text_size"
        :step="0.1"
        :tooltip="false"
        :min="SHOW_TEXT_SIZE_RANGE[0]"
        :max="SHOW_TEXT_SIZE_RANGE[1]"
      >
        <template #thumb>
          <n-icon-wrapper :size="24" :border-radius="12">
            <n-icon :size="18" :component="TextFontSize24Regular" />
          </n-icon-wrapper>
        </template>
      </n-slider>
    </n-flex>

    <n-switch v-model:value="ignore_case">
      <template #checked>{{ t('Ignore Case') }}</template>
      <template #unchecked>{{ t('Ignore Case') }}</template>
    </n-switch>
  </n-space>
</template>
