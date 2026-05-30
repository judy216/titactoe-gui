import sqlite3
from mosque import Mosque


class MosqueDatabase:
    """Handles all SQLite database operations for the Mosques Management System."""

    def __init__(self, db_path="mosques.db"):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Mosq (
                ID          INTEGER PRIMARY KEY,
                Name        TEXT    NOT NULL,
                Type        TEXT,
                Address     TEXT,
                Coordinates TEXT,
                Imam_name   TEXT
            )
        """)
        self.connection.commit()

    # ── public API ──────────────────────────────────────────────────────────

    def Display(self):
        """Return all mosque records as a list of Mosque objects."""
        self.cursor.execute("SELECT ID, Name, Type, Address, Coordinates, Imam_name FROM Mosq ORDER BY ID")
        rows = self.cursor.fetchall()
        return [Mosque(*row) for row in rows]

    def Search(self, name):
        """Return the mosque whose name matches exactly (case-insensitive), or None."""
        self.cursor.execute(
            "SELECT ID, Name, Type, Address, Coordinates, Imam_name FROM Mosq WHERE Name = ? COLLATE NOCASE",
            (name,)
        )
        row = self.cursor.fetchone()
        return Mosque(*row) if row else None

    def SearchAll(self, name):
        """Return all mosques whose name contains the given substring (case-insensitive)."""
        self.cursor.execute(
            "SELECT ID, Name, Type, Address, Coordinates, Imam_name FROM Mosq WHERE Name LIKE ? COLLATE NOCASE",
            (f"%{name}%",)
        )
        rows = self.cursor.fetchall()
        return [Mosque(*row) for row in rows]

    def GetAllNames(self):
        """Return a list of all mosque names (used for fuzzy matching)."""
        self.cursor.execute("SELECT Name FROM Mosq")
        return [row[0] for row in self.cursor.fetchall()]

    def Insert(self, mosque_id, name, mosque_type, address, coordinates, imam_name):
        """Insert a new mosque record."""
        self.cursor.execute(
            "INSERT INTO Mosq (ID, Name, Type, Address, Coordinates, Imam_name) VALUES (?, ?, ?, ?, ?, ?)",
            (mosque_id, name, mosque_type, address, coordinates, imam_name)
        )
        self.connection.commit()

    def Delete(self, mosque_id):
        """Delete a mosque by ID. Returns True if a row was removed."""
        self.cursor.execute("DELETE FROM Mosq WHERE ID = ?", (mosque_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def Update(self, mosque_id, imam_name):
        """Update the Imam name for a given mosque ID. Returns True on success."""
        self.cursor.execute(
            "UPDATE Mosq SET Imam_name = ? WHERE ID = ?",
            (imam_name, mosque_id)
        )
        self.connection.commit()
        return self.cursor.rowcount > 0

    def __del__(self):
        self.connection.close()
