<script setup lang="ts">
import { useLogStore, type LogRecord, LogType } from '@/stores/logStore'
import { storeToRefs } from 'pinia'
import { NList, NListItem, NTag, NButton, NAvatar } from 'naive-ui'

const { log_list } = storeToRefs(useLogStore())

const log_type__ntag_type = new Map<LogType, "success" | "info" | "warning" | "error">([
    [LogType.debug, 'success'],
    [LogType.info, 'info'],
    [LogType.warn, 'warning'],
    [LogType.error, 'error'],
])

const log_type_str_set = new Set(['string', 'number'] as const)

</script>

<template>
    <div style="position: relative;overflow-y: auto;padding: 1rem;height: calc(100% - 2rem);width: calc(100% - 2rem);">
        <n-list>
            <n-list-item v-for="(log, i) in [...log_list].reverse()">
                <div class="log-list-item">
                    <n-avatar round size="small">{{ log_list.length - i }}</n-avatar>
                    <n-tag :type="log_type__ntag_type.get(log.type) || 'default'"
                        style="width: 5em;display: flex;justify-content: center;">{{ log.type }}</n-tag>
                    <span>{{log.data.reduce(
                        (acc, curr) =>
                            acc + ' ' + (log_type_str_set.has(typeof curr as any) ? curr : `[${typeof curr}]`),
                        '')
                    }}</span>
                </div>
            </n-list-item>
        </n-list>
    </div>
</template>

<style scoped>
.log-list-item {
    display: flex;
    gap: 1rem;
    padding: 0 1rem;
}
</style>