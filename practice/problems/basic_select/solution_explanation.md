## Explanation: Basic Select

To retrieve all columns and all rows from a table, you use the `SELECT *` statement. If you want to specify individual columns, you list them separated by commas. The `FROM` clause specifies which table to query.

In this case, since you need all columns (`id`, `name`, `email`) and all rows from the `customers` table, the most straightforward query is `SELECT * FROM customers;`. Alternatively, you could explicitly list the columns: `SELECT id, name, email FROM customers;`.