DROP TABLE IF EXISTS customers CASCADE;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

INSERT INTO customers (name, email) VALUES
('Alice Smith', 'alice.s@example.com'),
('Bob Johnson', 'bob.j@example.com'),
('Charlie Brown', 'charlie.b@example.com');