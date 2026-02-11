import { test as base } from 'playwright-bdd';
import { LoginPage } from '../pages/login.page';
import { UpdateProfilePage } from '../pages/updateProfile.page';
import { RegistrationPage } from '../pages/registration.page';

type MyFixtures = {
    loginPage: LoginPage;
    updateProfilePage: UpdateProfilePage;
    registrationPage: RegistrationPage;
};

export const test = base.extend<MyFixtures>({
    loginPage: async ({ page }, use) => {
        await use(new LoginPage(page));
    },
    updateProfilePage: async ({ page }, use) => {
        await use(new UpdateProfilePage(page));
    },
    registrationPage: async ({ page }, use) => {
        await use(new RegistrationPage(page));
    },
});

export { expect } from '@playwright/test';
