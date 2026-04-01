from handles.clickhouse.execute_custom_query import execute_custom_query_clickhouse


if __name__ == "__main__":
    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS ods;")

    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS dds;")

    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS stg;")

    execute_custom_query_clickhouse(query="CREATE DATABASE IF NOT EXISTS et;")

    execute_custom_query_clickhouse(
        query="""
    CREATE TABLE et.et_ods_user
    (
        id Int64,
        created_at DateTime,
        first_name String,
        last_name String,
        middle_name String,
        birthday DateTime,
        email String
    )
    ENGINE = PostgreSQL(
        'oltp_source:5432',
        'oltp_users',
        'users',
        'postgres',
        'postgres',
        'public'
    );
    """
    )

    execute_custom_query_clickhouse(
        query="""
    CREATE TABLE et.et_ods_sales
    (
        id Int64,
        user_id Int64,
        created_at DateTime,
        branch Int64,
        amount Int64
    )
    ENGINE = PostgreSQL(
        'oltp_source:5432',
        'oltp_sales',
        'sales',
        'postgres',
        'postgres',
        'public'
    );
    """
    )

    execute_custom_query_clickhouse(
        query="""
    CREATE TABLE et.target_user_ltv_history
    (
        user_id Int64,
        stat_date Date,
        ltv Int64,
        user_class String
    )
    ENGINE = PostgreSQL(
        'oltp_target:5432',
        'ltv',
        'user_ltv_history',
        'postgres',
        'postgres'
    );
    """
    )

    execute_custom_query_clickhouse(
        query="""
    CREATE TABLE ods.ods_users
    (
        id Int64,
        created_at DateTime,
        first_name String,
        last_name String,
        middle_name String,
        birthday DateTime,
        email String
    )
    ENGINE = MergeTree
    PARTITION BY toYYYYMM(created_at)
    ORDER BY (id, created_at);
    """
    )

    execute_custom_query_clickhouse(
        query="""
    CREATE TABLE ods.ods_sales
    (
        id Int64,
        user_id Int64,
        created_at DateTime,
        branch Int64,
        amount Int64
    )
    ENGINE = MergeTree
    PARTITION BY toYYYYMM(created_at)
    ORDER BY (id, created_at);
    """
    )

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
