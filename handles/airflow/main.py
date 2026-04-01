from create_connection import create_airflow_connection


if __name__ == "__main__":
    # Пример использования функции для создания подключения
    create_airflow_connection(
        connection_id="olap_ch",
        conn_type="sqlite",
        host="olap_ch",
        port=9000,
        login="click",
        password="click",  # noqa: S106
        schema="default",
        user_name="airflow",
        password_auth="airflow",  # noqa: S106
    )

    create_airflow_connection(
        connection_id="oltp_target",
        schema="ltv",
        host="oltp_target",
        user_name="airflow",
        password_auth="airflow",  # noqa: S106
    )
