import { createBdd } from 'playwright-bdd';
import { test } from '../fixtures';
import { LoginPage } from '../pages/login.page';
import { OpenAccountPage } from '../pages/openAccount.page';
import { expect } from '@playwright/test';

const { Given, When, Then } = createBdd(test);

// Background Steps
Given('the user is logged in as a standard customer', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.navigate();
  await loginPage.enterUsername('john');
  await loginPage.enterPassword('demo');
  await loginPage.clickLoginButton();
  await loginPage.verifyRedirectedToAccountsOverview();
});

Given('the user has at least one existing account with number {string} containing sufficient funds', async ({ page }, accountId: string) => {
  // In a real scenario, we might use API to check/create account.
  // For UI test on Parabank, we assume 'john' has this account or we check if it exists in Overview.
  // We'll proceed assuming the environment is set up correctly as per prompt instructions.
  // We could add a check:
  // await expect(page.locator(`a[href*="activity.htm?id=${accountId}"]`)).toBeVisible();
  // But strictly, we just ensure we are ready.
  console.log(`Assuming account ${accountId} exists and has funds.`);
});

// Scenario 1
Given('the user is on the {string}', async ({ page }, pageName: string) => {
  if (pageName === 'Account Overview') {
    await expect(page).toHaveURL(/.*overview\.htm/);
  } else if (pageName === 'Open New Account page') { // Matches Scenario 2 start
    const openAccountPage = new OpenAccountPage(page);
    // Navigate via menu if not there
    await page.click('a[href*="openaccount.htm"]');
    await openAccountPage.verifyOnOpenAccountPage();
  } else {
    throw new Error(`Unknown page: ${pageName}`);
  }
});

When('the user looks at the "Account Services" menu', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifySidebarUpdated();
});

Then('the option {string} should be visible', async ({ page }, linkText: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyLinkPresent(linkText);
});

Then('clicking {string} redirects to the Open New Account form', async ({ page }, linkText: string) => {
  await page.click(`a:has-text("${linkText}")`);
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.verifyOnOpenAccountPage();
});

// Scenario 2 (Some steps reused above)
Given('the user is on the "Open New Account" page', async ({ page }) => {
  const openAccountPage = new OpenAccountPage(page);
  // Check if we are already there, else navigate
  if (!page.url().includes('openaccount.htm')) {
    await page.click('a[href*="openaccount.htm"]');
  }
  await openAccountPage.verifyOnOpenAccountPage();
});

When('the user selects account type {string}', async ({ page }, accountType: string) => {
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.selectAccountType(accountType);
});

When('the user selects source account {string} from the dropdown', async ({ page }, sourceAccountId: string) => {
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.selectSourceAccount(sourceAccountId);
});

When('the user clicks the "Open New Account" button', async ({ page }) => {
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.clickOpenAccountButton();
});


Then('the message {string} is displayed', async ({ page }, message: string) => {
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.verifySuccessMessage(message);
});

Then('the new account number is displayed with the prefix {string}', async ({ page }, prefix: string) => {
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.verifyNewAccountNumberDisplayed(prefix);
});

Then('the new account number is a clickable link', async ({ page }) => {
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.verifyNewAccountNumberIsLink();
});

Then('clicking the new account number redirects to the details page of the new account', async ({ page }) => {
  const openAccountPage = new OpenAccountPage(page);
  await openAccountPage.clickNewAccountNumber();
  await openAccountPage.verifyRedirectedToDetailsPage();
});
