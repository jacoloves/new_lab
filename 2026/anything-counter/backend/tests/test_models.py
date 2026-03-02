"""モデルのテスト — テーブル作成とレコード挿入の確認"""
from app.models import Counter, Record

class TestCounterModel:
    """Counterモデルのテスト"""

    def test_create_counter(serlf, sb):
        """カウンターを作成してDBに保存し、取得できることを確認"""
        counter = Counter(name="筋トレ")
        db.add(counter)
        db.commit()
        db.refresh(counter)

        assert counter.id is not None
        assert counter.name == "筋トレ"
        assert counter.sort_order == 0

    def test_create_counters(self, db):
        """複数のカウンターを作成して一覧取得できることを確認"""
        db.add(Counter(name="筋トレ"))
        db.add(Counter(name="読書"))
        db.commit()

        counters = db.query(Counter).all()
        assert len(counters) == 2


class TestRecordModel:
    """Recordモデルのテスト"""

    def test_create_record(self, db):
        """カウンターに紐づく実行記録を作成できることを確認"""
        counter = Counter(name="筋トレ")
        db.add(counter)
        db.commit()

        record = Record(counter_id=counter.id, date="2026-02-23")
        db.add(record)
        db.commit()
        db.refresh(record)

        assert record.id is not None
        assert record.counter_id == counter.id
        assert record.date == "2026-02-23"

    def test_delete_record(self, db):
        """cascade deleteが正しく動作することを確認"""
        counter = Counter(name="筋トレ")
        db.add(counter)
        db.commit()

        record = Record(counter_id=counter.id, date="2026-02-23")
        db.add(record)
        db.commit()

        db.delete(counter)
        db.commit()

        records = db.query(Record).all()
        assert len(records) == 0

    def test_same_record(self, db):


