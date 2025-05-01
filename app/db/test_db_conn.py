from app.db.db_conn import db_manager
from app.db.db_models.user import User
print(User)
from sqlalchemy.inspection import inspect

print("Mapped columns:", inspect(User).columns.keys())

def test_conn():
    print(type(User))
    with db_manager.session as session:
        users = session.query(User).all()
        assert True
