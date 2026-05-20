import sqlalchemy as db 
from pathlib import Path 

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "database.db" 
DB_PATH.parent.mkdir(parents=True, exist_ok=True) 

engine = db.create_engine(f"sqlite:///{DB_PATH}", future=True) 
metadata = db.MetaData() 

students = db.Table( 
    "students", metadata, 
        db.Column("student_id", db.Integer, primary_key=True), 
        db.Column("first_name", db.Text, nullable=False), 
        db.Column("last_name", db.Text, nullable=False), 
        db.Column("phone_number", db.Text, nullable=False), 
        db.Column("grade", db.Integer, nullable=False), 
) 

def init_db() -> None: 
    metadata.create_all(engine) 