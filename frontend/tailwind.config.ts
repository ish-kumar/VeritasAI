import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Sophisticated dark theme inspired by 21st.dev
        background: '#08080c',
        surface: '#0f0f14',
        border: '#1e1e28',
        
        // Shadcn/ui compatible tokens (for imported components)
        input: '#1e1e28',
        'muted-foreground': '#64647c',
        foreground: '#fafaff',
        
        // Shadcn primary (blue accent for our legal theme)
        primary: '#3b82f6',
        'primary-foreground': '#ffffff',
        
        // Shadcn destructive (red/rose for errors/destructive actions)
        destructive: '#f43f5e',
        'destructive-foreground': '#ffffff',
        
        // Shadcn accent (subtle hover states)
        accent: '#1e1e28',
        'accent-foreground': '#fafaff',
        
        // Shadcn ring (focus rings)
        ring: '#3b82f6',
        
        // Shadcn popover (dropdowns, menus)
        popover: '#0f0f14',
        'popover-foreground': '#fafaff',
        
        // Legacy support (for gradual migration)
        'dark-bg': '#08080c',
        'dark-card': '#0f0f14',
        'dark-border': '#1e1e28',
        
        // Text hierarchy
        'text-primary': '#fafaff',
        'text-secondary': '#a0a0b4',
        'text-muted': '#64647c',
        secondary: '#a0a0b4',
        muted: '#64647c',
        
        // Accent colors (modern palette)
        'accent-blue': '#3b82f6',
        'accent-purple': '#8b5cf6',
        'accent-emerald': '#34d399',
        'accent-amber': '#fbbf24',
        'accent-rose': '#f43f5e',
      },
      fontFamily: {
        sans: ['var(--font-plus-jakarta)', 'system-ui', 'sans-serif'],
        display: ['var(--font-space-grotesk)', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      animation: {
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'spin-slow': 'spin 3s linear infinite',
        'fade-in': 'fadeIn 0.6s ease-out forwards',
        'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
      },
      keyframes: {
        'gradient-shift': {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
};

export default config;
