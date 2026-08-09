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
        background: "var(--background)",
        foreground: "var(--foreground)",
        ...colors,
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
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