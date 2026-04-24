---
name: Modern Agritech System
colors:
  surface: '#fafaf4'
  surface-dim: '#dadad5'
  surface-bright: '#fafaf4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f4ee'
  surface-container: '#eeeee9'
  surface-container-high: '#e8e8e3'
  surface-container-highest: '#e3e3de'
  on-surface: '#1a1c19'
  on-surface-variant: '#42493e'
  inverse-surface: '#2f312e'
  inverse-on-surface: '#f1f1ec'
  outline: '#72796e'
  outline-variant: '#c2c9bb'
  surface-tint: '#3b6934'
  primary: '#154212'
  on-primary: '#ffffff'
  primary-container: '#2d5a27'
  on-primary-container: '#9dd090'
  inverse-primary: '#a1d494'
  secondary: '#5e5e5c'
  on-secondary: '#ffffff'
  secondary-container: '#e1dfdc'
  on-secondary-container: '#636360'
  tertiary: '#003c5f'
  on-tertiary: '#ffffff'
  tertiary-container: '#005482'
  on-tertiary-container: '#8bc8ff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#bcf0ae'
  primary-fixed-dim: '#a1d494'
  on-primary-fixed: '#002201'
  on-primary-fixed-variant: '#23501e'
  secondary-fixed: '#e4e2de'
  secondary-fixed-dim: '#c8c6c3'
  on-secondary-fixed: '#1b1c1a'
  on-secondary-fixed-variant: '#474744'
  tertiary-fixed: '#cde5ff'
  tertiary-fixed-dim: '#94ccff'
  on-tertiary-fixed: '#001d32'
  on-tertiary-fixed-variant: '#004b74'
  background: '#fafaf4'
  on-background: '#1a1c19'
  surface-variant: '#e3e3de'
typography:
  h1:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h2:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.25'
    letterSpacing: -0.01em
  h3:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1'
    letterSpacing: 0.05em
  tabular-nums:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '500'
    lineHeight: '1'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin: 32px
---

## Brand & Style

This design system is built on the intersection of biological precision and technological innovation. The brand personality is **authoritative, sustainable, and analytical**. It aims to evoke a sense of "grounded intelligence"—where the reliability of the earth meets the clarity of modern data science. 

The visual style is **Corporate / Modern** with a strong leaning toward **Minimalism**. It prioritizes high-density information environments while maintaining a premium feel through expansive white space and a "Data-First" hierarchy. The aesthetic avoids unnecessary flourishes, focusing instead on structural integrity and legibility to ensure users feel in total control of their agricultural operations.

## Colors

The palette is derived from natural elements, reinforced by analytical tones. 

- **Leaf Green (#2D5A27):** Used for primary actions, success states, and branding. It represents growth and health.
- **Earthy Cream (#FDFBF7):** The primary background surface. It provides a warmer, more premium alternative to pure white, reducing eye strain during long periods of data monitoring.
- **Data Blue (#0077B6):** Dedicated to technical indicators, sensor data, and interactive elements that are specifically data-driven (like links or chart toggles).
- **Soil Brown (#5D4037):** Used for grounding elements, secondary navigation accents, or specific soil-related metrics to provide a tactile connection to the earth.

Contrast ratios must strictly adhere to WCAG AA standards, particularly when placing Leaf Green or Data Blue against the Earthy Cream background.

## Typography

**Inter** is the sole typeface for this design system to ensure maximum utility and a clean, technical aesthetic across all platforms. 

- **Hierarchical Clarity:** Use heavy weights (700) sparingly for top-level page headers. 
- **Tabular Data:** For data tables and sensor readouts, always enable `tabular-nums` via font-feature-settings to ensure columns of numbers align vertically for easy comparison.
- **Readability:** Body text uses a generous 1.5–1.6 line height to maintain the "premium, spacious" feel requested.

## Layout & Spacing

This design system utilizes a **12-column fixed grid** for desktop (max-width: 1440px) and a **fluid 4-column grid** for mobile. 

- **Rhythm:** All spacing is based on an 8px scale.
- **Whitespace:** Emphasize "Macro-whitespace" (LG and XL units) between major sections to define the premium character of the interface. 
- **Data Density:** Use "Micro-whitespace" (XS and SM units) within data cards and tables to keep information compact without feeling cluttered.

## Elevation & Depth

To maintain a clean and data-driven aesthetic, this system avoids heavy shadows. Instead, it uses **Tonal Layers** and **Low-Contrast Outlines**.

- **Cards:** Elevated cards use a very subtle, diffused shadow (0px 4px 20px rgba(0,0,0,0.04)) and a 1px border colored at 10% opacity of the Soil Brown palette.
- **Active States:** Interactive elements like buttons or selected cards may use a slightly deeper shadow or a 2px Leaf Green border to indicate focus.
- **Backgrounds:** Use the Earthy Cream as the base layer, with white (#FFFFFF) used for elevated "Surface" containers like cards or panels to create a crisp distinction.

## Shapes

The shape language is **Soft**, utilizing a 0.25rem (4px) base radius. This creates a professional, precise appearance that feels modern but retains a slight organic softness.

- **Buttons & Inputs:** Use the base 4px radius.
- **Cards & Data Containers:** Use the `rounded-lg` (8px) radius to softly frame large blocks of information.
- **Badges:** Use a fully rounded pill shape to distinguish them from interactive buttons.

## Components

- **High-Contrast Cards:** Background: #FFFFFF. Border: 1px solid #5D4037 (10% opacity). Use Soil Brown for category labels and Leaf Green for primary metrics.
- **Data Tables:** Header rows should have a subtle Earthy Cream background. Use horizontal dividers only (no vertical lines) to maximize the clean look.
- **Modern Charts:**
    - **Radar:** Use Data Blue for the data area with a 20% opacity fill.
    - **Bar:** Use Leaf Green for "Current" data and Soil Brown for "Historical" or "Target" benchmarks.
- **Status Badges:** Use low-saturation background tints with high-saturation text. (e.g., Success: Light green background with Leaf Green text).
- **Iconography:** Use 2pt stroke icons. Soil icons should use Soil Brown, Sensor icons use Data Blue, and Plant/Growth icons use Leaf Green.
- **Input Fields:** 1px border in a neutral grey, moving to 2px Data Blue on focus.
- **Sensors/IoT Alerts:** High-visibility notification banners using Data Blue to signify technical updates or Soil Brown for environmental alerts.