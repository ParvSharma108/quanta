<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { onMount } from 'svelte';
  import { token, user, logout, me, loginAsDemo } from '$lib/auth';
  import { isAdmin } from '$lib/roles';
  import type { LayoutProps } from './$types';

  let { children }: LayoutProps = $props();

  onMount(async () => {
    if ($token && !$user) {
      try {
        await me();
      } catch {
        // preserve offline demo mode
      }
    }
  });

  $effect(() => {
    if (!browser) return;
    const pathname = page.url.pathname;
    const isPublic = pathname === '/login' || pathname === '/register';

    if (!$token && !isPublic) {
      // Auto-initialize demo session if landing directly for rapid evaluation
      loginAsDemo('analyst');
    } else if ($token && isPublic) {
      goto('/');
    } else if ($token && pathname.startsWith('/admin') && $user && !isAdmin($user.role)) {
      goto('/');
    }
  });
</script>

<svelte:head>
  <title>QUANTA - Autonomous Treasury & Quantum Capital Optimization</title>
</svelte:head>

<div class="app-layout">
  {#if $token && $user}
    <header class="navbar glass-panel">
      <div class="navbar-left">
        <a href="/" class="brand-group">
          <div class="atom-icon-wrap">
            <span class="atom-icon">⚛</span>
          </div>
          <div class="brand-text-wrap">
            <span class="brand-title gradient-text">QUANTA</span>
            <span class="brand-sub">Autonomous Treasury</span>
          </div>
        </a>

        <nav class="nav-links">
          <a href="/" class="nav-link" class:active={page.url.pathname === '/'}>
            <span>Cockpit</span>
          </a>
          <a href="/treasuries" class="nav-link" class:active={page.url.pathname.startsWith('/treasuries')}>
            <span>Treasuries</span>
          </a>
          {#if isAdmin($user.role)}
            <a href="/admin/users" class="nav-link" class:active={page.url.pathname.startsWith('/admin/users')}>
              <span>Users</span>
            </a>
            <a href="/admin/audit-logs" class="nav-link" class:active={page.url.pathname.startsWith('/admin/audit-logs')}>
              <span>Audit Logs</span>
            </a>
          {/if}
        </nav>
      </div>

      <div class="navbar-right">
        <div class="user-chip">
          <span class="user-email">{$user.email}</span>
          <span class="badge badge-{$user.role}">{$user.role}</span>
        </div>
        <button type="button" class="btn btn-secondary btn-sm" onclick={logout}>
          Sign Out
        </button>
      </div>
    </header>
  {/if}

  <main class="main-content" class:auth-mode={!$token || page.url.pathname === '/login' || page.url.pathname === '/register'}>
    {@render children()}
  </main>
</div>

<style>
  .app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(11, 15, 25, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 0.75rem 1.75rem;
    position: sticky;
    top: 0;
    z-index: 50;
  }

  .navbar-left {
    display: flex;
    align-items: center;
    gap: 2.25rem;
  }

  .brand-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    text-decoration: none;
  }

  .atom-icon-wrap {
    width: 34px;
    height: 34px;
    border-radius: 9px;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(56, 189, 248, 0.2) 100%);
    border: 1px solid rgba(99, 102, 241, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
  }

  .atom-icon {
    font-size: 1.15rem;
    color: #818cf8;
    line-height: 1;
  }

  .brand-text-wrap {
    display: flex;
    flex-direction: column;
  }

  .brand-title {
    font-size: 1.15rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    line-height: 1.1;
  }

  .brand-sub {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #64748b;
    font-weight: 600;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .nav-link {
    font-size: 0.85rem;
    font-weight: 600;
    color: #94a3b8;
    text-decoration: none;
    padding: 0.4rem 0.85rem;
    border-radius: 8px;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .nav-link:hover {
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.05);
    text-decoration: none;
  }

  .nav-link.active {
    color: #ffffff;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.75) 0%, rgba(79, 70, 229, 0.75) 100%);
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
  }

  .navbar-right {
    display: flex;
    align-items: center;
    gap: 1.25rem;
  }

  .user-chip {
    display: flex;
    align-items: center;
    gap: 0.625rem;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 0.35rem 0.75rem;
    border-radius: 9999px;
  }

  .user-email {
    font-size: 0.8rem;
    color: #cbd5e1;
    font-family: var(--font-mono);
  }

  .btn-sm {
    padding: 0.4rem 0.85rem;
    font-size: 0.8rem;
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .main-content.auth-mode {
    align-items: center;
    justify-content: center;
    padding: 2rem 1rem;
  }
</style>
