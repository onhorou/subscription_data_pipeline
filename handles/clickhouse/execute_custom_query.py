import logging

from clickhouse_driver import Client


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def execute_custom_query_clickhouse(  # noqa: PLR0913
    db_name: str | None = "default",
    host: str = "localhost",
    user: str = "click",
    password: str = "click",  # noqa: S107
    port: int = 9000,
    query: str | None = None,
) -> None:
    """
    Создаёт базу данных в ClickHouse.

    :param db_name: Имя базы данных.
    :param host: Хост базы данных.
    :param user: Пользователь базы данных.
    :param password: Пароль пользователя базы данных.
    :param port: Порт базы данных.
    :param query: Запрос для выполнения.
    :return: None
    """

    ch_client = Client(
        host=host,
        user=user,
        password=password,  # noqa: S106
        database=db_name,
        port=port,
    )

    ch_client.execute(query=query)

    logging.info(f"✅ Запрос: {query} к ClickHouse выполнен успешно")


# Пример использования
if __name__ == "__main__":
    pass
