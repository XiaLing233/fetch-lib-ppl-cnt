<template>
    <a-card title="更新日志" style="min-height: 100%;">
            <a-list item-layout="vertical" :data-source="log_list">
                <template #renderItem="{ item }">
                    <a-list-item>
                        <a-list-item-meta
                            :title="item.msg"
                            :description="item.time"
                        />
                    </a-list-item>
                </template>
            </a-list>
    </a-card>
</template>

<script>
export default {
    data() {
        return {
            log_list: []
        }
    },
    mounted() {
        this.getLogList()
    },
    methods: {
        getLogList() {
            fetch('/api/get-update-log')
                .then(response => response.json())
                .then(data => {
                    this.log_list = data.data
                })
                .catch(error => {
                    console.error('Error:', error)
                })
            }
    }
}
</script>