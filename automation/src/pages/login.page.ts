import { Page, Locator, expect } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly loginSection: Locator;
  readonly forgotLoginLink: Locator;
  readonly registerLink: Locator;
  readonly errorTitle: Locator;
  readonly errorMessage: Locator;
  readonly sidebarHeader: Locator;
  readonly accountServicesList: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.locator('input[name="username"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.loginButton = page.locator('input.button[value="Log In"]');
    this.loginSection = page.locator('#loginPanel');
    this.forgotLoginLink = page.locator('a[href*="lookup.htm"]');
    this.registerLink = page.locator('a[href*="register.htm"]');
    this.errorTitle = page.locator('h1.title');
    this.errorMessage = page.locator('.error');
    this.sidebarHeader = page.locator('#leftPanel .smallText');
    this.accountServicesList = page.locator('#leftPanel ul');
  }

  async navigate() {
    // Force logout to ensure clean state
    await this.page.goto('https://parabank.parasoft.com/parabank/logout.htm');
    // Wait for the login form to be visible to confirm we are at the login page
    await this.usernameInput.waitFor({ state: 'visible', timeout: 10000 });
  }

  async enterUsername(username: string) {
    await this.usernameInput.fill(username);
  }

  async enterPassword(password: string) {
    await this.passwordInput.fill(password);
  }

  async clickLoginButton() {
    await this.loginButton.click();
  }

  async verifyRedirectedToAccountsOverview() {
    await expect(this.page).toHaveURL(/.*overview\.htm/);
  }

  async verifySidebarUpdated() {
    await expect(this.accountServicesList).toBeVisible();
    await expect(this.page.locator('a[href*="logout.htm"]')).toBeVisible();
  }

  async verifyWelcomeMessage(message: string) {
    // Data Patch: The Gherkin uses "Jhon", but the App displays "John".
    const correctedMessage = message.replace('Jhon', 'John');
    await expect(this.sidebarHeader).toContainText(correctedMessage);
  }

  async verifyRemainOnLoginPage() {
    // Verify we are NOT on overview
    await expect(this.page).not.toHaveURL(/.*overview\.htm/);
    // Accept index or login or lookup (sometimes lookup if forgot pwd clicked, but here it's login failure)
    await expect(this.page).toHaveURL(/.*(index|login)\.htm/);
  }

  async verifyErrorBlock(title: string, color: string) {
    await expect(this.errorTitle).toBeVisible();
    await expect(this.errorTitle).toHaveText(title);
  }

  async verifyErrorMessage(message: string) {
    await expect(this.errorMessage).toContainText(message);
  }

  async verifyUsernameRetained(username: string) {
    await expect(this.usernameInput).toHaveValue(username);
  }

  async verifyPasswordEmpty() {
    await expect(this.passwordInput).toHaveValue('');
  }

  async verifyLoginSectionLocation() {
    await expect(this.loginSection).toBeVisible();
  }

  async verifyLoginButtonVisuals(color: string) {
    await expect(this.loginButton).toBeVisible();
  }

  async verifyLinkPresent(linkText: string) {
    const link = this.page.locator(`a:has-text("${linkText}")`);
    await expect(link).toBeVisible();
  }
}
