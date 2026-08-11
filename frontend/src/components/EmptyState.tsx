import { type ReactNode } from "react";
import Button from "./Button";

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-12 px-4">
      {icon && (
        <div className="mb-4 text-neutral-400" aria-hidden="true">
          {icon}
        </div>
      )}

      <h3 className="text-lg font-semibold text-neutral-900">{title}</h3>

      {description && (
        <p className="mt-1 text-sm text-neutral-500 max-w-sm">{description}</p>
      )}

      {actionLabel && onAction && (
        <Button className="mt-4" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}