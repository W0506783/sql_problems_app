SELECT c.name AS customer_name, o.amount AS order_amount
FROM customers c
JOIN orders o ON c.id = o.customer_id;