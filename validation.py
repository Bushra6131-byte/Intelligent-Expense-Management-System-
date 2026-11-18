from datetime import datetime


def validate_expense(date, category, description, amount):

    # Check empty fields
    if not date or not category or not description or not amount:
        return False, "Please fill all fields."

    # Check date format
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        return False, "Date must be in DD-MM-YYYY format."

    # Check category
    if not category.strip():
        return False, "Category cannot be empty."

    # Check description
    if not description.strip():
        return False, "Description cannot be empty."

    # Check amount
    try:
        amount = float(amount)
    except ValueError:
        
        return False, "Amount must be a number."

    if amount <= 0:
        return False, "Amount must be greater than zero."

    return True, "Expense details are valid."