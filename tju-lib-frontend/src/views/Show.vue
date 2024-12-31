<template>
    <a-config-provider :locale="zhCN">
        <div style="margin : 10px 10px 0px 10px">
            <a-card title="查询条件">
                <h3>请选择图书馆</h3>
                <a-select
                    v-model:value="selectedLibrary"
                    style="width: 200px"
                >
                    <a-select-option
                        v-for="library in libraries"
                        :key="library.value"
                        :value="library.value"
                    >
                        {{ library.label }}
                    </a-select-option>
                </a-select>
                <h3>请选择日期</h3>        
                <div :style="{ width: '300px', border: '1px solid #d9d9d9', borderRadius: '4px' }">
                    <a-calendar :value="selectedDate" :fullscreen="false" @select="onSelect" @panelChange="onPanelChange"/>
                </div>
                <a-button type="primary" style="margin-top: 16px" @click="fetchData">查询</a-button>
            </a-card>
        
            <a-card title="结果">
                <p>图书馆：{{ selectedLibrary }}</p>
                <p>日期：{{ selectedDate.format('YYYY-MM-DD') }}</p>

                <!--采用 Chartjs 的折线图展示 data 的数据-->
                <div v-if = "data.labels.length > 0">
                    <!-- <div>{{ data }}</div> -->
                    <LineChart :chartData="data" />
                </div>
                <div v-else>
                    <p>暂无数据</p>
                </div>
            </a-card>
        </div>
    </a-config-provider>
</template>

<script>
import dayjs from 'dayjs';
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import 'dayjs/locale/zh-cn';
import LineChart from '../components/LineChart.vue';

dayjs.locale('zh-cn');

export default {
    data() {
        return {
            zhCN, // 就必须得有这句..
            libraries: [ // 图书馆的列表，不需要向后端请求了，麻烦
                { value: '四平路校区图书馆', label: '四平路校区图书馆' },
                { value: '嘉定校区图书馆', label: '嘉定校区图书馆' },
                { value: '沪西校区图书馆', label: '沪西校区图书馆' },
                { value: '沪北校区图书馆', label: '沪北校区图书馆' },
                { value: '德文图书馆', label: '德文图书馆' },
            ],

            selectedLibrary: '嘉定校区图书馆', // 默认选嘉图，为我所用
            selectedDate: dayjs(), // 默认选今天
            data: {
                labels: [],
                datasets: [
                    {
                        label: '当前人数',
                        // skyblue
                        backgroundColor: 'rgba(2, 159, 253, 0.4)',
                        data: [],
                    },
                ],
            }, // 后端返回的数据
            isLoading: false,
        };
    },
    methods: {
        onSelect(date) {
            this.selectedDate = date;
            console.log(this.selectedDate);
        },
        onPanelChange(date) {
            this.selectedDate = date;
            console.log(this.selectedDate);
        },
        // 向后端请求数据
        /*
        传给后端的 json 数据格式：
        {
            "lib_name": "图书馆名称",
            "timestamp": "时间戳",  # 形如 "2024-05-20"
        }
        '''
        '''
        后端返回的 json 数据格式：
        {
            status: "ok" | "fail",
            msg: "错误信息",
            data[
                {
                    "lib_ppl_cur": "当前人数",
                    "time": "某一天的时间" # 形如 "10:23"
                }
            ]
        }
        */
        fetchData() {
            this.isLoading = true;
            const req_data = {
                lib_name: this.selectedLibrary,
                timestamp: this.selectedDate.format('YYYY-MM-DD'),
            };
            // console.log(req_data);
            fetch('http://127.0.0.1:8000/api/get-lib-ppl', {
            // fetch('/api/get-lib-ppl', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(req_data),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log('Success:', data);
                    if (data.status === 'ok') {
                        this.data = { // 必须整体赋值，否则不会触发更新
                            labels: data.data.map((item) => item.rec_time),
                            datasets: [{
                                label: '当前人数',
                                // 天蓝色
                                backgroundColor: 'rgba(2, 159, 253, 0.4)',
                                data: data.data.map((item) => item.lib_ppl_cur)
                            }]
                        };
                    } else {
                        this.$message.error(data.msg);
                    }
                    this.isLoading = false;
                })
                .catch((error) => {
                    console.error('Error:', error);
                    this.isLoading = false;
                });
        }
    },
    components: {
        LineChart,
    },
};
</script>