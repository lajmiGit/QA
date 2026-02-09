Feature: User Authentication (US_Login)
  As a registered user
  I want to securely log into the system
  So that I can access my account overview and services

  Background:
    Given the user is on the application home page

  @functional @happy_path
  Scenario Outline: Successful login with valid credentials
    When the user enters "<username>" in the username field
    And the user enters "<password>" in the password field
    And the user clicks the orange "LOG IN" button
    Then the user should be redirected to the "Accounts Overview" page
    And the sidebar should update to show the "Account Services" list
    And a welcome message "Welcome <firstname> <lastname>" should be displayed in the sidebar header

    Examples:
      | username | password | firstname | lastname |
      | jhon     | demo     | Jhon      | Smith    |

  @functional @error_handling @ignore
  Scenario Outline: Login failure due to invalid credentials
    When the user enters "<username>" in the username field
    And the user enters "<password>" in the password field
    And the user clicks the orange "LOG IN" button
    Then the user should remain on the current page
    And an error block should appear with the title "Error!" in blue color
    And the error message should read "<error_message>"
    And the username field should retain the value "<username>"
    And the password field should be empty

    Examples:
      | username   | password   | error_message                                    |
      | wrong.user | pass1234   | The username and password could not be verified. |
      | jhon       | wrong.pass | The username and password could not be verified. |

  @functional @validation
  Scenario Outline: Login validation for missing fields
    When the user enters "<username>" in the username field
    And the user enters "<password>" in the password field
    And the user clicks the orange "LOG IN" button
    Then the user should remain on the current page
    And an error block should appear with the title "Error!" in blue color
    And the error message should read "<error_message>"

    Examples:
      | username | password | error_message                         |
      |          | demo     | Please enter a username and password. |
      | jhon     |          | Please enter a username and password. |
      |          |          | Please enter a username and password. |

  @ui @visual
  Scenario Outline: Verify Login UI elements and states
    Then the login section should be located in the left sidebar
    And the "LOG IN" button should be visible and colored orange
    And the "<link_text>" link should be present but inactive

    Examples:
      | link_text           |
      | Forgot login info?  |
      | Register            |
