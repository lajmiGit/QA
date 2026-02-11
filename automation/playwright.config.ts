import { defineConfig, devices } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: 'features/*.feature',
  steps: ['src/steps/*.ts', 'src/fixtures/index.ts'],
});

export default defineConfig({
  testDir,
  fullyParallel: true,
  reporter: 'html',
  use: {
    baseURL: 'https://parabank.parasoft.com/parabank/',
    screenshot: 'on',
    video: 'on',
  },
  /* --- CONFIGURATION DES RETRIES --- */
  retries: process.env.CI ? 2 : 2, // Relance 2 fois chaque test qui échoue
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
