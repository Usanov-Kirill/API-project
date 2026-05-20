from pydantic import BaseModel, Field

class Student(BaseModel):
    student_id: int = Field(..., description="id")
    first_name: str = Field(..., description="имя")
    last_name: str = Field(..., description="фамилия")
    phone_number: str = Field(..., description="Электронная почта") 
    grade: int = Field(..., description="класс")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "student_id": 1,
                    "first_name": "имя",
                    "last_name": "фамилия",
                    "phone_number": "+7 000 000-00-00",
                    "grade": 0,
                }
            ]
        }
    }

class Error(BaseModel):
    detail: str

class UpdateStudent(BaseModel):
    student_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    grade: int | None = None
