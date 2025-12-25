CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    response TEXT,
    model VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);