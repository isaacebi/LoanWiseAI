# importing libraries
import pickle
import sklearn
import uvicorn
import warnings
from fastapi import FastAPI
from datetime import datetime
from src.schema import LoanApplication, LoanResults, error_check, fill_missing_data, preprocess

# ignore warning
warnings.filterwarnings('ignore')

# initiate FastAPI instance
app = FastAPI()

# Define a root endpoint accessible via a GET request to the base path (/).
@app.get("/")
async def root():
    # Return a simple JSON response with the message "Hello": "World"
    return {"Hello": "World"}

@app.post("/predict")
async def predict(request: LoanApplication):
    """ Run our loan model """
    start_time = datetime.now()  # Capture start time for processing time calculation

    try:
        # perform simple data error check
        df = error_check(request)

        # Handle missing values
        df = fill_missing_data(df)

        # Feature engineering and data preprocess
        df = preprocess(df)

        # load model
        with open('model.pkl', 'rb') as file:
            model = pickle.load(file)

        end_time = datetime.now()  # Capture end time
        total_time = end_time - start_time  # Calculate total time

        # Convert total time to milliseconds and round to two decimal places
        processing_time_ms = round(total_time.total_seconds() * 1000, 2)

        # Drop load id or user id
        X = df.drop(columns=['Loan_ID'])

        # Perform prediction
        df['label'] = model.predict(X)
        df['value'] = df['label'].apply(lambda x: "Approve" if x == 1 else "Reject")

        # Reconstruct pandas to dictionary
        results = df.to_dict(orient='records')

        # Iterate item if rows in df is more than 1
        for result in results:
            result['error_code'] = 0
            result['prediction'] = {'label': result['label'], 'value': result['value']}
            result['time_taken'] = f"{processing_time_ms} ms"
            result['status'] = 'success'

        # display only the last results for dataframe
        return LoanResults(**result)
    
    except:
        end_time = datetime.now() # Capture end time
        total_time = end_time - start_time # Calculate total time

        # Convert total time to milliseconds and round to two decimal places
        processing_time_ms = round(total_time.total_seconds() * 1000, 2)

        # Fail results to display
        result = {
            'status': 'failed',
            'error_code': 0,
            'prediction': {"label": None, "value": None},
            'time_taken': f"{processing_time_ms} ms"
        }

        return LoanResults(**result)
    

# So that python file can be call like a python file
if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
