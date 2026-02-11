Feature: Transfer Funds Functionality
  As a registered user of ParaBank
  I want to transfer funds between my accounts
  So that I can manage my finances directly from the application

  Background: User is logged in
    Given the user "John Smith" is logged in

  Scenario Outline: Successful fund transfer between different accounts
    Given the user navigates to the "Transfer Funds" page at "/parabank/transfer.htm"
    When the user enters the amount "<amount>"
    And the user selects the From Account "<from_account>"
    And the user selects the To Account "<to_account>"
    And the user clicks on the "Transfer" button
    Then the transfer should be processed successfully
    And the success message "<message>" should be displayed
    And the displayed message should contain the amount "<amount>"

    Examples: Valid Transfer Data
      | amount | from_account | to_account | message            |
      | 100.00 | 12345        | 12456      | Transfer Complete! |
      | 50.50  | 12456        | 12345      | Transfer Complete! |
