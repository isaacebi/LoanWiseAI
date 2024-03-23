import pandas as pd
from pydantic import BaseModel, Field, field_validator
from typing import Union


# input class
class LoanApplication(BaseModel):
    Loan_ID: Union[str, None]
    Gender: Union[str, None]
    Married: Union[str, None]
    Dependents: Union[str, None]
    Education: Union[str, None]
    Self_Employed: Union[str, None]
    ApplicantIncome: Union[int, None]
    CoapplicantIncome: Union[float, None]
    LoanAmount: Union[float, None]
    Loan_Amount_Term: Union[float, None]
    Credit_History: Union[float, None]
    Property_Area: Union[str, None]

    @field_validator('Gender')
    def gender_check(cls, value):
        if value.lower() not in ['male', 'female']:
            raise ValueError('Gender only support "Male" & "Female"')
        

# output class
class LoanResults(BaseModel):
    status: Union[str, None] = Field(default='failed')
    error_code: int = Field(default=1)
    prediction: dict[str, Union[str, int]] = Field(default={'label': None, 'value': None})
    time_taken: str


# check if df is valid, if no raise error
def error_check(data: LoanApplication):

    # load data
    data = data.model_dump()

    try:
        df = pd.DataFrame(data)
    except:
        df = pd.DataFrame(data, index=[0])

    if df.empty:
        return {"error": "Data is not valid format"}
    
    return df


# simple imputation
def fill_missing_data(df):

    # fill empty values for Credit_History column with value 1
    df['Credit_History'].fillna(1, inplace=True)
    df['Self_Employed'].fillna('No', inplace=True)
    df['Dependents'].fillna("0", inplace=True)
    df['Gender'].fillna("Male", inplace=True)

    # remove any data that is still has null value
    df = df.dropna()
    return df


# data preprocessing and transformation
def preprocess(df):
    # data processing and mapping
    df['Gender'] = df['Gender'].apply(lambda x: 1 if x == 'Male' else 0) 
    df['Married'] = df['Married'].apply(lambda x: 1 if x == 'Married' else 0)
    df['Dependents'] = df['Dependents'].map({'0': 0, '1': 1, '2': 2, '3+': 3}) # domain knowledge feature
    df['Education'] = df['Education'].apply(lambda x: 1 if x == 'Graduate' else 0)
    df['Self_Employed'] = df['Self_Employed'].apply(lambda x: 1 if x == 'No' else 0)
    df['Property_Area'] = df['Property_Area'].map({'Urban': 2, 'Rural': 0, 'Semiurban': 1}) #ordinal feature
    return df