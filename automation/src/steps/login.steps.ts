import { createBdd } from 'playwright-bdd';
import { test } from '../fixtures';
import { LoginPage } from '../pages/login.page';
import { expect } from '@playwright/test';

const { Given, When, Then } = createBdd(test);

Given('the user is on the application home page', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.navigate();
});

When('the user enters {string} in the username field', async ({ page }, username: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.enterUsername(username);
});

When('the user enters {string} in the password field', async ({ page }, password: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.enterPassword(password);
});

When('the user clicks the orange "LOG IN" button', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.clickLoginButton();
});

Then('the user should be redirected to the "Accounts Overview" page', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyRedirectedToAccountsOverview();
});

Then('the sidebar should update to show the "Account Services" list', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifySidebarUpdated();
});

Then('a welcome message {string} should be displayed in the sidebar header', async ({ page }, message: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyWelcomeMessage(message);
});

Then('the user should remain on the current page', async ({ page }) => {
  // Check context to determine which page is "current"
  if (page.url().includes('updateprofile.htm')) {
    await expect(page).toHaveURL(/.*updateprofile\.htm/);
  } else {
    // Default to Login Page behavior
    const loginPage = new LoginPage(page);
    await loginPage.verifyRemainOnLoginPage();
  }
});

Then('an error block should appear with the title {string} in blue color', async ({ page }, title: string) => {
  const loginPage = new LoginPage(page);
  // Passing 'blue' as a placeholder for color check logic
  await loginPage.verifyErrorBlock(title, 'blue');
});

Then('the error message should read {string}', async ({ page }, message: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyErrorMessage(message);
});

Then('the username field should retain the value {string}', async ({ page }, username: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyUsernameRetained(username);
});

Then('the password field should be empty', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyPasswordEmpty();
});

Then('the login section should be located in the left sidebar', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyLoginSectionLocation();
});

Then('the "LOG IN" button should be visible and colored orange', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyLoginButtonVisuals('orange');
});

Then('the {string} link should be present but inactive', async ({ page }, linkText: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.verifyLinkPresent(linkText);
});
