<script setup lang="ts">
import { useSettingStore } from '@/stores/settingStore';
import { NSpace, NSwitch } from 'naive-ui';
import { storeToRefs } from 'pinia';

const { is_debug } = storeToRefs(useSettingStore())

</script>


<template>
    <div style="padding: 1rem;">
        <n-space vertical>

            <n-switch v-model:value="is_debug">
                <template #checked>
                    Debug mode
                </template>
                <template #unchecked>
                    Debug mode
                </template>
            </n-switch>

        </n-space>
    </div>
</template>