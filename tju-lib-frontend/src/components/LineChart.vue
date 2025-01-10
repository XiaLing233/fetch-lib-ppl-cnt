<template>
    <Line
    ref="chart"
    :data="chartData"
    :options="chartOptions"
    />
</template>
  
  <script>
  import { Line } from 'vue-chartjs'
  import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
} from 'chart.js'

// import { zhCN } from 'date-fns/locale' // 添加中文本地化
import 'chartjs-adapter-date-fns' // 日期格式化
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn';

dayjs.locale('zh-cn');

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
)
  
  export default {
    name: 'LineChart',
    components: { Line },
    props: {
        chartData: {
            type: Object,
            required: true
        },
        chartOptions: {
            type: Object,
            default: () => ({
                maintainAspectRatio: false,  // 禁用保持宽高比，允许自适应
                responsive: true, // 得有这句，不然不会自适应
                scales: {
                    x: {
                        type: 'time', // 因为这句话的存在，所以不能删除 chartjs-adapter-date-fns，而原始时间戳也会被转换成日期格式，需要 dayjs 使用 parsed.x 来格式化！
                        time: {
                            unit: 'hour',
                            displayFormats: {
                                hour: 'HH:mm'
                            }
                        },
                        ticks: {
                            source: 'auto',
                            callback: function(value) {
                                return dayjs(value).format('HH:mm');
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: { // 对于每个数据点的提示
                        callbacks: {
                            title: function(context) {
                                return dayjs(context[0].parsed.x).format('HH:mm:ss') // parsed 表示已经被 Chartjs 解析过的数据
                            }
                        }
                    },
                        legend: { // 图例
                            display: false
                        },
                        title: { // 标题
                            display: true,
                            text: '人数变化趋势'
                        },
                    },
            })
        }
    },
    watch: {
    chartData(newValue, oldValue) {
      if (newValue !== oldValue && this.$refs.chart) {
        this.$nextTick(() => {
          this.$refs.chart.$chart.update()
        })
      }
    },
    chartOptions(newValue, oldValue) {
      if (newValue !== oldValue && this.$refs.chart) {
        this.$nextTick(() => {
          this.$refs.chart.$chart.update()
        })
      }
    }
  },
  }
  </script>