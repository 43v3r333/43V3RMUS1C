// ===============================================
// 43V3R CORE - Design System Tokens
// ===============================================

export const tokens = {
  colors: {
    // Primary palette
    primary: {
      DEFAULT: 'hsl(var(--primary))',
      foreground: 'hsl(var(--primary-foreground))',
    },
    // Neutral palette
    background: 'hsl(var(--background))',
    foreground: 'hsl(var(--foreground))',
    border: 'hsl(var(--border))',
    input: 'hsl(var(--input))',
    ring: 'hsl(var(--ring))',
    // Semantic colors
    destructive: {
      DEFAULT: 'hsl(var(--destructive))',
      foreground: 'hsl(var(--destructive-foreground))',
    },
    success: {
      DEFAULT: '142 76% 36%',
      foreground: '0 0%98%',
    },
    warning: {
      DEFAULT: '38 92% 50%',
      foreground: '0 0%98%',
    },
    info: {
      DEFAULT: '199 89% 48%',
      foreground: '0 0%98%',
    },
    muted: {
      DEFAULT: 'hsl(var(--muted))',
      foreground: 'hsl(var(--muted-foreground))',
    },
    accent: {
      DEFAULT: 'hsl(var(--accent))',
      foreground: 'hsl(var(--accent-foreground))',
    },
  },
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],
      sm: ['0.875rem', { lineHeight: '1.25rem' }],
      base: ['1rem', { lineHeight: '1.5rem' }],
      lg: ['1.125rem', { lineHeight: '1.75rem' }],
      xl: ['1.25rem', { lineHeight: '1.75rem' }],
      '2xl': ['1.5rem', { lineHeight: '2rem' }],
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
    },
  },
  spacing: {
    px: '1px',
    0: '0',
    1: '0.25rem',
    2: '0.5rem',
    3: '0.75rem',
    4: '1rem',
    5: '1.25rem',
    6: '1.5rem',
    8: '2rem',
    10: '2.5rem',
    12: '3rem',
    16: '4rem',
    20: '5rem',
  },
  borderRadius: {
    none: '0',
    sm: '0.25rem',
    DEFAULT: '0.5rem',
    md: 'calc(var(--radius) - 2px)',
    lg: 'var(--radius)',
    xl: 'calc(var(--radius) - 2px)',
    full: '9999px',
  },
  transition: {
    duration: {
      DEFAULT: '150ms',
      fast: '100ms',
      slow: '300ms',
    },
    easing: {
      DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
    },
  },
} as const

export type Tokens = typeof tokens