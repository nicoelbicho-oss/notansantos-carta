// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://notansantos-carta.vercel.app',
  build: {
    inlineStylesheets: 'always',
    assets: 'assets'
  },
  compressHTML: true
});
