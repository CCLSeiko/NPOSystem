"""Donation system models (donation schema)."""
from __future__ import annotations

import uuid

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class Donor(TimestampMixin, Base):
    """捐款人資料"""
    __tablename__ = "donors"
    __table_args__ = {"schema": "donation"}

    donor_no = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(50))
    address = Column(String(500))
    id_number = Column(String(20))
    email = Column(String(200))
    memo = Column(Text)
    is_active = Column(Integer, default=1)


class DonationRecord(TimestampMixin, Base):
    """單次捐款紀錄（銀行/郵局轉帳及現金捐款）"""
    __tablename__ = "donation_records"
    __table_args__ = {"schema": "donation"}

    sn = Column(Integer, primary_key=True, autoincrement=True)
    donor_no = Column(String(20), ForeignKey("donation.donors.donor_no"), nullable=False)
    donor = relationship("Donor")
    amount = Column(Numeric(12, 2), nullable=False)
    donation_date = Column(Date, nullable=False)
    donation_type = Column(String(20))  # bank/transfer/cash/postal
    bank_no = Column(String(20))
    memo = Column(Text)


class AutoDonation(TimestampMixin, Base):
    """自動扣款紀錄（信用卡或銀行郵局帳號）"""
    __tablename__ = "auto_donations"
    __table_args__ = {"schema": "donation"}

    sn = Column(Integer, primary_key=True, autoincrement=True)
    donor_no = Column(String(20), ForeignKey("donation.donors.donor_no"), nullable=False)
    donor = relationship("Donor")
    amount = Column(Numeric(12, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    frequency = Column(String(20))  # monthly/quarterly/yearly
    account_no = Column(String(100))
    is_active = Column(Integer, default=1)


class BankType(TimestampMixin, Base):
    """銀行類別"""
    __tablename__ = "bank_types"
    __table_args__ = {"schema": "donation"}

    bank_no = Column(String(20), primary_key=True)
    bank_name = Column(String(200), nullable=False)
    is_active = Column(Integer, default=1)
