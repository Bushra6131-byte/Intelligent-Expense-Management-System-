
from expense import load_expenses

# Calculate total spending
def total_spending():

    expenses = load_expenses()
    total = 0

    for expense in expenses:
        total += float(expense["Amount"])

    return total


# Calculate category-wise spending
def category_summary():

    expenses = load_expenses()
    summary = {}

    for expense in expenses:
        category = expense["Category"]
        amount = float(expense["Amount"])

        if category in summary:
            summary[category] += amount
        else:
            summary[category] = amount

    return summary


# Find highest spending category
def highest_spending_category():

    summary = category_summary()

    if not summary:
        return None, 0

    highest_category = max(summary, key=summary.get)

    return highest_category, summary[highest_category]
