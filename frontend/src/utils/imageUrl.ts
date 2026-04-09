/**
 * Resolve image URLs for both web and native platforms.
 * - Relative URLs like /api/uploads/xxx.jpg → absolute using backend URL
 * - data: URIs → pass through
 * - http(s) URLs → pass through
 * - empty/null → return undefined
 */

const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || '';

export function resolveImageUrl(url: string | null | undefined): string | undefined {
  if (!url || url.trim() === '') return undefined;
  
  // Already absolute or data URI
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }
  
  // Relative URL like /api/uploads/xxx.jpg
  if (url.startsWith('/')) {
    return `${API_URL}${url}`;
  }
  
  return url;
}
