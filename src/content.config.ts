import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    date: z.string(),
    author: z.string(),
    category: z.enum(['Research', 'Patient Stories', 'News', 'Events']),
    excerpt: z.string(),
    featuredImage: z.string().optional(),
  }),
});

const team = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/team' }),
  schema: z.object({
    name: z.string(),
    title: z.string(),
    roleType: z.enum(['board', 'advisory', 'staff']),
    bio: z.string(),
    photo: z.string().optional(),
    order: z.number(),
  }),
});

const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    draft: z.boolean().optional(),
    subtitle: z.string().optional(),
    description: z.string().optional(),
    // Home page fields
    heroTitle: z.string().optional(),
    heroHighlight: z.string().optional(),
    heroDescription: z.string().optional(),
    heroPrimaryText: z.string().optional(),
    heroPrimaryUrl: z.string().optional(),
    heroSecondaryText: z.string().optional(),
    heroSecondaryUrl: z.string().optional(),
    missionStatement: z.string().optional(),
    pillarsHeading: z.string().optional(),
    pillarsSubheading: z.string().optional(),
    pillars: z.array(z.object({
      title: z.string(),
      description: z.string(),
      href: z.string(),
    })).optional(),
    statsHeading: z.string().optional(),
    statsSubheading: z.string().optional(),
    stats: z.array(z.object({
      value: z.string(),
      label: z.string(),
    })).optional(),
    statsSource: z.string().optional(),
    // Mission page fields
    vision: z.string().optional(),
    values: z.array(z.object({
      name: z.string(),
      description: z.string(),
    })).optional(),
    // Medical pages
    showMedicalDisclaimer: z.boolean().optional(),
    callout: z.string().optional(),
    // CTA fields
    ctaText: z.string().optional(),
    ctaUrl: z.string().optional(),
    ctaStyle: z.string().optional(),
    // Caregiver resources
    resources: z.array(z.object({
      name: z.string(),
      description: z.string(),
    })).optional(),
    // Research page
    intro: z.string().optional(),
    researchAreas: z.array(z.object({
      name: z.string(),
      description: z.string(),
    })).optional(),
    ctaLinks: z.array(z.object({
      title: z.string(),
      description: z.string(),
      url: z.string(),
    })).optional(),
    // Get Involved page
    ways: z.array(z.object({
      name: z.string(),
      description: z.string(),
      url: z.string().optional(),
      contactUrl: z.string().optional(),
      contactText: z.string().optional(),
    })).optional(),
    // Volunteer page
    volunteerRoles: z.array(z.object({
      name: z.string(),
      description: z.string(),
    })).optional(),
    // Contact page
    contacts: z.array(z.object({
      label: z.string(),
      email: z.string(),
    })).optional(),
    responseTime: z.string().optional(),
    importantNote: z.string().optional(),
    // Donate page
    amounts: z.array(z.object({
      value: z.number(),
      impact: z.string(),
    })).optional(),
    whyGiftMatters: z.string().optional(),
    impactAreas: z.array(z.string()).optional(),
    otherWays: z.array(z.object({
      method: z.string(),
      description: z.string(),
    })).optional(),
    donateEmail: z.string().optional(),
  }),
});

export const collections = { blog, team, pages };
