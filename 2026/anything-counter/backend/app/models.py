"""SQLAlchemyモデル定義 — countersとrecordsの2テーブル"""

from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class Counter(Base):
    """習慣カウンターを表すテーブル。1行 = 1つの習慣（例: 筋トレ、読書）"""

    __tablename__ = "counters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)  # カウンター名
    created_at = Column(Text, nullable=False, server_default=func.now())  # 作成日時
    sort_order = Column(Integer, nullable=False, default=0)  # 表示順序

    # カウンター削除時に関連recordsも自動削除される（cascade）
    records = relationship(
        "Record", back_populates="counter", cascade="all, delete-orphan"
    )


class Record(Base):
    """実行記録を表すテーブル。1行 = ある日にある習慣を実行した記録"""

    __tablename__ = "records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    counter_id = Column(
        Integer, ForeignKey("counters.id", ondelete="CASCADE"), nullable=False
    )
    date = Column(Text, nullable=False)  # "YYYY-MM-DD"形式
    created_at = Column(Text, nullable=False, server_default=func.now())

    coutner = relationship("Counter", back_populates="records")

    # 同じカウンターで同じ日に2回記録できないようにする
    __table_args__ = UniqueConstraint("counter_id", "date", name="uq_counter_date")
