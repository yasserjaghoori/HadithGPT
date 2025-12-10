import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#e6f7f0",
          100: "#ccefe1",
          200: "#99dfc3",
          300: "#66cfa5",
          400: "#33bf87",
          500: "#00916e",  // Main Islamic green
          600: "#007458",
          700: "#005742",
          800: "#003a2c",
          900: "#001d16",
        },
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
    },
  },
  plugins: [],
};
export default config;
