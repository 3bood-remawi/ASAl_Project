import { type HTMLAttributes } from "react";

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circle" | "rectangle";
}

const variantStyles: Record<NonNullable<SkeletonProps["variant"]>, string> = {
  text: "rounded h-4 w-full",
  circle: "rounded-full h-10 w-10",
  rectangle: "rounded-md h-24 w-full",
};

export default function Skeleton({
  variant = "text",
  className = "",
  ...rest
}: SkeletonProps) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={`
        animate-pulse bg-neutral-200
        ${variantStyles[variant]}
        ${className}
      `}
      {...rest}
    />
  );
}