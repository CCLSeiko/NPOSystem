"""Organize system models (organize schema)."""
from __future__ import annotations

from sqlalchemy import Column, Date, Integer, Numeric, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class PartyMember(TimestampMixin, Base):
    """黨員資料"""
    __tablename__ = "party_members"
    __table_args__ = {"schema": "organize"}

    party_no = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    id_number = Column(String(20))
    phone = Column(String(50))
    address = Column(String(500))
    email = Column(String(200))
    status = Column(String(2), default="1")  # 1=現任, 2=新入黨, A=準備中, B=待審核, X=停權, 3=退黨, 9=死亡
    join_date = Column(Date)
    referrer_no = Column(String(20), ForeignKey("organize.party_members.party_no"))
    referrer = relationship("PartyMember", remote_side="PartyMember.party_no")


class GovernmentOfficial(TimestampMixin, Base):
    """公職人員"""
    __tablename__ = "government_officials"
    __table_args__ = {"schema": "organize"}

    sn = Column(Integer, primary_key=True, autoincrement=True)
    party_no = Column(String(20), ForeignKey("organize.party_members.party_no"), nullable=False)
    member = relationship("PartyMember")
    position = Column(String(200), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)


class PartyDue(TimestampMixin, Base):
    """黨費紀錄"""
    __tablename__ = "party_dues"
    __table_args__ = {"schema": "organize"}

    sn = Column(Integer, primary_key=True, autoincrement=True)
    party_no = Column(String(20), ForeignKey("organize.party_members.party_no"), nullable=False)
    member = relationship("PartyMember")
    amount = Column(Numeric(10, 2), nullable=False)
    due_year = Column(Integer, nullable=False)
    pay_date = Column(Date)
    memo = Column(Text)


class PartyActivity(TimestampMixin, Base):
    """活動紀錄"""
    __tablename__ = "party_activities"
    __table_args__ = {"schema": "organize"}

    sn = Column(Integer, primary_key=True, autoincrement=True)
    party_no = Column(String(20), ForeignKey("organize.party_members.party_no"), nullable=False)
    member = relationship("PartyMember")
    activity_name = Column(String(200), nullable=False)
    activity_date = Column(Date)
    memo = Column(Text)


class ReferrerPoints(TimestampMixin, Base):
    """推薦人點數管理"""
    __tablename__ = "referrer_points"
    __table_args__ = {"schema": "organize"}

    sn = Column(Integer, primary_key=True, autoincrement=True)
    referrer_no = Column(String(20), ForeignKey("organize.party_members.party_no"), nullable=False)
    referrer = relationship("PartyMember", foreign_keys=[referrer_no])
    new_member_no = Column(String(20), ForeignKey("organize.party_members.party_no"), nullable=False)
    new_member = relationship("PartyMember", foreign_keys=[new_member_no])
    points = Column(Integer, default=0)
    memo = Column(Text)
