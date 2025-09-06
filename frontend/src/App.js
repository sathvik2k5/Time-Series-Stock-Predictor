import React, { useState } from "react";
import "./App.css"; // We'll create this CSS file

function App() {
  const [company, setCompany] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [predictDate, setPredictDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedPlot, setSelectedPlot] = useState(null);
  const [activeTab, setActiveTab] = useState("train"); // 'train' or 'predict'

  // Call /create-data
  const handleCreateData = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:5000/create-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: company,
          start_date: startDate,
          end_date: endDate,
        }),
      });

      if (!response.ok) throw new Error("Failed to create data");

      const data = await response.json();
      alert("✅ " + data); // show success
    } catch (error) {
      console.error(error);
      alert("Error creating data");
    } finally {
      setLoading(false);
    }
  };

  // Run Notebook (train + plots)
  const handleRunNotebook = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setSelectedPlot(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/run-notebook", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: company,
          start_date: startDate,
          end_date: endDate,
        }),
      });

      if (!response.ok) throw new Error("Failed to fetch results");

      const data = await response.json();
      const usefulPlots = data.plots ? data.plots : [];
      setResult({ ...data, plots: usefulPlots });
    } catch (error) {
      console.error(error);
      alert("Error running notebook");
    } finally {
      setLoading(false);
    }
  };

  const handleRunNotebook2 = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setSelectedPlot(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/run-notebook-2", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: company,
          start_date: startDate,
          end_date: endDate,
        }),
      });

      if (!response.ok) throw new Error("Failed to fetch results");

      const data = await response.json();
      const usefulPlots = data.plots ? data.plots : [];
      setResult({ ...data, plots: usefulPlots });
    } catch (error) {
      console.error(error);
      alert("Error running notebook");
    } finally {
      setLoading(false);
    }
  };

  // Predict future date
  const handlePredictDate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setSelectedPlot(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/predict-date", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: company,
          start_date: startDate,
          end_date: endDate,
          predict_date: predictDate,
        }),
      });

      if (!response.ok) throw new Error("Failed to fetch results");

      const data = await response.json();
      const usefulPlots = data.plots ? data.plots : [];
      setResult({ ...data, plots: usefulPlots });
    } catch (error) {
      console.error(error);
      alert("Error running prediction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>📈 Stock Prediction Dashboard</h1>
        <p>Analyze and predict stock prices with machine learning</p>
      </header>

      <div className="main-content">
        <div className="input-section">
          <div className="tabs">
            <button
              className={`tab ${activeTab === "train" ? "active" : ""}`}
              onClick={() => setActiveTab("train")}
            >
              🔹 Train Model
            </button>
            <button
              className={`tab ${activeTab === "predict" ? "active" : ""}`}
              onClick={() => setActiveTab("predict")}
            >
              🔹 Predict Price
            </button>
          </div>

          {/* Form 1: Create Data + Train Notebook */}
          {activeTab === "train" && (
            <form className="input-form">
              <h2>Model Training</h2>
              <p>Prepare data and train the model</p>

              <div className="form-group">
                <label>Company Ticker Symbol</label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="e.g. AAPL, MSFT, GOOGL"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Create Data Button */}
              <button
                onClick={handleCreateData}
                disabled={loading}
                className="submit-btn"
              >
                {loading ? "Processing..." : "Create Data"}
              </button>

              {/* Train Model Button */}
              <button
                onClick={handleRunNotebook}
                disabled={loading}
                className="submit-btn"
              >
                {loading ? "Training Model..." : "Run Notebook & Train"}
              </button>

              {/* Train Model Button */}
              <button
                onClick={handleRunNotebook2}
                disabled={loading}
                className="submit-btn"
              >
                {loading ? "Training Model..." : "Run LSTM Notebook & Train"}
              </button>
            </form>
          )}

          {/* Form 2: Predict by Date */}
          {activeTab === "predict" && (
            <form onSubmit={handlePredictDate} className="input-form">
              <h2>Price Prediction</h2>
              <p>Predict stock price for a specific date</p>

              <div className="form-group">
                <label>Company Ticker Symbol</label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="e.g. AAPL, MSFT, GOOGL"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label>End Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Prediction Date</label>
                <input
                  type="date"
                  value={predictDate}
                  onChange={(e) => setPredictDate(e.target.value)}
                  required
                />
              </div>

              <button type="submit" disabled={loading} className="submit-btn">
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    Predicting...
                  </>
                ) : (
                  "Predict Price"
                )}
              </button>
            </form>
          )}
        </div>

        {/* Results Section */}
        {result && (
          <div className="results-section">
            <h2>📊 Analysis Results</h2>

            {result.error ? (
              <div className="error-message">
                <h3>Error</h3>
                <p>{result.error}</p>
              </div>
            ) : (
              <>
                {/* Logs */}
                <div className="logs-container">
                  <h3>Training Logs</h3>
                  <div className="logs-content">
                    {Array.isArray(result.outputs)
                      ? result.outputs
                          .filter((line) => line.trim() !== "")
                          .map((line, idx) => (
                            <div
                              key={idx}
                              className={`log-line ${
                                line.startsWith("✅")
                                  ? "success"
                                  : line.startsWith("Epoch")
                                  ? "epoch"
                                  : line.toLowerCase().includes("error")
                                  ? "error"
                                  : ""
                              }`}
                            >
                              {line}
                            </div>
                          ))
                      : JSON.stringify(result, null, 2)}
                  </div>
                </div>

                {/* Plot Buttons */}
                {result.plots && result.plots.length > 0 && (
                  <div className="plots-section">
                    <h3>Generated Charts</h3>
                    <div className="plot-buttons">
                      {result.plots.map((_, idx) => (
                        <button
                          key={idx}
                          onClick={() => setSelectedPlot(result.plots[idx])}
                          className={`plot-btn ${
                            selectedPlot === result.plots[idx] ? "active" : ""
                          }`}
                        >
                          Chart {idx + 1}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Selected Plot */}
                {selectedPlot && (
                  <div className="selected-plot">
                    <h3>Selected Chart</h3>
                    <img src={selectedPlot} alt="Stock analysis chart" />
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {loading && (
        <div className="overlay">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Processing your request...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
