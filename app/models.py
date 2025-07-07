from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20))
    department = Column(String(100))
    position = Column(String(100))
    location = Column(String(255))
    status = Column(String(20), default="ACTIVE")
    avatar_url = Column(Text)
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now())
    org_id = Column(Integer, index=True)



class OrgConfig(Base):
    __tablename__ = "org_column_config"
    org_id = Column(Integer, primary_key=True, index=True)
    visible_columns = Column(ARRAY(Text))
