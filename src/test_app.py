import pytest

from fastapi import FastAPI, HTTPException, Query, Path as PathParam, Response
import sqlalchemy as db
from src.database import engine, students, init_db
from src.schemas import Student, UpdateStudent, Error

import src.app
import logging 
 
log = logging.getLogger(__name__) 
 
 
def log_response(method: str, url: str, response): 
    log.info("%s %s -> %s", method, url, response.status_code) 

    if response.status_code >= 400: 
        log.warning("Response body: %s", response.text[:500])

#---get---

def test_health(client):
    response = client.get("/")
    log_response("GET", "/", response) 
    assert response.status_code == 200 

def test_get_all_students(client): 
    response = client.get("/students")
    log_response("GET", "/students", response) 
    assert response.status_code == 200 

def test_get_students_by_grade(client): 
    response = client.get("/students/3") 
    log_response("GET", "/students/3", response) 
    assert response.status_code == 200 
    data = response.json() 
    assert all(s["grade"] == 3 for s in data) 

#---post---

def test_create_student(client):
    form = { 
        "student_id": 10, 
        "first_name": "Пётр", 
        "last_name": "Сидоров", 
        "phone_number": "email@gmail.com",
        "grade": 5, 
    } 
    response_1 = client.post("/students", json=form) 
    log_response("POST", "/students", response_1) 
    assert response_1.status_code == 201

    response_2 = client.post("/students", json=form) 
    log_response("POST", "/students", response_2) 
    assert response_2.status_code == 409

#---put---

def test_replace_student(client):
    client.post("/students", json={ 
        "student_id": 11,
        "first_name": "Пётр", 
        "last_name": "Сидоров", 
        "phone_number": "email4@email.com",
        "grade": 4, 
    }) 
 
    ok = { 
        "student_id": 11, 
        "first_name": "Пётр", 
        "last_name": "Сидоров", 
        "phone_number": "email5@gmail.com",
        "grade": 5, 
    } 
    response_ok = client.put("/students/11", json=ok) 
    log_response("PUT", "/students/11", response_ok) 
    assert response_ok.status_code == 200 
    assert response_ok.json()["grade"] == 5 
 
    bad = ok.copy() 
    bad["student_id"] = 999 
    response_bad = client.put("/students/11", json=bad) 
    log_response("PUT", "/students/11", response_bad) 
    assert response_bad.status_code == 400 

#---patch---
def test_update_student(client):
    rsp = client.post("/students", json={ 
        "student_id": 14,
        "first_name": "Имя", 
        "last_name": "Фамилия", 
        "phone_number": "7892421512", 
        "grade": 1, 
    }) 

    ok = { 
        "student_id": 14, 
        "grade": 3, 
    } 
    response = client.patch("/students/14", json=ok) 
    log_response("PATCH", "/students/14", response) 
    assert response.status_code == 200

#---delete---

def test_delete_student(client):
    rsp = client.post("/students", json={ 
        "student_id": 13,
        "first_name": "Гена", 
        "last_name": "Елкин", 
        "phone_number": "7194184194", 
        "grade": 2, 
    }) 

    response = client.delete("/students/13")
    log_response("DELETE", "/students/13", response) 
    assert response.status_code == 200