## Explanation: Joining Customers and Orders

This problem requires combining data from two tables, `customers` and `orders`, based on a common column. The `customer_id` in the `orders` table links to the `id` in the `customers` table.

We use an `INNER JOIN` (or just `JOIN`, which defaults to `INNER JOIN`) to link these tables. The `ON` clause specifies the condition for joining, which is `c.id = o.customer_id`. We use aliases `c` for `customers` and `o` for `orders` to make the query more readable.

Finally, we select the `name` from the `customers` table (aliased as `customer_name`) and the `amount` from the `orders` table (aliased as `order_amount`).