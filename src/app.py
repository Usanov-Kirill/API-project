from fastapi import FastAPI, HTTPException, Query, Path as PathParam, Response
import sqlalchemy as db
from sqlalchemy import func
from src.database import engine, students, init_db
from src.schemas import Student, UpdateStudent, Error

import random

def create_app():
    #init_db()

    app = FastAPI(
        title="Students",
        description="Тестовое API для студентов.",
        version="1.0",
    )
    app.openapi_tags = [
        {"name": "test"},
        {"name": "students.get"},
        {"name": "students.post"},
        {"name": "students.put"},
        {"name": "students.patch"},
        {"name": "students.delete"},
    ]

    # ---health--------------------------------------------------

    @app.get(
        "/",
        tags=["test"],
        summary="Проверка на работоспособность",
    )
    def health():
        return {"message": "всё работает"}

    # ---Random-student-and-groups-(GET)---------------------------------------

    @app.get(
        "/students/random",
        tags=["students.get"],
        summary="случайный студент",
        description="Вернёт случайного студента",
    )
    def random_student():
        with engine.begin() as conn:
            all_id = conn.scalars(db.select(students.c.student_id)).all()
            rand_id = random.choice(all_id)

            stmt = db.select(students).where(students.c.student_id == rand_id) 
            stmt = stmt.order_by(students.c.student_id) 
            rows = conn.execute(stmt).fetchall() 

            return [dict(r._mapping) for r in rows]
        
    @app.get(
        "/students/random_group",
        tags=["students.get"],
        summary="случайная групаа",
        description="Вернёт случайно собранную группу из определённого кол-ва студентов",
    )
    def random_group(count: int):
        with engine.begin() as conn:
            all_id = conn.scalars(db.select(students.c.student_id)).all()
            total = len(all_id)
            group_ids = []
            if count > total:
                raise HTTPException(status_code=400, detail="your count is bigger than count of students")

            while len(group_ids) < count:
                rand_id = random.choice(all_id)
                if rand_id not in group_ids:
                    group_ids.append(rand_id)
            
            stmt = db.select(students).where(students.c.student_id.in_(group_ids))
            stmt = stmt.order_by(students.c.student_id) 
            rows = conn.execute(stmt).fetchall() 

            return [dict(r._mapping) for r in rows]
        
    # ---GET------------------------------------------------------

    @app.get(
        "/students",
        tags=["students.get"],
        summary="список студентов",
        description="Вернёт всех студентов",
    )
    def get_all_students(grade: int | None = Query(None, ge=1, le=11),): 
        with engine.begin() as conn: 
            stmt = db.select(students)
            if grade is not None: 
                stmt = stmt.where(students.c.grade == grade) 

            stmt = stmt.order_by(students.c.student_id) 
            rows = conn.execute(stmt).fetchall() 

            return [dict(r._mapping) for r in rows]

    @app.get(
        "/students/{grade}",
        tags=["students.get"],
        summary="студент по классу",
        description="Вернёт конкретного студента по классу",
    )
    def get_students_by_grade(
        grade: int = PathParam(..., ge=1, le=11),
        last_name: str | None = Query(None),
    ):
        with engine.begin() as conn: 
            stmt = db.select(students).where(students.c.grade == grade) 
    
            if last_name: 
                ln = last_name.strip() 
                stmt = stmt.where(db.func.lower(students.c.last_name) == db.func.lower(ln)) 
    
            stmt = stmt.order_by(students.c.student_id) 
            rows = conn.execute(stmt).fetchall() 
    
            return [dict(r._mapping) for r in rows]

    # ---POST-------------------------------------------------

    @app.post(
        "/students",
        tags=["students.post"],
        summary="создать студента",
        description="принимает запись, создает студента",
        status_code=201,
        response_model=Student,
        responses={
            201: {"description": "Создано"},
            409: {"model": Error, "description": "студент c таким id уже есть"},
        },
    )
    def create_student(payload: Student):
        with engine.begin() as conn:
            exists = conn.execute(
                db.select(students.c.student_id).where(
                    students.c.student_id == payload.student_id
                )
            ).fetchone()

            if exists is not None:
                raise HTTPException(status_code=409, detail="student_id already exists")

            conn.execute(db.insert(students), [payload.model_dump()])

        return payload

    # ---PUT-------------------------------------------------

    @app.put(
        "/students/{student_id}",
        tags=["students.put"],
        summary="Полная замена",
        description="Заменяет запись целиком",
        response_model=Student,
        responses={
            400: {"model": Error, "description": "Несовпадение id"},
            404: {"model": Error, "description": "Ученик не найден"},
        },
    )
    def replace_student(student_id: int, payload: Student):
        if payload.student_id != student_id:
            raise HTTPException(
                status_code=400, detail="student_id in path and body must match"
            )

        with engine.begin() as conn:
            result = conn.execute(
                db.update(students)
                .where(students.c.student_id == student_id)
                .values(**payload.model_dump(exclude={"student_id"}))
            )
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="student not found")

        return payload

    # ---PATCH-------------------------------------------------
    @app.patch(
        "/students/{student_id}",
        tags=["students.patch"],
        summary="обновление",
        description="обновляет запись студента",
        response_model=UpdateStudent,
        responses={
            400: {"model": Error, "description": "Несовпадение id"},
            404: {"model": Error, "description": "Ученик не найден"},
        },
    )
    def update_student(student_id: int, patch: UpdateStudent):
        if patch.student_id != student_id:
            raise HTTPException(
                status_code=400, detail="student_id in path and body must match"
            )

        with engine.begin() as conn:
            upd = patch.model_dump(exclude_unset=True)

            result = conn.execute(
                db.update(students)
                .where(students.c.student_id == student_id)
                .values(**upd)
            )
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="student not found")

        return patch

    # ---DELETE-------------------------------------------------
    @app.delete(
        "/students/{student_id}",
        tags=["students.delete"],
        summary="удаление",
        description="удаляет по id",
    )
    def delete_student(student_id: int):
        with engine.begin() as conn:
            conn.execute(
                db.delete(students).where(students.c.student_id == student_id)
            )

            rows = conn.execute(db.select(students)).fetchall()

            return [dict(r._mapping) for r in rows]


    return app

#---create-app---

app = create_app()