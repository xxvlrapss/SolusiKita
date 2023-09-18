from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import json
import requests

with open('../api_keys/apikey.json', 'r') as api_file:
    api_data = json.load(api_file)
    API_KEY = api_data['apikey']

deployment_url = 'https://us-south.ml.cloud.ibm.com/ml/v4/deployments/9d1305ff-c8f2-42dc-bc8d-064ba0131a50/predictions?version=2021-05-01'

app = FastAPI()

templates = Jinja2Templates(directory='../templates')

@app.get('/')
def read_root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.post('/predict')
async def predict_stunting(
    Sex: int = Form(...),
    Age: float = Form(...),
    Weight: float = Form(...),
    Length: float = Form(...)
):

    token_response = requests.post('https://iam.cloud.ibm.com/identity/token',
                                   data={"apikey": API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
    
    mltoken = token_response.json()["access_token"]

    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}

    array_of_input_fields = ["Sex", "Age", "Weight", "Length"]
    array_of_values_to_be_scored = [Sex, Age, Weight, Length]

    payload_scoring = {"input_data": [{"fields": [array_of_input_fields], "values": [array_of_values_to_be_scored]}]}

    response_scoring = requests.post(deployment_url, json=payload_scoring, headers={'Authorization': 'Bearer ' + mltoken})
    output_json = response_scoring.json()
    prediction = output_json['predictions'][0]['values'][0][0]

    if prediction == 1:
        return {'prediction': "Kamu Terkena Stunting"}
    
    elif prediction == 0: 
        return {'prediction': "Kamu Tidak Terkena Stunting"}
    
    else:
        return {'error': 'gagal mendapatkan prediksi'}
    
if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)