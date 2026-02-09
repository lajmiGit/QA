import { test as base } from 'playwright-bdd';

/**
 * Modern BDD Fixtures - Professional Architecture
 * This file serves as the dependency injection root.
 * Future Page Objects will be extended here.
 */

type MyFixtures = {
    // Add page objects here -> e.g., loginPage: LoginPage;
};

export const test = base.extend<MyFixtures>({});

export { expect } from '@playwright/test';
