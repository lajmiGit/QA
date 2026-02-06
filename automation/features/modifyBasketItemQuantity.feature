@SCRUM-8
Feature: Modify Item Quantity in Shopping Basket

  Background:
    Given the user is on the shopping cart page

  @SCRUM-95
  Scenario: Increase quantity of an item
    When the user increases the quantity of "Keyboard" from 1 to 2
    Then the quantity of "Keyboard" in the cart should be 2
