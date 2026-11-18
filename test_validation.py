
from validation import validate_expense


print("===== EXPENSE VALIDATION TESTING =====")


# Test 1: Correct expense
print("\nTest 1: Valid Expense")
print(validate_expense("15-11-2026", "Food", "Lunch", "250"))


# Test 2: Empty fields
print("\nTest 2: Empty Fields")
print(validate_expense("", "", "", ""))


# Test 3: Wrong date format
print("\nTest 3: Invalid Date")
print(validate_expense("2026/11/15", "Food", "Lunch", "250"))


# Test 4: Text instead of amount
print("\nTest 4: Invalid Amount")
print(validate_expense("15-11-2026", "Food", "Lunch", "abc"))


# Test 5: Negative amount
print("\nTest 5: Negative Amount")
print(validate_expense("15-11-2026", "Food", "Lunch", "-500"))


# Test 6: Zero amount
print("\nTest 6: Zero Amount")
print(validate_expense("15-11-2026", "Food", "Lunch", "0"))
