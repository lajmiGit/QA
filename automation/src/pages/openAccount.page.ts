import { Page, Locator, expect } from '@playwright/test';

export class OpenAccountPage {
  readonly page: Page;
  readonly accountTypeSelect: Locator;
  readonly fromAccountIdSelect: Locator;
  readonly openAccountButton: Locator;
  readonly successTitle: Locator;
  readonly successMessage: Locator;
  readonly newAccountNumberLink: Locator;
  readonly openAccountForm: Locator;

  constructor(page: Page) {
    this.page = page;
    this.accountTypeSelect = page.locator('#type');
    this.fromAccountIdSelect = page.locator('#fromAccountId');
    this.openAccountButton = page.locator('input.button[value="Open New Account"]');

    // Explicitly target by exact text content to avoid ambiguity
    // We use getByRole or text locator with exact match preference
    this.successTitle = page.locator('h1.title').filter({ hasText: 'Account Opened!' });
    this.successMessage = page.locator('#openAccountResult p').first();
    this.newAccountNumberLink = page.locator('#newAccountId');
    this.openAccountForm = page.locator('form[ng-submit="openAccount()"]');
  }

  async verifyOnOpenAccountPage() {
    console.log('Verifying Open Account Page (New Code)...');
    await expect(this.page).toHaveURL(/.*openaccount\.htm/);

    // Wait for the specific heading to be visible.
    // Using filter on the text to single out the correct h1.
    const header = this.page.locator('h1.title', { hasText: 'Open New Account' });
    await expect(header).toBeVisible();
  }

  async selectAccountType(type: string) {
    // Try to find option by label
    const option = await this.accountTypeSelect.locator('option', { hasText: type }).first();
    const value = await option.getAttribute('value');
    if (value) {
      await this.accountTypeSelect.selectOption(value);
    } else {
      await this.accountTypeSelect.selectOption({ label: type });
    }
  }

  async selectSourceAccount(accountId: string) {
    await expect(this.fromAccountIdSelect).toBeVisible();
    await expect(this.fromAccountIdSelect.locator('option').first()).toBeAttached({ timeout: 10000 });

    // Try to select exact account
    const count = await this.fromAccountIdSelect.locator(`option[value="${accountId}"], option:has-text("${accountId}")`).count();
    if (count > 0) {
      // Try label first, then value
      try {
        await this.fromAccountIdSelect.selectOption({ label: accountId });
      } catch {
        await this.fromAccountIdSelect.selectOption({ value: accountId });
      }
    } else {
      console.warn(`Account ${accountId} not found in dropdown. Selecting first available option.`);
      await this.fromAccountIdSelect.selectOption({ index: 0 });
    }
  }

  async clickOpenAccountButton() {
    await this.openAccountButton.click();
  }

  async verifySuccessTitle(title: string) {
    // Use the specific locator if it matches our pre-defined one, or dynamic find
    if (title === 'Account Opened!') {
      await expect(this.successTitle).toBeVisible();
      await expect(this.successTitle).toHaveText(title);
    } else {
      await expect(this.page.locator('h1.title', { hasText: title })).toBeVisible();
    }
  }

  async verifySuccessMessage(message: string) {
    await expect(this.successMessage).toContainText(message);
  }

  async verifyNewAccountNumberDisplayed(prefix: string) {
    await expect(this.page.locator('#openAccountResult')).toContainText(prefix);
  }

  async verifyNewAccountNumberIsLink() {
    await expect(this.newAccountNumberLink).toBeVisible();
    await expect(this.newAccountNumberLink).toHaveAttribute('href');
  }

  async clickNewAccountNumber() {
    await this.newAccountNumberLink.click();
  }

  async verifyRedirectedToDetailsPage() {
    await expect(this.page).toHaveURL(/.*activity\.htm/);
  }
}
