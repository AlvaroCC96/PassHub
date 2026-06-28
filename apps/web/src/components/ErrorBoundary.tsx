import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Unhandled UI error", error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex h-full w-full flex-col items-center justify-center gap-2 py-16 text-center">
          <p className="text-lg font-semibold">Something went wrong.</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">{this.state.error.message}</p>
        </div>
      );
    }
    return this.props.children;
  }
}
