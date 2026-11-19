<script lang="ts">
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { login, loginAsDemo } from '$lib/auth';
  import { ApiError } from '$lib/api';

  let email = $state('');
  let password = $state('');
  let isLoading = $state(false);
  let formError = $state<string | null>(null);
  let fieldErrors = $state<{ email?: string; password?: string }>({});

  const isJustRegistered = $derived(page.url.searchParams.get('registered') === '1');

  function validate(): boolean {
    const errors: { email?: string; password?: string } = {};
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email.trim()) {
      errors.email = 'Email address is required.';
    } else if (!emailPattern.test(email.trim())) {
      errors.email = 'Enter a valid email address.';
    }

    if (!password) {
      errors.password = 'Password is required.';
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters.';
    }

    fieldErrors = errors;
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    formError = null;

    if (!validate()) {
      return;
    }

    isLoading = true;

    try {
      await login(email.trim(), password);
      await goto('/');
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          formError = 'Invalid credentials. Please check your email and password.';
        } else if (err.details && err.details.length > 0) {
          formError = err.details.join(', ');
        } else {
          formError = err.message || 'Authentication failed.';
        }
      } else if (err instanceof Error) {
        formError = err.message;
      } else {
        formError = 'An unexpected error occurred.';
      }
    } finally {
      isLoading = false;
    }
  }

  function handleQuickDemo(role: 'admin' | 'analyst') {
    loginAsDemo(role);
  }
</script>

<div class="auth-card card glass-panel quantum-glow">
  <div class="auth-header">
    <div class="brand-badge">
      <span class="brand-icon">⚛</span>
      <span class="gradient-text font-bold text-xl tracking-wider">QUANTA</span>
    </div>
    <h1 class="auth-title">Autonomous Treasury Portal</h1>
    <p class="auth-subtitle">AI-Driven Balance Sheet Optimization & Quantum Solvers</p>
  </div>

  {#if isJustRegistered}
    <div class="alert alert-success">
      Registration successful. Please sign in with your credentials.
    </div>
  {/if}

  {#if formError}
    <div class="alert alert-danger">
      {formError}
    </div>
  {/if}

  <form onsubmit={handleSubmit} novalidate>
    <div class="form-group">
      <label for="email" class="form-label">Email Address</label>
      <input
        id="email"
        type="email"
        class="form-input"
        class:has-error={!!fieldErrors.email}
        placeholder="quant@organization.com"
        bind:value={email}
        disabled={isLoading}
        autocomplete="email"
      />
      {#if fieldErrors.email}
        <p class="field-error">{fieldErrors.email}</p>
      {/if}
    </div>

    <div class="form-group">
      <label for="password" class="form-label">Password</label>
      <input
        id="password"
        type="password"
        class="form-input"
        class:has-error={!!fieldErrors.password}
        placeholder="••••••••"
        bind:value={password}
        disabled={isLoading}
        autocomplete="current-password"
      />
      {#if fieldErrors.password}
        <p class="field-error">{fieldErrors.password}</p>
      {/if}
    </div>

    <div class="form-actions">
      <button type="submit" class="btn btn-primary btn-block w-full" disabled={isLoading}>
        {isLoading ? 'Authenticating...' : 'Sign In'}
      </button>
    </div>
  </form>

  <div class="quick-demo-section">
    <div class="divider">
      <span>OR INSTANT SANDBOX</span>
    </div>
    <div class="demo-buttons">
      <button type="button" class="btn btn-secondary w-full" onclick={() => handleQuickDemo('analyst')}>
        ⚡ Launch as Treasury Quant
      </button>
      <button type="button" class="btn btn-secondary w-full mt-2" onclick={() => handleQuickDemo('admin')}>
        🛡️ Launch as Risk Admin
      </button>
    </div>
  </div>

  <div class="auth-footer">
    <span>Need an account?</span>
    <a href="/register">Register new organization</a>
  </div>
</div>

<style>
  .auth-card {
    width: 100%;
    max-width: 440px;
    margin: 2rem auto;
    padding: 2.25rem;
    border-radius: 16px;
  }

  .auth-header {
    text-align: center;
    margin-bottom: 1.75rem;
  }

  .brand-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.85rem;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 9999px;
    margin-bottom: 1rem;
  }

  .brand-icon {
    font-size: 1.25rem;
    color: #818cf8;
  }

  .auth-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.35rem;
  }

  .auth-subtitle {
    font-size: 0.825rem;
    color: var(--color-text-muted);
    line-height: 1.4;
  }

  .form-actions {
    margin-top: 1.25rem;
  }

  .field-error {
    color: var(--color-danger);
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }

  .quick-demo-section {
    margin-top: 1.5rem;
    margin-bottom: 1.25rem;
  }

  .divider {
    text-align: center;
    position: relative;
    margin-bottom: 1rem;
  }

  .divider::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    height: 1px;
    background: var(--color-border);
  }

  .divider span {
    position: relative;
    background: #111827;
    padding: 0 0.75rem;
    font-size: 0.675rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--color-text-muted);
  }

  .auth-footer {
    text-align: center;
    font-size: 0.825rem;
    color: var(--color-text-muted);
    border-top: 1px solid var(--color-border);
    padding-top: 1.25rem;
    display: flex;
    justify-content: center;
    gap: 0.375rem;
  }
</style>
