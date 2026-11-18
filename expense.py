
import csv
import os

FILE_NAME = "expenses.csv"


# Add a new expense
def add_expense(date, category, description, amount):

    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Category",
                "Description",
                "Amount"
            ])

        writer.writerow([
            date,
            category,
            description,
            amount
        ])


# Load all saved expenses
def load_expenses():

    expenses = []

    if not os.path.isfile(FILE_NAME):
        return expenses

    with open(FILE_NAME, "r", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:
            expenses.append(row)

    return expenses


# Calculate total expenses
def get_total_expenses():

    total = 0

    expenses = load_expenses()

    for expense in expenses:
        total += float(expense["Amount"])

    return total


# Delete an expense using its row index
def delete_expense(index):

    expenses = load_expenses()

    if index < 0 or index >= len(expenses):
        return False

    # Remove only the selected expense
    expenses.pop(index)

    # Rewrite the CSV file
    with open(FILE_NAME, "w", newline="") as file:

        fieldnames = [
            "Date",
            "Category",
            "Description",
            "Amount"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(expenses)

    return True

