import { Button } from "@passhub/ui";

export function LoginPage() {
  return (
    <form className="flex flex-col gap-4">
      <h1 className="text-xl font-semibold">Sign in</h1>
      <label className="flex flex-col gap-1 text-sm">
        Email
        <input
          type="email"
          name="email"
          className="rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        Password
        <input
          type="password"
          name="password"
          className="rounded-md border border-slate-300 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800"
        />
      </label>
      <Button type="submit">Sign in</Button>
    </form>
  );
}
