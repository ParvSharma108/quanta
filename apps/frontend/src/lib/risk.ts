export function parseAllocations(raw: any): Record<string, number> {
  if (!raw) return {};
  if (typeof raw === 'object') return raw;
  try {
    return JSON.parse(raw);
  } catch {
    return {};
  }
}

export function extractAllocations(raw: any): Array<{ name: string; amount: number; percentage: number }> {
  const parsed = parseAllocations(raw);
  const total = Object.values(parsed).reduce((acc, v) => acc + (typeof v === 'number' ? v : 0), 0) || 1;
  
  return Object.entries(parsed).map(([key, val]) => {
    const amount = typeof val === 'number' ? val : 0;
    return {
      name: key,
      amount,
      percentage: (amount / total) * 100
    };
  });
}

export function calculateLiquidityFloor(treasury: { total_capital?: number; min_liquidity_ratio?: number } | null | undefined): number {
  if (!treasury || !treasury.total_capital) return 0;
  const ratio = treasury.min_liquidity_ratio ?? 0.20;
  return treasury.total_capital * ratio;
}

export function formatBayesianEvidence(evidence: { feature?: string; likelihood_ratio?: number; interpretation?: string } | null | undefined): string {
  if (!evidence) return '';
  if (evidence.interpretation) return evidence.interpretation;
  return `${evidence.feature || 'Risk Factor'}: ${evidence.likelihood_ratio ? evidence.likelihood_ratio.toFixed(2) + 'x' : 'Observed'}`;
}

export function getRiskTierClass(tier: string | undefined | null): string {
  switch ((tier || '').toLowerCase()) {
    case 'low':
      return 'badge-low';
    case 'medium':
      return 'badge-medium';
    case 'high':
      return 'badge-high';
    case 'critical':
      return 'badge-critical';
    default:
      return 'badge-default';
  }
}

export function formatTreasuryAction(action: string | undefined | null): string {
  if (!action) return '';
  return action
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}
