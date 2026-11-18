import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry

from expense import (
    add_expense as save_expense_record,
    get_total_expenses,
    load_expenses,
    delete_expense,
)
from validation import validate_expense
from analysis import (
    total_spending,
    category_summary,
    highest_spending_category,
)

# ---------------- THEME ----------------

BG = "#f5f7fb"
SURFACE = "#ffffff"
TEXT = "#172033"
MUTED = "#64748b"
BORDER = "#e2e8f0"
BLUE = "#2563eb"
GREEN = "#16a34a"
PURPLE = "#7c3aed"
ORANGE = "#d97706"
RED = "#dc2626"

SETTINGS_FILE = "settings.json"


def load_settings():
    defaults = {"total_available": 0.0, "monthly_budget": 0.0}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)
        return {
            "total_available": float(saved.get("total_available", 0)),
            "monthly_budget": float(saved.get("monthly_budget", 0)),
        }
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        return defaults


def save_settings(total_available, monthly_budget):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {
                "total_available": total_available,
                "monthly_budget": monthly_budget,
            },
            file,
            indent=4,
        )


# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("Intelligent Expense Management System")
root.geometry("1200x850")
root.minsize(980, 760)
root.configure(bg=BG)

# Configure a consistent table style.
style = ttk.Style()
try:
    style.theme_use("clam")
except tk.TclError:
    pass

style.configure(
    "Expense.Treeview",
    background=SURFACE,
    foreground=TEXT,
    fieldbackground=SURFACE,
    rowheight=30,
    font=("Segoe UI", 10),
    borderwidth=0,
)
style.configure(
    "Expense.Treeview.Heading",
    background="#edf2f7",
    foreground=TEXT,
    font=("Segoe UI", 10, "bold"),
    padding=(8, 9),
    relief="flat",
)
style.map(
    "Expense.Treeview",
    background=[("selected", "#dbeafe")],
    foreground=[("selected", TEXT)],
)
style.map(
    "Expense.Treeview.Heading",
    background=[("active", "#e2e8f0")],
)


# ---------------- HEADER ----------------

header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=28, pady=(18, 4))

tk.Label(
    header,
    text="Intelligent Expense Management System",
    font=("Segoe UI", 23, "bold"),
    bg=BG,
    fg=TEXT,
).pack()

tk.Label(
    header,
    text="A budget is telling your money where to go instead of wondering where it went.",
    font=("Segoe UI", 10, "italic"),
    bg=BG,
    fg=MUTED,
).pack(pady=(5, 1))

tk.Label(
    header,
    text="— John C. Maxwell",
    font=("Segoe UI", 9, "bold"),
    bg=BG,
    fg=MUTED,
).pack()


# ---------------- DASHBOARD CARDS ----------------

dashboard_frame = tk.Frame(root, bg=BG)
dashboard_frame.pack(fill="x", padx=28, pady=(14, 10))
dashboard_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cards")


def create_card(parent, column, title, value, accent):
    card = tk.Frame(
        parent,
        bg=SURFACE,
        highlightbackground=BORDER,
        highlightthickness=1,
    )
    card.grid(row=0, column=column, sticky="nsew", padx=7)
    tk.Frame(card, bg=accent, height=5).pack(fill="x")

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 11, "bold"),
        bg=SURFACE,
        fg=MUTED,
    ).pack(pady=(14, 5))

    value_label = tk.Label(
        card,
        text=value,
        font=("Segoe UI", 21, "bold"),
        bg=SURFACE,
        fg=accent,
    )
    value_label.pack(pady=(0, 15))
    return value_label


saved_settings = load_settings()
available_value = saved_settings["total_available"]
budget_value = saved_settings["monthly_budget"]
total_value = get_total_expenses()

expense_amount = create_card(
    dashboard_frame, 0, "Total Spent", f"₹{total_value:.2f}", RED
)
income_amount = create_card(
    dashboard_frame, 1, "Total Available", f"₹{available_value:.2f}", GREEN
)
balance_amount = create_card(
    dashboard_frame, 2, "Remaining Balance",
    f"₹{available_value - total_value:.2f}", BLUE
)
budget_amount = create_card(
    dashboard_frame, 3, "Monthly Budget", f"₹{budget_value:.2f}", ORANGE
)


def update_dashboard_cards():
    settings = load_settings()
    total = get_total_expenses()
    available = float(settings["total_available"])
    budget = float(settings["monthly_budget"])

    expense_amount.config(text=f"₹{total:.2f}")
    income_amount.config(text=f"₹{available:.2f}")
    balance_amount.config(text=f"₹{available - total:.2f}")
    budget_amount.config(text=f"₹{budget:.2f}")


# ---------------- QUICK ACTIONS ----------------

quick_actions = tk.Frame(root, bg=BG)
quick_actions.pack(fill="x", padx=280, pady=(2, 10))


def action_button(parent, text, color, command):
    return tk.Button(
        parent,
        text=text,
        font=("Segoe UI", 10, "bold"),
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        padx=16,
        pady=9,
        cursor="hand2",
        relief="flat",
        bd=0,
        command=command,
    )


# ---------------- ADD EXPENSE FORM ----------------

form_frame = tk.Frame(
    root,
    bg=SURFACE,
    highlightbackground=BORDER,
    highlightthickness=1,
)
# The form is created now but shown only when the user clicks Add Expense.
# It will be packed immediately above Today's Transactions when opened.

tk.Label(
    form_frame,
    text="Add New Expense",
    font=("Segoe UI", 17, "bold"),
    bg=SURFACE,
    fg=TEXT,
).pack(pady=(13, 8))

fields_frame = tk.Frame(form_frame, bg=SURFACE)
fields_frame.pack(pady=(0, 8))
fields_frame.grid_columnconfigure((0, 1), weight=1)

label_options = {
    "font": ("Segoe UI", 10, "bold"),
    "bg": SURFACE,
    "fg": MUTED,
}

tk.Label(fields_frame, text="Date (DD-MM-YYYY)", **label_options).grid(
    row=0, column=0, padx=18, pady=(2, 5), sticky="w"
)
date_entry = DateEntry(
    fields_frame,
    font=("Segoe UI", 11),
    width=27,
    date_pattern="dd-mm-yyyy",
    background="#1e3a5f",
    foreground="white",
    borderwidth=1,
)
date_entry.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="ew")

tk.Label(fields_frame, text="Category", **label_options).grid(
    row=0, column=1, padx=18, pady=(2, 5), sticky="w"
)
category_entry = ttk.Combobox(
    fields_frame,
    font=("Segoe UI", 11),
    width=28,
    values=[
        "Food", "Shopping", "Travel", "Education",
        "Entertainment", "Bills", "Health", "Other",
    ],
    state="normal",
)
category_entry.grid(row=1, column=1, padx=18, pady=(0, 8), sticky="ew")

tk.Label(fields_frame, text="Description", **label_options).grid(
    row=2, column=0, padx=18, pady=(2, 5), sticky="w"
)
description_entry = tk.Entry(
    fields_frame,
    font=("Segoe UI", 11),
    width=30,
    bd=1,
    relief="solid",
)
description_entry.grid(row=3, column=0, padx=18, pady=(0, 8), sticky="ew")

tk.Label(fields_frame, text="Amount (₹)", **label_options).grid(
    row=2, column=1, padx=18, pady=(2, 5), sticky="w"
)
amount_entry = tk.Entry(
    fields_frame,
    font=("Segoe UI", 11),
    width=30,
    bd=1,
    relief="solid",
)
amount_entry.grid(row=3, column=1, padx=18, pady=(0, 8), sticky="ew")

DESCRIPTION_PLACEHOLDER = "e.g. Lunch with friends"
AMOUNT_PLACEHOLDER = "e.g. 500"


def add_placeholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg="#94a3b8")

    def on_focus_in(_event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg=TEXT)

    def on_focus_out(_event):
        if not entry.get().strip():
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.config(fg="#94a3b8")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def reset_placeholder(entry, placeholder):
    entry.delete(0, tk.END)
    entry.insert(0, placeholder)
    entry.config(fg="#94a3b8")


add_placeholder(description_entry, DESCRIPTION_PLACEHOLDER)
add_placeholder(amount_entry, AMOUNT_PLACEHOLDER)


# ---------------- TODAY'S TRANSACTIONS ----------------

today_frame = tk.Frame(
    root,
    bg=SURFACE,
    highlightbackground=BORDER,
    highlightthickness=1,
)
today_frame.pack(fill="both", expand=True, padx=35, pady=(0, 16))

today_header = tk.Frame(today_frame, bg=SURFACE)
today_header.pack(fill="x", padx=16, pady=(11, 4))

tk.Label(
    today_header,
    text="Today's Transactions",
    font=("Segoe UI", 16, "bold"),
    bg=SURFACE,
    fg=TEXT,
).pack()

tk.Label(
    today_header,
    text="Showing today's expense records",
    font=("Segoe UI", 9),
    bg=SURFACE,
    fg=MUTED,
).pack(pady=(2, 0))

columns = ("Date", "Category", "Description", "Amount")
table_container = tk.Frame(today_frame, bg=SURFACE)
table_container.pack(fill="both", expand=True, padx=14, pady=(7, 13))

transaction_table = ttk.Treeview(
    table_container,
    columns=columns,
    show="headings",
    height=5,
    style="Expense.Treeview",
)

for column in columns:
    transaction_table.heading(column, text=column)
    transaction_table.column(column, anchor="center", width=200, stretch=True)

transaction_table.column("Description", width=300, stretch=True)
transaction_table.pack(side="left", fill="both", expand=True)

today_scrollbar = ttk.Scrollbar(
    table_container,
    orient="vertical",
    command=transaction_table.yview,
)
transaction_table.configure(yscrollcommand=today_scrollbar.set)
today_scrollbar.pack(side="right", fill="y")


def refresh_transactions():
    for row in transaction_table.get_children():
        transaction_table.delete(row)

    today = date.today()
    for expense in load_expenses():
        try:
            expense_date = datetime.strptime(
                expense["Date"], "%d-%m-%Y"
            ).date()
        except (ValueError, TypeError):
            continue

        if expense_date == today:
            try:
                amount_text = f"₹{float(expense['Amount']):.2f}"
            except (ValueError, TypeError):
                amount_text = expense.get("Amount", "")

            transaction_table.insert(
                "",
                "end",
                values=(
                    expense.get("Date", ""),
                    expense.get("Category", ""),
                    expense.get("Description", ""),
                    amount_text,
                ),
            )


def toggle_add_form():
    """Show or hide the Add Expense form above today's transaction table."""
    if form_frame.winfo_manager():
        form_frame.pack_forget()
        add_expense_action_button.config(text="＋ Add Expense")
    else:
        form_frame.pack(fill="x", padx=35, pady=(0, 12), before=today_frame)
        add_expense_action_button.config(text="✕ Close Form")
        date_entry.focus_set()


def hide_add_form():
    if form_frame.winfo_manager():
        form_frame.pack_forget()
    add_expense_action_button.config(text="＋ Add Expense")


# ---------------- SETTINGS WINDOW ----------------

def show_settings_window():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("460x360")
    settings_window.resizable(False, False)
    settings_window.configure(bg=BG)
    settings_window.transient(root)
    settings_window.grab_set()

    panel = tk.Frame(
        settings_window,
        bg=SURFACE,
        highlightbackground=BORDER,
        highlightthickness=1,
    )
    panel.pack(fill="both", expand=True, padx=22, pady=22)

    tk.Label(
        panel,
        text="Manage Your Settings",
        font=("Segoe UI", 17, "bold"),
        bg=SURFACE,
        fg=TEXT,
    ).pack(pady=(20, 16))

    current = load_settings()

    tk.Label(
        panel, text="Total Available Money (₹)", **label_options
    ).pack(anchor="w", padx=55, pady=(4, 5))
    available_entry = tk.Entry(panel, font=("Segoe UI", 12), width=28)
    available_entry.pack()
    available_entry.insert(0, str(current["total_available"]))

    tk.Label(
        panel, text="Monthly Budget (₹)", **label_options
    ).pack(anchor="w", padx=55, pady=(15, 5))
    budget_entry = tk.Entry(panel, font=("Segoe UI", 12), width=28)
    budget_entry.pack()
    budget_entry.insert(0, str(current["monthly_budget"]))

    def update_settings():
        try:
            available = float(available_entry.get().strip())
            budget = float(budget_entry.get().strip())
            if available < 0 or budget < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Input",
                "Enter valid amounts greater than or equal to zero.",
                parent=settings_window,
            )
            return

        try:
            save_settings(available, budget)
        except OSError as error:
            messagebox.showerror(
                "Save Error", f"Could not save settings:\n{error}",
                parent=settings_window,
            )
            return

        update_dashboard_cards()
        messagebox.showinfo(
            "Success", "Settings saved successfully!",
            parent=settings_window,
        )
        settings_window.destroy()

    tk.Button(
        panel,
        text="Save Settings",
        font=("Segoe UI", 10, "bold"),
        bg=GREEN,
        fg="white",
        activebackground="#15803d",
        activeforeground="white",
        padx=22,
        pady=9,
        relief="flat",
        cursor="hand2",
        command=update_settings,
    ).pack(pady=22)


# ---------------- FULL HISTORY WINDOW ----------------

def show_full_history():
    history_window = tk.Toplevel(root)
    history_window.title("Full Expense History")
    history_window.geometry("1000x600")
    history_window.minsize(800, 450)
    history_window.configure(bg=BG)

    tk.Label(
        history_window,
        text="Full Expense History",
        font=("Segoe UI", 20, "bold"),
        bg=BG,
        fg=TEXT,
    ).pack(pady=(18, 8))

    search_frame = tk.Frame(history_window, bg=BG)
    search_frame.pack(fill="x", padx=22, pady=8)

    search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), width=38)
    search_entry.pack(side="left", padx=(0, 8), ipady=5)

    history_table_frame = tk.Frame(history_window, bg=SURFACE)
    history_table_frame.pack(fill="both", expand=True, padx=22, pady=10)

    history_table = ttk.Treeview(
        history_table_frame,
        columns=columns,
        show="headings",
        height=15,
        style="Expense.Treeview",
    )
    for column in columns:
        history_table.heading(column, text=column)
        history_table.column(column, width=220, anchor="center", stretch=True)
    history_table.column("Description", width=300, stretch=True)
    history_table.pack(side="left", fill="both", expand=True)

    history_scrollbar = ttk.Scrollbar(
        history_table_frame,
        orient="vertical",
        command=history_table.yview,
    )
    history_table.configure(yscrollcommand=history_scrollbar.set)
    history_scrollbar.pack(side="right", fill="y")

    def refresh_history(search_text=""):
        for row in history_table.get_children():
            history_table.delete(row)

        for index, expense in enumerate(load_expenses()):
            searchable = " ".join(
                str(expense.get(field, ""))
                for field in ("Date", "Category", "Description", "Amount")
            ).lower()

            if search_text.lower().strip() in searchable:
                try:
                    amount_text = f"₹{float(expense['Amount']):.2f}"
                except (ValueError, TypeError):
                    amount_text = expense.get("Amount", "")

                history_table.insert(
                    "",
                    "end",
                    iid=str(index),
                    values=(
                        expense.get("Date", ""),
                        expense.get("Category", ""),
                        expense.get("Description", ""),
                        amount_text,
                    ),
                )

    def search_history():
        refresh_history(search_entry.get())

    def clear_search():
        search_entry.delete(0, tk.END)
        refresh_history()

    def delete_selected():
        selected = history_table.selection()
        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an expense to delete.",
                parent=history_window,
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete the selected expense?",
            parent=history_window,
        ):
            return

        # The row iid is the original CSV list index.
        selected_index = int(selected[0])
        if delete_expense(selected_index):
            refresh_history(search_entry.get())
            refresh_transactions()
            update_dashboard_cards()
            messagebox.showinfo(
                "Success",
                "Expense deleted successfully!",
                parent=history_window,
            )
        else:
            messagebox.showerror(
                "Delete Error",
                "The selected expense could not be found.",
                parent=history_window,
            )

    action_button(
        search_frame, "Search", BLUE, search_history
    ).pack(side="left", padx=4)
    action_button(
        search_frame, "Clear", "#64748b", clear_search
    ).pack(side="left", padx=4)

    action_button(
        history_window,
        "Delete Selected Expense",
        RED,
        delete_selected,
    ).pack(pady=(2, 14))

    search_entry.bind("<Return>", lambda _event: search_history())
    refresh_history()


# ---------------- EXPENSE ANALYSIS WINDOW ----------------

def show_analysis_window():
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Expense Analysis")
    analysis_window.geometry("560x500")
    analysis_window.minsize(450, 350)
    analysis_window.configure(bg=BG)

    tk.Label(
        analysis_window,
        text="Expense Analysis",
        font=("Segoe UI", 20, "bold"),
        bg=BG,
        fg=TEXT,
    ).pack(pady=(18, 12))

    total = total_spending()
    summary = category_summary()
    highest_category, highest_amount = highest_spending_category()

    summary_card = tk.Frame(
        analysis_window,
        bg=SURFACE,
        highlightbackground=BORDER,
        highlightthickness=1,
    )
    summary_card.pack(fill="x", padx=25, pady=8)

    tk.Label(
        summary_card,
        text=f"Total Spending: ₹{total:.2f}",
        font=("Segoe UI", 15, "bold"),
        bg=SURFACE,
        fg=RED,
    ).pack(pady=15)

    tk.Label(
        analysis_window,
        text="Category-wise Spending",
        font=("Segoe UI", 13, "bold"),
        bg=BG,
        fg=TEXT,
    ).pack(pady=(14, 6))

    category_frame = tk.Frame(analysis_window, bg=SURFACE)
    category_frame.pack(fill="both", expand=True, padx=25, pady=5)

    if summary:
        for category, amount in summary.items():
            tk.Label(
                category_frame,
                text=f"{category}: ₹{amount:.2f}",
                font=("Segoe UI", 11),
                bg=SURFACE,
                fg=TEXT,
                anchor="w",
            ).pack(fill="x", padx=18, pady=5)
    else:
        tk.Label(
            category_frame,
            text="No expenses found yet.",
            font=("Segoe UI", 11),
            bg=SURFACE,
            fg=MUTED,
        ).pack(pady=20)

    if highest_category is not None:
        highest_text = (
            f"Highest Spending: {highest_category} "
            f"(₹{highest_amount:.2f})"
        )
    else:
        highest_text = "No expenses found."

    tk.Label(
        analysis_window,
        text=highest_text,
        font=("Segoe UI", 11, "bold"),
        bg=BG,
        fg=BLUE,
    ).pack(pady=14)


# ---------------- BUTTONS ----------------

# Arrange the four main actions in a centered 2-by-2 layout.
quick_actions.grid_columnconfigure((0, 1), weight=1, uniform="actions")

add_expense_action_button = action_button(
    quick_actions, "＋ Add Expense", BLUE,
    lambda: toggle_add_form()
)
add_expense_action_button.grid(row=0, column=0, padx=7, pady=5, sticky="ew")

action_button(
    quick_actions, "▥ View Expense Analysis", GREEN,
    show_analysis_window
).grid(row=0, column=1, padx=7, pady=5, sticky="ew")

action_button(
    quick_actions, "◷ View Full History", PURPLE,
    show_full_history
).grid(row=1, column=0, padx=7, pady=5, sticky="ew")

action_button(
    quick_actions, "⚙ Settings", ORANGE,
    show_settings_window
).grid(row=1, column=1, padx=7, pady=5, sticky="ew")


def add_expense():
    expense_date = date_entry.get()
    category = category_entry.get().strip()

    description = description_entry.get().strip()
    if description == DESCRIPTION_PLACEHOLDER:
        description = ""

    amount_text = amount_entry.get().strip()
    if amount_text == AMOUNT_PLACEHOLDER:
        amount_text = ""

    is_valid, message = validate_expense(
        expense_date, category, description, amount_text
    )
    if not is_valid:
        messagebox.showerror("Invalid Expense", message, parent=root)
        return

    try:
        save_expense_record(
            expense_date,
            category,
            description,
            float(amount_text),
        )
    except (OSError, ValueError) as error:
        messagebox.showerror(
            "Save Error", f"Could not save expense:\n{error}", parent=root
        )
        return

    refresh_transactions()
    update_dashboard_cards()

    date_entry.set_date(date.today())
    category_entry.set("")
    reset_placeholder(description_entry, DESCRIPTION_PLACEHOLDER)
    reset_placeholder(amount_entry, AMOUNT_PLACEHOLDER)

    hide_add_form()
    messagebox.showinfo(
        "Success", "Expense saved successfully!", parent=root
    )


action_button(
    form_frame, "Add Expense", BLUE, add_expense
).pack(pady=(0, 14))

# Load today's records when the application starts.
refresh_transactions()

root.mainloop()
