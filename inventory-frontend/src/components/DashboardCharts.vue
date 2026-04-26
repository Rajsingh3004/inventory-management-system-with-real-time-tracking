<template>
  <div class="charts-container"> 

    <div class="chart-card">
  <div class="chart-scroll" ref="stockWrapper">
    <canvas ref="stockChart"></canvas>
  </div>
</div>

    <div v-if="userRole === 'admin'" class="chart-card">
      <canvas ref="requestChart"></canvas>
    </div>

    <div v-if="userRole === 'admin'" class="chart-card">
  <canvas ref="salesChart"></canvas>
</div>

  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'
import { nextTick } from 'vue'

onMounted(async () => {
  await nextTick()
  renderCharts()
})

const props = defineProps({
  items: Array,
  requests: Array,
  sales: Array,
  userRole: String 
})
const stockChart = ref(null)
const requestChart = ref(null)
const salesChart = ref(null)
const stockWrapper = ref(null)


let salesInstance = null
let stockInstance = null
let requestInstance = null

const renderCharts = () => {
  // --- 1. STOCK CHART ---
  if (stockChart.value) {
    if (stockInstance) stockInstance.destroy()
    
    // Dynamic height logic
    const itemCount = props.items.length
    if (stockWrapper.value) stockWrapper.value.style.height = (itemCount * 60) + 'px'

    stockInstance = new Chart(stockChart.value, {
      type: 'bar',
      data: {
        labels: props.items.map(i => i.name),
        datasets: [{
          label: 'Stock Quantity',
          data: props.items.map(i => i.quantity),
          backgroundColor: props.items.map(i => i.quantity < 5 ? '#ef4444' : '#3b82f6'),
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#e4e4e7' } } },
        scales: {
          x: { ticks: { color: '#a1a1aa' } },
          y: { ticks: { color: '#a1a1aa' } }
        }
      }
    })
  }

  // --- 2. REQUEST CHART ---
  if (requestChart.value) {
    if (requestInstance) requestInstance.destroy()
    
    const statusCount = { pending: 0, approved: 0, rejected: 0 }
    props.requests.forEach(r => {
      const s = r.status?.toLowerCase()
      if (statusCount[s] !== undefined) statusCount[s]++
    })

    requestInstance = new Chart(requestChart.value, {
      type: 'pie',
      data: {
        labels: ['Pending', 'Approved', 'Rejected'],
        datasets: [{
          data: [statusCount.pending, statusCount.approved, statusCount.rejected],
          backgroundColor: ['#facc15', '#22c55e', '#ef4444']
        }]
      },
      options: {
        plugins: { legend: { labels: { color: '#e4e4e7' } } }
      }
    })
  }

  // --- 3. SALES CHART (Only for Admin) ---
  if (salesChart.value && props.userRole === 'admin') {
    if (salesInstance) salesInstance.destroy()
    
    salesInstance = new Chart(salesChart.value, {
      type: 'line',
      data: {
        labels: props.sales.map(s => new Date(s.created_at).toLocaleDateString()),
        datasets: [{
          label: 'Sales Quantity',
          data: props.sales.map(s => s.quantity),
          borderColor: '#22c55e',
          backgroundColor: 'rgba(34,197,94,0.2)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#e4e4e7' } } },
        scales: {
          x: { ticks: { color: '#a1a1aa' } },
          y: { ticks: { color: '#a1a1aa' } }
        }
      }
    })
  }
}

onMounted(() => {
  renderCharts()
})

watch(() => [props.items, props.requests, props.sales], async () => {
  if (props.items.length || props.requests.length || props.sales.length) {
    await nextTick()
    renderCharts()
  }
})
</script>

<style>

/* ================= CHARTS LAYOUT FIX ================= */

.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
  gap: 20px;
  margin-bottom: 30px;
}

/* Chart Card */
.chart-card {
  background: linear-gradient(145deg, #111113, #0a0a0c);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 15px;
  position: relative;
  transition: 0.3s ease;
  height: 350px;
  overflow: visible;   
  width: 100%;
  flex-direction: column;
}


/* Hover effect */
.chart-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.5);
}

/* Canvas full fit */
.chart-card canvas {
  width: 100% !important;
  display: block;
}
/* ================= RESPONSIVE ================= */

@media (max-width: 1024px) {
  .charts-container {
    grid-template-columns: 1fr 1fr; /* 2 per row */
  }
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr; /* 1 per row */
  }
}
.chart-scroll {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 5px;
}


</style>