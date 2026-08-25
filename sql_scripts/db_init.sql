CREATE DATABASE test_notifier;

GRANT ALL PRIVILEGES ON DATABASE test_notifier TO dev;
GRANT ALL PRIVILEGES ON TABLE notifications TO dev;

CREATE TABLE notifications (
    id          BIGSERIAL PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    n_method    VARCHAR(20) NOT NULL CHECK (n_method IN ('Telegram', 'Email', 'WhatsApp', 'SMS')),
    n_text      TEXT NOT NULL,
    n_time      TIMESTAMP NOT NULL,
    r_time      TIMESTAMP NOT NULL,
    priority    INTEGER NOT NULL DEFAULT 1,
    is_repeat   BOOLEAN NOT NULL DEFAULT FALSE
);
