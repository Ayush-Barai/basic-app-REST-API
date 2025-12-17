from fastapi import FastAPI, Path, Query, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated, Optional, Dict
import json

app = FastAPI(title="Patient Management API")

DATA_FILE = "patients.json"

def load_data() -> Dict:
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"File not found"}

def save_data(data: Dict):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Patient ID", example="P001")]
    name: Annotated[str, Field(..., description="Patient Name")]
    age: Annotated[int, Field(..., ge=0, le=120)]
    hospital: Annotated[str, Field(...)]
    weight: Annotated[float, Field(..., gt=0)]
    height: Annotated[float, Field(..., gt=0)]

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0)
    hospital: Optional[str] = None
    weight: Optional[float] = Field(default=None, gt=0)
    height: Optional[float] = Field(default=None, gt=0)

@app.get("/patients", status_code=status.HTTP_200_OK)
def view_all_patients(data: Dict = Depends(load_data)):
    return data

@app.get("/patients/{patient_id}", status_code=status.HTTP_200_OK)
def view_patient(
    patient_id: str = Path(..., description="Patient ID", example="P001"),
    data: Dict = Depends(load_data)
):
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    return data[patient_id]


@app.get("/patients/sort/")
def sort_patients(
    sort_by: str = Query(..., description="Sort by age, weight, or height"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    data: Dict = Depends(load_data)
):
    if sort_by not in ["age", "weight", "height"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    reverse = order == "desc"
    return sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=reverse)

@app.post("/patients", status_code=status.HTTP_201_CREATED)
def create_patient(patient: Patient, data: Dict = Depends(load_data)):
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")

    data[patient.id] = patient.model_dump(exclude={"id"})
    save_data(data)

    return {"message": "Patient created successfully"}

@app.put("/patients/{patient_id}", status_code=status.HTTP_200_OK)
def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    data: Dict = Depends(load_data)
):
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    updates = patient_update.model_dump(exclude_unset=True)
    data[patient_id].update(updates)
    save_data(data)

    return {"message": "Patient updated successfully"}


@app.delete("/patients/{patient_id}", status_code=status.HTTP_200_OK)
def delete_patient(patient_id: str, data: Dict = Depends(load_data)):
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    del data[patient_id]
    save_data(data)

    return {"message": "Patient deleted successfully"}
