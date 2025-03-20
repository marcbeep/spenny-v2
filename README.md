# Spenny - Zero Based Budgeting App

## Overview

Spenny is a zero-based budgeting application that helps users track their income, expenses, and allocate funds to predefined categories to control their finances. Each user can create multiple budgets, define categories, and track transactions related to their accounts.

### Concepts

1. **User**: A person using the app, with authentication via Supabase.
2. **Budget**: A collection of categories, accounts, and transactions belonging to a user.
3. **Category**: Predefined spending areas to allocate funds (e.g., Rent, Groceries).
4. **Account**: Real-world financial sources (e.g., Checking, Credit Card).
5. **Transaction**: Records of money inflow (income) or outflow (expense), associated with accounts and optionally categories.

### Workflow

1. **Budget Creation**:
   - A user can create one or more budgets.
   - Each budget has categories to allocate funds for specific purposes.
2. **Account Setup**:
   - Users create financial accounts (e.g., Checking, Credit Card).
   - Each account has an initial balance, updated after each transaction.
3. **Category Allocation**:
   - Users can allocate a specific amount of money to each category in their budget.
   - The total of all category allocations should equal the available budget amount, adhering to the zero-based budgeting principle.
4. **Transaction Management**:
   - Users can record transactions that affect accounts.
   - Transactions can be categorized for better tracking of spending (e.g., groceries, entertainment).
   - Each transaction modifies the balance of an account and can either be income (+) or expense (-).
5. **Reconciliation**:
   - Transactions can be marked as "cleared" once reconciled with actual account activity.
   - The system ensures that the user's account balances and category allocations are accurately reflected.
