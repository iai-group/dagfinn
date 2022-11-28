"""
File contains:
    - a class that connects to a database and methods to query it.
    - a function to create a string of questionmarks.
"""

import sqlite3


class DBConnector:
    def __init__(self, filename="dagfinn"):
        """Connects to the database and allows queries.

        Args:
            filename: Name of the database file.
        """
        self.con = sqlite3.connect(f"db/{filename}.db")
        self.cur = self.con.cursor()

    def create_table(self, name: str, content: str) -> None:

        """Creates a table in the database.

        Args:
            name: The name of the table.
            content: A string with the column names and types.
        """

        self.cur.execute(f"CREATE TABLE IF NOT EXISTS {name} ({content})")
        self.con.commit()

    def delete_table(self, table: str) -> None:
        """Deletes a table from the database.

        Args:
            table: Name of the table to be deleted.
        """

        self.cur.execute(f"DROP TABLE {table}")
        self.con.commit()

    def insert(self, table: str, content: tuple) -> None:
        """Inserts data into the given table. Ignores if row already exists.

        Args:
            table: The table the data will be inserted into.
            content: A tuple of data to be inserted.
        """
        str = create_string(len(content))
        self.cur.execute(
            f"INSERT OR IGNORE INTO {table} VALUES ({str})", content
        )
        self.con.commit()

    def insert_with_fields(self, table: str, content: dict) -> None:
        """Inserts data in specific fields into the given table. Ignores if
        row already exists.
        Args:
            table: The table the data will be inserted into.
            content: A dictionary of data with keys being fields of the table
        """
        str = create_string(len(content))
        fields = ",".join(content.keys())
        values = tuple(content.values())
        self.cur.execute(
            f"INSERT OR IGNORE INTO {table} ({fields}) VALUES ({str})", values
        )
        self.con.commit()

    def delete(self, table: str, parameters: str) -> None:
        """Deletes a row with certain parameters.

        Args:
            table: The table the row will be deleted from.
            parameters: A string with the deletion requirements.
        """
        self.cur.execute(f"DELETE FROM {table} WHERE ({parameters})")
        self.con.commit()

    def update(self, table: str, change: str, parameters: str) -> None:
        """Updates a row with the given parameters.

        Args:
            table: The table in which the row will be updated in.
            change: The data to be changed.
            parameters: The required data for the update.
        """
        self.cur.execute(f"UPDATE {table} SET {change} WHERE ({parameters})")
        self.con.commit()

    def select(self, table: str, select: str) -> list:
        """Selects columns from the database.

        Args:
            table: The table to select from.
            select: The columns to select.

        Returns:
            The columns from the database.
        """
        self.cur.execute(f"SELECT {select} FROM {table}")
        selection = self.cur.fetchall()
        return selection

    def select_where(self, table: str, column: str, where: str) -> list:
        """Selects columns from the database with parameters.

        Args:
            table: The table to select from.
            column: The columns to select.
            where: The parameters to filter by, e.g Id > 2

        Returns:
            The columns from the database.
        """
        self.cur.execute(f"SELECT {column} FROM {table} WHERE {where}")
        selection = self.cur.fetchall()
        return selection


def create_string(amount: int) -> str:
    """Creates a string with questionmarks.

    Args:
        amount: The amount of questionmarks or entries.

    Returns:
        A string with questionmarks, for example: ?, ?, ?
    """
    return ", ".join(["?"] * amount)
