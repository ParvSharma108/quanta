export function isAdmin(role?: string | null): boolean {
  return role === 'admin';
}

export function canWrite(role?: string | null): boolean {
  return role === 'admin' || role === 'analyst';
}

export function isViewer(role?: string | null): boolean {
  return role === 'viewer';
}
