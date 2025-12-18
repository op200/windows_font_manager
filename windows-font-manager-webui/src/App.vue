<script setup lang="ts">
import { useMainStore } from '@/stores/mainStore';
import { AppGeneric20Regular, ArrowSync24Filled, CellularData124Filled, CellularOff24Filled, DarkTheme24Filled, Info24Regular, LocalLanguage24Filled, Settings24Regular, TextBulletListSquare20Regular } from '@vicons/fluent';
import { NButton, NConfigProvider, NFlex, NIcon, NLayout, NLayoutSider, NMenu, darkTheme, dateEnUS, dateZhCN, enUS, lightTheme, zhCN, type MenuOption } from 'naive-ui';
import type { Key } from 'naive-ui/es/cascader/src/interface';
import { storeToRefs } from 'pinia';
import { h, onBeforeMount, ref, watch } from 'vue';
import { RouterLink, RouterView, useRoute } from 'vue-router';
import { log } from './utils/log';
import { compare_version, open_page } from './utils/utils';

const route = useRoute()

const { ws, is_connect, back_info } = storeToRefs(useMainStore())

const currentTheme = ref()
const css_data_theme = ref<string>()
const currentLang = ref({ 'lang': zhCN, 'dateLang': dateZhCN })

watch(currentTheme, newVal => {
    log.info(currentTheme.value.name)
    css_data_theme.value = currentTheme.value.name
})

onBeforeMount(() => {
    currentTheme.value = window.matchMedia('(prefers-color-scheme: dark)').matches ? darkTheme : lightTheme;
    window.matchMedia('(prefers-color-scheme: dark)')
        .addEventListener('change', () =>
            currentTheme.value = window.matchMedia('(prefers-color-scheme: dark)').matches ? darkTheme : lightTheme); // 监听系统主题
});

const menuOptions: MenuOption[] = [
    {
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'manager',
                    }
                },
                { default: () => 'Manager' }
            ),
        key: 'manager',
        icon: () => h(AppGeneric20Regular),
    },
    {
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'setting',
                    }
                },
                { default: () => 'Setting' }
            ),
        key: 'setting',
        icon: () => h(Settings24Regular)
    },
    {
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'log',
                    }
                },
                { default: () => 'Log' }
            ),
        key: 'log',
        icon: () => h(TextBulletListSquare20Regular)
    },
    {
        label: () =>
            h(
                RouterLink,
                {
                    to: {
                        name: 'about',
                    }
                },
                { default: () => 'About' }
            ),
        key: 'about',
        icon: () => h(Info24Regular)
    },
];

const route_name = ref(route.name)
// 根据当前路由设置高亮
watch(() => route.name, newRouteName => route_name.value = newRouteName);

const collapseMenu = ref(true);


</script>

<template>
    <n-config-provider :theme="currentTheme" :data-theme="css_data_theme" :locale="currentLang.lang"
        :date-locale="currentLang.dateLang">
        <n-flex id="outermost" vertical style="gap:0;">

            <!-- 顶部按钮栏 -->
            <n-flex id="topButtonBarFlex" justify="end">

                <n-button dashed type="primary"
                    @click="open_page('https://github.com/op200/windows_font_manager/releases')"
                    v-if="back_info && compare_version(back_info.latest_release_ver, back_info.version) > 0">
                    New version v{{ back_info.latest_release_ver }}
                </n-button>

                <n-button strong tertiary circle tag="div" :type="is_connect ? 'default' : 'warning'"
                    style="cursor: inherit;background-color: transparent;">
                    <n-icon size="28" v-show="is_connect">
                        <CellularData124Filled />
                    </n-icon>
                    <n-icon size="28" v-show="!is_connect">
                        <CellularOff24Filled />
                    </n-icon>
                </n-button>

                <n-button strong tertiary circle @click="ws.send(JSON.stringify({
                    'get_fonts': '',
                }))">
                    <n-icon size="large">
                        <ArrowSync24Filled />
                    </n-icon>
                </n-button>

                <n-button strong tertiary circle @click="() => {
                    if (currentLang.lang.name === 'zh-CN')
                        currentLang.lang = enUS, currentLang.dateLang = dateEnUS;
                    else
                        currentLang.lang = zhCN, currentLang.dateLang = dateZhCN;
                }">
                    <n-icon size="large">
                        <LocalLanguage24Filled />
                    </n-icon>
                </n-button>

                <n-button strong tertiary circle
                    @click="() => currentTheme = currentTheme.name === 'light' ? darkTheme : lightTheme">
                    <n-icon size="large">
                        <DarkTheme24Filled />
                    </n-icon>
                </n-button>

            </n-flex>


            <n-flex id="controlSpace">
                <n-layout has-sider>

                    <!-- 左侧菜单栏 -->
                    <n-layout-sider bordered collapse-mode="width" :width="170" :collapsed="collapseMenu" show-trigger
                        @collapse="collapseMenu = true" @expand="collapseMenu = false">
                        <n-menu :collapsed="collapseMenu" :options="menuOptions" :value="(route_name as Key)" />
                    </n-layout-sider>

                    <!-- 右侧编辑区 -->
                    <n-layout>
                        <RouterView />
                    </n-layout>

                </n-layout>
            </n-flex>

        </n-flex>
    </n-config-provider>
</template>

<style scoped>
#outermost {
    width: 100vw;
    height: 100vh;
    position: relative;
    background-color: v-bind('currentTheme.common.bodyColor');
}

#topButtonBarFlex {
    height: calc(2rem + 2px);
    position: relative;
    gap: 1rem;
    padding: 0.5rem;
    border-bottom: 1px solid v-bind('currentTheme.common.borderColor');
}

#controlSpace {
    height: calc(100% - 2rem - 3px);
    position: relative;
    overflow: hidden;

    >.n-layout {
        max-height: 100%;
    }
}
</style>
