
import { test, expect } from '@playwright/test';
import { LoginPage } from '../src/pages/login.page';

test('debug wrong user', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.navigate();
  await loginPage.enterUsername('wrong.user.random.123');
  await loginPage.enterPassword('pass1234');
  await loginPage.clickLoginButton();
  console.log('Current URL:', page.url());
  await expect(page).toHaveURL(/.*index\.htm/);
});
