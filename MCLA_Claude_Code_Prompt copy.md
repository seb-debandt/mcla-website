# Claude Code Prompt — Build the MCLA Website

Use this prompt to brief Claude Code. Copy and paste it as your initial instruction. You may want to break it into phases (start with Phase 1, then feed Phase 2 after review).

---

## THE PROMPT

Build a complete, professional website for the **Mantle Cell Lymphoma Alliance (MCLA)** — a new U.S. nonprofit dedicated to mantle cell lymphoma (a rare blood cancer). The site must project the credibility and trust of an established health organization while being warm and patient-centered.

### Tech Stack

- **Framework:** Astro (latest stable version)
- **Styling:** Tailwind CSS
- **CMS:** Decap CMS (formerly Netlify CMS) with Git Gateway for content management by non-technical users
- **Hosting target:** Netlify (include netlify.toml config)
- **Donations:** Stripe checkout integration (use Stripe's embeddable pricing/donation components; include placeholder for API keys)
- **Forms:** Netlify Forms for contact and newsletter signup
- **Search:** Pagefind for client-side search
- **Analytics:** Placeholder for Plausible or GA4 script

### Color Palette

```
Primary teal:    #0D7377 (trust, health, calm)
Secondary gold:  #D4920B (hope, warmth)
Charcoal:        #2D3748 (text, headers)
Warm white:      #FAFAF8 (backgrounds)
Sage light:      #E8F0ED (card/section backgrounds)
Coral CTA:       #E8614D (donate buttons, urgent CTAs)
```

### Typography

- Headings: `Source Serif 4` from Google Fonts (authoritative serif)
- Body: `Inter` from Google Fonts (clean, highly readable sans-serif)
- Base body size: 18px, line-height: 1.7

### Site Structure

Build these pages with full layout and placeholder content:

```
/ (Homepage)
/about/mission
/about/our-story
/about/team
/about/partners
/understanding-mcl/what-is-mcl
/understanding-mcl/newly-diagnosed
/understanding-mcl/treatment-options
/understanding-mcl/find-specialist
/understanding-mcl/caregiver-support
/research (overview/index page for the Research section)
/research/priorities
/research/for-researchers
/news (blog listing — CMS-managed via markdown)
/news/[slug] (individual blog post template)
/get-involved (overview: ways to help, volunteer, fundraise, share your story)
/get-involved/volunteer
/get-involved/partner
/donate
/contact
/privacy-policy
/terms-of-use
```

### Homepage Layout (top to bottom)

1. **Sticky header** with logo (text placeholder "MCLA" for now), primary navigation with dropdowns, and a "Donate" button in the nav (coral color).

2. **Hero section:** Full-width with a subtle gradient background (teal to white). Large headline: "Advancing hope for those facing mantle cell lymphoma." Subheadline: brief mission summary. Two CTA buttons: "Learn About MCL" (teal) and "Support Our Mission" (coral outline).

3. **Mission statement section:** Centered text block on a warm white background. The full mission statement from: "The Mantle Cell Lymphoma Alliance supports those facing mantle cell lymphoma with trusted information and expert-guided support. We connect patients, caregivers, researchers, and oncologists across all clinical settings to improve outcomes and expand access to care. We support targeted research that advances progress toward better treatments and ultimately a cure."

4. **Three pillars section:** Three cards in a row (stacked on mobile): "Advancing Research," "Trusted Education & Access," "Collaboration & Community." Each with an icon (use Lucide icons or similar), brief description, and a "Learn more" link.

5. **Impact statistics section:** Dark teal background, white text. 3-4 key statistics about MCL in large type (e.g., "~4,000 new cases/year in the U.S.", "Median age at diagnosis: 68", "MCL accounts for ~6% of all non-Hodgkin lymphomas"). Use a note that these are sourced from published medical literature.

6. **Latest news section:** 3 most recent blog posts as cards with image, title, date, excerpt.

7. **Donate CTA section:** Warm, compelling section. "Every gift brings us closer to better treatments and a cure." Donate button.

8. **Newsletter signup:** Simple email capture form with "Stay informed. Join our community."

9. **Footer:** Logo, brief mission tagline, quick links (organized in columns), social media icon placeholders, newsletter signup repeat, 501(c)(3) notice ("MCLA is a 501(c)(3) tax-exempt organization. EIN pending."), copyright, privacy/terms links.

### Key Design Requirements

- **Mobile-first responsive design.** Every page must look excellent on phones, tablets, and desktop.
- **Generous whitespace.** Do not cram content. Whitespace = trust.
- **Consistent section rhythm.** Alternate between white and very light sage (#E8F0ED) backgrounds to create visual rhythm.
- **Smooth scroll behavior.** Subtle, professional transitions.
- **Sticky navigation** that becomes compact on scroll.
- **Accessible:** WCAG 2.1 AA compliant. All images need alt text. Color contrast must pass. Keyboard navigation must work. Include skip-to-content link. All form inputs must have proper labels.
- **Fast:** Target Lighthouse 90+ on all metrics. Optimize images, lazy load below-fold content, minimal JavaScript.

### Donate Page Specifics

- Headline: "Your Impact Starts Here"
- Brief narrative about why donations matter for rare cancer research
- Suggested amounts: $25, $50, $100, $250, $500, Other
- Each amount with a one-line impact description (e.g., "$50 — Helps fund patient education materials")
- Toggle between one-time and monthly recurring
- Stripe checkout integration (use placeholder keys, clearly marked)
- Trust signals: lock icon, "Secure donation powered by Stripe," 501(c)(3) tax notice
- Memorial/honorary giving option (text fields for "In honor of" / "In memory of")
- Below the form: "Questions about giving? Contact us at donate@mantlecellalliance.org"

### Blog / News Setup

- Content collection in Astro using markdown files in `src/content/blog/`
- Each post: title, date, author, category (Research, Patient Stories, News, Events), featured image, body content
- Listing page shows cards with image, title, date, excerpt, category tag
- Category filtering
- Individual post template with proper typography, share buttons, related posts
- Decap CMS config (`public/admin/config.yml`) that allows creating and editing blog posts through the CMS UI

### Decap CMS Configuration

Set up `/public/admin/index.html` and `/public/admin/config.yml` for:
- Blog posts (create, edit, delete — with title, date, author, category, featured image, body)
- Team members (name, title, role type [board/advisory/staff], bio, photo, order)
- Events (title, date, location, description, link — for future use, include the collection now)
- Basic page content editing (mission, vision, about text)
- Resource documents (title, description, file upload for PDFs and guides)
- Media uploads (images for posts, team photos, partner logos)
- Use Netlify Identity for authentication

### Content Tone

All placeholder content should be written in MCLA's voice:
- Authoritative but accessible
- Hopeful but honest
- Collaborative ("we" language)
- Action-oriented (every section has a clear next step)
- Patient-facing content at 8th-grade reading level
- Medical disclaimers on all health content pages: "This information is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment."

### SEO

- Semantic HTML (proper h1 > h2 > h3 hierarchy on every page)
- Unique meta title and description for every page
- Open Graph and Twitter Card meta tags
- Organization structured data (JSON-LD)
- Auto-generated XML sitemap
- robots.txt
- Canonical URLs

### File Structure

```
/
├── astro.config.mjs
├── netlify.toml
├── tailwind.config.mjs
├── package.json
├── public/
│   ├── admin/
│   │   ├── index.html
│   │   └── config.yml
│   ├── favicon.svg
│   └── robots.txt
├── src/
│   ├── layouts/
│   │   ├── BaseLayout.astro (html head, nav, footer)
│   │   └── BlogPost.astro
│   ├── components/
│   │   ├── Header.astro
│   │   ├── Footer.astro
│   │   ├── Hero.astro
│   │   ├── PillarCards.astro
│   │   ├── StatsSection.astro
│   │   ├── NewsCards.astro
│   │   ├── DonateForm.astro
│   │   ├── NewsletterSignup.astro
│   │   ├── TeamMember.astro
│   │   ├── MedicalDisclaimer.astro
│   │   └── ContactForm.astro
│   ├── content/
│   │   └── blog/
│   │       ├── welcome-to-mcla.md
│   │       ├── what-is-mcl.md
│   │       └── why-mcla-exists.md
│   ├── pages/
│   │   ├── index.astro
│   │   ├── about/
│   │   │   ├── mission.astro
│   │   │   ├── our-story.astro
│   │   │   ├── team.astro
│   │   │   └── partners.astro
│   │   ├── understanding-mcl/
│   │   │   ├── what-is-mcl.astro
│   │   │   ├── newly-diagnosed.astro
│   │   │   ├── treatment-options.astro
│   │   │   ├── find-specialist.astro
│   │   │   └── caregiver-support.astro
│   │   ├── research/
│   │   │   ├── index.astro
│   │   │   ├── priorities.astro
│   │   │   └── for-researchers.astro
│   │   ├── news/
│   │   │   ├── index.astro
│   │   │   └── [...slug].astro
│   │   ├── get-involved/
│   │   │   ├── index.astro
│   │   │   ├── volunteer.astro
│   │   │   └── partner.astro
│   │   ├── donate.astro
│   │   ├── contact.astro
│   │   ├── privacy-policy.astro
│   │   └── terms-of-use.astro
│   └── styles/
│       └── global.css
```

### Important Notes

- Use placeholder images (solid color blocks with text overlays describing what image should go there, or use Unsplash source URLs for relevant medical/nature imagery).
- Include a clear `README.md` explaining how to: install dependencies, run locally, deploy to Netlify, access the CMS, and configure Stripe keys.
- All Stripe API keys should be environment variables (referenced but never hardcoded).
- Include a `.env.example` file showing required environment variables.
- The site should be fully functional with placeholder content — ready to deploy and start replacing content immediately.

### Quality Checklist

Before considering the build complete, verify:
- [ ] All pages render without errors
- [ ] Navigation works on all pages (including mobile hamburger menu)
- [ ] Responsive design looks good at 320px, 768px, 1024px, 1440px
- [ ] Donate page form is functional (with test Stripe keys)
- [ ] Contact form submits correctly
- [ ] Newsletter signup works
- [ ] Blog posts render from markdown
- [ ] CMS admin panel loads at /admin
- [ ] Lighthouse scores 90+ on Performance, Accessibility, Best Practices, SEO
- [ ] All links work (no 404s)
- [ ] Medical disclaimers present on health content pages
- [ ] Footer shows on all pages with correct content
- [ ] Meta tags and OG tags present on all pages
- [ ] Site builds successfully with `npm run build`

---

*This prompt is designed to be given to Claude Code in one piece for Phase 1 (all pages), or split into phases if preferred. Reference the full MCLA_Website_Plan.md for additional context on content strategy, audience needs, and organizational background.*
