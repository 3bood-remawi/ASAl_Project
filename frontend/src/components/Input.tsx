import { forwardRef, useId, type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  helperText?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { label, helperText, error, disabled, className = "", id, ...rest },
    ref
  ) => {
    const generatedId = useId();
    const inputId = id || generatedId;
    const helperId = `${inputId}-helper`;
    const errorId = `${inputId}-error`;

    return (
      <div className="flex flex-col gap-1.5">
        <label
          htmlFor={inputId}
          className="text-sm font-medium text-neutral-700"
        >
          {label}
        </label>

        <input
          ref={ref}
          id={inputId}
          disabled={disabled}
          aria-invalid={!!error}
          aria-describedby={error ? errorId : helperText ? helperId : undefined}
          className={`
            w-full rounded-md border px-3 py-2 text-sm font-sans
            transition-colors
            focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-1
            disabled:cursor-not-allowed disabled:bg-neutral-50 disabled:text-neutral-400
            ${
              error
                ? "border-danger-500 focus-visible:ring-danger-500"
                : "border-neutral-300 focus-visible:ring-primary-500"
            }
            ${className}
          `}
          {...rest}
        />

        {error && (
          <p id={errorId} className="text-xs text-danger-600">
            {error}
          </p>
        )}

        {!error && helperText && (
          <p id={helperId} className="text-xs text-neutral-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;