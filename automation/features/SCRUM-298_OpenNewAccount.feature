Feature: Open New Account
  As an authenticated customer
  I want to open a new Checking or Savings account
  So that I can manage my funds in separate accounts

  Background:
    Given the user is logged in as a standard customer
    And the user has at least one existing account with number "12345" containing sufficient funds

  Scenario Outline: Navigate to Open New Account page
    Given the user is on the "<current_page>"
    When the user looks at the "Account Services" menu
    Then the option "<menu_link>" should be visible
    And clicking "<menu_link>" redirects to the Open New Account form

    Examples:
      | current_page     | menu_link        |
      | Account Overview | Open New Account |

  Scenario Outline: Successfully open a new account
    Given the user is on the "Open New Account" page
    When the user selects account type "<account_type>"
    And the user selects source account "<source_account_id>" from the dropdown
    And the user clicks the "Open New Account" button
    Then the page title should be "Account Opened!"
    And the message "Congratulations, your account is now open." is displayed
    And the new account number is displayed with the prefix "Your new account number:"
    And the new account number is a clickable link
    And clicking the new account number redirects to the details page of the new account

    Examples:
      | account_type | source_account_id |
      | Checking     | 12345             |
      | Savings      | 12345             |
