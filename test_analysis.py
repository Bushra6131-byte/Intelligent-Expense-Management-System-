
from analysis import (
    total_spending,
    category_summary,
    highest_spending_category
)

print("TOTAL SPENDING")
print("₹", total_spending())

print("\nCATEGORY-WISE SPENDING")
summary = category_summary()

for category, amount in summary.items():
    print(category, ":", f"₹{amount:.2f}")

print("\nHIGHEST SPENDING CATEGORY")
category, amount = highest_spending_category()

if category is not None:
    print(category, ":", f"₹{amount:.2f}")
else:
    print("No expenses found.")
