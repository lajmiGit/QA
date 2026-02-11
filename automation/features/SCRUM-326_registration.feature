@SCRUM-189
Feature: User Registration
  As a new user
  I want to register an account
  So that I can access the platform services

  Background:
    Given the user navigates to the registration page via the 'Register' link
    Then the page title should be "Signing up is easy!"

  @SCRUM-341
  Scenario Outline: Successful registration with different phone number states
    When the user fills the form with "<firstName>", "<lastName>", "<address>", "<city>", "<state>", "<zipCode>", "<phone>", "<ssn>", "<username>", "<password>", and "<confirm>"
    And they click the "Register" button
    Then the success message "Your account was created successfully. You are now logged in." is displayed
    And the banner displays "Welcome <username>"

    Examples:
      | firstName | lastName | address      | city     | state | zipCode | phone    | ssn       | username      | password | confirm  |
      | John      | Doe      |  123 Main St | New York | NY    |   10001 | 555-0199 | 999-00-01 | jdoe_purist   | Pass123  | Pass123  |
      | Jane      | Smith    | 456 Park Ave | Boston   | MA    |   02108 |          |   987-654 | jsmith_purist | Secure98 | Secure98 |

  @SCRUM-340
  Scenario Outline: Validation of mandatory fields
    When the user leaves the mandatory field "<field_missing>" empty
    And they fill all other required fields correctly
    And they click the "Register" button
    Then the inline error message "<error_message>" is displayed in red to the right of the field

    Examples:
      | field_missing | error_message                       |
      | First Name    | First name is required.             |
      | Last Name     | Last name is required.              |
      | Address       | Address is required.                |
      | City          | City is required.                   |
      | State         | State is required.                  |
      | Zip Code      | Zip Code is required.               |
      | SSN           | Social Security Number is required. |
      | Username      | Username is required.               |
      | Password      | Password is required.               |
      | Confirm       | Password confirmation is required.  |

  @SCRUM-339
  Scenario Outline: Verification of username uniqueness
    Given an account already exists with the username "<existing_user>"
    When the user enters "<existing_user>" in the registration username field
    And they fill all other required fields correctly
    And they click the "Register" button
    Then the inline error message "This username already exists." is displayed in red

    Examples:
      | existing_user |
      | john          |

  @SCRUM-330
  Scenario Outline: Password mismatch and security UX behavior
    When the user enters "<password>" in the registration password field
    And they enter "<confirm>" in the registration confirmation field
    And they fill all other required fields correctly
    And they click the "Register" button
    Then the inline error message "Passwords did not match." is displayed in red
    And the "Password" and "Confirm" fields are cleared by the system

    Examples:
      | password   | confirm     |
      | complex123 | mismatch456 |
      | CaseSens   | casesens    |
