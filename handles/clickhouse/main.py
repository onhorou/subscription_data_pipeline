from handles.clickhouse.execute_custom_query import execute_custom_query_clickhouse


if __name__ == "__main__":
    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS ods;")

    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS dds;")

    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS stg;")

    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS et;")

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE et.users
        (
            id UUID,
            email String,
            first_name String,
            last_name String,
            birthday DateTime,
            password_hash String,
            created_at DateTime
        )
        ENGINE = PostgreSQL(
            'oltp_source:5432',
            'subscriptions_db',
            'users',
            'postgres',
            'postgres',
            'public'
        );
        """
    )

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE et.plans
        (
            id UUID,
            name String,
            price_amount Int64,
            currency String,
            duration_days Int64,
            provider_type String
        )
        ENGINE = PostgreSQL(
            'oltp_source:5432',
            'subscriptions_db',
            'plans',
            'postgres',
            'postgres',
            'public'
        );
        """
    )

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE et.subscriptions
        (
            id UUID,
            user_id UUID,
            plan_id UUID,
            status String,
            starts_at DateTime,
            ends_at DateTime,
            auto_renew Boolean,
            last_order_id UUID,
            created_at DateTime
        )
        ENGINE = PostgreSQL(
            'oltp_source:5432',
            'subscriptions_db',
            'subscriptions',
            'postgres',
            'postgres',
            'public'
        );
        """
    )

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE et.payment_methods
        (
            id UUID,
            user_id UUID,
            type String,
            provider_name String,
            gateway_token String,
            card_last4 String,
            is_active Boolean,
            created_at DateTime
        )
        ENGINE = PostgreSQL(
            'oltp_source:5432',
            'payments_db',
            'payment_methods',
            'postgres',
            'postgres',
            'public'
        );
        """
    )

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE et.orders
        (
            id UUID,
            user_id UUID,
            plan_id UUID,
            payment_method_id UUID,
            amount Int64,
            status String,
            external_id String,
            refunded_at DateTime,
            created_at DateTime
        )
        ENGINE = PostgreSQL(
            'oltp_source:5432',
            'payments_db',
            'orders',
            'postgres',
            'postgres',
            'public'
        );
        """
    )

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE et.transactions
        (
            id UUID,
            order_id UUID,
            external_reference String,
            status String,
            error_code String,
            raw_response String,
            created_at DateTime
        )
        ENGINE = PostgreSQL(
            'oltp_source:5432',
            'payments_db',
            'transactions',
            'postgres',
            'postgres',
            'public'
        );
        """
    )

    # ODS TABLES
    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE ods.users
        (
            id UUID,
            email String,
            first_name String,
            last_name String,
            birthday DateTime,
            password_hash String,
            created_at DateTime
        )
        ENGINE = MergeTree
        PARTITION BY toYYYYMM(created_at)
        ORDER BY (id, created_at);
        """
    )

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE ods.plans
        (
            id UUID,
            name String,
            price_amount Int64,
            currency String,
            duration_days Int64,
            provider_type String
        )
        ENGINE = MergeTree
        ORDER BY (id);
        """
    )

    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE ods.orders
        (
            id UUID,
            user_id UUID,
            plan_id UUID,
            payment_method_id UUID,
            amount Int64,
            status String,
            external_id String,
            refunded_at DateTime,
            created_at DateTime
        )
        ENGINE = MergeTree
        PARTITION BY toYYYYMM(created_at)
        ORDER BY (id, created_at);
        """
    )

    # DDS TABLES
    execute_custom_query_clickhouse(
        query="""
        CREATE TABLE dds.user_ltv_history
        (
            user_id Int64,
            execution_day Date,
            ltv Int64,
            user_class String
        )
        ENGINE = ReplacingMergeTree()
        PARTITION BY toYYYYMM(execution_day)
        ORDER BY (user_id, execution_day)
        SETTINGS index_granularity = 8192;
        """
    )
