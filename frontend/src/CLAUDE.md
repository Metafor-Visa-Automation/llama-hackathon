# 🎨 Otovize - Design System & Style Guide

> Premium, elegant, and modern design system for visa application platform

---

## 🎯 Design Philosophy

**Premium Minimalism** - Clean, sophisticated, trustworthy
- Apple-inspired smooth interactions
- Glassmorphism & modern depth
- Calming emerald green palette
- Elegant serif typography

---

## 🎨 Color Palette

### Primary Colors (Emerald Green)
```css
--primary-50:  #F0FDF4   /* Light backgrounds, subtle highlights */
--primary-100: #DCFCE7   /* Hover states, light accents */
--primary-200: #A7F3D0   /* Schengen countries base color */
--primary-300: #34D399   /* Hover states for map */
--primary-500: #10B981   /* Primary brand color, main CTA */
--primary-600: #059669   /* Hover states, darker accent */
--primary-700: #047857   /* Deep interactions */
--primary-900: #064E3B   /* Text on light backgrounds */
```

### Neutral Colors
```css
--white:       #FFFFFF   /* Cards, surfaces */
--gray-50:     #F9FAFB   /* Subtle backgrounds */
--gray-100:    #F5F5F5   /* Light dividers */
--gray-200:    #E5E7EB   /* Borders, disabled states */
--gray-400:    #9CA3AF   /* Placeholder text */
--gray-600:    #666666   /* Secondary text */
--black:       #1A1A1A   /* Primary text, headers */
```

### Accent Colors
```css
--error:       #EF4444   /* Error messages */
--success:     #10B981   /* Success states (same as primary) */
--warning:     #F59E0B   /* Warnings */
--info:        #3B82F6   /* Information */
```

---

## 📝 Typography

### Font Family
```css
font-family: "Playfair Display", serif;
```
**Why Playfair Display?**
- Elegant serif with high contrast
- Professional and trustworthy
- Excellent readability
- Premium feel for visa services

### Type Scale
```css
/* Headings */
h1: 4rem (64px)    - font-weight: 800, line-height: 1.1
h2: 3rem (48px)    - font-weight: 700, line-height: 1.2
h3: 2rem (32px)    - font-weight: 700, line-height: 1.3
h4: 1.5rem (24px)  - font-weight: 600, line-height: 1.4

/* Body */
body-large:  1.25rem (20px) - font-weight: 400, line-height: 1.7
body:        1rem (16px)    - font-weight: 400, line-height: 1.6
body-small:  0.875rem (14px) - font-weight: 400, line-height: 1.5

/* Labels & Captions */
label:       0.95rem (15px) - font-weight: 600, line-height: 1.5
caption:     0.75rem (12px) - font-weight: 400, line-height: 1.4
```

### Text Styling
```css
/* Letter Spacing */
uppercase-text: letter-spacing: 0.12em
heading-text:   letter-spacing: -0.03em
body-text:      letter-spacing: normal

/* Text Colors */
primary-text:   #1A1A1A
secondary-text: #666666
muted-text:     #9CA3AF
white-text:     #FFFFFF
```

---

## 🎭 Component Patterns

### Glassmorphism Cards
```css
background-color: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);
border-radius: 24px;
border: 1px solid rgba(255, 255, 255, 0.8);
box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
```

### Primary Buttons
```css
/* Default State */
background: linear-gradient(135deg, #10b981 0%, #059669 100%);
color: #FFFFFF;
padding: 0.875rem 2rem;
border-radius: 50px; /* Fully rounded pill shape */
font-weight: 700;
box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Hover State */
background: linear-gradient(135deg, #059669 0%, #047857 100%);
transform: scale(1.05);
box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5);

/* Disabled State */
background: #CCCCCC;
cursor: not-allowed;
opacity: 0.5;
box-shadow: none;
```

### Input Fields (MUI Styled)
```css
/* Container */
border-radius: 12px;
background-color: #F0FDF4;

/* Border */
border-color: #A7F3D0;
border-width: 2px;

/* Hover */
border-color: #10B981;

/* Focus */
border-color: #10B981;
border-width: 2px;
box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);

/* Label */
color: #064E3B;
font-weight: 600;
```

### Dynamic Island (User Greeting)
```css
/* Authenticated State */
background-color: rgba(26, 26, 26, 0.95);
backdrop-filter: blur(20px);
border-radius: 50px;
border: 2px solid rgba(255, 255, 255, 0.1);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);

/* Not Authenticated */
background-color: rgba(16, 185, 129, 0.95);
border: 2px solid rgba(255, 255, 255, 0.3);
box-shadow: 0 8px 32px rgba(16, 185, 129, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2);
```

---

## ✨ Animations & Transitions

### Page Transitions
```jsx
// Framer Motion settings
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
exit={{ opacity: 0, y: -20 }}
transition={{
  duration: 0.5,
  ease: [0.22, 1, 0.36, 1] // Custom Apple-like easing
}
```

### Hover Effects
```css
/* Standard Hover */
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

/* Scale on Hover */
transform: scale(1.05);

/* Button Hover */
transform: translateY(-2px);
box-shadow: 0 8px 25px rgba(16, 185, 129, 0.5);
```

### Micro-interactions
```css
/* Pulse Animation (Badge) */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 6px 30px rgba(16, 185, 129, 0.5);
  }
}
animation: pulse 2s ease-in-out infinite;

/* Slide Down (Dynamic Island) */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
animation: slideDown 0.5s ease-out;
```

---

## 🎪 Shadow System

```css
/* Elevation Levels */
shadow-sm:  0 4px 12px rgba(0, 0, 0, 0.08)
shadow-md:  0 6px 20px rgba(0, 0, 0, 0.12)
shadow-lg:  0 8px 32px rgba(0, 0, 0, 0.15)
shadow-xl:  0 20px 60px rgba(0, 0, 0, 0.15)

/* Colored Shadows (Brand) */
shadow-primary-md: 0 6px 20px rgba(16, 185, 129, 0.4)
shadow-primary-lg: 0 8px 32px rgba(16, 185, 129, 0.4)

/* Inner Shadows (Glassmorphism) */
inset-light: inset 0 1px 0 rgba(255, 255, 255, 0.2)
inset-dark:  inset 0 -1px 0 rgba(0, 0, 0, 0.1)
```

---

## 🔲 Border Radius Scale

```css
/* Rounded Corners */
radius-sm:   8px   /* Small elements, icons */
radius-md:   12px  /* Input fields, cards */
radius-lg:   24px  /* Large cards, modals */
radius-full: 50px  /* Buttons, pills, badges */
radius-circle: 50% /* Avatar, icon buttons */
```

---

## 📐 Spacing System

```css
/* Base: 4px (0.25rem) */
space-1:  0.25rem  (4px)
space-2:  0.5rem   (8px)
space-3:  0.75rem  (12px)
space-4:  1rem     (16px)
space-5:  1.25rem  (20px)
space-6:  1.5rem   (24px)
space-8:  2rem     (32px)
space-10: 2.5rem   (40px)
space-12: 3rem     (48px)
space-16: 4rem     (64px)
space-20: 5rem     (80px)
```

---

## 🖼️ Background System

### Primary Background
```css
/* Full-screen background */
background-image: url(../assets/vibe-bg1.webp);
background-size: cover;
background-position: center;
background-attachment: fixed;
```

### Gradient Backgrounds
```css
/* Primary Gradient (CTA, Buttons) */
background: linear-gradient(135deg, #10b981 0%, #059669 100%);

/* Light Gradient (Map Container) */
background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);

/* Text Gradient */
background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
```

### Overlay/Blur Effects
```css
/* Glassmorphism Blur */
backdrop-filter: blur(20px);
-webkit-backdrop-filter: blur(20px);

/* Dark Overlay */
background-color: rgba(0, 0, 0, 0.5);

/* Light Overlay */
background-color: rgba(255, 255, 255, 0.95);
```

---

## 🗺️ Interactive Map Styling

### Schengen Countries
```css
/* Base State */
color: #A7F3D0;
hover-color: #34D399;

/* Selected State */
color: #10B981;
hover-color: #059669;
```

### Map Navigation (Zoom Buttons)
```css
/* Button Style */
background-color: rgba(255, 255, 255, 0.65);
border: 1px solid rgba(0, 0, 0, 0.05);
border-radius: 50%;
width: 42px;
height: 42px;
box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
backdrop-filter: blur(8px);

/* Hover */
background-color: #FFFFFF;
transform: scale(1.05);
box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);

/* Icon Color */
fill: #059669;
```

---

## 🎯 Icon System

### Icon Library
**Material-UI Icons** - Consistent, professional, widely recognized

### Icon Sizes
```css
icon-sm:  16px - 18px  /* Small UI elements */
icon-md:  20px - 24px  /* Standard buttons, inputs */
icon-lg:  28px - 32px  /* Feature highlights */
icon-xl:  40px - 48px  /* Hero sections */
```

### Icon Colors
```css
primary-icon:   #10B981 (brand green)
secondary-icon: #666666 (neutral)
light-icon:     #FFFFFF (on dark backgrounds)
muted-icon:     #9CA3AF (disabled/inactive)
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */
mobile:     0px    - 640px
tablet:     641px  - 1024px
desktop:    1025px - 1440px
wide:       1441px+

/* Common Patterns */
@media (max-width: 768px) {
  /* Stack elements vertically */
  /* Reduce font sizes by 10-20% */
  /* Full-width buttons */
  /* Adjust padding/spacing */
}
```

---

## ⚡ Performance Guidelines

### Images
- Use WebP format for backgrounds
- Lazy load images below the fold
- Optimize images (max 200KB for backgrounds)
- Use appropriate image sizes for device

### Animations
- Prefer `transform` and `opacity` (GPU accelerated)
- Avoid animating `width`, `height`, `top`, `left`
- Keep animation duration between 200ms - 500ms
- Use `will-change` sparingly

### Loading States
```jsx
// Button loading state
{isLoading ? 'Giriş yapılıyor...' : 'Giriş Yap'}

// Skeleton screens for content
// Spinners for async operations
```

---

## 🎨 Design Tokens (Tailwind Config)

```js
// tailwind.config.js reference
colors: {
  primary: {
    50: '#F0FDF4',
    100: '#DCFCE7',
    200: '#A7F3D0',
    300: '#34D399',
    500: '#10B981',
    600: '#059669',
    700: '#047857',
    900: '#064E3B',
  }
}

fontFamily: {
  serif: ['"Playfair Display"', 'serif'],
}

borderRadius: {
  'xl': '12px',
  '2xl': '24px',
  '3xl': '50px',
}
```

---

## 🧩 Component Library Structure

```
components/
├── InteractiveWorldMap.jsx    - Map with country selection
├── UserGreeting.jsx           - Dynamic Island authentication
├── ProcessSteps.jsx           - Step-by-step guide
├── PageTransition.jsx         - Page animations wrapper
└── [Future Components]

pages/
├── Landing.jsx                - Home page
├── Login.jsx                  - Authentication
└── [Future Pages]
```

---

## ✅ Accessibility Guidelines

### Color Contrast
- Text on white: minimum 4.5:1 ratio
- Primary green (#10B981) on white: AAA compliant
- Always provide sufficient contrast

### Focus States
```css
/* Keyboard focus */
outline: 2px solid #10B981;
outline-offset: 2px;
border-radius: 4px;
```

### Interactive Elements
- Minimum touch target: 44x44px
- Clear hover/focus states
- Descriptive labels for form inputs
- ARIA labels for icon-only buttons

### Screen Readers
- Use semantic HTML (header, nav, main, footer)
- Alt text for images
- Aria-labels for complex interactions

---

## 🎯 Brand Voice & Tone

### Personality
- **Professional** yet friendly
- **Trustworthy** and reliable
- **Helpful** and supportive
- **Modern** and efficient

### Writing Style
- Clear and concise
- Action-oriented (CTAs)
- Empathetic to user concerns
- Turkish language, formal but warm

### Example Phrases
✅ "Hazırlamaya Başla" (not "Start")
✅ "Hoşgeldin, [Name]" (warm greeting)
✅ "Hesabınıza giriş yapın" (clear, formal)
✅ "Vize başvuruna devam et" (encouraging)

---

## 🚀 Quick Start Patterns

### Creating a New Button
```jsx
<button
  style={{
    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    color: '#FFFFFF',
    padding: '0.875rem 2rem',
    borderRadius: '50px',
    fontWeight: '700',
    fontFamily: '"Playfair Display", serif',
    boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)',
    transition: 'all 0.3s ease',
  }}
>
  Button Text
</button>
```

### Creating a Glass Card
```jsx
<div style={{
  backgroundColor: 'rgba(255, 255, 255, 0.95)',
  backdropFilter: 'blur(20px)',
  borderRadius: '24px',
  padding: '2rem',
  boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
  border: '1px solid rgba(255, 255, 255, 0.8)'
}}>
  {/* Content */}
</div>
```

### MUI TextField Styling
```jsx
<TextField
  sx={{
    '& .MuiOutlinedInput-root': {
      borderRadius: '12px',
      backgroundColor: '#F0FDF4',
      fontFamily: '"Playfair Display", serif',
      '& fieldset': {
        borderColor: '#A7F3D0',
        borderWidth: '2px',
      },
      '&:hover fieldset': {
        borderColor: '#10B981',
      },
      '&.Mui-focused fieldset': {
        borderColor: '#10B981',
      },
    },
  }}
/>
```

---

## 🎨 Design Inspiration

- **Apple** - Smooth animations, attention to detail
- **Stripe** - Clean layouts, trustworthy design
- **Linear** - Modern gradients, premium feel
- **Notion** - Glassmorphism, elegant simplicity

---

## 📚 Resources

### Fonts
- [Playfair Display](https://fonts.google.com/specimen/Playfair+Display) - Google Fonts

### Icons
- [@mui/icons-material](https://mui.com/material-ui/material-icons/) - Material-UI Icons

### Animation
- [Framer Motion](https://www.framer.com/motion/) - Animation library
- [Cubic-bezier.com](https://cubic-bezier.com/) - Easing function generator

### Colors
- [Coolors.co](https://coolors.co/) - Color palette generator

---

## 🎯 Key Takeaways

1. **Consistency is key** - Use design tokens for all components
2. **Premium feel** - Glassmorphism, shadows, smooth animations
3. **Green is our brand** - Emerald/green palette throughout
4. **Serif typography** - Playfair Display for elegance
5. **Smooth transitions** - Apple-like easing, 300-500ms duration
6. **Trustworthy design** - Professional, clean, accessible
