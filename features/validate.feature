Feature: Validate the input file for a biobox
  In order for developers to build bioboxes
  The validate-input provides useful errors if the input file in invalid
  So that the developer can return these errors to the user

  Scenario Outline: Arguments are missing
   Given an empty file named "thresholds.yml"
     And an empty file named "schema.yml"
    When I run `../../build/validate-input <arguments>`
    Then the stderr should contain exactly:
      """
      usage: validate-input [-h] --schema SCHEMA_FILE --input THRESHOLD_FILE
      validate-input: error: argument <arg> is required

      """
     And the exit status should not be 0

    Examples:
      | arguments           | arg         |
      | --input=input.yml   | --schema/-s |
      | --schema=schema.yml | --input/-i  |