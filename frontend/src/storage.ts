// Small per-browser conveniences. Everything is wrapped because storage can be blocked.

export function load<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    return fallback;
  }
}

export function save(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage unavailable, nothing to do */
  }
}

const RECENT_KEY = "sortify-recent-folders";

export const recentFolders = (): string[] => load<string[]>(RECENT_KEY, []);

export function rememberFolder(path: string) {
  save(RECENT_KEY, [path, ...recentFolders().filter((p) => p !== path)].slice(0, 4));
}
