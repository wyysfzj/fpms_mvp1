# Package Usage (for coding agents)

This package is a **design + style contract** for implementing the enhanced patent UI in a Vue3 SPA.

## Quick integration suggestion (not mandatory)
- Import styles in your Vite entry:
  - `styles/tokens.css`
  - `styles/layout.css`
  - `styles/components.css`

## Immersive mode
- Toggle `document.body.classList.toggle('mode-immersive')` on Case Detail pages only.
- Ensure you remove the class when leaving the route.

## Finance panel requirement
- The interactive prototype omitted the finance panel on dashboard.
- The spec requires the dashboard Split Grid to include the Financial Loop panel.
