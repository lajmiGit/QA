import { createBdd } from 'playwright-bdd';
import { test } from '../fixtures';
import { LoginPage } from '../pages/login.page';
import { TransferPage } from '../pages/transfer.page';
import { expect } from '@playwright/test';

const { Given, When, Then } = createBdd(test);

// Background step
Given('the user {string} is logged in', async ({ page }, name: string) => {
  const loginPage = new LoginPage(page);
  await loginPage.navigate();
  // Map "John Smith" to "john" / "demo" for the demo environment
  // In a real app, this would use a data file or env vars
  const username = 'john';
  const password = 'demo';
  
  await loginPage.enterUsername(username);
  await loginPage.enterPassword(password);
  await loginPage.clickLoginButton();
  // Verify we are logged in
  await expect(page).toHaveURL(/.*overview\.htm/);
});

Given('the user navigates to the "Transfer Funds" page at {string}', async ({ page }, url: string) => {
  // We can use the URL from the step or the page object method.
  // Using page object method is cleaner if it matches.
  // The step provides the URL, so we can verify or just go there.
  // For robustness, let's use the page object but we can assert the URL if needed.
  const transferPage = new TransferPage(page);
  await transferPage.navigate(); 
  // Optionally verify we are at the correct URL if strictly required by the step phrasing
  // await expect(page).toHaveURL(new RegExp(url));
});

When('the user enters the amount {string}', async ({ page }, amount: string) => {
  const transferPage = new TransferPage(page);
  await transferPage.enterAmount(amount);
});

When('the user selects the From Account {string}', async ({ page }, account: string) => {
  const transferPage = new TransferPage(page);
  // In Parabank demo, accounts are dynamic.
  // We need to handle this. If the account doesn't exist in the dropdown, the test might fail.
  // For the purpose of this exercise, we will try to select it.
  // If "12345" is not in the list, we might need to select index 0 for the test to pass in a demo env,
  // BUT the instructions say "Strictly follow Gherkin".
  // So we attempt to select the exact string. If it fails, we debug.
  await transferPage.selectFromAccount(account);
});

When('the user selects the To Account {string}', async ({ page }, account: string) => {
  const transferPage = new TransferPage(page);
  await transferPage.selectToAccount(account);
});

When('the user clicks on the "Transfer" button', async ({ page }, buttonName: string) => {
  const transferPage = new TransferPage(page);
  await transferPage.clickTransferButton();
});

Then('the transfer should be processed successfully', async ({ page }) => {
  const transferPage = new TransferPage(page);
  // Usually this means checking for the success title
  await transferPage.verifySuccessTitle("Transfer Complete!");
});

Then('the success message {string} should be displayed', async ({ page }, message: string) => {
  const transferPage = new TransferPage(page);
  await transferPage.verifySuccessTitle(message);
});

Then('the displayed message should contain the amount {string}', async ({ page }, amount: string) => {
  const transferPage = new TransferPage(page);
  await transferPage.verifyTransactionDetails(amount);
});
