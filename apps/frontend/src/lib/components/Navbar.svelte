<script lang="ts">
  import { 
    Activity, 
    Cpu, 
    Atom, 
    Bot, 
    Sliders, 
    Layers
  } from 'lucide-svelte';

  export let activeTab: string = 'dashboard';
  export let onTabChange: (tab: string) => void;

  const navigation = [
    { id: 'dashboard', label: 'Treasury Overview', icon: Activity, badge: 'Live' },
    { id: 'quantum', label: 'Quantum QAOA Lab', icon: Atom, badge: '20 Qubits' },
    { id: 'solvers', label: 'Classical Benchmark', icon: Cpu, badge: '5 Solvers' },
    { id: 'ai-agents', label: 'AI Deliberation Council', icon: Bot, badge: 'Multi-Agent' },
    { id: 'config', label: 'Balance Sheet Editor', icon: Sliders, badge: 'Config' },
    { id: 'benchmarks', label: 'Empirical Results', icon: Layers, badge: 'Charts' }
  ];
</script>

<header class="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex items-center justify-between h-16">
      
      <!-- Brand Logo -->
      <button 
        type="button"
        class="flex items-center gap-3 cursor-pointer text-left focus:outline-none" 
        on:click={() => onTabChange('dashboard')}
      >
        <div class="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-600 to-purple-600 shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
          <Atom class="w-6 h-6 text-white animate-spin-slow" />
          <div class="absolute inset-0 rounded-xl bg-white/20 blur-[1px]"></div>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xl font-extrabold tracking-tight text-white">QUANTA</span>
            <span class="px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              v2.0
            </span>
          </div>
          <p class="text-[11px] font-medium text-slate-400">Autonomous Financial Treasury & Quantum Capital Optimization</p>
        </div>
      </button>

      <!-- Navigation Tabs -->
      <nav class="hidden md:flex items-center gap-1 bg-slate-900/60 p-1.5 rounded-2xl border border-slate-800">
        {#each navigation as item}
          <button
            type="button"
            on:click={() => onTabChange(item.id)}
            class={`relative flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
              activeTab === item.id
                ? 'bg-gradient-to-r from-indigo-600 to-indigo-500 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <svelte:component this={item.icon} class="w-4 h-4" />
            <span>{item.label}</span>
            {#if item.badge && activeTab !== item.id}
              <span class="text-[9px] px-1.5 py-0.2 rounded-md bg-slate-800 text-slate-400 font-mono">
                {item.badge}
              </span>
            {/if}
          </button>
        {/each}
      </nav>

      <!-- System Health Indicator -->
      <div class="flex items-center gap-3">
        <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Engines Active</span>
        </div>
        
        <a 
          href="https://github.com/ParvSharma108/quanta" 
          target="_blank" 
          rel="noopener noreferrer"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 text-xs font-medium transition-colors"
        >
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
          <span class="hidden sm:inline">GitHub</span>
        </a>
      </div>

    </div>
  </div>

  <!-- Mobile Navigation Bar -->
  <div class="md:hidden flex overflow-x-auto gap-1 p-2 bg-slate-900 border-t border-slate-800 scrollbar-none">
    {#each navigation as item}
      <button
        type="button"
        on:click={() => onTabChange(item.id)}
        class={`whitespace-nowrap flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold ${
          activeTab === item.id ? 'bg-indigo-600 text-white' : 'text-slate-400 bg-slate-950'
        }`}
      >
        <svelte:component this={item.icon} class="w-3.5 h-3.5" />
        <span>{item.label}</span>
      </button>
    {/each}
  </div>
</header>

<style>
  @keyframes spin-slow {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  .animate-spin-slow {
    animation: spin-slow 20s linear infinite;
  }
</style>
