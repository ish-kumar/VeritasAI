# Design System Reference

## 🎨 Color Palette

### Background Colors
```css
background: #08080c     /* Main background - rich black */
surface: #0f0f14        /* Elevated cards and surfaces */
border: #1e1e28         /* Subtle borders */
```

### Text Hierarchy
```css
text-primary: #fafaff   /* Primary text - almost white */
text-secondary: #a0a0b4 /* Secondary text - light gray */
text-muted: #64647c     /* Muted text - dark gray */
```

### Accent Colors
```css
accent-blue: #3b82f6    /* Primary actions */
accent-purple: #8b5cf6  /* Secondary actions */
accent-emerald: #34d399 /* Success states */
accent-amber: #fbbf24   /* Warning states */
accent-rose: #f43f5e    /* Error/danger states */
```

## 🔤 Typography

### Font Families

**Plus Jakarta Sans** (Body & UI)
- Modern, geometric sans-serif
- Used for body text, buttons, labels
- Weights: 300, 400, 500, 600, 700, 800
- Usage: `font-sans` (default)

**Space Grotesk** (Headings)
- Distinctive, modern display font
- Used for h1, h2, h3 headings
- Weights: 400, 500, 600, 700
- Usage: `font-display` or auto-applied to headings

**Monospace** (Code)
- System monospace font
- Used for code snippets, technical text
- Usage: `font-mono`

### Font Hierarchy

```tsx
// Headings (Space Grotesk)
<h1> // text-5xl font-bold tracking-tight letter-spacing: -0.02em - Hero headlines
<h2> // text-3xl font-semibold tracking-tight letter-spacing: -0.01em - Section titles
<h3> // text-xl font-semibold - Card titles

// Body text (Plus Jakarta Sans)
<h4> // text-lg font-semibold - Subsection titles
text-lg       // Large body (main content)
text-base     // Default body
text-sm       // Small body (metadata)
text-xs       // Extra small (labels)

// Code (Monospace)
font-mono text-sm // Inline code
```

### Font Weight Scale
```
font-light    = 300 (subtle text)
font-normal   = 400 (body text)
font-medium   = 500 (UI elements)
font-semibold = 600 (emphasis)
font-bold     = 700 (headings)
font-extrabold = 800 (hero text)
```

## 🎭 Utility Classes

### Glassmorphism
```tsx
className="glass" 
// Applies: bg-white/[0.02] backdrop-blur-xl border border-white/10
```

### Card Hover Effect
```tsx
className="card-hover"
// Applies: lift on hover with shadow
```

### Button Press
```tsx
className="button-press"
// Applies: scale down on click
```

### Gradient Text
```tsx
className="gradient-text"
// Applies: blue → purple → pink gradient
```

### Animated Background
```tsx
className="gradient-bg-animated"
// Applies: animated gradient background
```

## 🧩 Component Patterns

### Glassmorphism Card
```tsx
<div className="p-6 rounded-2xl glass hover:border-blue-500/30 transition-all">
  {/* Content */}
</div>
```

### Gradient Button
```tsx
<button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 
                   rounded-xl font-semibold hover:shadow-lg 
                   hover:shadow-blue-500/25 transform hover:-translate-y-0.5 
                   transition-all button-press">
  Click me
</button>
```

### Icon Container
```tsx
<div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 
                to-purple-500/20 flex items-center justify-center">
  <Icon className="w-5 h-5 text-blue-400" />
</div>
```

## 🎬 Animations

### Available Animations
- `animate-gradient-shift` - 8s gradient position shift
- `animate-spin-slow` - 3s slow spin
- `animate-spin` - Default Tailwind spin
- `animate-pulse` - Default Tailwind pulse

### Custom Transitions
```css
transition-all duration-200 ease-out  /* Quick interactions */
transition-all duration-500 ease-out  /* Smooth state changes */
```

## 📐 Spacing Scale (8px base unit)

```
0.5  = 4px  (xs)
1    = 8px  (sm)
1.5  = 12px (md)
2    = 16px (lg)
3    = 24px (xl)
4    = 32px (2xl)
6    = 48px (3xl)
8    = 64px (4xl)
```

## 🎯 Icon Usage (Lucide React)

```tsx
import { Search, Upload, CheckCircle, AlertTriangle } from 'lucide-react';

<Search className="w-5 h-5 text-blue-400" />
```

### Common Icons
- `Search` - Search/query
- `Upload` - File upload
- `FileText` - Documents
- `CheckCircle` - Success/verification
- `AlertTriangle` - Warnings
- `XCircle` - Errors
- `Info` - Information
- `Scale` - Legal/justice (logo)
- `Shield` - Security/protection
- `Zap` - Performance/speed

## 🖼️ Layout Patterns

### Centered Container
```tsx
<div className="max-w-6xl mx-auto px-8 py-12">
  {/* Content */}
</div>
```

### Grid Layouts
```tsx
// 4 columns (stats)
<div className="grid grid-cols-4 gap-4">

// 2 columns (cards)
<div className="grid md:grid-cols-2 gap-6">

// 3 columns (features)
<div className="grid md:grid-cols-3 gap-6">
```

### Bento Box (Asymmetric)
```tsx
<div className="grid grid-cols-3 gap-4">
  <div className="col-span-2 row-span-2">{/* Large card */}</div>
  <div>{/* Small card */}</div>
  <div>{/* Small card */}</div>
</div>
```

## 🎨 Gradient Examples

### Primary Gradient (Blue → Purple)
```css
bg-gradient-to-r from-blue-600 to-purple-600
```

### Success Gradient (Emerald)
```css
bg-gradient-to-br from-emerald-500/10 to-transparent
```

### Warning Gradient (Amber)
```css
bg-gradient-to-br from-amber-500/10 to-transparent
```

### Text Gradient
```css
bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent
```

---

**Note:** This design system is inspired by [21st.dev](https://21st.dev) and focuses on sophisticated minimalism, subtle luxury, and professional aesthetics.
