<template>
  <Line
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
  Legend
} from 'chart.js'
  
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)
  
  export default {
    name: 'LineChart',
    components: { Line },
    props: {
        chartData: {
            type: Object,
            required: true,
        },
        chartOptions: {
            type: Object,
            default: null,
        },
    },
    watch: {
    // 监听 chartData 或 chartOptions 的变化，并手动触发更新
    chartData(newValue, oldValue) {
        console.log("hi")
        console.log(newValue, oldValue)
      if (newValue !== oldValue) {
        console.log('chartData changed')
        this.$nextTick(() => {
          this.$refs.chart.$chart.update()
        })
      }
    },
    chartOptions(newValue, oldValue) {
      if (newValue !== oldValue) {
        console.log('chartOptions changed')
        this.$nextTick(() => {
          this.$refs.chart.$chart.update()
        })
      }
    }
  }
  }
  </script>