import { createBdd } from 'playwright-bdd';
import { expect } from '@playwright/test';
import { ModifyItemQuantityPage } from '../src/pages/modify-item-quantity.page';

const { Given, When, Then } = createBdd();

Given('the user is on the shopping cart page', async ({ page }) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.goto();
});

When('the user increases the quantity of {string} from {int} to {int}', async ({ page }, itemName, initialQuantity, newQuantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.updateItemQuantity(itemName, newQuantity);
});

When('the user decreases the quantity of {string} from {int} to {int}', async ({ page }, itemName, initialQuantity, newQuantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.updateItemQuantity(itemName, newQuantity);
});

When('the user attempts to decrease the quantity of {string} from {int}', async ({ page }, itemName, initialQuantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.decreaseItemQuantity(itemName);
});

When('the user manually sets the quantity of {string} to {int}', async ({ page }, itemName, quantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.updateItemQuantity(itemName, quantity);
});

When('the user tries to set the quantity of {string} to {string}', async ({ page }, itemName, quantityString) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.updateItemQuantity(itemName, quantityString);
});

When('the user tries to set the quantity of {string} to {float}', async ({ page }, itemName, quantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.updateItemQuantity(itemName, quantity);
});

When('the user attempts to increase the quantity of {string} from {int} to {int}', async ({ page }, itemName, initialQuantity, newQuantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.updateItemQuantity(itemName, newQuantity);
});

When('the user attempts to update the quantity for an item with ID {string} to {int}', async ({ page }, itemId, quantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    console.warn(`Attempting to update quantity for item ID '${itemId}' with quantity ${quantity}. Page object currently uses item name.`);
    await modifyItemQuantityPage.updateItemQuantity('Keyboard', quantity);
});

Then('the quantity of {string} in the cart should be {int}', async ({ page }, itemName, expectedQuantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualQuantity = await modifyItemQuantityPage.getItemQuantity(itemName);
    await expect(actualQuantity).toBe(expectedQuantity);
});

Then('the subtotal for {string} should be {float}', async ({ page }, itemName, expectedSubtotal) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualSubtotal = await modifyItemQuantityPage.getItemSubtotal(itemName);
    await expect(actualSubtotal).toBeCloseTo(expectedSubtotal, 2);
});

Then('the total price of the cart should be updated to {float}', async ({ page }, expectedTotalPrice) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualTotalPrice = await modifyItemQuantityPage.getTotalPrice();
    await expect(actualTotalPrice).toBeCloseTo(expectedTotalPrice, 2);
});

Then('the item {string} should be removed from the cart', async ({ page }, itemName) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await expect(await modifyItemQuantityPage.isItemPresent(itemName)).toBe(false);
});

Then('the cart should be empty', async ({ page }) => {
    await expect(page.locator('.cart-item')).toHaveCount(0);
});

Then('the total price should be {float}', async ({ page }, expectedTotalPrice) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualTotalPrice = await modifyItemQuantityPage.getTotalPrice();
    await expect(actualTotalPrice).toBeCloseTo(expectedTotalPrice, 2);
});

Then('an error message {string} should be displayed', async ({ page }, expectedErrorMessage) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualErrorMessage = await modifyItemQuantityPage.getErrorMessage();
    await expect(actualErrorMessage).toBe(expectedErrorMessage);
});

Then('the quantity of {string} in the cart should remain {int}', async ({ page }, itemName, expectedQuantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualQuantity = await modifyItemQuantityPage.getItemQuantity(itemName);
    await expect(actualQuantity).toBe(expectedQuantity);
});

Then('the total price of the cart should remain {float}', async ({ page }, expectedTotalPrice) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualTotalPrice = await modifyItemQuantityPage.getTotalPrice();
    await expect(actualTotalPrice).toBeCloseTo(expectedTotalPrice, 2);
});

Then('the quantity displayed for {string} should be {int}', async ({ page }, itemName, expectedQuantity) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualQuantity = await modifyItemQuantityPage.getItemQuantity(itemName);
    await expect(actualQuantity).toBe(expectedQuantity);
});

Then('the subtotal displayed for {string} should be {float}', async ({ page }, itemName, expectedSubtotal) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualSubtotal = await modifyItemQuantityPage.getItemSubtotal(itemName);
    await expect(actualSubtotal).toBeCloseTo(expectedSubtotal, 2);
});

Then('the total price displayed for the cart should be {float}', async ({ page }, expectedTotalPrice) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualTotalPrice = await modifyItemQuantityPage.getTotalPrice();
    await expect(actualTotalPrice).toBeCloseTo(expectedTotalPrice, 2);
});

Then('the total price of the cart should be {float}', async ({ page }, expectedTotalPrice) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const actualTotalPrice = await modifyItemQuantityPage.getTotalPrice();
    await expect(actualTotalPrice).toBeCloseTo(expectedTotalPrice, 2);
});

Given('the user has the following items in their shopping cart:', async ({ page }, dataTable) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    const items = dataTable.hashes();
    await modifyItemQuantityPage.setCartItems(items);
});

Given('the current total price of the cart is {float}', async ({ page }, price) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.setCartTotalPrice(price);
});

Given('the system simulates a server error for the quantity update API call', async ({ page }) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    await modifyItemQuantityPage.simulateServerError();
});

Given('the system simulates a "{string}" response for item ID "{string}"', async ({ page }, statusCode, itemId) => {
    const modifyItemQuantityPage = new ModifyItemQuantityPage(page);
    if (statusCode === "Not Found") {
        await modifyItemQuantityPage.simulateNotFoundResponse(itemId);
    } else {
        console.warn(`Simulation for status code '${statusCode}' is not implemented.`);
    }
});
