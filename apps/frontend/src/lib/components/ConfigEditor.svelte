<script lang="ts">
  import { 
    Sliders, 
    Plus, 
    Trash2, 
    RotateCcw, 
    Save, 
    Coins, 
    ShieldAlert, 
    Droplet,
    Sparkles,
    Check
  } from 'lucide-svelte';
  import type { FinancialProblem, Asset } from '../types';
  import { DEFAULT_PROBLEM } from '../api';

  export let problem: FinancialProblem;
  export let onSave: (updated: FinancialProblem) => void;

  let localProblem: FinancialProblem = JSON.parse(JSON.stringify(problem));
  let savedSuccess: boolean = false;

  function addAsset() {
    const newId = `asset_${Date.now()}`;
    localProblem.assets = [
      ...localProblem.assets,
      {
        id: newId,
        name: `New Asset ${localProblem.assets.length + 1}`,
        asset_type: 'other',
        cost: 15.0,
        expected_return: 0.08,
        risk: 0.15,
        liquidity: 0.70,
        volatility: 0.10
      }
    ];
  }

  function removeAsset(index: number) {
    localProblem.assets = localProblem.assets.filter((_, i) => i !== index);
  }

  function resetDefaults() {
    localProblem = JSON.parse(JSON.stringify(DEFAULT_PROBLEM));
    saveChanges();
  }

  function saveChanges() {
    onSave(JSON.parse(JSON.stringify(localProblem)));
    savedSuccess = true;
    setTimeout(() => {
      savedSuccess = false;
    }, 2500);
  }
</script>

<div class="space-y-6 animate-fade-in">

  <!-- Header Banner -->
  <div class="glass-panel p-6 rounded-3xl relative overflow-hidden">
    <div class="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <Sliders class="w-3.5 h-3.5 text-indigo-400" />
          <span>Interactive Parameter Control</span>
        </div>
        <h1 class="text-3xl font-extrabold text-white tracking-tight">
          Balance Sheet & Treasury Configuration
        </h1>
        <p class="text-sm text-slate-400 mt-1 max-w-2xl">
          Customize total capital, statutory liquidity minimums, corporate risk tolerance, and asset universe tickets. Changes instantly propagate to Classical and Quantum solvers.
        </p>
      </div>

      <div class="flex items-center gap-3">
        <button
          on:click={resetDefaults}
          class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700/80 text-slate-300 text-xs font-semibold transition-all hover:scale-[1.02]"
        >
          <RotateCcw class="w-4 h-4" />
          <span>Reset Defaults</span>
        </button>

        <button
          on:click={saveChanges}
          class="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all hover:scale-[1.02]"
        >
          {#if savedSuccess}
            <Check class="w-4 h-4 text-white" />
            <span>Saved!</span>
          {:else}
            <Save class="w-4 h-4" />
            <span>Apply to Solvers</span>
          {/if}
        </button>
      </div>
    </div>
  </div>

  <!-- Global Balance Sheet Sliders -->
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

    <!-- Total Capital Slider -->
    <div class="glass-panel p-5 rounded-2xl space-y-3">
      <div class="flex items-center justify-between text-xs font-semibold text-slate-300">
        <span class="flex items-center gap-1.5">
          <Coins class="w-4 h-4 text-cyan-400" />
          <span>Total Balance Sheet Capital:</span>
        </span>
        <span class="font-mono text-cyan-400 font-bold text-sm">₹{localProblem.capital.toFixed(1)} Cr</span>
      </div>
      <input 
        type="range" 
        min="50" 
        max="300" 
        step="10" 
        bind:value={localProblem.capital}
        class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
      />
      <div class="flex justify-between text-[10px] text-slate-500">
        <span>₹50 Cr</span>
        <span>₹100 Cr (Standard)</span>
        <span>₹300 Cr</span>
      </div>
    </div>

    <!-- Risk Tolerance Slider -->
    <div class="glass-panel p-5 rounded-2xl space-y-3">
      <div class="flex items-center justify-between text-xs font-semibold text-slate-300">
        <span class="flex items-center gap-1.5">
          <ShieldAlert class="w-4 h-4 text-purple-400" />
          <span>Corporate Risk Appetite (λ):</span>
        </span>
        <span class="font-mono text-purple-400 font-bold text-sm">{(localProblem.risk_tolerance * 100).toFixed(0)}%</span>
      </div>
      <input 
        type="range" 
        min="0.1" 
        max="0.9" 
        step="0.05" 
        bind:value={localProblem.risk_tolerance}
        class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
      />
      <div class="flex justify-between text-[10px] text-slate-500">
        <span>Conservative (10%)</span>
        <span>Balanced (50%)</span>
        <span>Aggressive (90%)</span>
      </div>
    </div>

    <!-- Minimum Liquidity Floor Slider -->
    <div class="glass-panel p-5 rounded-2xl space-y-3">
      <div class="flex items-center justify-between text-xs font-semibold text-slate-300">
        <span class="flex items-center gap-1.5">
          <Droplet class="w-4 h-4 text-emerald-400" />
          <span>Statutory Liquidity Floor:</span>
        </span>
        <span class="font-mono text-emerald-400 font-bold text-sm">{(localProblem.minimum_liquidity * 100).toFixed(0)}%</span>
      </div>
      <input 
        type="range" 
        min="0.10" 
        max="0.60" 
        step="0.05" 
        bind:value={localProblem.minimum_liquidity}
        class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
      />
      <div class="flex justify-between text-[10px] text-slate-500">
        <span>10% Floor</span>
        <span>25% (Standard)</span>
        <span>60% (Crunch)</span>
      </div>
    </div>

  </div>

  <!-- Asset Universe Editor Table -->
  <div class="glass-panel rounded-3xl overflow-hidden p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-base font-bold text-white">Investment Asset Universe</h2>
        <p class="text-xs text-slate-400">Configure eligible investment vehicles, ticket sizes, returns, and risk profiles</p>
      </div>

      <button
        on:click={addAsset}
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all"
      >
        <Plus class="w-4 h-4" />
        <span>Add Asset</span>
      </button>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left text-xs">
        <thead>
          <tr class="text-slate-400 font-semibold border-b border-slate-800">
            <th class="pb-3">Asset Name</th>
            <th class="pb-3">Cost (₹ Cr)</th>
            <th class="pb-3">Exp Return (%)</th>
            <th class="pb-3">Risk Index (0-1)</th>
            <th class="pb-3">Liquidity (0-1)</th>
            <th class="pb-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60 font-medium">
          {#each localProblem.assets as asset, idx}
            <tr>
              <td class="py-3 pr-4">
                <input 
                  type="text" 
                  bind:value={asset.name}
                  class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white font-semibold text-xs focus:outline-none focus:border-indigo-500"
                />
              </td>
              <td class="py-3 pr-4">
                <input 
                  type="number" 
                  step="5" 
                  min="5" 
                  max="100" 
                  bind:value={asset.cost}
                  class="w-24 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200 font-mono text-xs focus:outline-none focus:border-indigo-500"
                />
              </td>
              <td class="py-3 pr-4">
                <input 
                  type="number" 
                  step="0.01" 
                  min="0.01" 
                  max="0.50" 
                  bind:value={asset.expected_return}
                  class="w-24 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-emerald-400 font-mono text-xs focus:outline-none focus:border-indigo-500"
                />
              </td>
              <td class="py-3 pr-4">
                <input 
                  type="number" 
                  step="0.05" 
                  min="0.01" 
                  max="1.0" 
                  bind:value={asset.risk}
                  class="w-24 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-rose-400 font-mono text-xs focus:outline-none focus:border-indigo-500"
                />
              </td>
              <td class="py-3 pr-4">
                <input 
                  type="number" 
                  step="0.05" 
                  min="0.1" 
                  max="1.0" 
                  bind:value={asset.liquidity}
                  class="w-24 bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-cyan-300 font-mono text-xs focus:outline-none focus:border-indigo-500"
                />
              </td>
              <td class="py-3 text-right">
                <button
                  on:click={() => removeAsset(idx)}
                  disabled={localProblem.assets.length <= 2}
                  class="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors disabled:opacity-30"
                  title="Remove asset"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  </div>

</div>
