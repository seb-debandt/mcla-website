# MCLA — Mantle Cell Lymphoma Alliance Website

A professional nonprofit website for the Mantle Cell Lymphoma Alliance, built with Astro, Tailwind CSS, and Decap CMS.

## Tech Stack

- **Framework:** Astro 5
- **Styling:** Tailwind CSS 4
- **CMS:** Decap CMS with Git Gateway
- **Hosting:** Netlify
- **Donations:** Stripe Checkout
- **Forms:** Netlify Forms
- **Analytics:** Placeholder for Plausible or GA4

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Install Dependencies

```sh
npm install
```

### Run Locally

```sh
npm run dev
```

Open [http://localhost:4321](http://localhost:4321) in your browser.

### Build for Production

```sh
npm run build
```

### Preview Production Build

```sh
npm run preview
```

## Deploy to Netlify

1. Push this repo to GitHub/GitLab
2. Connect the repo to Netlify
3. Netlify will auto-detect the build settings from `netlify.toml`
4. Enable **Netlify Identity** in Site Settings > Identity
5. Enable **Git Gateway** in Site Settings > Identity > Services
6. Set environment variables in Netlify dashboard (see `.env.example`)

## Decap CMS (Content Management)

Access the CMS at `/admin` after deploying to Netlify with Identity enabled.

**Managed content:**
- Blog posts (News & Updates)
- Team members
- Events (future use)
- Resources (PDFs, guides)
- Page content (mission, about)

## Configure Stripe

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get your publishable and secret keys
3. Set them as environment variables:
   - `PUBLIC_STRIPE_PUBLISHABLE_KEY`
   - `STRIPE_SECRET_KEY`
4. The donate page includes a placeholder Stripe integration — connect it to your Stripe checkout session endpoint

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

## Project Structure

```
src/
  layouts/       - BaseLayout (HTML shell, nav, footer)
  components/    - Reusable UI components
  content/blog/  - Markdown blog posts (CMS-managed)
  pages/         - All site pages (file-based routing)
  styles/        - Global CSS with Tailwind
public/
  admin/         - Decap CMS config
  favicon.svg    - Site favicon
  robots.txt     - Search engine directives
```

## Commands

| Command           | Action                                |
| :---------------- | :------------------------------------ |
| `npm install`     | Install dependencies                  |
| `npm run dev`     | Start dev server at localhost:4321    |
| `npm run build`   | Build production site to `./dist/`    |
| `npm run preview` | Preview production build locally      |
