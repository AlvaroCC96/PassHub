/** Maps the backend's `icon` string (a plain keyword, not an asset path) to
 * a glyph. Swap this for a real icon set in a later sprint — kept to emoji
 * for now so Platform Core doesn't pull in an icon library dependency. */
const MODULE_ICONS: Record<string, string> = {
  car: "🚗",
  home: "🏠",
  paw: "🐾",
  heart: "❤️",
  users: "👥",
};

export function getModuleIcon(icon: string): string {
  return MODULE_ICONS[icon] ?? "✨";
}
