export function formatCurrency(amount: number | undefined | null, currency: string = 'INR'): string {
  if (amount === undefined || amount === null || isNaN(amount)) return '₹0';
  
  if (currency.toUpperCase() === 'INR') {
    if (Math.abs(amount) >= 1e7) {
      return `₹${(amount / 1e7).toFixed(2)} Cr`;
    }
    if (Math.abs(amount) >= 1e5) {
      return `₹${(amount / 1e5).toFixed(2)} L`;
    }
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0
  }).format(amount);
}

export function formatNumber(value: number | undefined | null, decimals: number = 2): string {
  if (value === undefined || value === null || isNaN(value)) return '0';
  return Number(value).toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
}

export function formatPercent(value: number | undefined | null, decimals: number = 2): string {
  if (value === undefined || value === null || isNaN(value)) return '0.00%';
  const num = Number(value);
  const formatted = num <= 1 && num >= -1 ? num * 100 : num;
  return `${formatted.toFixed(decimals)}%`;
}

export function formatDate(dateString: string | undefined | null): string {
  if (!dateString) return '—';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(d);
  } catch {
    return dateString;
  }
}
