import { LogType, useLogStore } from '@/stores/logStore'


export namespace log {
    export function debug(...data: any[]): void {
        console.debug(...data)
        useLogStore().log_list.push({ type: LogType.debug, data: data, time: new Date() })
    }
    export function info(...data: any[]): void {
        console.info(...data)
        useLogStore().log_list.push({ type: LogType.info, data: data, time: new Date() })
    }
    export function warn(...data: any[]): void {
        console.warn(...data)
        useLogStore().log_list.push({ type: LogType.warn, data: data, time: new Date() })
    }
    export function error(...data: any[]): void {
        console.error(...data)
        useLogStore().log_list.push({ type: LogType.error, data: data, time: new Date() })
    }
}