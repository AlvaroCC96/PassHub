interface FavoriteBadgeProps {
  active: boolean;
  onClick?: () => void;
  disabled?: boolean;
}

/** A star toggle. When `active`, the vehicle is the user's single favorite —
 * clicking a non-active badge requests making it the favorite (the backend
 * unsets whichever vehicle was favorite before). */
export function FavoriteBadge({ active, onClick, disabled }: FavoriteBadgeProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || active}
      aria-label={active ? "Favorite vehicle" : "Mark as favorite"}
      aria-pressed={active}
      className={`text-lg leading-none transition-colors disabled:cursor-default ${
        active ? "text-amber-500" : "text-slate-300 hover:text-amber-400 dark:text-slate-600"
      }`}
    >
      {active ? "★" : "☆"}
    </button>
  );
}
