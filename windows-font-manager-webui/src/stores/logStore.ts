import { defineStore } from 'pinia'
import { ref } from 'vue'

export enum LogType {
    debug = "DEBUG",
    info = "INFO",
    warn = "WARN",
    error = "ERROR",
}
export interface LogRecord {
    type: LogType
    data: any[]
    time: Date
}

export const useLogStore = defineStore('log', () => {
    const log_list = ref<LogRecord[]>([])

    return { log_list }
})
