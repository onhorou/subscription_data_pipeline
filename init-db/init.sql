CREATE DATABASE subscriptions_db;
CREATE DATABASE payments_db;

\c subscriptions_db

-- Таблица пользователей
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Тарифная сетка
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    price_amount INTEGER NOT NULL, -- в копейках (1000 = 10.00)
    currency VARCHAR(3) NOT NULL,  -- USD, RUB
    duration_days INTEGER NOT NULL,
    provider_type VARCHAR(50) NOT NULL -- internal/partner
);

-- Добавление планов по умолчанию
INSERT INTO plans (id, name, price_amount, currency, duration_days, provider_type) VALUES
    (gen_random_uuid(), 'Basic', 500,  'RUB', 30, 'internal'),
    (gen_random_uuid(), 'Pro',   1500, 'RUB', 30, 'internal');

-- Состояние подписки
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    plan_id UUID NOT NULL REFERENCES plans(id),
    status VARCHAR(20) NOT NULL,     -- active, expired, cancelled
    starts_at TIMESTAMPTZ NOT NULL,
    ends_at TIMESTAMPTZ NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    last_order_id UUID,              -- Логическая ссылка на payments_db.orders.id
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

\c payments_db

-- Способы оплаты (карты, токены)
CREATE TABLE payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,          -- Ссылка на subscriptions_db.users.id
    type VARCHAR(20) NOT NULL,       -- card, apple_pay, google_pay
    provider_name VARCHAR(100),      -- Stripe, CloudPayments, Tinkoff
    gateway_token TEXT,              -- Токен карты в системе провайдера
    card_last4 VARCHAR(4),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Заказы (Бизнес-логика покупки)
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,           -- Ссылка на subscriptions_db.users.id
    plan_id UUID NOT NULL,           -- Ссылка на subscriptions_db.plans.id
    payment_method_id UUID REFERENCES payment_methods(id),
    amount INTEGER NOT NULL,         -- Сумма на момент оплаты
    status VARCHAR(20) NOT NULL,      -- paid, failed, pending, refunded
    external_id TEXT,                -- ID транзакции в банковской системе
    refunded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Транзакции (Технический лог попыток оплаты)
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    external_reference TEXT,         -- Ссылка на попытку в шлюзе
    status VARCHAR(20),              -- success, declined, error
    error_code VARCHAR(50),          -- Например: insufficient_funds
    raw_response JSONB,              -- Полный лог ответа от API банка
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);