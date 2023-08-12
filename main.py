import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import csv
import os
from io import BytesIO, StringIO
import base64
import networkx as nx
import matplotlib.pyplot as plt


# Initialization
if 'persons' not in st.session_state:
    st.session_state.persons = []

if 'expenses' not in st.session_state:
    st.session_state.expenses = []

if 'transfers' not in st.session_state:
    st.session_state.transfers = []

if 'update_sidebar' not in st.session_state:
    st.session_state.update_sidebar = False

if 'previous_split_between' not in st.session_state:
    st.session_state.previous_split_between = []


def calculate_total_paid_by_person(expenses):
    total_paid = {}
    for expense in expenses:
        payer = expense['payer']
        amount = expense['amount']

        if payer in total_paid:
            total_paid[payer] += amount
        else:
            total_paid[payer] = amount

    return total_paid


# UI to add persons
with st.sidebar:
    st.title("Add Person")
    person_name = st.text_input("Name:")
    if st.button("Add Person"):
        if person_name not in st.session_state.persons:
            st.session_state.persons.append(person_name)
            st.success(f"Added {person_name}")
        else:
            st.warning(f"{person_name} already exists!")

    # Signal to update the sidebar
    if st.session_state.update_sidebar:
        st.session_state.update_sidebar = False

    st.subheader("Added Persons:")
    total_paid_by_persons = calculate_total_paid_by_person(st.session_state.expenses)
    for person in st.session_state.persons:
        amount_paid = total_paid_by_persons.get(person, 0)  # get the total amount paid or default to 0
        st.write(f"{person} (Paid: ${amount_paid:.2f})")

    st.title("Make Payment")
    payer_transfer = st.selectbox("Who is transferring?", st.session_state.persons)
    recipient = st.selectbox("Who are they paying?", [p for p in st.session_state.persons if p != payer_transfer])
    transfer_amount = st.number_input("Amount in NZ$:", min_value=0.1, step=0.1, value=10.0)

    if st.button("Submit Payment"):
        transfer_data = {
            "payer": payer_transfer,
            "recipient": recipient,
            "amount": transfer_amount,
            "date": datetime.now().date()
        }
        st.session_state.transfers.append(transfer_data)

        # Create an adjustment in the expense list to reflect the payment
        owes_data = {payer_transfer: -transfer_amount, recipient: transfer_amount}
        adjustment_data = {
            "description": f"{transfer_amount}$ Payment from {payer_transfer} to {recipient}",
            "date": datetime.now().date(),
            "category": "Payment",
            "amount": 0,  # No net change in the total amount
            "payer": payer_transfer,  # This is just to show who initiated the payment
            "owes": owes_data,
            "recurring": False
        }
        st.session_state.expenses.append(adjustment_data)

        # Update the sidebar to reflect changes in total paid
        st.session_state.update_sidebar = not st.session_state.update_sidebar

# UI to add expenses
st.title("Expense Splitter")

expense_description = st.text_input("Expense Description:")
expense_date = st.date_input("Date:", datetime.now())
expense_amount = st.number_input("Amount:", min_value=0.1, step=0.1, key="expense_amount_input", value=10.0)
expense_category = st.selectbox("Category", ["Meals", "Transport", "Activities", "Other"])
payer = st.selectbox("Who paid?", st.session_state.persons)
split_between = st.multiselect("Split between:", st.session_state.persons)

default_split = 0
owes = {}
if split_between:
    default_split = expense_amount / len(split_between)

# Check if current split_between is different from previous_split_between
if st.session_state.previous_split_between != split_between:
    st.session_state.previous_split_between = split_between  # Update previous_split_between with current values

    owes = {}  # Reset the owes dictionary
    for person in split_between:
        owes[person] = st.number_input(f"Amount owed by {person}:", min_value=0.0, max_value=expense_amount, step=0.1,
                                       value=default_split, key=f"owes_{person}")

else:
    for person in split_between:
        if f"owes_{person}" not in st.session_state:
            st.session_state[f"owes_{person}"] = default_split
        owes[person] = st.session_state[f"owes_{person}"]
if not st.session_state.get("edit_mode"):

    if st.button("Add Expense"):
        # Validation: the sum of amounts owed should be equal to the total expense amount
        if sum(owes.values()) != expense_amount:
            st.error("The sum of amounts owed does not match the total expense!")
        else:
            expense_data = {
                "description": expense_description,
                "date": expense_date,
                "category": expense_category,
                "amount": expense_amount,
                "payer": payer,
                "owes": owes,
            }
            st.session_state.expenses.append(expense_data)
            st.success("Expense added!")
            st.session_state.update_sidebar = not st.session_state.update_sidebar

else:
    idx_to_edit = st.session_state.edit_idx
    expense_to_edit = st.session_state.expenses[idx_to_edit]

    expense_description = st.text_input("Expense Description:", value=expense_to_edit['description'])

    if st.button("Save Changes"):
        st.session_state.expenses[idx_to_edit]['description'] = expense_description
        st.success(f"Updated {expense_to_edit['description']} entry!")
        st.session_state.edit_mode = False

st.subheader("Manage Expenses:")
for idx, expense in enumerate(st.session_state.expenses):
    st.write(f"{expense['description']}, Amount: ${expense['amount']}, Paid by: {expense['payer']}")
    edit_btn, delete_btn = st.columns(2)
    if edit_btn.button(f"Edit", key=f"edit_{idx}"):  # unique key based on the index
        st.session_state.edit_mode = True
        st.session_state.edit_idx = idx
    if delete_btn.button(f"Delete", key=f"delete_{idx}"):  # unique key based on the index
        del st.session_state.expenses[idx]
        st.success(f"Deleted {expense['description']} entry!")

if st.session_state.expenses:
    data = []
    for expense in st.session_state.expenses:
        for person, amount in expense['owes'].items():
            color = "red" if amount > 0 else "green"
            sign = "+" if amount > 0 else "-"
            data.append([
                expense['description'],
                expense['date'],
                expense['payer'],
                expense['category'],
                f"<span style='color:{color}'>{sign} ${abs(amount):.2f}</span>",
                person
            ])

    df = pd.DataFrame(data, columns=["Description", "Date", "Payer", "Category", "Amount", "Person"])
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)


def calculate_net_amounts(expenses, persons):
    net = {person: 0 for person in persons}

    for expense in expenses:
        payer = expense['payer']
        for person, amount_owed in expense['owes'].items():
            # Subtract the amount the person owes
            net[person] -= amount_owed
            # Add the amount to the payer
            net[payer] += amount_owed

    return net


# Simplify expenses
def simplify_expenses(net):
    debtors = sorted([(person, amount) for person, amount in net.items() if amount < 0], key=lambda x: x[1])
    creditors = sorted([(person, amount) for person, amount in net.items() if amount > 0], key=lambda x: x[1],
                       reverse=True)

    settlements = []

    while debtors and creditors:
        debtor, debt_amount = debtors[0]
        creditor, credit_amount = creditors[0]

        # If the absolute debt amount is greater than or equal to the credit amount, pay the entire credit
        if abs(debt_amount) >= credit_amount:
            settlements.append((debtor, creditor, credit_amount))
            debtors[0] = (debtor, debt_amount + credit_amount)
            creditors.pop(0)
        else:
            settlements.append((debtor, creditor, abs(debt_amount)))
            creditors[0] = (creditor, credit_amount + debt_amount)
            debtors.pop(0)

        # Clean up lists: remove those whose amounts have been settled
        debtors = [item for item in debtors if item[1] < 0]
        creditors = [item for item in creditors if item[1] > 0]

    return settlements


# Total expenses
if st.button("Calculate Total"):
    totals = {person: 0 for person in st.session_state.persons}
    for expense in st.session_state.expenses:
        for person, amount in expense['owes'].items():
            totals[person] += amount

    for person, total in totals.items():
        st.write(f"{person} owes: ${total:.2f}")

if st.button("Simplify Expenses"):
    net = calculate_net_amounts(st.session_state.expenses, st.session_state.persons)
    settlements = simplify_expenses(net)

    st.subheader("Settlements:")
    for debtor, creditor, amount in settlements:
        st.write(f"{debtor} should pay {creditor} ${amount:.2f}")

st.subheader("Expense Trend Over Time:")

# Prepare data
dates = [expense['date'] for expense in st.session_state.expenses]
unique_dates = sorted(list(set(dates)))

# Dictionary to store cumulative expenses for each person on each date
cumulative_expenses = {person: [0 for _ in unique_dates] for person in st.session_state.persons}

for idx, unique_date in enumerate(unique_dates):
    for expense in st.session_state.expenses:
        if expense['date'] == unique_date:
            for person, amount in expense['owes'].items():
                if idx > 0:
                    # Add to previous cumulative value
                    cumulative_expenses[person][idx] = cumulative_expenses[person][idx - 1] + amount
                else:
                    cumulative_expenses[person][idx] = amount

# Create plotly figure
fig = go.Figure()

for person, expenses in cumulative_expenses.items():
    fig.add_trace(go.Scatter(x=unique_dates, y=expenses, mode='lines+markers', name=person))

fig.update_layout(title='Cumulative Expenses Over Time',
                  xaxis_title='Date',
                  yaxis_title='Cumulative Expense (NZ$)',
                  hovermode='x unified')

st.plotly_chart(fig)

st.subheader("Total Expenses per Person:")

total_paid_by_persons = calculate_total_paid_by_person(st.session_state.expenses)

# Extract data for plotting
persons = list(total_paid_by_persons.keys())
totals = list(total_paid_by_persons.values())

# Create a Plotly bar chart
bar_fig = go.Figure([go.Bar(x=persons, y=totals, text=totals, textposition='auto')])

bar_fig.update_layout(title='Total Amount Spent by Each Person',
                      xaxis_title='Person',
                      yaxis_title='Total Amount Spent ($)',
                      hovermode='x')

st.plotly_chart(bar_fig)


def convert_all_to_csv(expenses, persons, payments):
    """
    Convert all data to a CSV format.
    """
    csv_data = StringIO()

    # Write expenses
    csv_data.write("Expenses\n")
    expenses_writer = csv.DictWriter(csv_data, fieldnames=expenses[0].keys())
    expenses_writer.writeheader()
    expenses_writer.writerows(expenses)

    # Spacer
    csv_data.write("\n\n")

    # Write persons
    csv_data.write("Persons\n")
    persons_writer = csv.writer(csv_data)
    persons_writer.writerow(["Person Name"])
    for person in persons:
        persons_writer.writerow([person])

    # Spacer
    csv_data.write("\n\n")

    # Write payments
    csv_data.write("Payments\n")
    payments_writer = csv.DictWriter(csv_data, fieldnames=payments[0].keys())
    payments_writer.writeheader()
    payments_writer.writerows(payments)

    csv_data.seek(0)
    return csv_data.getvalue()


st.subheader("Export Data")

if st.button("Export All Data"):
    # Check if there's any data to export
    if st.session_state.expenses or st.session_state.persons or st.session_state.transfers:
        csv_content = convert_all_to_csv(st.session_state.expenses, st.session_state.persons,
                                         st.session_state.transfers)

        b64 = base64.b64encode(csv_content.encode()).decode()
        st.markdown(f'<a href="data:file/txt;base64,{b64}" download="all_data.csv">Download All Data</a>',
                    unsafe_allow_html=True)
    else:
        st.warning("No data to export.")