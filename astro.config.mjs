// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import netlify from '@astrojs/netlify';
import rehypeExternalLinks from 'rehype-external-links';

export default defineConfig({
  site: 'https://mantlecellalliance.org',
  output: 'static',
  adapter: netlify(),
  integrations: [
    sitemap(),
  ],
  markdown: {
    rehypePlugins: [
      [rehypeExternalLinks, { target: '_blank', rel: ['noopener', 'noreferrer'] }],
    ],
  },
  vite: {
    plugins: [tailwindcss()],
  },
});
