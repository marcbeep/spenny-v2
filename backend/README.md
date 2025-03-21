# Spenny Backend

<aside>

We use FastAPI and Supabase.

</aside>

## Overview

Spenny helps users manage income and expenses using zero-based budgeting. Each user gets a default budget with predefined categories. Users can create multiple budgets, track transactions, and allocate funds efficiently.

---

## Core Relationships

- **A User (1) → (M) Budgets**: A user can create multiple budgets.
- **A Budget (1) → (M) Categories**: A budget has predefined categories but can be customized.
- **A Budget (1) → (0..M) Accounts**: A budget may have multiple accounts or none.
- **An Account (1) → (M) Transactions**: Every transaction belongs to an account.
- **A Budget (1) → (M) Transactions**: All transactions are linked to a budget.
- **A Transaction (1) → (0..1) Category**: A transaction may be categorized but is not required.

---

## Data Model

### 1. Users (1) → (M) Budgets

| Column     | Type      | Constraints                           | Description              |
| ---------- | --------- | ------------------------------------- | ------------------------ |
| id         | UUID      | PRIMARY KEY DEFAULT gen_random_uuid() | Unique user identifier.  |
| email      | TEXT      | NOT NULL UNIQUE                       | Used for authentication. |
| name       | TEXT      | NOT NULL                              | Display name.            |
| created_at | TIMESTAMP | NOT NULL DEFAULT now()                | Record creation time.    |

### 2. Budgets (1) → (M) Categories, (1) → (0..M) Accounts, (1) → (M) Transactions

| Column     | Type      | Constraints                                     | Description               |
| ---------- | --------- | ----------------------------------------------- | ------------------------- |
| id         | UUID      | PRIMARY KEY DEFAULT gen_random_uuid()           | Unique budget identifier. |
| user_id    | UUID      | NOT NULL REFERENCES users(id) ON DELETE CASCADE | Owner of this budget.     |
| name       | TEXT      | NOT NULL                                        | Name of the budget.       |
| is_default | BOOLEAN   | NOT NULL DEFAULT FALSE                          | Marks the default budget. |
| created_at | TIMESTAMP | NOT NULL DEFAULT now()                          | Record creation time.     |

### 3. Categories (1) → (M) Transactions (optional)

| Column     | Type          | Constraints                                       | Description                      |
| ---------- | ------------- | ------------------------------------------------- | -------------------------------- |
| id         | UUID          | PRIMARY KEY DEFAULT gen_random_uuid()             | Unique category identifier.      |
| budget_id  | UUID          | NOT NULL REFERENCES budgets(id) ON DELETE CASCADE | Budget this category belongs to. |
| name       | TEXT          | NOT NULL                                          | Name of the category.            |
| allocated  | NUMERIC(10,2) | NOT NULL DEFAULT 0.00                             | Amount allocated.                |
| created_at | TIMESTAMP     | NOT NULL DEFAULT now()                            | Record creation time.            |

### 4. Accounts (1) → (M) Transactions

| Column     | Type          | Constraints                                       | Description                         |
| ---------- | ------------- | ------------------------------------------------- | ----------------------------------- |
| id         | UUID          | PRIMARY KEY DEFAULT gen_random_uuid()             | Unique account identifier.          |
| budget_id  | UUID          | NOT NULL REFERENCES budgets(id) ON DELETE CASCADE | Budget this account belongs to.     |
| name       | TEXT          | NOT NULL                                          | Name of the account.                |
| type       | TEXT          | NOT NULL                                          | Type (e.g., Checking, Credit Card). |
| balance    | NUMERIC(10,2) | NOT NULL DEFAULT 0.00                             | Current balance.                    |
| created_at | TIMESTAMP     | NOT NULL DEFAULT now()                            | Record creation time.               |

### 5. Transactions (Belongs to One Budget, One Account, and Optionally One Category)

| Column      | Type          | Constraints                                        | Description                           |
| ----------- | ------------- | -------------------------------------------------- | ------------------------------------- |
| id          | UUID          | PRIMARY KEY DEFAULT gen_random_uuid()              | Unique transaction identifier.        |
| budget_id   | UUID          | NOT NULL REFERENCES budgets(id) ON DELETE CASCADE  | Budget this transaction belongs to.   |
| account_id  | UUID          | NOT NULL REFERENCES accounts(id) ON DELETE CASCADE | The account affected.                 |
| category_id | UUID          | REFERENCES categories(id) ON DELETE SET NULL       | Optional category.                    |
| date        | DATE          | NOT NULL                                           | Transaction date.                     |
| payee       | TEXT          | NOT NULL                                           | Entity receiving/sending money.       |
| amount      | NUMERIC(10,2) | NOT NULL                                           | Amount (+ for income, - for expense). |
| note        | TEXT          |                                                    | Optional transaction note.            |
| cleared     | BOOLEAN       | NOT NULL DEFAULT FALSE                             | Reconciled status.                    |
| created_at  | TIMESTAMP     | NOT NULL DEFAULT now()                             | Record creation time.                 |

---

## API Endpoints

### Users

| Method | Endpoint   | Description        |
| ------ | ---------- | ------------------ |
| POST   | /users     | Create a new user  |
| GET    | /users/:id | Retrieve user info |
| DELETE | /users/:id | Delete a user      |

### Budgets

| Method | Endpoint     | Description                |
| ------ | ------------ | -------------------------- |
| POST   | /budgets     | Create a new budget        |
| GET    | /budgets     | Retrieve all budgets       |
| GET    | /budgets/:id | Retrieve a specific budget |
| DELETE | /budgets/:id | Delete a budget            |

### Categories

| Method | Endpoint        | Description                  |
| ------ | --------------- | ---------------------------- |
| POST   | /categories     | Create a new category        |
| GET    | /categories     | Retrieve all categories      |
| GET    | /categories/:id | Retrieve a specific category |
| DELETE | /categories/:id | Delete a category            |

### Accounts

| Method | Endpoint      | Description                 |
| ------ | ------------- | --------------------------- |
| POST   | /accounts     | Create a new account        |
| GET    | /accounts     | Retrieve all accounts       |
| GET    | /accounts/:id | Retrieve a specific account |
| DELETE | /accounts/:id | Delete an account           |

### Transactions

| Method | Endpoint          | Description                     |
| ------ | ----------------- | ------------------------------- |
| POST   | /transactions     | Create a new transaction        |
| GET    | /transactions     | Retrieve all transactions       |
| GET    | /transactions/:id | Retrieve a specific transaction |
| DELETE | /transactions/:id | Delete a transaction            |

---

## Security & Access Control

- **Row-Level Security (RLS)** ensures users access only their own data.
- **Supabase Auth** handles authentication.
- **API endpoints** enforce user-based data filtering.

### Existing RLS Policies

Users

```
CREATE POLICY "users_select" ON users FOR SELECT TO public USING (id = auth.uid());
CREATE POLICY "users_update" ON users FOR UPDATE TO public USING (id = auth.uid());
CREATE POLICY "users_insert" ON users FOR INSERT TO public WITH CHECK (auth.uid() = id);
CREATE POLICY "users_delete" ON users FOR DELETE TO public USING (id = auth.uid());
```

Budgets

```
CREATE POLICY "select_budgets" ON budgets FOR SELECT TO public USING (user_id = auth.uid());
CREATE POLICY "budgets_insert" ON budgets FOR INSERT TO public WITH CHECK (user_id = auth.uid());
CREATE POLICY "budgets_update" ON budgets FOR UPDATE TO public USING (user_id = auth.uid());
CREATE POLICY "budgets_delete" ON budgets FOR DELETE TO public USING (user_id = auth.uid());
```

Categories

```
CREATE POLICY "categories_select" ON categories FOR SELECT TO public USING (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
CREATE POLICY "categories_insert" ON categories FOR INSERT TO public WITH CHECK (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
CREATE POLICY "categories_update" ON categories FOR UPDATE TO public USING (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
CREATE POLICY "categories_delete" ON categories FOR DELETE TO public USING (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
```

Accounts

```
CREATE POLICY "accounts_select" ON accounts FOR SELECT TO public USING (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
CREATE POLICY "accounts_insert" ON accounts FOR INSERT TO public WITH CHECK (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
CREATE POLICY "accounts_update" ON accounts FOR UPDATE TO public USING (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
CREATE POLICY "accounts_delete" ON accounts FOR DELETE TO public USING (budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())));
```

Transactions

```
CREATE POLICY "transactions_select" ON transactions FOR SELECT TO public USING (account_id IN (SELECT accounts.id FROM accounts WHERE (accounts.budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())))));
CREATE POLICY "transactions_insert" ON transactions FOR INSERT TO public WITH CHECK (account_id IN (SELECT accounts.id FROM accounts WHERE (accounts.budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())))));
CREATE POLICY "transactions_update" ON transactions FOR UPDATE TO public USING (account_id IN (SELECT accounts.id FROM accounts WHERE (accounts.budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())))));
CREATE POLICY "transactions_delete" ON transactions FOR DELETE TO public USING (account_id IN (SELECT accounts.id FROM accounts WHERE (accounts.budget_id IN (SELECT budgets.id FROM budgets WHERE (budgets.user_id = auth.uid())))));
```
