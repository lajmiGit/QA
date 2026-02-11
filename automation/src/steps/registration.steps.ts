import { createBdd } from 'playwright-bdd';
import { test, expect } from '../fixtures';

const { Given, When, Then } = createBdd(test);

// Using common steps where possible or making them unique to avoid collisions

Given("the user navigates to the registration page via the 'Register' link", async ({ page }) => {
    await page.goto('https://parabank.parasoft.com/parabank/index.htm');
    await page.getByRole('link', { name: 'Register' }).click();
});

// REMOVED duplicate 'the page title should be {string}' because it exists in common.steps.ts

When('the user fills the form with {string}, {string}, {string}, {string}, {string}, {string}, {string}, {string}, {string}, {string}, and {string}', 
    async ({ registrationPage }, firstName, lastName, address, city, state, zipCode, phone, ssn, username, password, confirm) => {
    
    const randomSuffix = Math.random().toString(36).substring(2, 7);
    const uniqueUsername = (username === 'jdoe_purist' || username === 'jsmith_purist') ? `${username}_${randomSuffix}` : username;

    await registrationPage.fillRegistrationForm({
        firstName, lastName, address, city, state, zipCode, phone, ssn, username: uniqueUsername, password, confirm
    });
});

When('they click the {string} button', async ({ registrationPage }, buttonName) => {
    await registrationPage.clickRegister();
});

Then('the success message {string} is displayed', async ({ registrationPage }, message) => {
    await expect(registrationPage.successMessage).toHaveText(message);
});

Then('the banner displays {string}', async ({ registrationPage }, welcomeMsg) => {
    await expect(registrationPage.welcomeBanner).toContainText(welcomeMsg);
});

When('the user leaves the mandatory field {string} empty', async ({ registrationPage }, fieldMissing) => {
    (registrationPage as any).fieldMissing = fieldMissing;
});

When('they fill all other required fields correctly', async ({ registrationPage }) => {
    const fieldMissing = (registrationPage as any).fieldMissing;
    const defaultData = {
        firstName: fieldMissing === 'First Name' ? '' : 'John',
        lastName: fieldMissing === 'Last Name' ? '' : 'Doe',
        address: fieldMissing === 'Address' ? '' : '123 Main St',
        city: fieldMissing === 'City' ? '' : 'New York',
        state: fieldMissing === 'State' ? '' : 'NY',
        zipCode: fieldMissing === 'Zip Code' ? '' : '10001',
        ssn: fieldMissing === 'SSN' ? '' : '999-00-01',
        username: fieldMissing === 'Username' ? '' : `user_${Date.now()}`,
        password: fieldMissing === 'Password' ? '' : 'Pass123',
        confirm: fieldMissing === 'Confirm' ? '' : 'Pass123'
    };
    await registrationPage.fillRegistrationForm(defaultData);
});

Then('the inline error message {string} is displayed in red to the right of the field', async ({ registrationPage }, errorMessage) => {
    const fieldMissing = (registrationPage as any).fieldMissing;
    const actualError = await registrationPage.getInlineErrorMessage(fieldMissing);
    expect(actualError).toBe(errorMessage);
});

Given('an account already exists with the username {string}', async ({ registrationPage }, existingUser) => {
    await registrationPage.navigateTo();
    await registrationPage.fillRegistrationForm({
        firstName: 'Existing', lastName: 'User', address: '123', city: 'City', 
        state: 'ST', zipCode: '123', ssn: '123', 
        username: existingUser, password: 'password', confirm: 'password'
    });
    await registrationPage.clickRegister();
});

// Use a more specific step for registration username to avoid conflict with login.steps.ts
When('the user enters {string} in the registration username field', async ({ registrationPage }, username) => {
    await registrationPage.usernameInput.fill(username);
});

Then('the inline error message {string} is displayed in red', async ({ registrationPage }, errorMessage) => {
    const error = await registrationPage.getInlineErrorMessage('Username') || 
                  await registrationPage.getInlineErrorMessage('Confirm') || 
                  await registrationPage.getGeneralErrorMessage();
    expect(error).toContain(errorMessage);
});

// Use more specific steps for password/confirm to avoid conflict with login.steps.ts
When('the user enters {string} in the registration password field', async ({ registrationPage }, password) => {
    await registrationPage.passwordInput.fill(password);
});

When('they enter {string} in the registration confirmation field', async ({ registrationPage }, confirm) => {
    await registrationPage.confirmInput.fill(confirm);
});

Then('the {string} and {string} fields are cleared by the system', async ({ registrationPage }) => {
    await expect(registrationPage.passwordInput).toHaveValue('');
    await expect(registrationPage.confirmInput).toHaveValue('');
});
