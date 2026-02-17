Feature: User Registration
  As a new visitor
  I want to register an account
  So that I can access restricted banking features

  Background:
    Given I am on the ParaBank home page
    When I click the "Register" link from the left menu
    Then I should see the page title "Signing up is easy!"

  @RG-001 @RG-002 @RG-007 @RG-008 @RG-009
  Scenario Outline: Successful account registration with valid data
    Given I fill the registration form with the following details:
      | First Name | <firstName> |
      | Last Name  | <lastName>  |
      | Address    | <address>   |
      | City       | <city>      |
      | State      | <state>     |
      | Zip Code   | <zipCode>   |
      | Phone      | <phone>     |
      | SSN        | <ssn>       |
      | Username   | <unique>    |
      | Password   | <password>  |
      | Confirm    | <password>  |
    When I submit the registration form
    Then I should be redirected to the success page
    And I should see the success message "Your account was created successfully. You are now logged in."
    And I should see the welcome message "Welcome <unique>"

    Examples:
      | firstName | lastName | address     | city     | state | zipCode | phone    | ssn         | password | unique        |
      | John      | Doe      | 123 Main St | New York | NY    |   10001 | 555-0100 | 123-45-6789 | Pass1234 | user_auto_123 |
      | Jane      | Smith    | 456 Elm Ave | Austin   | TX    |   73301 |          | 987-65-4321 | Secure!1 | user_auto_456 |

  @RG-004 @RG-006 @RG-010
  Scenario Outline: Registration fails due to password mismatch
    Given I fill the registration form with valid data but mismatching passwords:
      | Password | <password> |
      | Confirm  | <confirm>  |
    When I submit the registration form
    Then I should see the error message "Passwords did not match."
    And the password fields should be automatically reset

    Examples:
      | password | confirm  |
      | secret12 | secret99 |
      | abcdefg  | abcDEFG  |

  @RG-005 @RG-006 @RG-010
  Scenario Outline: Registration fails due to existing username
    Given a user already exists with the username "<existingUser>"
    When I fill the registration form using the username "<existingUser>"
    And I submit the registration form
    Then I should see the error message "This username already exists."
    And the password fields should be automatically reset

    Examples:
      | existingUser |
      | admin        |
      | demo         |

  @RG-003 @RG-006 @RG-010
  Scenario Outline: Registration fails when mandatory fields are missing
    When I leave the "<field>" field empty
    And I submit the registration form
    Then I should see the inline error message "<errorMessage>"
    And the password fields should be automatically reset

    Examples:
      | field      | errorMessage                        |
      | First Name | First name is required.             |
      | Last Name  | Last name is required.              |
      | Address    | Address is required.                |
      | City       | City is required.                   |
      | State      | State is required.                  |
      | Zip Code   | Zip Code is required.               |
      | SSN        | Social Security Number is required. |
      | Username   | Username is required.               |
      | Password   | Password is required.               |
      | Confirm    | Password confirmation is required.  |
