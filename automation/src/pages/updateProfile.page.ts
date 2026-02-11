import { Page, Locator, expect } from '@playwright/test';

export class UpdateProfilePage {
  readonly page: Page;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly addressInput: Locator;
  readonly cityInput: Locator;
  readonly stateInput: Locator;
  readonly zipCodeInput: Locator;
  readonly phoneNumberInput: Locator;
  readonly updateProfileButton: Locator;
  readonly title: Locator;
  readonly updateProfileLink: Locator;

  constructor(page: Page) {
    this.page = page;
    this.firstNameInput = page.locator('#rightPanel input[id="customer.firstName"]');
    this.lastNameInput = page.locator('#rightPanel input[id="customer.lastName"]');
    this.addressInput = page.locator('#rightPanel input[id="customer.address.street"]');
    this.cityInput = page.locator('#rightPanel input[id="customer.address.city"]');
    this.stateInput = page.locator('#rightPanel input[id="customer.address.state"]');
    this.zipCodeInput = page.locator('#rightPanel input[id="customer.address.zipCode"]');
    this.phoneNumberInput = page.locator('#rightPanel input[id="customer.phoneNumber"]');
    this.updateProfileButton = page.locator('#rightPanel input.button[value="Update Profile"]');
    this.title = page.locator('#rightPanel h1.title').filter({ visible: true }).first();
    this.updateProfileLink = page.locator('a[href*="updateprofile.htm"]');
  }

  async navigateToUpdateProfile() {
    await this.updateProfileLink.click();
    await this.page.waitForLoadState('networkidle');
    // Ensure we are on the right page
    await expect(this.title).toHaveText('Update Profile');
  }

  async fillProfile(data: { [key: string]: string }) {
    if (data['First Name']) await this.firstNameInput.fill(data['First Name']);
    if (data['Last Name']) await this.lastNameInput.fill(data['Last Name']);
    if (data['Address']) await this.addressInput.fill(data['Address']);
    if (data['City']) await this.cityInput.fill(data['City']);
    if (data['State']) await this.stateInput.fill(data['State']);
    if (data['Zip Code']) await this.zipCodeInput.fill(data['Zip Code']);
    if (data['Phone #']) await this.phoneNumberInput.fill(data['Phone #']);
  }

  async clickUpdateProfile() {
    await this.updateProfileButton.click();
  }

  async verifyTitle(expectedTitle: string) {
    await expect(this.title).toHaveText(expectedTitle);
  }

  async verifySuccessMessage(expectedMessage: string) {
    // success message is usually in a paragraph following the title or in the main content
    // Parabank structure varies. often <p>Your updated address ...</p>
    await expect(this.page.locator('#rightPanel p').first()).toContainText(expectedMessage);
  }

  async clearField(fieldName: string) {
    let input: Locator;
    switch (fieldName) {
      case 'First Name': input = this.firstNameInput; break;
      case 'Last Name': input = this.lastNameInput; break;
      case 'Address': input = this.addressInput; break;
      case 'City': input = this.cityInput; break;
      case 'State': input = this.stateInput; break;
      case 'Zip Code': input = this.zipCodeInput; break;
      case 'Phone #': input = this.phoneNumberInput; break;
      default: throw new Error(`Field ${fieldName} not recognized`);
    }
    await input.fill('');
  }

  async verifyInlineError(expectedError: string, fieldName: string) {
    // Parabank errors are usually span.error or just .error next to the field
    const errorLocator = this.page.locator('.error').filter({ hasText: expectedError });
    await expect(errorLocator.first()).toBeVisible();
  }

  async verifyEmailFieldNotVisible() {
    // Check if there is an input for email. Usually id="customer.email"? 
    // We can just check that no label or input with "Email" exists in the form context
    // Or specifically check that the common ID is absent
    const emailInput = this.page.locator('input[id*="email"]');
    await expect(emailInput).not.toBeVisible();
  }

  async verifyButtonLabel(label: string) {
    await expect(this.updateProfileButton).toHaveAttribute('value', label);
  }

  async verifyPreFilledData(data: { [key: string]: string }) {
    // Wait for data to load - often network idle is enough, but values are populated by JS or server
    // We might need to wait for one value to be populated
    await expect(this.firstNameInput).not.toHaveValue('', { timeout: 10000 });

    if (data['First Name']) await expect(this.firstNameInput).toHaveValue(data['First Name']);
    if (data['Last Name']) await expect(this.lastNameInput).toHaveValue(data['Last Name']);
    if (data['Address']) await expect(this.addressInput).toHaveValue(data['Address']);
    if (data['City']) await expect(this.cityInput).toHaveValue(data['City']);
    if (data['State']) await expect(this.stateInput).toHaveValue(data['State']);
    if (data['Zip Code']) await expect(this.zipCodeInput).toHaveValue(data['Zip Code']);
    if (data['Phone #']) await expect(this.phoneNumberInput).toHaveValue(data['Phone #']);
  }
}
