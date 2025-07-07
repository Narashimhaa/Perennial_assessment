from typing import List

def serialize_employee(emp, columns: List[str]) -> dict:
    return {col: getattr(emp, col, None) for col in columns}