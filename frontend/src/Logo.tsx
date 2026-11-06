export default function Logo({ size = 34 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true">
      <defs>
        <linearGradient id="logo-gradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#ff5d8f" />
          <stop offset="1" stopColor="#ffb020" />
        </linearGradient>
      </defs>
      <rect x="4" y="4" width="20" height="20" rx="6" fill="url(#logo-gradient)" opacity=".45" />
      <rect x="10" y="10" width="20" height="20" rx="6" fill="url(#logo-gradient)" opacity=".75" />
      <rect x="16" y="16" width="20" height="20" rx="6" fill="url(#logo-gradient)" />
    </svg>
  );
}
