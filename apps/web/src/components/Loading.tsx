import { Spinner } from "@passhub/ui";

export function Loading() {
  return (
    <div className="flex h-full w-full items-center justify-center py-16">
      <Spinner size="lg" />
    </div>
  );
}
