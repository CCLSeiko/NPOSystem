"""Common / shared database models (common schema)."""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Employee(TimestampMixin, Base):
    """員工資料"""
    __tablename__ = "employees"
    __table_args__ = {"schema": "common"}

    emp_no = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    department = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    is_active = Column(Boolean, default=True)


class Department(TimestampMixin, Base):
    """部門資料"""
    __tablename__ = "departments"
    __table_args__ = {"schema": "common"}

    dept_no = Column(String(20), primary_key=True)
    dept_name = Column(String(200), nullable=False)
    parent_dept_no = Column(String(20), ForeignKey("common.departments.dept_no"))
    is_active = Column(Boolean, default=True)


class LookupClass(TimestampMixin, Base):
    """通用類代碼表 — 用於系統中各類下拉選單"""
    __tablename__ = "lookup_classes"
    __table_args__ = {"schema": "common"}

    class_no = Column(String(20), primary_key=True)
    class_name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    items = relationship("LookupItem", back_populates="lookup_class", order_by="LookupItem.sort_order")


class LookupItem(TimestampMixin, Base):
    """代碼表明細"""
    __tablename__ = "lookup_items"
    __table_args__ = {"schema": "common"}

    item_no = Column(String(20), primary_key=True)
    class_no = Column(String(20), ForeignKey("common.lookup_classes.class_no"), nullable=False)
    item_name = Column(String(200), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    lookup_class = relationship("LookupClass", back_populates="items")
