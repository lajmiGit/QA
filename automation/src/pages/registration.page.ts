import { Page, Locator } from '@playwright/test';

export class RegistrationPage {
    readonly page: Page;
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
    readonly confirmInput: Locator;
    readonly registerButton: Locator;
    readonly pageTitle: Locator;
    readonly successMessage: Locator;
    readonly welcomeBanner: Locator;

    constructor(page: Page) {
        this.page = page;
        this.firstNameInput = page.locator('id=customer.firstName');
        this.lastNameInput = page.locator('id=customer.lastName');
        this.addressInput = page.locator('id=customer.address.street');
        this.cityInput = page.locator('id=customer.address.city');
        this.stateInput = page.locator('id=customer.address.state');
        this.zipCodeInput = page.locator('id=customer.address.zipCode');
        this.phoneInput = page.locator('id=customer.phoneNumber');
        this.ssnInput = page.locator('id=customer.ssn');
        this.usernameInput = page.locator('id=customer.username');
        this.passwordInput = page.locator('id=customer.password');
        this.confirmInput = page.locator('id=repeatedPassword');
        this.registerButton = page.locator('input[value="Register"]');
        this.pageTitle = page.locator('h1.title');
        this.successMessage = page.locator('#rightPanel p');
        this.welcomeBanner = page.locator('#rightPanel h1.title');
    }

    async navigateTo() {
        await this.page.goto('https://parabank.parasoft.com/parabank/register.htm');
    }

    async fillRegistrationForm(data: any) {
        if (data.firstName !== undefined) await this.firstNameInput.fill(data.firstName);
        if (data.lastName !== undefined) await this.lastNameInput.fill(data.lastName);
        if (data.address !== undefined) await this.addressInput.fill(data.address);
        if (data.city !== undefined) await this.cityInput.fill(data.city);
        if (data.state !== undefined) await this.stateInput.fill(data.state);
        if (data.zipCode !== undefined) await this.zipCodeInput.fill(data.zipCode);
        if (data.phone !== undefined) await this.phoneInput.fill(data.phone);
        if (data.ssn !== undefined) await this.ssnInput.fill(data.ssn);
        if (data.username !== undefined) await this.usernameInput.fill(data.username);
        if (data.password !== undefined) await this.passwordInput.fill(data.password);
        if (data.confirm !== undefined) await this.confirmInput.fill(data.confirm);
    }

    async clickRegister() {
        await this.registerButton.click();

    }

    async getInlineErrorMessage(fieldName: string) {
        // Find error message to the right of the field.
        // In ParaBank, errors are usually in a span after the input
        const fieldMap: { [key: string]: string } = {
            'First Name': 'customer.firstName',
            'Last Name': 'customer.lastName',
            'Address': 'customer.address.street',
            'City': 'customer.address.city',
            'State': 'customer.address.state',
            'Zip Code': 'customer.address.zipCode',
            'SSN': 'customer.ssn',
            'Username': 'customer.username',
            'Password': 'customer.password',
            'Confirm': 'repeatedPassword'
        };
        const id = fieldMap[fieldName] || fieldName;
        await this.page.waitForTimeout(3000); // Délai de 3s demandé
        return this.page.locator(`id=${id}.errors`).textContent();
    }
    
    async getGeneralErrorMessage() {
         await this.page.waitForTimeout(3000); // Délai de 3s demandé
         return this.page.locator('span.error').textContent();
    }
}
