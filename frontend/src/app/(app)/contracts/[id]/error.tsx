"use client";

interface ContractDetailErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function ContractDetailError({ error, reset }: ContractDetailErrorProps) {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <h1 className="text-xl font-semibold text-gray-900">Something went wrong</h1>
      <p className="mt-2 text-gray-600">{error.message}</p>
      <button
        onClick={() => reset()}
        className="mt-4 rounded-md bg-gray-900 px-4 py-2 text-sm text-white"
      >
        Try again
      </button>
    </div>
  );
}