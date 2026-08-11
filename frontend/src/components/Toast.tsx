"use client";

import { useEffect } from "react";

export type ToastVariant = "success" | "error";

interface ToastProps {
  id: string;
  message: string;
  variant: ToastVariant;
  onDismiss: (id: string) => void;
  duration?: number;
}

const variantStyles: Record<ToastVariant, string> = {
  success: "bg-success-50 border-success-200 text-success-800",
  error: "bg-danger-50 border-danger-200 text-danger-800",
};

export default function Toast({
  id,
  message,
  variant,
  onDismiss,
  duration = 4000,
}: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(id);
    }, duration);

    return () => clearTimeout(timer);
  }, [id, duration, onDismiss]);

  return (
    <div
      role="status"
      aria-live="polite"
      className={`
        flex items-center justify-between gap-3
        rounded-md border px-4 py-3 text-sm shadow-md
        ${variantStyles[variant]}
      `}
    >
      <span>{message}</span>
      <button
        onClick={() => onDismiss(id)}
        aria-label="Dismiss notification"
        className="text-current opacity-70 hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1 focus-visible:ring-current rounded"
      >
        ✕
      </button>
    </div>
  );
}