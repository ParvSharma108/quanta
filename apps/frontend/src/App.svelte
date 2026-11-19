<script lang="ts">
  import { onMount } from 'svelte';
  import Navbar from './lib/components/Navbar.svelte';
  import TreasuryDashboard from './lib/components/TreasuryDashboard.svelte';
  import QuantumLab from './lib/components/QuantumLab.svelte';
  import ClassicalBenchmark from './lib/components/ClassicalBenchmark.svelte';
  import AIAgents from './lib/components/AIAgents.svelte';
  import ConfigEditor from './lib/components/ConfigEditor.svelte';
  import BenchmarkResults from './lib/components/BenchmarkResults.svelte';

  import type { FinancialProblem, OptimizationCompareResponse } from './lib/types';
  import { DEFAULT_PROBLEM, runCompareSolvers } from './lib/api';

  let activeTab: string = 'dashboard';
  let problem: FinancialProblem = { ...DEFAULT_PROBLEM };
  let compareData: OptimizationCompareResponse | null = null;
  let loadingSolvers: boolean = false;

  async function loadSolvers() {
    loadingSolvers = true;
    try {
      compareData = await runCompareSolvers(problem);
    } catch (err) {
      console.error('Failed to load compare data:', err);
    } finally {
      loadingSolvers = false;
    }
  }

  function handleProblemSave(updatedProblem: FinancialProblem) {
    problem = updatedProblem;
    loadSolvers();
  }

  onMount(() => {
    loadSolvers();
  });
</script>

<div class="min-h-screen flex flex-col bg-slate-950 text-slate-100">
  
  <!-- Navigation Header -->
  <Navbar {activeTab} onTabChange={(tab) => (activeTab = tab)} />

  <!-- Main Workspace Content -->
  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
    {#if activeTab === 'dashboard'}
      <TreasuryDashboard 
        {problem} 
        {compareData} 
        loading={loadingSolvers} 
        onRefresh={loadSolvers} 
        onNavigateToTab={(tab) => (activeTab = tab)} 
      />
    {:else if activeTab === 'quantum'}
      <QuantumLab {problem} />
    {:else if activeTab === 'solvers'}
      <ClassicalBenchmark 
        {compareData} 
        loading={loadingSolvers} 
        onRefresh={loadSolvers} 
      />
    {:else if activeTab === 'ai-agents'}
      <AIAgents {problem} />
    {:else if activeTab === 'config'}
      <ConfigEditor {problem} onSave={handleProblemSave} />
    {:else if activeTab === 'benchmarks'}
      <BenchmarkResults />
    {/if}
  </main>

  <!-- Modern Enterprise Footer -->
  <footer class="border-t border-slate-900 bg-slate-950/80 py-6 text-xs text-slate-500">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-2">
        <span class="font-bold text-slate-300">QUANTA</span>
        <span>•</span>
        <span>Autonomous Financial Treasury & Capital Optimization</span>
      </div>
      <div class="flex items-center gap-4 text-[11px]">
        <span>Member 1: Atharv (AI Engine)</span>
        <span>•</span>
        <span class="text-indigo-400 font-medium">Member 2: Parv (Optimization Engine)</span>
        <span>•</span>
        <span>Member 3: Aryan (Platform & Frontend)</span>
      </div>
    </div>
  </footer>

</div>
