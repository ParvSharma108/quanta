<script lang="ts">
  import { onMount } from 'svelte';
  import { Chart, registerables } from 'chart.js';

  Chart.register(...registerables);

  export let type: 'doughnut' | 'bar' | 'line' | 'radar' = 'doughnut';
  export let data: any;
  export let options: any = {};
  export let height: string = '240px';

  let canvas: HTMLCanvasElement;
  let chartInstance: Chart | null = null;

  $: if (chartInstance && data) {
    chartInstance.data = data;
    chartInstance.update();
  }

  onMount(() => {
    if (canvas) {
      chartInstance = new Chart(canvas, {
        type,
        data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          color: '#94a3b8',
          plugins: {
            legend: {
              labels: {
                color: '#cbd5e1',
                font: { family: 'Plus Jakarta Sans', size: 11 }
              }
            },
            tooltip: {
              backgroundColor: 'rgba(15, 23, 42, 0.9)',
              titleColor: '#f8fafc',
              bodyColor: '#cbd5e1',
              borderColor: 'rgba(255, 255, 255, 0.1)',
              borderWidth: 1,
              padding: 10,
              boxPadding: 4,
              usePointStyle: true
            }
          },
          ...options
        }
      });
    }

    return () => {
      if (chartInstance) {
        chartInstance.destroy();
      }
    };
  });
</script>

<div class="relative w-full" style="height: {height};">
  <canvas bind:this={canvas}></canvas>
</div>
