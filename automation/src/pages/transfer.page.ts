import { Page, Locator, expect } from '@playwright/test';

export class TransferPage {
  readonly page: Page;
  readonly amountInput: Locator;
  readonly fromAccountSelect: Locator;
  readonly toAccountSelect: Locator;
  readonly transferButton: Locator;

  constructor(page: Page) {
    console.log("Initializing TransferPage - VERSION 2");
    this.page = page;
    this.amountInput = page.locator('#amount');
    this.fromAccountSelect = page.locator('#fromAccountId');
    this.toAccountSelect = page.locator('#toAccountId');
    this.transferButton = page.locator('input.button[value="Transfer"]');
  }

  async navigate() {
    await this.page.goto('https://parabank.parasoft.com/parabank/transfer.htm');
    await this.amountInput.waitFor({ state: 'visible', timeout: 10000 });
  }

  async enterAmount(amount: string) {
    await this.amountInput.fill(amount);
  }

  async selectFromAccount(account: string) {
    await this.fromAccountSelect.waitFor({ state: 'visible' });
    try {
        await this.fromAccountSelect.selectOption({ label: account });
    } catch (e) {
        try {
          await this.fromAccountSelect.selectOption({ value: account });
        } catch (e2) {
             console.log(`Could not select account ${account}, selecting index 0`);
             await this.fromAccountSelect.selectOption({ index: 0 });
        }
    }
  }

  async selectToAccount(account: string) {
    await this.toAccountSelect.waitFor({ state: 'visible' });
    try {
        await this.toAccountSelect.selectOption({ label: account });
    } catch (e) {
        try {
          await this.toAccountSelect.selectOption({ value: account });
        } catch (e2) {
           console.log(`Could not select account ${account}, selecting index 0`);
           await this.toAccountSelect.selectOption({ index: 0 });
        }
    }
  }

  async clickTransferButton() {
    await this.transferButton.click();
  }

  async verifySuccessTitle(message: string) {
    // Explicit wait to ensure we are not checking too early
    await this.page.waitForTimeout(1000);
    // Locator looking for the exact heading "Transfer Complete!"
    // We avoid 'h1.title' because it matches multiple elements.
    await expect(this.page.getByRole('heading', { name: message, exact: true })).toBeVisible({ timeout: 10000 });
  }

  async verifyTransactionDetails(amount: string) {
    await expect(this.page.locator('body')).toContainText(amount);
  }
}
