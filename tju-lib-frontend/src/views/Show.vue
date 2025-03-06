<template>
    <a-config-provider :locale="zhCN">
        <div style="margin : 10px 10px 0px 10px">
            <a-card title="查询条件">
                <h3>请选择图书馆</h3>
                <a-select
                    v-model:value="selectedLibrary"
                    style="width: 200px"
                    @change="fetchData"
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
                <!-- <a-button type="primary" style="margin-top: 16px" @click="fetchData">查询</a-button> -->
            </a-card>
        
            <a-card title="结果">
                <h3>图书馆：{{ selectedLibrary }}</h3>
                <h3>日期：{{ selectedDate.format('YYYY-MM-DD') }}</h3>
            <a-card :loading="isLoading">
                <!--采用 Chartjs 的折线图展示 data 的数据-->
                <div v-if = "data.labels.length > 0" style="height: 50vh; display: flex; justify-content: center; align-items: center;">
                    <!-- <div>{{ data }}</div> -->
                    <LineChart :chartData="data" />
                </div>
                <div v-else style="text-align: center; padding: 20px;">
                    <h2>暂无数据</h2>
                </div>
            </a-card>
                
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
            libPplMax: 0,
            data: {
                labels: [],
                datasets: [
                    {
                        label: '当前人数',
                        // skyblue
                        backgroundColor: 'rgba(2, 159, 253, 0.0)',
                        borderColor: 'rgba(2, 159, 253, 1)', // 默认是啥都无所谓
                        // fill: true, // 是否填充区域
                        pointStyle: false, // 设置为 false，隐藏散点
                        tension: 0.4, // 线条的平滑度
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
            this.fetchData();
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
                    "time": "某一天的时间" # 形如 "2024-05-20 12:00:00"
                }
            ]
            lib_ppl_max: "最大人数"
        }
        */
        fetchData() {
            this.isLoading = true;
            const req_data = {
                lib_name: this.selectedLibrary,
                timestamp: this.selectedDate.format('YYYY-MM-DD'),
            };
            // console.log(req_data);
            fetch('/api/get-lib-ppl', {
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
                        this.libPplMax = data.lib_ppl_max;
                        // console.log(this.libPplMax);
                        this.data = { // 必须整体赋值，否则不会触发更新
                            labels: data.data.map((item) => item.rec_time),
                            datasets: [{
                                label: '当前人数',
                                // 天蓝色
                                backgroundColor: (context) => {
                                    const value = context.raw || 0;
                                    return value < this.libPplMax ? 'rgba(2, 159, 253, 0.4)' : 'rgba(255, 0, 0, 0.4)';
                                },
                                segment: {
                                    borderColor: (context) => { // 边框颜色
                                        const value = context.p1.parsed.y;
                                        // 获取相邻两点的时间值
                                        const time1 = new Date(context.p0.parsed.x);
                                        const time2 = new Date(context.p1.parsed.x);
                                        // 计算时间差（毫秒）
                                        const timeDiff = Math.abs(time2 - time1);
                                        
                                        // 如果时间差大于1小时（3600000毫秒）
                                        if (timeDiff > 3600000) {
                                            return 'rgba(128, 128, 128, 0.5)'; // 灰色半透明
                                        }

                                        return value < this.libPplMax ? 'rgba(2, 159, 253, 1)' : 'rgba(255, 0, 0, 1)';
                                    },
                                    borderDash: (context) => { // 虚线显示
                                        const time1 = new Date(context.p0.parsed.x);
                                        const time2 = new Date(context.p1.parsed.x);
                                        const timeDiff = Math.abs(time2 - time1);
                                        
                                        // 时间差大于1小时时使用虚线
                                        return timeDiff > 3600000 ? [5, 5] : [];
                                    },
                                },
                                data: data.data.map((item) => item.lib_ppl_cur),
                                pointStyle: false, // 设置为 false，隐藏散点
                                // fill: true, // 是否填充区域
                                tension: 0.4 // 线条的平滑度
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
    mounted() {
        this.fetchData();
    },
};
</script>
