import enum
import uuid
from decimal import Decimal
from datetime import datetime, date, timezone
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Numeric, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc)

class Base(DeclarativeBase): pass
class Institution(Base):
    __tablename__ = 'institutions'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    aicte_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    spoc_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200))

class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    full_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(40))
    institution_id: Mapped[str | None] = mapped_column(ForeignKey('institutions.id'))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class FDR(Base):
    __tablename__ = 'fdr_records'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    institution_id: Mapped[str] = mapped_column(ForeignKey('institutions.id'), index=True)
    assigned_officer_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'), index=True)
    instrument_number: Mapped[str] = mapped_column(String(80), index=True)
    bank_name: Mapped[str] = mapped_column(String(200))
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2))
    issue_date: Mapped[date] = mapped_column(Date)
    maturity_date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(30), default='Pending', index=True)
    file_key: Mapped[str] = mapped_column(String(200))
    file_sha256: Mapped[str] = mapped_column(String(64))
    original_filename: Mapped[str] = mapped_column(String(200))
    ocr_json: Mapped[str] = mapped_column(Text, default='{}')
    risk_json: Mapped[str] = mapped_column(Text, default='{}')
    bank_result: Mapped[str] = mapped_column(String(20), default='Not checked')
    discrepancy_note: Mapped[str | None] = mapped_column(Text)
    release_justification: Mapped[str | None] = mapped_column(Text)
    release_status: Mapped[str] = mapped_column(String(30), default='Not requested')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (UniqueConstraint('institution_id', 'instrument_number', name='uq_institution_instrument'),)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id'))
    fdr_id: Mapped[str | None] = mapped_column(ForeignKey('fdr_records.id'))
    action: Mapped[str] = mapped_column(String(100))
    detail: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AlertLog(Base):
    __tablename__ = 'alert_logs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    fdr_id: Mapped[str] = mapped_column(ForeignKey('fdr_records.id'))
    threshold_days: Mapped[int] = mapped_column(Integer)
    maturity_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    __table_args__ = (UniqueConstraint('fdr_id','threshold_days','maturity_date', name='uq_alert_once'),)
