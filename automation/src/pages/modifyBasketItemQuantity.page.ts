import { Page, expect } from '@playwright/test';

export class ModifyBasketItemQuantityPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // Locators
  private getBasketItemRow(itemName: string) {
    return this.page.locator(`div.basket-item[data-test='basket-item-${itemName}']`);
  }

  private getBasketItemQuantityInput(itemName: string) {
    return this.getBasketItemRow(itemName).locator('input[data-test="item-quantity-input"]');
  }

  private getBasketItemPrice(itemName: string) {
    return this.getBasketItemRow(itemName).locator('[data-test="item-price"]');
  }

  private getBasketItemRemoveButton(itemName: string) {
    return this.getBasketItemRow(itemName).locator('button[data-test="remove-item-button"]');
  }

  private getTotalBasketAmount() {
    return this.page.locator('[data-test="total-basket-amount"]');
  }

  private getErrorMessage() {
    return this.page.locator('[data-test="error-message"]');
  }

  // Actions
  async increaseQuantity(itemName: string, amount: number) {
    const quantityInput = this.getBasketItemQuantityInput(itemName);
    await quantityInput.fill((await quantityInput.inputValue()) + amount);
    await quantityInput.press('Enter'); // To trigger update
  }

  async decreaseQuantity(itemName: string, amount: number) {
    const quantityInput = this.getBasketItemQuantityInput(itemName);
    const currentQuantity = parseInt(await quantityInput.inputValue(), 10);
    await quantityInput.fill((currentQuantity - amount).toString());
    await quantityInput.press('Enter'); // To trigger update
  }

  async setQuantity(itemName: string, quantity: number) {
    const quantityInput = this.getBasketItemQuantityInput(itemName);
    await quantityInput.fill(quantity.toString());
    await quantityInput.press('Enter'); // To trigger update
  }

  async attemptToUpdateQuantityOfNonExistentItem(quantity: number) {
    // Assuming there's a general input or a way to trigger for a non-existent item
    // This might need adjustment based on actual UI implementation
    await this.page.fill('[data-test="non-existent-item-input"]', quantity.toString());
    await this.page.press('[data-test="non-existent-item-input"]', 'Enter');
  }

  async simulateTechnicalErrorDuringUpdate(itemName: string) {
    // This is a placeholder for simulating an error. In a real scenario,
    // this would likely involve mocking API responses or specific UI interactions.
    console.log(`Simulating technical error for ${itemName}`);
    // For now, we'll just proceed without a real simulation.
  }

  // Assertions
  async assertItemQuantity(itemName: string, expectedQuantity: number) {
    const quantityInput = this.getBasketItemQuantityInput(itemName);
    await expect(quantityInput).toHaveValue(expectedQuantity.toString());
  }

  async assertItemPrice(itemName: string, expectedPrice: string) {
    const priceElement = this.getBasketItemPrice(itemName);
    await expect(priceElement).toHaveText(expectedPrice);
  }

  async assertItemRemoved(itemName: string) {
    await expect(this.getBasketItemRow(itemName)).not.toBeVisible();
  }

  async assertTotalBasketAmount(expectedAmount: string) {
    await expect(this.getTotalBasketAmount()).toHaveText(expectedAmount);
  }

  async assertErrorMessage(expectedMessage: string) {
    await expect(this.getErrorMessage()).toBeVisible();
    await expect(this.getErrorMessage()).toHaveText(expectedMessage);
  }

  async assertNoErrorMessage() {
    await expect(this.getErrorMessage()).not.toBeVisible();
  }

  async assertItemQuantityRemains(itemName: string, expectedQuantity: number) {
    const quantityInput = this.getBasketItemQuantityInput(itemName);
    await expect(quantityInput).toHaveValue(expectedQuantity.toString());
  }
}
