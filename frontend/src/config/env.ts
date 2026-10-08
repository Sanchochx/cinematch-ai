const DEFAULT_API_URL = 'http://localhost:3000';

export function resolveApiUrl(raw: string | undefined): string {
  const value = raw?.trim();
  return (value || DEFAULT_API_URL).replace(/\/+$/, '');
}

export const API_URL: string = resolveApiUrl(import.meta.env.VITE_API_URL);
