
import libs.database_lite as db
from libs.constant import *
from abc import ABC, abstractmethod

class TagConfig():
    def __init__(self, **kwargs) -> None:
        self._values = kwargs
        self._key = ""

    def change(self, **new_kwargs):
        self._values = new_kwargs

    @property
    def key(self):
        return self._key
    
    @key.setter
    def key(self, val:str):
        self._key = val
    
    @property
    def table_name(self):
        return self._values.get("table_name", "").lower()
    
    @property
    def name(self):
        return self._values.get("name", "")
    
    @property
    def x(self):
        return self._values.get("x", "")
    
    @property
    def y(self):
        return self._values.get("y", "")
    
    @property
    def rfid(self):
        return self._values.get("rfid", "")
    
    @property
    def dir(self):
        return self._values.get("dir", "")
    
    @property
    def type(self):
        return self._values.get("type", "")
    
    @property
    def group_tag(self):
        return self._values.get("group_tag", "")
    
    @property
    def state(self):
        return self._values.get("state", "")
    
    @property
    def speed(self):
        return self._values.get("speed", "")
    
    @property
    def coordinates(self):
        return self._values.get("coordinates", "")
    
    @property
    def values(self):
        return tuple(self._values.values())[1:] if self._values else ()
    
    @property
    def columns(self):
        return tuple(self._values.keys())[1:] if self._values else ()
    
    def __setitem__(self, key, value:str):
        self._values[key] = value
    
    def __getitem__(self, key):
        return self._values[key]

    def is_key_change(self):
        return not self.name == self.key

    def is_insert_in_db(self):
        rows = self.select_db()
        return True if rows else False
        
    def select_db(self):
        conn = db.create_db(DATABASE_PATH)
        values = (self.key, )
        sql = f"select * from {self.table_name} where name=?"
        rows = db.select(conn, sql, values)
        return rows
        
    def insert_db(self):
        conn = db.create_db(DATABASE_PATH)
        values = self.values
        spare = len(values) * ["?"]
        spare = "values(" + ",".join(spare) + ")"

        error = ""
        if conn:
            try:
                sql = f"insert into {self.table_name} {spare}"
                db.insert(conn, sql, values)
                self.key = self.name
                return True, error
            except Exception as ex:
                error = str(ex)
                return False, error

    def update_db(self):
        conn = db.create_db(DATABASE_PATH)

        values = self.values
        values += (self.name, )
        columns = self.columns

        spare = []
        for col in columns:
            spare.append(f"{col}=?")
        spare = ",".join(spare)

        error = ""
        if conn:
            try:
                sql = f"update {self.table_name} SET {spare} where name=?"
                db.update(conn, sql, values)
                self.key = self.name
                return True, error
            except Exception as ex:
                error = str(ex)
                return False, error
            
    def delete_db(self):
        error = ""
        try:
            conn = db.create_db(DATABASE_PATH)
            sql = f"delete from {self.table_name} where name=?"
            values = (self.key, )

            db.delete(conn, sql, values)
            return True, error
        except Exception as ex:
            error = str(ex)
            return False, error


        