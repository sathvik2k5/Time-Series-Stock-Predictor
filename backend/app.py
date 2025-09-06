from flask import Flask, request, jsonify
from flask_cors import CORS
import nbformat
from nbclient import NotebookClient
import joblib
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import io, base64
from datetime import datetime, timedelta
import yfinance as yf  # We'll use yfinance to get actual historical data
import os

UPLOAD_NOTEBOOK = r"C:\Users\SATHVIK\Downloads\Quant Project\QP\backend\venv\Notebook_1_ARIMA_Fourier.ipynb"
create_notebook = r"C:\Users\SATHVIK\Downloads\Quant Project\QP\backend\venv\Create_Data.ipynb"
NOTEBOOK_2 = r"C:\Users\SATHVIK\Downloads\Quant Project\QP\backend\venv\Notebook_2_Predict.ipynb"

app = Flask(__name__)
CORS(app)

@app.route("/create-data", methods = ["POST"])
def create_data():
    data = request.json
    company_name = data.get("company_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not company_name or not start_date or not end_date:
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Construct filename based on params
    safe_name = f"{company_name}_{start_date}_{end_date}.csv"
    print(safe_name)
    file_path = os.path.join("./", safe_name)   # save under ./data/

    # 1️⃣ Check if file already exists
    if os.path.exists(file_path):
        return jsonify({"message": f"Data already exists."})

    print("DEBUG:", company_name, start_date, end_date)

    with open(create_notebook, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    nb["cells"].insert(0, nbformat.v4.new_code_cell(
    f"""
company_name = "{company_name}"
start_date = "{start_date}"
end_date = "{end_date}"
print("Injected params from Flask:", company_name, start_date, end_date)
    """
))

    # Execute notebook
    client = NotebookClient(nb)
    client.execute()

    return jsonify("Successfully Created Notebook", 500)


@app.route("/run-notebook", methods=["POST"])
def run_notebook():
    data = request.json
    company_name = data.get("company_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not company_name or not start_date or not end_date:
        return jsonify({"error": "Missing required parameters"}), 400

    print("DEBUG:", company_name, start_date, end_date)

    with open(UPLOAD_NOTEBOOK, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Inject parameters into notebook
    nb["cells"].append(nbformat.v4.new_code_cell(
        f"""
company_name = "{company_name}"
start_date = "{start_date}"
end_date = "{end_date}"
print("Injected params:", company_name, start_date, end_date)
        """
    ))

    # Execute notebook
    client = NotebookClient(nb)
    client.execute()

    outputs = []
    plots = []

    # Collect logs and plot images
    for cell in nb.cells:
        if "outputs" in cell:
            for out in cell["outputs"]:
                if out.output_type == "stream":
                    outputs.append(out.text)

                elif out.output_type == "display_data":
                    if "image/png" in out.data:
                        plots.append("data:image/png;base64," + out.data["image/png"])

                elif out.output_type == "error":
                    outputs.append("Error: " + " ".join(out.evalue))

    return jsonify({"outputs": outputs, "plots": plots})

@app.route("/run-notebook-2", methods=["POST"])
def run_notebook2():
    data = request.json
    company_name = data.get("company_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not company_name or not start_date or not end_date:
        return jsonify({"error": "Missing required parameters"}), 400

    print("DEBUG:", company_name, start_date, end_date)

    with open(NOTEBOOK_2, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Inject parameters into notebook
    nb["cells"].append(nbformat.v4.new_code_cell(
        f"""
company_name = "{company_name}"
start_date = "{start_date}"
end_date = "{end_date}"
print("Injected params:", company_name, start_date, end_date)
        """
    ))

    # Execute notebook
    client = NotebookClient(nb)
    client.execute()

    outputs = []
    plots = []

    # Collect logs and plot images
    for cell in nb.cells:
        if "outputs" in cell:
            for out in cell["outputs"]:
                if out.output_type == "stream":
                    outputs.append(out.text)

                elif out.output_type == "display_data":
                    if "image/png" in out.data:
                        plots.append("data:image/png;base64," + out.data["image/png"])

                elif out.output_type == "error":
                    outputs.append("Error: " + " ".join(out.evalue))

    return jsonify({"outputs": outputs, "plots": plots})


@app.route("/predict-date", methods=["POST"])
def predict_date():
    data = request.json
    company_name = data.get("company_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    predict_date = data.get("predict_date")

    if not company_name or not predict_date:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # Load trained model + scaler
        model = joblib.load("saved_model.pkl")
        scaler = joblib.load("scaler.pkl")
        print("✅ Model and Scaler loaded successfully")

        # Load historical data
        hist_data = pd.read_csv(f"{company_name}_{start_date}_{end_date}.csv")
        
        if hist_data.empty:
            return jsonify({"error": f"Could not fetch data for {company_name}"}), 400
            
        hist_data['Date'] = pd.to_datetime(hist_data['Date'])
        
        # Use the most recent data for prediction
        close_prices = hist_data["Close"].values.reshape(-1, 1)
        
        # Get the last date from historical data
        last_train_date = hist_data['Date'].max()
        target_date = pd.to_datetime(predict_date)
        
        # Calculate days to predict
        steps_ahead = (target_date - last_train_date).days
        print(f"DEBUG: Predicting {steps_ahead} days ahead")
        
        if steps_ahead <= 0:
            return jsonify({"error": f"Prediction date must be after {last_train_date.strftime('%Y-%m-%d')}"}), 400

        # Transform with the saved scaler
        scaled_data = scaler.transform(close_prices)

        # Use a rolling window approach for better predictions
        window_size = 1  # Same as training
        predictions = []
        
        # Start with the last window of data - CORRECTED SHAPE
        current_window = scaled_data[-window_size:].reshape(1, window_size, 1)
        
        # Predict step by step
        for i in range(steps_ahead):
            # Predict next value
            next_pred = model.predict(current_window, verbose=0)
            predictions.append(next_pred[0, 0])
            
            # Update the window: remove first value, add prediction
            # CORRECTED: Properly update the window while maintaining shape
            current_window = np.roll(current_window, -1, axis=1)
            current_window[0, -1, 0] = next_pred[0, 0]

        # Inverse transform predictions
        forecast = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        predicted_price = float(forecast[-1][0])
        
        # Generate plot with historical data and prediction
        plot_data = generate_prediction_plot(hist_data, last_train_date, target_date, forecast, company_name)
        
        return jsonify({
            "outputs": [f"✅ Predicted price for {company_name} on {predict_date}: ${predicted_price:.2f}"],
            "plots": [plot_data],
            "predicted_price": predicted_price,
            "last_historical_date": last_train_date.strftime('%Y-%m-%d')
        })

    except Exception as e:
        import traceback
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


def generate_prediction_plot(historical_data, last_date, target_date, predictions, company_name):
    """
    Generate a plot showing historical prices and future predictions
    """
    # Create future dates for predictions
    future_dates = pd.date_range(
        start=last_date + timedelta(days=1),
        end=target_date
    )
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Plot historical data (last 90 days for better visualization)
    recent_data = historical_data[historical_data['Date'] >= (last_date - timedelta(days=90))]
    plt.plot(recent_data['Date'], recent_data['Close'], 
             label='Historical Prices', color='blue', linewidth=2)
    
    # Plot predictions
    plt.plot(future_dates, predictions, 
             label='Predicted Prices', color='red', linestyle='--', linewidth=2)
    
    # Highlight the transition from historical to predicted
    plt.axvline(x=last_date, color='gray', linestyle=':', alpha=0.7)
    
    # Highlight the target prediction date
    plt.axvline(x=target_date, color='green', linestyle=':', 
                label=f'Prediction Date: {target_date.strftime("%Y-%m-%d")}')
    
    # Add a marker for the predicted price on the target date
    predicted_price = predictions[-1][0]
    plt.plot(target_date, predicted_price, 'go', markersize=8)
    plt.annotate(f'${predicted_price:.2f}', 
                 (target_date, predicted_price),
                 textcoords="offset points", 
                 xytext=(0,10), 
                 ha='center',
                 fontsize=10,
                 bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))
    
    # Format the plot
    plt.title(f'{company_name} Stock Price Prediction', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price ($)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return "data:image/png;base64," + plot_data


if __name__ == "__main__":
    app.run(debug=True)