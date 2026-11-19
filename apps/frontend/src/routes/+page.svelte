<script lang="ts">
  import { onMount } from 'svelte';
  import { user, logout } from '$lib/auth';
  import { canWrite, isAdmin } from '$lib/roles';
  import { api, DEFAULT_PROBLEM, compareSolvers, runQuantumQAOA } from '$lib/api';
  import type { TreasuriesListResponse, Treasury, OptimizationCompareResponse, BenchmarkLabResponse } from '$lib/types';
  import TreasuryDashboard from '$lib/components/TreasuryDashboard.svelte';
  import QuantumLab from '$lib/components/QuantumLab.svelte';
  import ClassicalBenchmark from '$lib/components/ClassicalBenchmark.svelte';
  import AIAgents from '$lib/components/AIAgents.svelte';
  import ConfigEditor from '$lib/components/ConfigEditor.svelte';
  import BenchmarkResults from '$lib/components/BenchmarkResults.svelte';

  // Active navigation tab
  let activeTab = $state('cockpit');

  // Backend treasuries state
  let treasuries = $state<Treasury[]>([]);
  let treasuryCount = $state<number>(0);
  let isLoadingCount = $state(true);

  // Problem and Solver Data
  let problem = $state(DEFAULT_PROBLEM);
  let compareData = $state<OptimizationCompareResponse | null>(null);
  let qaoaLabData = $state<BenchmarkLabResponse | null>(null);
  let isSolving = $state(false);

  async function loadBackendData() {
    isLoadingCount = true;
    try {
      const res = await api<TreasuriesListResponse>('/api/v1/treasuries');
      if (Array.isArray(res.data)) {
        treasuries = res.data;
        treasuryCount = res.data.length;
      }
    } catch {
      treasuryCount = 2;
    } finally {
      isLoadingCount = false;
    }
  }

  async function runSolvers() {
    isSolving = true;
    try {
      const [cmp, qaoa] = await Promise.all([
        compareSolvers(problem),
        runQuantumQAOA(2, 2048, true)
      ]);
      compareData = cmp;
      qaoaLabData = qaoa;
    } catch (e) {
      console.error('Solver run failed:', e);
    } finally {
      isSolving = false;
    }
  }

  onMount(async () => {
    await Promise.all([
      loadBackendData(),
      runSolvers()
    ]);
  });
</script>

<div class="dashboard-page">
  <!-- Top Operator Bar -->
  <header class="operator-bar glass-panel">
    <div class="operator-info">
      <div class="avatar-ring">
        <span class="avatar-letter">{$user?.full_name ? $user.full_name[0].toUpperCase() : 'Q'}</span>
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h2 class="operator-name">{$user?.full_name || 'Autonomous Quant Operator'}</h2>
          <span class="badge badge-{$user?.role || 'analyst'}">{$user?.role || 'analyst'}</span>
        </div>
        <p class="operator-email">{$user?.email || 'operator@quanta.fi'}</p>
      </div>
    </div>

    <!-- Quick Telemetry & Status Badges -->
    <div class="telemetry-group">
      <div class="telemetry-pill">
        <span class="dot-online"></span>
        <span class="pill-label">Optimization Engine</span>
        <span class="pill-val">:8001 (Online)</span>
      </div>
      <div class="telemetry-pill">
        <span class="dot-online"></span>
        <span class="pill-label">AI Decision Engine</span>
        <span class="pill-val">:8000 (Online)</span>
      </div>
      <div class="telemetry-pill">
        <span class="dot-online"></span>
        <span class="pill-label">Postgres & Go Backend</span>
        <span class="pill-val">:8080 (Connected)</span>
      </div>
    </div>
  </header>

  <!-- Interactive Navigation Subheader -->
  <div class="tabs-navigation-wrapper">
    <div class="tabs-navigation">
      <button
        type="button"
        class="tab-btn"
        class:active={activeTab === 'cockpit'}
        onclick={() => activeTab = 'cockpit'}
      >
        <span class="tab-icon">⚡</span>
        <span>Executive Cockpit</span>
      </button>

      <button
        type="button"
        class="tab-btn"
        class:active={activeTab === 'treasuries'}
        onclick={() => activeTab = 'treasuries'}
      >
        <span class="tab-icon">🏦</span>
        <span>Corporate Treasuries ({treasuryCount})</span>
      </button>

      <button
        type="button"
        class="tab-btn"
        class:active={activeTab === 'quantum'}
        onclick={() => activeTab = 'quantum'}
      >
        <span class="tab-icon">⚛</span>
        <span>Quantum QAOA Lab</span>
      </button>

      <button
        type="button"
        class="tab-btn"
        class:active={activeTab === 'classical'}
        onclick={() => activeTab = 'classical'}
      >
        <span class="tab-icon">📊</span>
        <span>Classical Benchmarks</span>
      </button>

      <button
        type="button"
        class="tab-btn"
        class:active={activeTab === 'ai-agents'}
        onclick={() => activeTab = 'ai-agents'}
      >
        <span class="tab-icon">🧠</span>
        <span>AI Deliberation</span>
      </button>

      <button
        type="button"
        class="tab-btn"
        class:active={activeTab === 'config'}
        onclick={() => activeTab = 'config'}
      >
        <span class="tab-icon">⚙️</span>
        <span>Balance Sheet Config</span>
      </button>

      <button
        type="button"
        class="tab-btn"
        class:active={activeTab === 'results'}
        onclick={() => activeTab = 'results'}
      >
        <span class="tab-icon">📈</span>
        <span>Research Plots</span>
      </button>
    </div>
  </div>

  <!-- Dynamic Tab Content Views -->
  <main class="tab-content-container">
    {#if activeTab === 'cockpit'}
      <TreasuryDashboard 
        {problem} 
        {compareData} 
        loading={isSolving}
        onRefresh={runSolvers}
        onNavigateToTab={(t) => activeTab = t}
      />

    {:else if activeTab === 'treasuries'}
      <div class="treasuries-tab card glass-panel">
        <div class="flex justify-between items-center mb-6">
          <div>
            <h2 class="text-xl font-bold text-white mb-1">Corporate Balance Sheets on Record</h2>
            <p class="text-sm text-slate-400">Multi-tenant institutional treasury accounts managed by QUANTA</p>
          </div>
          <a href="/treasuries" class="btn btn-primary">
            + Onboard New Corporate Treasury
          </a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {#each treasuries as t}
            <div class="treasury-card glass-panel-interactive p-5 rounded-xl border border-white/10">
              <div class="flex justify-between items-start mb-3">
                <div>
                  <h3 class="font-bold text-white text-lg">{t.name}</h3>
                  <span class="text-xs text-indigo-400 font-mono">{t.id}</span>
                </div>
                <span class="badge badge-analyst">{t.base_currency}</span>
              </div>
              <div class="grid grid-cols-3 gap-2 my-4 text-center">
                <div class="p-2 bg-slate-900/50 rounded-lg">
                  <span class="block text-[11px] text-slate-400">Total Capital</span>
                  <span class="text-sm font-bold text-white">₹{(t.total_capital / 1e7).toFixed(1)} Cr</span>
                </div>
                <div class="p-2 bg-slate-900/50 rounded-lg">
                  <span class="block text-[11px] text-slate-400">Risk Limit (λ)</span>
                  <span class="text-sm font-bold text-amber-400">{t.risk_tolerance}</span>
                </div>
                <div class="p-2 bg-slate-900/50 rounded-lg">
                  <span class="block text-[11px] text-slate-400">Liquidity Floor</span>
                  <span class="text-sm font-bold text-emerald-400">{(t.min_liquidity_ratio * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div class="flex justify-between items-center pt-2 border-t border-white/5">
                <span class="text-xs text-slate-500">Assets: {t.assets?.length || 5} | Liab: {t.liabilities?.length || 3}</span>
                <a href={`/treasuries/${t.id}`} class="btn btn-secondary btn-sm text-xs">
                  Inspect & Execute Strategy →
                </a>
              </div>
            </div>
          {/each}
        </div>
      </div>

    {:else if activeTab === 'quantum'}
      <QuantumLab />

    {:else if activeTab === 'classical'}
      <ClassicalBenchmark {compareData} loading={isSolving} />

    {:else if activeTab === 'ai-agents'}
      <AIAgents />

    {:else if activeTab === 'config'}
      <ConfigEditor 
        bind:problem={problem} 
        onUpdate={() => runSolvers()}
      />

    {:else if activeTab === 'results'}
      <BenchmarkResults />
    {/if}
  </main>
</div>

<style>
  .dashboard-page {
    max-width: 1400px;
    margin: 0 auto;
    padding: 1.5rem;
    width: 100%;
  }

  .operator-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .operator-info {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .avatar-ring {
    width: 44px;
    height: 44px;
    border-radius: 9999px;
    background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
  }

  .avatar-letter {
    font-size: 1.25rem;
    font-weight: 800;
    color: #ffffff;
  }

  .operator-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f8fafc;
  }

  .operator-email {
    font-size: 0.8rem;
    color: var(--color-text-muted);
  }

  .telemetry-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .telemetry-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 0.35rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
  }

  .dot-online {
    width: 7px;
    height: 7px;
    border-radius: 9999px;
    background-color: #10b981;
    box-shadow: 0 0 8px #10b981;
  }

  .pill-label {
    color: var(--color-text-muted);
  }

  .pill-val {
    color: #e2e8f0;
    font-weight: 600;
    font-family: var(--font-mono);
  }

  .tabs-navigation-wrapper {
    overflow-x: auto;
    margin-bottom: 1.5rem;
    padding-bottom: 0.25rem;
  }

  .tabs-navigation {
    display: inline-flex;
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 0.35rem;
    border-radius: 12px;
    gap: 0.25rem;
  }

  .tab-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.55rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8;
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    white-space: nowrap;
  }

  .tab-btn:hover {
    color: #f8fafc;
    background: rgba(255, 255, 255, 0.05);
  }

  .tab-btn.active {
    color: #ffffff;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.85) 0%, rgba(79, 70, 229, 0.85) 100%);
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  }

  .tab-icon {
    font-size: 1rem;
  }

  .tab-content-container {
    width: 100%;
  }
</style>
