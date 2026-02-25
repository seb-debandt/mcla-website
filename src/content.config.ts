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

export const collections = { blog };
