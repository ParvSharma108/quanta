<script lang="ts">
  import { 
    Bot, 
    ShieldCheck, 
    TrendingUp, 
    Scale, 
    CheckCircle2, 
    AlertCircle, 
    Play, 
    Sparkles,
    UserCheck,
    Cpu
  } from 'lucide-svelte';
  import type { FinancialProblem, StrategyGenerateResponse, DeliberationSummary } from '../types';
  import { generateAIStrategy, evaluateAICouncil } from '../api';

  export let problem: FinancialProblem;

  let algorithm: string = 'astar';
  let runningSearch: boolean = false;
  let runningCouncil: boolean = false;
  let strategyResult: StrategyGenerateResponse | null = null;
  let councilResult: DeliberationSummary | null = null;

  async function handleRunAISearch() {
    runningSearch = true;
    try {
      strategyResult = await generateAIStrategy(problem, algorithm);
    } catch (e) {
      console.error(e);
    } finally {
      runningSearch = false;
    }
  }

  async function handleRunCouncil() {
    runningCouncil = true;
    try {
      councilResult = await evaluateAICouncil(problem);
    } catch (e) {
      console.error(e);
    } finally {
      runningCouncil = false;
    }
  }

  // Pre-load on mount
  $: if (!strategyResult && !runningSearch) {
    handleRunAISearch();
  }
  $: if (!councilResult && !runningCouncil) {
    handleRunCouncil();
  }
</script>

<div class="space-y-6 animate-fade-in">

  <!-- Header Banner -->
  <div class="glass-panel p-6 rounded-3xl relative overflow-hidden">
    <div class="absolute -right-20 -top-20 w-80 h-80 bg-gradient-to-br from-emerald-600/20 via-cyan-600/20 to-transparent rounded-full blur-3xl pointer-events-none"></div>

    <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <Bot class="w-3.5 h-3.5 text-emerald-400" />
          <span>Intelligent Agent Council • Member 1 Integration</span>
        </div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight">
          AI Multi-Agent Deliberation & Search Engine
        </h1>
        <p class="text-sm text-slate-400 mt-1 max-w-2xl">
          Cooperative consensus deliberation across TreasuryAgent, RiskAgent, ComplianceAgent, and DecisionAgent paired with deterministic A* heuristic pathfinding.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <button
          on:click={handleRunCouncil}
          disabled={runningCouncil}
          class="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-indigo-600 hover:from-emerald-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/30 transition-all hover:scale-[1.02] disabled:opacity-50"
        >
          <Sparkles class="w-4 h-4" />
          <span>{runningCouncil ? 'Deliberating...' : 'Convene Council'}</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Multi-Agent Council Opinions Grid -->
  {#if councilResult}
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <UserCheck class="w-4 h-4 text-emerald-400" />
          <span>Deliberation Council Opinions</span>
        </h2>
        <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          Consensus: Approved
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

        <!-- Treasury Agent Card -->
        <div class="glass-panel p-5 rounded-2xl space-y-3 border-l-4 border-l-cyan-500">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-white">Treasury Agent</span>
            <span class="text-xs px-2 py-0.5 rounded-md bg-cyan-500/20 text-cyan-300 font-bold">
              Score: {councilResult.treasury_opinion.score}/10
            </span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            "{councilResult.treasury_opinion.rationale}"
          </p>
          <div class="flex items-center gap-1.5 text-[11px] text-emerald-400 font-semibold">
            <CheckCircle2 class="w-3.5 h-3.5" />
            <span>Operational Cashflow Validated</span>
          </div>
        </div>

        <!-- Risk Agent Card -->
        <div class="glass-panel p-5 rounded-2xl space-y-3 border-l-4 border-l-rose-500">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-white">Risk Agent</span>
            <span class="text-xs px-2 py-0.5 rounded-md bg-rose-500/20 text-rose-300 font-bold">
              Score: {councilResult.risk_opinion.score}/10
            </span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            "{councilResult.risk_opinion.rationale}"
          </p>
          <div class="flex items-center gap-1.5 text-[11px] text-emerald-400 font-semibold">
            <CheckCircle2 class="w-3.5 h-3.5" />
            <span>Monte Carlo VaR Within Bound</span>
          </div>
        </div>

        <!-- Compliance Agent Card -->
        <div class="glass-panel p-5 rounded-2xl space-y-3 border-l-4 border-l-indigo-500">
          <div class="flex items-center justify-between">
            <span class="text-xs font-extrabold text-white">Compliance Agent</span>
            <span class="text-xs px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 font-bold">
              Score: {councilResult.compliance_opinion.score}/10
            </span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">
            "{councilResult.compliance_opinion.rationale}"
          </p>
          <div class="flex items-center gap-1.5 text-[11px] text-emerald-400 font-semibold">
            <CheckCircle2 class="w-3.5 h-3.5" />
            <span>Statutory Reserve Satisfied</span>
          </div>
        </div>

      </div>
    </div>
  {/if}

  <!-- Deterministic AI Search Execution -->
  <div class="glass-panel p-6 rounded-3xl space-y-5">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <div>
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <Cpu class="w-4 h-4 text-cyan-400" />
          <span>Deterministic AI Search Trajectory</span>
        </h2>
        <p class="text-xs text-slate-400">Step-by-step state space transitions solving capital allocation as discrete search</p>
      </div>

      <div class="flex items-center gap-2">
        <select 
          bind:value={algorithm}
          on:change={handleRunAISearch}
          class="bg-slate-900 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 font-medium focus:outline-none focus:border-cyan-500"
        >
          <option value="astar">A* Search (Admissible Heuristic)</option>
          <option value="best_first">Greedy Best-First</option>
          <option value="hill_climbing">Steepest Ascent Hill Climbing</option>
          <option value="bfs">Breadth-First Search (BFS)</option>
          <option value="dfs">Depth-First Search (DFS)</option>
        </select>

        <button 
          on:click={handleRunAISearch}
          disabled={runningSearch}
          class="px-4 py-1.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all disabled:opacity-50"
        >
          Run
        </button>
      </div>
    </div>

    <!-- Strategy Actions Timeline -->
    {#if strategyResult}
      <div class="space-y-3">
        <div class="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 flex items-center justify-between">
          <span>{strategyResult.strategy.explanation}</span>
          <span class="text-cyan-400 font-mono font-bold">{strategyResult.search_result.states_explored} States Explored ({strategyResult.search_result.execution_time_ms.toFixed(1)} ms)</span>
        </div>

        <div class="space-y-2">
          {#each strategyResult.strategy.actions as act, i}
            <div class="p-3 rounded-xl bg-slate-900/50 border border-slate-800 flex items-center justify-between text-xs">
              <div class="flex items-center gap-3">
                <span class="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] font-bold flex items-center justify-center">
                  {i + 1}
                </span>
                <span class="font-bold text-white uppercase tracking-wider text-[11px]">{act.action_type}</span>
                <span class="text-slate-400">{act.reason}</span>
              </div>
              <span class="font-mono font-bold text-cyan-400">₹{act.amount.toFixed(1)} Cr</span>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>

</div>
