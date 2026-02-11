Feature: SCRUM-303 Update User Profile Information

  As a registered user
  I want to update my contact information (excluding email)
  So that my delivery address and phone number are current

  Background:
    Given I am a logged-in user on the "Update Profile" page

  @Functional @Nominal
  Scenario Outline: Successful profile update with valid data
    Given the current user profile data is loaded
    When I update the profile fields with the following details:
      | First Name | <firstName> |
      | Last Name  | <lastName>  |
      | Address    | <address>   |
      | City       | <city>      |
      | State      | <state>     |
      | Zip Code   | <zipCode>   |
      | Phone #    | <phoneNumber>|
    And I click on the "UPDATE PROFILE" button
    Then I should be redirected to the Confirmation Screen
    And I should see the title "<expectedTitle>"
    And I should see the success message "<expectedMessage>"

    Examples:
      | firstName | lastName | address          | city   | state | zipCode | phoneNumber | expectedTitle   | expectedMessage                                                      |
      | Jhonnn    | Doe      | 123 Baker Street | London | UK    | W1U 6   | 1234567890  | Profile Updated | Your updated address and phone number have been added to the system. |
      | Jane      | Smith    | 456 Elm Blvd     | Oxford | UK    | TextZip |             | Profile Updated | Your updated address and phone number have been added to the system. |

  @Functional @Validation
  Scenario Outline: Validation errors for mandatory fields
    When I clear the "<fieldToClear>" field
    And I click on the "UPDATE PROFILE" button
    Then I should remain on the "Update Profile" page
    And I should see the inline error message "<expectedError>" next to the "<fieldToClear>" field

    Examples:
      | fieldToClear | expectedError           |
      | First Name   | First Name is required. |
      | Last Name    | Last Name is required.  |
      | Address      | Address is required.    |
      | City         | City is required.       |
      | State        | State is required.      |
      | Zip Code     | Zip Code is required.   |

  @UI @Initialization
  Scenario Outline: Verify form structure, pre-filling, and field exclusion
    Given the user has the following existing data:
      | First Name | <existingFirst> |
      | Last Name  | <existingLast>  |
      | Address    | <existingAddr>  |
      | City       | <existingCity>  |
      | State      | <existingState> |
      | Zip Code   | <existingZip>   |
      | Phone #    | <existingPhone> |
    When I view the "Update Profile" form
    Then the "Email" field should not be visible
    And the fields should be pre-filled with the corresponding existing data
    And the submit button should be labeled "UPDATE PROFILE"

    Examples:
      | existingFirst | existingLast | existingAddr  | existingCity | existingState | existingZip | existingPhone |
      | Alice         | Wonderland   | 1 Rabbit Hole | London       | UK            | OX1 1AA     | 1234567890    |
