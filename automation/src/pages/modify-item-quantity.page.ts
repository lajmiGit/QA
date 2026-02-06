import { Page, expect } from '@playwright/test';

export class ModifyItemQuantityPage {
    readonly page: Page;

    constructor(page: Page) {
        this.page = page;
    }

    async goto() {
        await this.page.goto('/cart'); // Assuming cart is the relevant page
    }

    async getItemRow(itemName: string) {
        return this.page.locator(`//td[text()='${itemName}']/ancestor::tr`);
    }

    async updateItemQuantity(itemName: string, quantity: number | string) {
        const itemRow = await this.getItemRow(itemName);
        const quantityInput = itemRow.locator('input[type="number"]'); // Adjust selector as needed
        await quantityInput.fill(quantity.toString());
        await quantityInput.press('Enter'); // Or click an update button
        // Optional: Add a small wait or assertion to ensure update is processed
        await this.page.waitForLoadState('networkidle');
    }

    async increaseItemQuantity(itemName: string) {
        const itemRow = await this.getItemRow(itemName);
        // Assuming there's a '+' button or similar to increase quantity
        await itemRow.locator('button.increase-quantity').click(); // Adjust selector
        await this.page.waitForLoadState('networkidle');
    }

    async decreaseItemQuantity(itemName: string) {
        const itemRow = await this.getItemRow(itemName);
        // Assuming there's a '-' button or similar to decrease quantity
        await itemRow.locator('button.decrease-quantity').click(); // Adjust selector
        await this.page.waitForLoadState('networkidle');
    }

    async getItemQuantity(itemName: string): Promise<number> {
        const itemRow = await this.getItemRow(itemName);
        const quantityInput = itemRow.locator('input[type="number"]'); // Adjust selector
        const quantity = await quantityInput.inputValue();
        return parseInt(quantity, 10);
    }

    async getItemSubtotal(itemName: string): Promise<number> {
        const itemRow = await this.getItemRow(itemName);
        // Assuming subtotal is displayed in a specific element within the row
        const subtotalText = await itemRow.locator('.item-subtotal').textContent(); // Adjust selector
        return parseFloat(subtotalText.replace(/[^0-9.]/g, ''));
    }

    async getTotalPrice(): Promise<number> {
        const totalPriceText = await this.page.locator('#total-price').textContent(); // Adjust selector for total price
        return parseFloat(totalPriceText.replace(/[^0-9.]/g, ''));
    }

    async isItemPresent(itemName: string): Promise<boolean> {
        return this.page.isVisible(`//td[text()='${itemName}']`);
    }

    async getErrorMessage(): Promise<string | null> {
        const errorMessageElement = this.page.locator('.error-message'); // Adjust selector for error messages
        if (await errorMessageElement.isVisible()) {
            return await errorMessageElement.textContent();
        }
        return null;
    }

    async simulateServerError() {
        // This is a placeholder. Actual implementation depends on how you mock API calls.
        // For example, using playwright's request interception.
        await this.page.route('**/api/update-cart', async route => {
            await route.fulfill({
                status: 500,
                contentType: 'application/json',
                body: JSON.stringify({ message: 'Internal Server Error' }),
            });
        });
    }

    async simulateNotFoundResponse(itemId: string) {
        // This is a placeholder. Actual implementation depends on how you mock API calls.
        await this.page.route(`**/api/cart/${itemId}`, async route => {
            await route.fulfill({
                status: 404,
                contentType: 'application/json',
                body: JSON.stringify({ message: 'Item not found' }),
            });
        });
    }

    async setCartItems(items: Array<{ item_name: string, quantity: number, unit_price: number }>)
    {
        // This method is for setting up the cart state for tests, potentially via API or specific UI actions
        // depending on how your application handles initial cart state.
        // For now, we'll assume it's done by other means or is part of a background step.
        console.log('Setting cart items:', items);
    }

    async setCartTotalPrice(price: number) {
        // Similar to setCartItems, this is for setup.
        console.log('Setting cart total price to:', price);
    }
}
