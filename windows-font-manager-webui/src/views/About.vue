<script setup lang="ts">
import { NCard } from 'naive-ui'

const home_url = "https://github.com/op200/"
</script>


<template>
    <div style="display: grid;gap: 1rem;padding: 1rem;position: relative;overflow-x: hidden;">

        <n-card title="Windows Font Manager WebUI">
            <template #header-extra>
                <a :href=home_url>
                    {{ home_url }}
                </a>
            </template>
            <div>
                介绍
            </div>
        </n-card>

    </div>
</template>