<script setup lang="ts">
import { NCard } from 'naive-ui'
import { useMainStore } from '@/stores/mainStore'
import { storeToRefs } from 'pinia'

const { back_info } = storeToRefs(useMainStore())

const home_url = "https://github.com/op200/windows_font_manager"
</script>


<template>
    <div style="display: grid;gap: 1rem;padding: 1rem;position: relative;overflow-x: hidden;">

        <n-card title="Windows Font Manager">
            <template #header-extra>
                <a :href=home_url>{{ home_url }}</a>
            </template>
            <div>
                <span v-if="back_info">v{{ back_info.version }}</span>
            </div>
        </n-card>

    </div>
</template>