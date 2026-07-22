# 🌐 NEET Web Interface & Admin Dashboard (`neet_bot/web/`)

This directory contains the responsive web frontend, stylesheet design system, interactive JavaScript application, assets, and protected Admin Analytics Dashboard.

---

## 📂 File-by-File Breakdown

| File Name | Purpose & Functionality |
| :--- | :--- |
| **`index.html`** | Main web landing page and interactive Web Test Simulator. Features hero launcher cards for `@gptbiologybot`, `@gptphysicsbot`, `@gptchemistrybot`, Student Value/Outcome cards, Web Practice Mode, and Creator Connect section with Instagram & LinkedIn links for Arun Yadav. |
| **`style.css`** | Vanilla CSS design system. Implements organic cream/forest dark-mode theme, HSL color tokens, glassmorphism cards, ambient floating blur orbs, and responsive breakpoints. |
| **`app.js`** | Client-side JavaScript application. Manages subject tabs (`biology`, `physics`, `chemistry`), chapter selection, multi-chapter search filters, 1-minute question countdown timers, quiz state, score calculation, and dynamic AI evaluation rendering. |
| **`admin.html`** | Protected Admin Analytics Dashboard (`/admin`). Displays multi-bot stat cards, active user count, test sessions completed, average score per subject, and recent activity logs. |
| **`logo.png`** | Platform branding emblem image used in navbar, hero badge, and footer. |

---

## 🎨 Theme & Typography

- **Headings Font**: `Outfit` (Google Fonts)
- **Body Font**: `Inter` (Google Fonts)
- **Colors**:
  - Biology: `#2e8b57` (Sea Green)
  - Physics: `#0284c7` (Sky Blue)
  - Chemistry: `#d97706` (Amber Gold)
  - Background: Organic Ivory Dark Pine (`#132924`)
