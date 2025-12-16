from fastapi import FastAPI , Path , HTTPException , Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel , Field
from typing import Annotated , Optional
import json

app = FastAPI()


class Patient(BaseModel):
    id : Annotated[str , Field(... , description="Patient ID" , example="P001")]
    name : Annotated[str , Field(... , description="Patient Name")] 
    age : Annotated[int , Field(... , description="Patient Age" , ge=0 , le=120)] 
    hospital : Annotated[str , Field(... , description="Hospital Name")] 
    weight : Annotated[float , Field(... , description="Patient Weight in kg" , gt=0)] 
    height : Annotated[float , Field(... , description="Patient Height in cm" , gt=0)] 

class PatientUpdate(BaseModel):
    name : Annotated[Optional[str] , Field(default=None)] 
    age : Annotated[Optional[int] , Field(default=None , gt=0)] 
    hospital : Annotated[Optional[str] ,Field(default=None)] 
    weight : Annotated[Optional[float] , Field(default=None,gt=0)] 
    height : Annotated[Optional[float] , Field(default=None,gt=0)] 

def save_data(data):
    with open( 'patients.json', 'w') as file:
        json.dump(data, file)
   

def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
    return data 

@app.get('/View')
def view_data():
    data = load_data()
    return data

@app.get('/View/{patient_id}')
def view_patient(patient_id : str = Path(... , description = "Id of Patients" , example= "P001")):

    data = load_data()

    if patient_id in data:
            return data[patient_id]
    raise HTTPException(status_code=404 , detail='Patient Not Found')



@app.get('/Sort')
def sord_by_age (sort_by : str = Query(... , description='sort on basis on age ' ),
order : str = Query('asc' , description = 'sort by asc or desc order' )):
    
    if sort_by not in ['age' , 'weight' , 'height']:
        raise HTTPException(status_code=400 , detail='Invalid sort_by parameter')
    
    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values() , key=lambda x: x.get(sort_by,0) , reverse=sort_order)

    return sorted_data 


@app.post('/Insert')
def create_patient(patient : Patient):
    
    #load data from json file 
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400 , detail='Patient ID already exists')

    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data)

    return JSONResponse(status_code=201 , content={'message' : 'Patient created successfully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id : str, patient_update : PatientUpdate):

    data = load_data()

    if patient_id not in data :
        raise HTTPException(status_code=404 , detail='Patient Not Found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset=True) 

    for key , value in updated_patient_info.items():
        existing_patient_info[key] = value 

    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(status_code=201 , content={'message' : 'Patient Updated successfully'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id : str):

    data = load_data()

    if patient_id not in data :
        raise HTTPException(status_code=404 , detail='Patient Not Found')

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200 , content={'message' : 'Patient Deleted successfully'})


