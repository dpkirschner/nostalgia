# Nostalgia Frontend Design System

## Overview

This document defines the design tokens, patterns, and conventions for the Nostalgia frontend UI. All components should adhere to these standards for consistency.

## Design Tokens

### Spacing Scale

Using Tailwind's default spacing scale (1 unit = 0.25rem / 4px):

- **Micro spacing**: `gap-1` (4px), `gap-2` (8px) - for tight layouts
- **Default spacing**: `gap-3` (12px), `gap-4` (16px) - most common use
- **Comfortable spacing**: `gap-6` (24px), `gap-8` (32px) - section breaks
- **Container padding**: `p-3` (mobile), `p-4` (tablet+) - safe area padding
- **Section padding**: `p-6 sm:p-8` - page sections

**Mobile-first approach**: Start with smaller values, scale up with responsive modifiers (`sm:`, `md:`, `lg:`).

### Z-Index Layers

Explicit z-index contract to prevent stacking conflicts:

| Layer              | Value | Usage                        | Tailwind Class |
| ------------------ | ----- | ---------------------------- | -------------- |
| **Map Canvas**     | 0     | Background map layer         | `z-0`          |
| **UI Chrome**      | 10    | Logo, buttons, floating UI   | `z-10`         |
| **Drawer Overlay** | 20    | Modal overlays, drawer scrim | `z-20`         |

**Rule**: Never use arbitrary z-index values outside this contract. If you need a new layer, document it here first.

### Border Radii

| Element                | Value  | Tailwind Class  | Usage                    |
| ---------------------- | ------ | --------------- | ------------------------ |
| **Drawer top corners** | 16px   | `rounded-t-2xl` | Bottom drawer, modal top |
| **Card corners**       | 12px   | `rounded-xl`    | Cards, panels            |
| **Button (pill)**      | 9999px | `rounded-full`  | FAB, pill buttons        |
| **Input fields**       | 8px    | `rounded-lg`    | Form inputs              |
| **Small elements**     | 6px    | `rounded-md`    | Chips, badges            |

### Shadows

| Element              | Tailwind Class | Usage                             |
| -------------------- | -------------- | --------------------------------- |
| **FAB**              | `shadow-lg`    | Floating action button (elevated) |
| **FAB hover**        | `shadow-xl`    | FAB on hover (more elevated)      |
| **Drawer**           | `shadow-2xl`   | Bottom drawer, modals             |
| **Cards**            | `shadow-md`    | Content cards                     |
| **Subtle elevation** | `shadow-sm`    | Subtle lift                       |

### Animation & Transitions

| Property          | Duration | Easing      | Usage                     |
| ----------------- | -------- | ----------- | ------------------------- |
| **Drawer slide**  | 200ms    | ease-out    | Drawer open/close         |
| **Overlay fade**  | 250ms    | ease-in-out | Scrim fade in/out         |
| **Button hover**  | 150ms    | ease        | Button scale/shadow       |
| **Button active** | 100ms    | ease        | Button press feedback     |
| **Focus ring**    | 150ms    | ease        | Keyboard focus indication |

**Tailwind utilities**:

- `transition-all duration-200`
- `transition-transform duration-150`
- `transition-opacity duration-250`

### Colors & Contrast

Using Tailwind's default color palette with semantic meaning:

#### Backgrounds

- **Light mode**: `bg-white`, `bg-gray-50` (subtle)
- **Dark mode**: `bg-gray-900`, `bg-gray-800` (subtle)
- **Backdrop blur**: `bg-white/80`, `bg-gray-900/80` (semi-transparent with blur)

#### Text

- **Primary text**: `text-gray-900 dark:text-gray-100`
- **Secondary text**: `text-gray-600 dark:text-gray-400`
- **Muted text**: `text-gray-500 dark:text-gray-500`

#### Interactive

- **Primary CTA**: `bg-blue-600 hover:bg-blue-700` (or brand color)
- **Danger**: `bg-red-600 hover:bg-red-700`
- **Success**: `bg-green-600 hover:bg-green-700`

#### Overlays

- **Modal scrim**: `bg-black/50` (50% opacity)
- **Drawer scrim**: `bg-black/50 backdrop-blur-sm`

**Accessibility requirement**: All text must meet WCAG AA contrast ratio of **≥4.5:1** against its background.

## Component Patterns

### Backdrop Blur Pattern

For UI elements overlaying the map:

```tsx
<div className="backdrop-blur-sm bg-white/80 dark:bg-gray-900/80">
  {/* Content */}
</div>
```

Provides:

- Legibility over varying backgrounds
- Modern glass-morphism aesthetic
- Maintains map visibility

### Focus Visible Pattern

All interactive elements must have visible focus rings for keyboard navigation:

```tsx
<button className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2">
  {/* Content */}
</button>
```

### Responsive Spacing Pattern

Start with mobile-first spacing, scale up on larger screens:

```tsx
<div className="p-3 sm:p-4 md:p-6">
  {/* Mobile: 12px, Tablet: 16px, Desktop: 24px */}
</div>
```

### Safe Area Pattern

For elements positioned at screen edges, respect safe areas:

```tsx
<div className="absolute top-0 left-0 p-3 sm:p-4">
  {/* Ensures content doesn't touch screen edge */}
</div>
```

## Layout Conventions

### Full Viewport Page

```tsx
<div className="h-screen w-screen overflow-hidden">{/* Page content */}</div>
```

Prevents body scroll and ensures viewport-filling layout.

### Absolute Positioning for Layers

```tsx
<div className="relative h-screen w-screen overflow-hidden">
  {/* Map - base layer */}
  <div className="absolute inset-0 z-0">{/* Map */}</div>

  {/* UI Chrome - overlay layer */}
  <div className="absolute top-0 left-0 z-10">{/* Logo */}</div>
  <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-10">
    {/* FAB */}
  </div>
</div>
```

### Drawer Content Structure

```tsx
<DrawerContent>
  {/* Header - sticky at top */}
  <div className="sticky top-0 bg-white border-b">
    <DrawerHandle />
    <DrawerTitle />
  </div>

  {/* Body - scrollable */}
  <div className="flex-1 overflow-y-auto p-4">{/* Content */}</div>

  {/* Footer - sticky at bottom (optional) */}
  <div className="sticky bottom-0 bg-white border-t p-4">{/* Actions */}</div>
</DrawerContent>
```

## Accessibility Guidelines

### Keyboard Navigation

1. **Tab order**: Logical flow top-to-bottom, left-to-right
2. **Focus trap**: Modals/drawers trap focus until closed
3. **Escape key**: Closes all modal interfaces
4. **Enter/Space**: Activates buttons and interactive elements

### Screen Readers

1. **VisuallyHidden**: Use for screen-reader-only text

   ```tsx
   <VisuallyHidden>Descriptive label for context</VisuallyHidden>
   ```

2. **ARIA labels**: All interactive regions must have labels

   ```tsx
   <div role="dialog" aria-labelledby="drawer-title">
     <h2 id="drawer-title">Drawer Title</h2>
   </div>
   ```

3. **Announcements**: Important state changes should announce to screen readers

### Touch Targets

Minimum touch target size: **48×48px** (iOS/Android guideline)

```tsx
<button className="min-h-[48px] min-w-[48px]">
  {/* Ensures tappable area */}
</button>
```

## Naming Conventions

### Component Files

- **PascalCase**: `MapCanvas.tsx`, `PrimaryFAB.tsx`
- **One component per file** (except tightly coupled sub-components)

### CSS Classes

- **Use Tailwind utilities** by default
- **Avoid custom CSS** unless absolutely necessary
- **Use `cn()` utility** from `lib/utils.ts` to merge class names safely

### Props

- **TypeScript interfaces**: Define in component file or `types/components.ts`
- **Callback props**: Prefix with `on` (e.g., `onPress`, `onOpenChange`)
- **Boolean props**: Use `is` or `has` prefix (e.g., `isOpen`, `hasError`)

## File Structure

```
web/src/
├── components/
│   ├── layout/        # Layout shells (AppLayout, PageLayout)
│   ├── map/           # Map-related components (MapCanvas, Marker)
│   └── ui/            # Reusable UI primitives (Button, Drawer, FAB)
├── lib/
│   └── utils.ts       # Utility functions (cn, formatters)
├── types/
│   └── components.ts  # Shared TypeScript interfaces
└── assets/            # Static assets (images, icons)
```

## Tools & Utilities

### `cn()` Function

Located in `lib/utils.ts`, combines `clsx` and `tailwind-merge`:

```tsx
import { cn } from '@/lib/utils'

<div className={cn(
  "base-class",
  condition && "conditional-class",
  props.className
)}>
```

Benefits:

- Handles conditional classes cleanly
- Merges conflicting Tailwind classes correctly
- Type-safe with TypeScript

## Performance Considerations

1. **Lazy load** components not needed on initial render
2. **Debounce** map interaction handlers (e.g., `onIdle` for bounds changes)
3. **Memoize** expensive computations with `useMemo`
4. **Avoid re-renders** with `React.memo` for pure components

## Browser Support

- **Modern evergreen browsers**: Chrome, Firefox, Safari, Edge (last 2 versions)
- **Mobile**: iOS Safari 15+, Chrome Android 100+
- **No IE11 support**

## Future Enhancements

Areas to expand as the design system grows:

- [ ] Icon library (Lucide React, Heroicons, or custom)
- [ ] Typography scale (headings, body, captions)
- [ ] Motion presets (spring animations, stagger children)
- [ ] Theme variants (brand colors, dark mode refinements)
- [ ] Form components (inputs, selects, checkboxes)
- [ ] Toast/notification system
- [ ] Loading states (skeletons, spinners)
