import pytest 
import sqlalchemy as db 
from sqlalchemy.pool import StaticPool 
from fastapi.testclient import TestClient 
import src.database as database 
import src.app as app_module 

 
@pytest.fixture() 
def client(): 
    test_engine = db.create_engine( 
        "sqlite+pysqlite:///:memory:", 
        future=True,
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool, 
    ) 
    database.engine = test_engine 
    app_module.engine = test_engine 
 
    database.metadata.create_all(test_engine) 
 
    with test_engine.begin() as conn: 
        conn.execute(db.delete(database.students)) 
        conn.execute( 
            db.insert(database.students), 
            [ 
                { 
                    "student_id": 1, 
                    "first_name": "Иван", 
                    "last_name": "Иванов", 
                    "phone_number": "78124015112", 
                    "grade": 3,
                }, 
                { 
                    "student_id": 2, 
                    "first_name": "Анна", 
                    "last_name": "Петрова", 
                    "phone_number": "71456785120", 
                    "grade": 2, 
                }, 
            ], 
        ) 
    app = app_module.create_app() 
    database.init_db()

    with TestClient(app) as c: 
        yield c 