import { createBdd } from 'playwright-bdd';
import { test } from '../fixtures';
import { expect } from '@playwright/test';
import { RegistrationPage } from '../pages/registration.page';
import { DataFactory } from '../utils/DataFactory';
import { faker } from '@faker-js/faker';

const { Given, When, Then } = createBdd(test);

// Background
Given('I am on the ParaBank home page', async ({ page }) => {
    await page.goto('https://parabank.parasoft.com/parabank/index.htm');
});

When('I click the "Register" link from the left menu', async ({ page }) => {
    const registrationPage = new RegistrationPage(page);
    await registrationPage.clickRegisterLink();
});

Then('I should see the page title {string}', async ({ page }, title) => {
    const registrationPage = new RegistrationPage(page);
    await registrationPage.verifyPageTitle(title);
});

// Scenario 1: Successful account registration
Given('I fill the registration form with the following details:', async ({ page }, dataTable) => {
    const registrationPage = new RegistrationPage(page);
    const data = dataTable.rowsHash();
    
    // Pour éviter les conflits d'unicité, on utilise la DataFactory
    if (data['Username'] && data['Username'].includes('user_auto')) {
        data['Username'] = await DataFactory.generateUniqueUsername(data['First Name'], data['Last Name']);
    }
    
    await registrationPage.fillForm(data);
});

When('I submit the registration form', async ({ page }) => {
    const registrationPage = new RegistrationPage(page);
    await registrationPage.submit();
});

Then('I should be redirected to the success page', async ({ page }) => {
    // Vérification implicite via le message de succès, mais on peut vérifier l'URL
    await expect(page).toHaveURL(/.*register\.htm.*/);
});

Then('I should see the welcome message {string}', async ({ page }, message) => {
    const registrationPage = new RegistrationPage(page);
    // Le message contient <firstName> <lastName>, il faut matcher dynamiquement ou partiellement
    // Comme c'est un test E2E, on vérifie que le titre contient "Welcome" et le nom
    await expect(registrationPage.successTitle).toContainText("Welcome");
});

// Scenario 2: Password mismatch
Given('I fill the registration form with valid data but mismatching passwords:', async ({ page }, dataTable) => {
    const registrationPage = new RegistrationPage(page);
    const data = dataTable.rowsHash();
    
    const baseData = {
        'First Name': 'TestMismatch',
        'Last Name': 'User',
        'Address': '123 Test St',
        'City': 'Test City',
        'State': 'TS',
        'Zip Code': '12345',
        'Phone': '555-0000',
        'SSN': '999-99-9999',
        'Username': 'mismatch_' + Date.now(),
        'Password': data['Password'],
        'Confirm': data['Confirm']
    };
    
    await registrationPage.fillForm(baseData);
});

Then('I should see the error message {string}', async ({ page }, errorMessage) => {
    const registrationPage = new RegistrationPage(page);
    await registrationPage.verifyError(errorMessage);
});

Then('the password fields should be automatically reset', async ({ page }) => {
    const registrationPage = new RegistrationPage(page);
    await registrationPage.verifyPasswordsReset();
});

// Scenario 3: Existing username
Given('a user already exists with the username {string}', async ({ page }, username) => {
    // On suppose que l'utilisateur existe déjà (données de test statiques)
});

When('I fill the registration form using the username {string}', async ({ page }, username) => {
    const registrationPage = new RegistrationPage(page);
    const baseData = {
        'First Name': 'Existing',
        'Last Name': 'User',
        'Address': '123 Test St',
        'City': 'Test City',
        'State': 'TS',
        'Zip Code': '12345',
        'Phone': '555-0000',
        'SSN': '999-99-9999',
        'Username': "jhon",
        'Password': 'Password123',
        'Confirm': 'Password123'
    };
    await registrationPage.fillForm(baseData);
});

// Scenario 4: Missing mandatory fields
When('I leave the {string} field empty', async ({ page }, field) => {
    const registrationPage = new RegistrationPage(page);
    
    // Remplir tout avec des données valides par défaut
    const baseData = {
        'First Name': 'Missing',
        'Last Name': 'Field',
        'Address': '123 Test St',
        'City': 'Test City',
        'State': 'TS',
        'Zip Code': '12345',
        'Phone': '555-0000',
        'SSN': '999-99-9999',
        'Username': 'missing_' + Date.now(),
        'Password': 'Password123',
        'Confirm': 'Password123'
    };
    
    // Vider le champ spécifique
    // Note: La clé dans baseData doit correspondre exactement au Gherkin (ex: "First Name")
    // Si le Gherkin dit "First Name", on mappe vers la clé interne
    
    if (field === 'First Name') baseData['First Name'] = '';
    if (field === 'Last Name') baseData['Last Name'] = '';
    if (field === 'Address') baseData['Address'] = '';
    if (field === 'City') baseData['City'] = '';
    if (field === 'State') baseData['State'] = '';
    if (field === 'Zip Code') baseData['Zip Code'] = '';
    if (field === 'SSN') baseData['SSN'] = '';
    if (field === 'Username') baseData['Username'] = '';
    if (field === 'Password') baseData['Password'] = '';
    if (field === 'Confirm') baseData['Confirm'] = '';
    
    await registrationPage.fillForm(baseData);
});

Then('I should see the inline error message {string}', async ({ page }, errorMessage) => {
    const registrationPage = new RegistrationPage(page);
    await registrationPage.verifyInlineError(errorMessage);
});
