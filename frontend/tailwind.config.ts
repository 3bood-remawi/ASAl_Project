import type { Config } from "tailwindcss";
import { colors, radius } from "./src/theme/tokens";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Flat tokens straight from the CSS custom properties in globals.css.
        // Wrapped in hsl() here because the variables themselves store bare
        // "H S% L%" triples (e.g. --background: 240 33% 97%), which is only
        // valid inside hsl(...) - not as a standalone color value.
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        brand: {
          DEFAULT: "hsl(var(--brand))",
          foreground: "hsl(var(--brand-foreground))",
        },
        destructive: "hsl(var(--destructive))",
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        sidebar: {
          DEFAULT: "hsl(var(--sidebar))",
          foreground: "hsl(var(--sidebar-foreground))",
          border: "hsl(var(--sidebar-border))",
        },

        // These three names are shared with the numeric 50-900 scales below
        // (used by Button/Card/Input/etc via e.g. bg-primary-600). Tailwind
        // lets a color key mix numbered shades with a DEFAULT/foreground
        // pair, so both bg-primary-600 and bare bg-primary now resolve.
        primary: {
          ...colors.primary,
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        success: {
          ...colors.success,
          DEFAULT: "hsl(var(--success))",
        },
        warning: {
          ...colors.warning,
          DEFAULT: "hsl(var(--warning))",
        },

        neutral: colors.neutral,
        danger: colors.danger,
      },
      fontFamily: {
        sans: [
          "var(--font-inter)",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: [
          "var(--font-geist-mono)",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Consolas",
          "monospace",
        ],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1rem" }],      
        sm: ["0.875rem", { lineHeight: "1.25rem" }],  
        base: ["1rem", { lineHeight: "1.5rem" }],      
        lg: ["1.125rem", { lineHeight: "1.75rem" }],   
        xl: ["1.25rem", { lineHeight: "1.75rem" }],    
        "2xl": ["1.5rem", { lineHeight: "2rem" }],     
        "3xl": ["1.875rem", { lineHeight: "2.25rem" }],
      },
      spacing: {
        18: "4.5rem",
        88: "22rem", 
      },
      borderRadius: radius,
    },
  },
  plugins: [],
};
export default config;