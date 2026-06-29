import { VehicleStatus } from "@passhub/shared";

const STYLES: Record<VehicleStatus, string> = {
  [VehicleStatus.Active]: "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400",
  [VehicleStatus.Inactive]: "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  [VehicleStatus.Archived]: "bg-slate-200 text-slate-500 dark:bg-slate-800 dark:text-slate-500",
};

const LABELS: Record<VehicleStatus, string> = {
  [VehicleStatus.Active]: "Active",
  [VehicleStatus.Inactive]: "Inactive",
  [VehicleStatus.Archived]: "Archived",
};

export function VehicleStatusBadge({ status }: { status: VehicleStatus }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[status]}`}>
      {LABELS[status]}
    </span>
  );
}
