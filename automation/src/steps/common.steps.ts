import { createBdd } from 'playwright-bdd';
import { test } from '../fixtures';
import { expect } from '@playwright/test';

const { Given, When, Then } = createBdd(test);

Then('the page title should be {string}', async ({ page }, title: string) => {
    await expect(page.locator('#rightPanel .title').filter({ visible: true, hasText: title }).first()).toBeVisible();
});

Given('the user navigates to {string}', async ({ page }, linkText: string) => {
    await page.click(`a:has-text("${linkText}")`);
});
