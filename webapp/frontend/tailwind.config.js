/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Dark theme color palette
        background: {
          DEFAULT: '#0a0a0a',
          secondary: '#111111',
          tertiary: '#1a1a1a',
        },
        foreground: {
          DEFAULT: '#ffffff',
          secondary: '#a3a3a3',
          tertiary: '#737373',
        },
        border: {
          DEFAULT: '#262626',
          secondary: '#404040',
          accent: '#fbbf24', // Gold accent
        },
        card: {
          DEFAULT: '#111111',
          secondary: '#1a1a1a',
          accent: '#262626',
        },
        primary: {
          DEFAULT: '#fbbf24', // Gold
          foreground: '#0a0a0a',
        },
        secondary: {
          DEFAULT: '#404040',
          foreground: '#ffffff',
        },
        accent: {
          DEFAULT: '#fbbf24', // Gold
          foreground: '#0a0a0a',
        },
        destructive: {
          DEFAULT: '#dc2626',
          foreground: '#ffffff',
        },
        muted: {
          DEFAULT: '#262626',
          foreground: '#a3a3a3',
        },
        popover: {
          DEFAULT: '#111111',
          foreground: '#ffffff',
        },
        input: {
          DEFAULT: '#262626',
          border: '#404040',
        },
        ring: {
          DEFAULT: '#fbbf24',
        },
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-subtle': 'bounceSubtle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
      boxShadow: {
        'glow': '0 0 20px rgba(251, 191, 36, 0.3)',
        'glow-sm': '0 0 10px rgba(251, 191, 36, 0.2)',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
