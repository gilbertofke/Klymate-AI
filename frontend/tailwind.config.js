/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        // Klymate AI Primary Colors - Green to Blue Gradient
        primary: {
          gradient: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
          green: '#10B981',
          blue: '#3B82F6',
          greenLight: '#34D399',
          blueLight: '#60A5FA',
          greenDark: '#059669',
          blueDark: '#2563EB',
        },
        // Secondary Gray Scale
        secondary: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
        // Status Colors
        status: {
          success: '#10B981',
          warning: '#F59E0B',
          error: '#EF4444',
          info: '#3B82F6',
        },
        // Background Colors
        background: {
          primary: '#FFFFFF',
          secondary: '#F9FAFB',
          tertiary: '#F3F4F6',
          gradient: 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
        },
        // Text Colors
        text: {
          primary: '#111827',
          secondary: '#4B5563',
          tertiary: '#6B7280',
          muted: '#9CA3AF',
          white: '#FFFFFF',
        },
        // Border Colors
        border: {
          light: '#E5E7EB',
          medium: '#D1D5DB',
          dark: '#9CA3AF',
        }
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
        'gradient-button': 'linear-gradient(135deg, #10B981 0%, #3B82F6 100%)',
        'gradient-card': 'linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%)',
        'gradient-hero': 'linear-gradient(135deg, #10B981 0%, #34D399 25%, #60A5FA 75%, #3B82F6 100%)',
      },
      boxShadow: {
        'gradient': '0 4px 20px rgba(16, 185, 129, 0.15)',
        'card': '0 1px 3px rgba(0, 0, 0, 0.1)',
        'card-hover': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'button': '0 2px 4px rgba(16, 185, 129, 0.2)',
        'button-hover': '0 4px 8px rgba(16, 185, 129, 0.3)',
      },
      borderRadius: {
        'card': '12px',
        'button': '8px',
        'badge': '20px',
        'input': '6px',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
        'bounce-slow': 'bounce 2s infinite',
        'gradient': 'gradient 6s ease infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
      backgroundSize: {
        'gradient-animated': '200% 200%',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}