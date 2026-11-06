import type { ReactNode, SVGProps } from "react";

// Sortify's own icon set: 24px grid, rounded 2px strokes and a soft two-tone fill (.duo).
// Each icon is drawn from these few shapes so the whole set feels like one family.

const shape = (d: string) => (
  <>
    <path className="duo" d={d} />
    <path d={d} />
  </>
);

const rect = (x: number, y: number, w: number, h: number, r: number) => (
  <>
    <rect className="duo" x={x} y={y} width={w} height={h} rx={r} />
    <rect x={x} y={y} width={w} height={h} rx={r} />
  </>
);

const circle = (cx: number, cy: number, r: number) => (
  <>
    <circle className="duo" cx={cx} cy={cy} r={r} />
    <circle cx={cx} cy={cy} r={r} />
  </>
);

const FOLDER =
  "M3.5 7A2.5 2.5 0 0 1 6 4.5h3.2c.6 0 1.2.3 1.6.8L12 7h6A2.5 2.5 0 0 1 20.5 9.5v8A2.5 2.5 0 0 1 18 20H6a2.5 2.5 0 0 1-2.5-2.5z";
const FILE = "M7 3h7l5 5v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z";

const ICONS = {
  home: (
    <>
      {shape("M4 10.5 12 4l8 6.5V19a1.5 1.5 0 0 1-1.5 1.5H15v-5.5H9v5.5H5.5A1.5 1.5 0 0 1 4 19z")}
    </>
  ),
  monitor: (
    <>
      {rect(3, 4.5, 18, 12, 2.5)}
      <path d="M8.5 20.5h7M12 16.5v4" />
    </>
  ),
  download: (
    <>
      {rect(4, 15.5, 16, 5, 2)}
      <path d="M12 3.5v9M8 9l4 4 4-4" />
    </>
  ),
  documents: (
    <>
      {shape(FILE)}
      <path d="M14 3v5h5M9 13h6M9 17h4" />
    </>
  ),
  image: (
    <>
      {rect(3.5, 4.5, 17, 15, 3)}
      <circle cx="9" cy="10" r="1.6" />
      <path d="m4.5 18 5-5 3.5 3.5 2.5-2.5 4 4" />
    </>
  ),
  folder: shape(FOLDER),
  folderMinus: (
    <>
      {shape(FOLDER)}
      <path d="M9.5 14h5" />
    </>
  ),
  chevronRight: <path d="m9 6 6 6-6 6" />,
  chevronUp: <path d="m6 15 6-6 6 6" />,
  x: <path d="M6 6l12 12M18 6 6 18" />,
  search: (
    <>
      {circle(11, 11, 6.5)}
      <path d="m20 20-4.2-4.2" />
    </>
  ),
  copy: (
    <>
      {rect(9, 9, 11.5, 11.5, 2.5)}
      <path d="M15 9V6.5A2.5 2.5 0 0 0 12.5 4h-6A2.5 2.5 0 0 0 4 6.5v6A2.5 2.5 0 0 0 6.5 15H9" />
    </>
  ),
  check: <path d="m5 12.5 4.5 4.5L19 7.5" />,
  checkCircle: (
    <>
      {circle(12, 12, 9)}
      <path d="m8 12.5 3 3 5-6" />
    </>
  ),
  undo: <path d="M8 4.5 4 8.5l4 4M4 8.5h9.5a5.5 5.5 0 0 1 0 11H9" />,
  clock: (
    <>
      {circle(12, 12, 9)}
      <path d="M12 7v5l3 2" />
    </>
  ),
  lock: (
    <>
      {rect(5, 10.5, 14, 10, 2.5)}
      <path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" />
    </>
  ),
  eye: (
    <>
      {shape("M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z")}
      <circle cx="12" cy="12" r="2.8" />
    </>
  ),
  layers: (
    <>
      {shape("M12 3.5 3.5 8 12 12.5 20.5 8z")}
      <path d="m3.5 12 8.5 4.5 8.5-4.5M3.5 16l8.5 4.5 8.5-4.5" />
    </>
  ),
  calendar: (
    <>
      {rect(3.5, 5, 17, 15.5, 3)}
      <path d="M3.5 10h17M8 3v4M16 3v4" />
    </>
  ),
  move: (
    <>
      {circle(12, 12, 9)}
      <path d="M8 12h8M13 8.5l3.5 3.5-3.5 3.5" />
    </>
  ),
  trash: (
    <>
      {shape("M6 7l.8 11.5a2 2 0 0 0 2 1.9h6.4a2 2 0 0 0 2-1.9L18 7")}
      <path d="M4 7h16M9.5 7V5a1.5 1.5 0 0 1 1.5-1.5h2A1.5 1.5 0 0 1 14.5 5v2M10 11v5M14 11v5" />
    </>
  ),
  fileX: (
    <>
      {shape(FILE)}
      <path d="M14 3v5h5M9.5 12.5l5 5m0-5-5 5" />
    </>
  ),
  arrowRight: <path d="M5 12h14M13 6l6 6-6 6" />,
  arrowLeft: <path d="M19 12H5M11 6l-6 6 6 6" />,
  sparkle: (
    <>
      {shape("M12 3.5 14 9l5.5 2L14 13l-2 5.5L10 13l-5.5-2L10 9z")}
      <path d="M19 3v3M17.5 4.5h3" />
    </>
  ),
  alert: (
    <>
      {shape("M12 4 3 19.5h18z")}
      <path d="M12 10v4.5M12 17.3v.1" />
    </>
  ),
} satisfies Record<string, ReactNode>;

export type IconName = keyof typeof ICONS;

type Props = { name: IconName; size?: number } & Omit<SVGProps<SVGSVGElement>, "name">;

export function Icon({ name, size = 22, ...rest }: Props) {
  return (
    <svg
      className="icon"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...rest}
    >
      {ICONS[name]}
    </svg>
  );
}
