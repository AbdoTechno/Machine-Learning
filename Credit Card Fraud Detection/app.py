from flask import Flask, render_template, request, send_file
import pandas as pd
import pickle
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

# Load trained model
MODEL_PATH = os.path.join("models", "logistic_regression_model.pkl")
with open(MODEL_PATH, 'rb') as file:
    model = pickle.load(file)

EXPECTED_FEATURES = [
    'Time', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9',
    'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18',
    'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', 'V27',
    'V28', 'Amount'
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return render_template('result.html', error="⚠️ No file uploaded.")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('result.html', error="⚠️ Please choose a CSV file.")

    try:
        data = pd.read_csv(file)
    except Exception as e:
        return render_template('result.html', error=f"❌ Error reading file: {e}")

    
    required_columns = [
        'Time', 'V1','V2','V3','V4','V5','V6','V7','V8','V9','V10',
        'V11','V12','V13','V14','V15','V16','V17','V18','V19','V20',
        'V21','V22','V23','V24','V25','V26','V27','V28','Amount'
    ]
    missing = [c for c in required_columns if c not in data.columns]
    if missing:
        return render_template('result.html', error=f"❌ Missing required columns: {', '.join(missing)}")

   
    if 'Hour' not in data.columns and 'Time' in data.columns:
        data['Hour'] = (data['Time'] / 3600) % 24  

    
    expected_features = required_columns.copy()
    expected_features.append('Hour')
    X = data[expected_features]

   
    predictions = model.predict(X)
    data['Prediction'] = predictions
    data['Prediction_Label'] = data['Prediction'].map({0: 'Legit', 1: 'Fraud'})

   
    total = len(data)
    fraud_cases = int((data['Prediction'] == 1).sum())
    legit_cases = total - fraud_cases
    fraud_percent = round((fraud_cases / total) * 100, 2)

    summary = {
        "Total Samples": total,
        "Fraud Cases": fraud_cases,
        "Legit Cases": legit_cases,
        "Fraud Percentage": fraud_percent
    }

    
    output_path = os.path.join("static", "predicted_results.csv")
    data.to_csv(output_path, index=False)

    
    import matplotlib.pyplot as plt
    plt.figure(figsize=(4, 4))
    plt.bar(['Legit', 'Fraud'], [legit_cases, fraud_cases], color=['#4CAF50', '#F44336'])
    plt.title("Fraud Detection Summary")
    plt.xlabel("Transaction Type")
    plt.ylabel("Count")
    plt.tight_layout()
    chart_path = os.path.join("static", "fraud_chart.png")
    plt.savefig(chart_path)
    plt.close()

    
    fraud_samples = data[data['Prediction'] == 1].head(10)
    fraud_samples = fraud_samples.drop([ 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20', 'V21', 'V22', 'V23', 'V24', 'V25', 'V26', ], axis=1)

    return render_template(
        'result.html',
        summary=summary,
        fraud_samples=fraud_samples.to_html(classes='table table-striped', index=False),
        chart_url="static/fraud_chart.png",
        download_link="static/predicted_results.csv"
    )


@app.route('/download')
def download():
    return send_file("static/predicted_results.csv", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)


