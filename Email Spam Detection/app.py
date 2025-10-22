from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load the saved models
model = pickle.load(open('Models/model.pkl', 'rb'))
vectorizer = pickle.load(open('Models/vectorizer.pkl', 'rb'))
le = pickle.load(open('Models/labelencoder.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        message = request.form['message'] # Get the email message from the form
        data = [message]
        email_count = vectorizer.transform(data).toarray()
        prediction = model.predict(email_count)
        result = le.inverse_transform([prediction])[0]
        return render_template('index.html', prediction=result, message=message)  
    # Pass the prediction and message to the template

if __name__ == '__main__':
    app.run(debug=True)