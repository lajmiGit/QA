import { Page, Locator, expect } from '@playwright/test';

export class RegistrationPage {
    readonly page: Page;
    readonly title: Locator;
    
    // Form fields
    readonly firstNameInput: Locator;
    readonly lastNameInput: Locator;
    readonly addressInput: Locator;
    readonly cityInput: Locator;
    readonly stateInput: Locator;
    readonly zipCodeInput: Locator;
    readonly phoneInput: Locator;
    readonly ssnInput: Locator;
    readonly usernameInput: Locator;
    readonly passwordInput: Locator;
    readonly confirmPasswordInput: Locator;
    
    // Actions
    readonly registerButton: Locator;
    
    // Messages
    readonly successTitle: Locator; // Souvent "Welcome user"
    readonly successText: Locator; // "Your account was created..."
    
    constructor(page: Page) {
        this.page = page;
        this.title = page.locator('h1.title');
        
        // Sélecteurs basés sur l'exploration précédente
        this.firstNameInput = page.locator('input[id="customer.firstName"]');
        this.lastNameInput = page.locator('input[id="customer.lastName"]');
        this.addressInput = page.locator('input[id="customer.address.street"]');
        this.cityInput = page.locator('input[id="customer.address.city"]');
        this.stateInput = page.locator('input[id="customer.address.state"]');
        this.zipCodeInput = page.locator('input[id="customer.address.zipCode"]');
        this.phoneInput = page.locator('input[id="customer.phoneNumber"]');
        this.ssnInput = page.locator('input[id="customer.ssn"]');
        this.usernameInput = page.locator('input[id="customer.username"]');
        this.passwordInput = page.locator('input[id="customer.password"]');
        this.confirmPasswordInput = page.locator('#repeatedPassword');
        
        this.registerButton = page.getByRole('button', { name: 'Register' });
        
        // Après inscription réussie
        this.successTitle = page.locator('h1.title');
        this.successText = page.locator('#rightPanel p');
    }

    async navigate() {
        await this.page.goto('https://parabank.parasoft.com/parabank/register.htm');
    }

    async clickRegisterLink() {
        await this.page.getByRole('link', { name: 'Register' }).click();
    }

    async verifyPageTitle(text: string) {
        await expect(this.title).toHaveText(text);
    }

    async fillForm(data: Record<string, string>) {
        if (data['First Name']) await this.firstNameInput.fill(data['First Name']);
        if (data['Last Name']) await this.lastNameInput.fill(data['Last Name']);
        if (data['Address']) await this.addressInput.fill(data['Address']);
        if (data['City']) await this.cityInput.fill(data['City']);
        if (data['State']) await this.stateInput.fill(data['State']);
        if (data['Zip Code']) await this.zipCodeInput.fill(data['Zip Code']);
        if (data['Phone']) await this.phoneInput.fill(data['Phone']);
        if (data['SSN']) await this.ssnInput.fill(data['SSN']);
        if (data['Username']) await this.usernameInput.fill(data['Username']);
        if (data['Password']) await this.passwordInput.fill(data['Password']);
        if (data['Confirm']) await this.confirmPasswordInput.fill(data['Confirm']);
    }

    async submit() {
        await this.registerButton.click();
    }

    async verifySuccess(message: string) {
        await expect(this.successText).toContainText(message);
    }

    async verifyWelcome(message: string) {
        await expect(this.successTitle).toHaveText(message);
    }

    async verifyError(message: string) {
        // Les erreurs globales ou par champ
        await expect(this.page.locator(`text=${message}`)).toBeVisible();
    }
    
    async verifyInlineError(message: string) {
        // Souvent <span id="customer.firstName.errors" class="error">
        await expect(this.page.locator('.error', { hasText: message })).toBeVisible();
    }

    async verifyPasswordsReset() {
        await expect(this.passwordInput).toBeEmpty();
        await expect(this.confirmPasswordInput).toBeEmpty();
    }
}
