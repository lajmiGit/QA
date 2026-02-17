import { createBdd } from 'playwright-bdd';
import { test } from '../fixtures';
import { expect } from '@playwright/test';
import { UpdateProfilePage } from '../pages/updateProfile.page';
import { LoginPage } from '../pages/login.page';

const { Given, When, Then } = createBdd(test);

Given('I am a logged-in user on the "Update Profile" page', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.navigate();
  await loginPage.enterUsername('john');
  await loginPage.enterPassword('demo');
  await loginPage.clickLoginButton();
  await loginPage.verifyRedirectedToAccountsOverview();

  const updateProfilePage = new UpdateProfilePage(page);
  await updateProfilePage.navigateToUpdateProfile();
});

Given('the current user profile data is loaded', async ({ page }) => {
  // Implicit wait on navigation, but we verify fields are populated
  const updateProfilePage = new UpdateProfilePage(page);
  await expect(updateProfilePage.firstNameInput).not.toHaveValue('');
});

When('I update the profile fields with the following details:', async ({ page }, dataTable) => {
  const data = dataTable.rowsHash();
  const updateProfilePage = new UpdateProfilePage(page);

  // Mapping Gherkin keys to Page Object keys
  const mappedData: Record<string, string> = {};
  for (const [key, value] of Object.entries(data)) {
    mappedData[key] = value as string;
  }

  // Fill the fields
  // Need to handle clearing first as fill replaces but maybe we want to be explicit? 
  // Playwright fill() clears before typing.
  await updateProfilePage.fillProfile(mappedData);
});

When('I click on the "UPDATE PROFILE" button', async ({ page }) => {
  const updateProfilePage = new UpdateProfilePage(page);
  await updateProfilePage.clickUpdateProfile();
});

Then('I should be redirected to the Confirmation Screen', async ({ page }) => {
  const updateProfilePage = new UpdateProfilePage(page);
  // Verify title changes to Profile Updated
  await expect(updateProfilePage.title).toHaveText('Profile Updated');
});

Then('I should see the title {string}', async ({ page }, title) => {
  const updateProfilePage = new UpdateProfilePage(page);
  await updateProfilePage.verifyTitle(title);
});

When('I clear the {string} field', async ({ page }, fieldName) => {
  const updateProfilePage = new UpdateProfilePage(page);
  await updateProfilePage.clearField(fieldName);
});

Then('I should remain on the "Update Profile" page', async ({ page }) => {
  const updateProfilePage = new UpdateProfilePage(page);
  await expect(updateProfilePage.title).toHaveText('Update Profile');
});

Then('I should see the inline error message {string} next to the {string} field', async ({ page }, errorMessage, fieldName) => {
  const updateProfilePage = new UpdateProfilePage(page);
  // We need to implement checking the specific error span
  // The page object method verifyInlineError handles the logic

  // Map field names to ID or locator strategy inside the page object
  // For validation, we need to inspect where errors appear.
  // Assuming standard Parabank behavior: <span id="customer.firstName.errors" class="error">...</span>

  // However, I need to know the mapping. 
  // Let's implement a mapping in the step or page object. 
  // I'll put logic in Page Object 'verifyInlineError'
  await updateProfilePage.verifyInlineError(errorMessage, fieldName);
});

Given('the user has the following existing data:', async ({ page }, dataTable) => {
  const data = dataTable.rowsHash();
  const updateProfilePage = new UpdateProfilePage(page);

  // To ensure the "pre-filled" check passes, we actually SET the data now.
  // This satisfies the "corresponding existing data" requirement in the Then step.
  await updateProfilePage.navigateToUpdateProfile();
  await updateProfilePage.fillProfile(data);
  await updateProfilePage.clickUpdateProfile();

  // Go back to the form to see it pre-filled
  await updateProfilePage.navigateToUpdateProfile();
  (page as any).expectedProfileData = data;
});

When('I view the "Update Profile" form', async ({ page }) => {
  const updateProfilePage = new UpdateProfilePage(page);
  // Already navigated in Background, but let's ensure
  await expect(updateProfilePage.title).toHaveText('Update Profile');
});

Then('the "Email" field should not be visible', async ({ page }) => {
  const updateProfilePage = new UpdateProfilePage(page);
  await updateProfilePage.verifyEmailFieldNotVisible();
});

Then('the fields should be pre-filled with the corresponding existing data', async ({ page }) => {
  const expectedData = (page as any).expectedProfileData;
  if (!expectedData) throw new Error('No expected data found from Given step');

  const updateProfilePage = new UpdateProfilePage(page);

  // If we are strictly following "Immutable Gherkin", and the Gherkin says "Alice",
  // and the app says "John", we have a problem.
  // Real world: we would seed the DB.
  // Here: We might need to update the profile TO Alice first?
  // But we are in the "Initialization" scenario.

  // Workaround: We will assert what is currently there match what is expected. 
  // If it fails, we will see.
  // Exception: if the Gherkin is just illustrative, we might need to be smart.
  // But Gherkin examples are usually strict.

  await updateProfilePage.verifyPreFilledData(expectedData);
});

Then('the submit button should be labeled "UPDATE PROFILE"', async ({ page }) => {
  const updateProfilePage = new UpdateProfilePage(page);
  await updateProfilePage.verifyButtonLabel('Update Profile');
});
