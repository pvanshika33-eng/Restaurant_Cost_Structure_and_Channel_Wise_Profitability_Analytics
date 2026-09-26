# Restaurant_Cost_Structure_and_Channel_Wise_Profitability_Analytics

### Streamlit Dashboard

## Overview

This project presents an AI-driven restaurant analytics system designed for cost structure analysis, profitability optimization, operational intelligence, and channel-wise financial performance evaluation within multi-channel restaurant ecosystems. The system combines exploratory data analysis, feature engineering, clustering techniques, PCA visualization, ensemble machine learning models, and predictive analytics to analyze restaurant performance and identify profitability patterns across multiple sales channels.

The project was developed as an enterprise-grade Business Intelligence and Machine Learning solution focused on restaurant operational analytics, delivery ecosystem intelligence, and AI-powered financial decision support.

---

## Objectives

- Analyze restaurant operational performance using business intelligence analytics
- Evaluate channel-wise revenue and profitability across multiple sales platforms
- Identify high-profit and low-profit restaurant patterns
- Analyze operational cost structures and commission impact
- Segment restaurants into meaningful business groups using clustering techniques
- Predict restaurant profitability using machine learning models
- Build an AI-driven restaurant intelligence framework
- Develop an interactive Streamlit dashboard for visualization and prediction

---

## Dataset Information

A restaurant analytics dataset containing 1,500+ restaurant records was used to simulate:

- Restaurant operational behaviour
- Revenue generation patterns
- Multi-channel delivery performance
- Profitability distribution
- Cost structure analysis
- Cuisine performance
- Segment-based operational analytics
- Aggregator dependency behaviour
- Delivery ecosystem dynamics

The dataset includes operational and financial information from multiple restaurant channels including:

- In-Store Dining
- Uber Eats
- DoorDash
- Self-Delivery

The project focuses on understanding how operational expenses, delivery platforms, customer order behaviour, and channel dependencies influence restaurant profitability and business sustainability.

---

## Technologies Used

### Programming Language

- Python

### Libraries & Frameworks

- Pandas
- NumPy
- Scikit-learn
- LightGBM
- XGBoost
- Matplotlib
- Seaborn
- Plotly
- Streamlit
- Joblib
- SciPy

---

## Exploratory Data Analysis (EDA)

The project includes detailed EDA involving:

- Revenue distribution analysis
- Profit margin analysis
- Channel-wise profitability comparison
- Cuisine performance analysis
- Segment-wise operational analysis
- Cost structure decomposition
- Delivery radius analysis
- Aggregator dependency analysis
- Correlation heatmaps
- Outlier detection and treatment
- Operational efficiency analysis
- Restaurant performance distribution analysis

---

## Feature Engineering

Several engineered features were created, including:

- TotalRevenue
- TotalNetProfit
- ProfitMargin
- AggregatorDependency
- SelfDeliveryEfficiency
- CommissionDrag

These engineered features improved restaurant profiling and machine learning model performance.

---

## Restaurant Segmentation

### Clustering Techniques Used

- K-Means Clustering
- PCA-based Visualization

### Evaluation Methods

- Elbow Method
- Silhouette Score Analysis

### Business Segments Identified

The clustering pipeline helped identify meaningful restaurant groups such as:

- High-profit restaurants
- Delivery-heavy restaurants
- Aggregator-dependent restaurants
- Operationally efficient restaurants
- High-cost restaurants
- Premium revenue restaurants

---

## Machine Learning Models Evaluated

| Model | Accuracy |
|---|---|
| LightGBM | 98.82% |
| Random Forest | 98.53% |
| XGBoost | 98.53% |
| Logistic Regression | 95.29% |

---

## Best Performing Model

### LightGBM Classifier

- Accuracy: 98.82%
- Strong overall profitability prediction capability
- Effective handling of complex operational patterns
- High business applicability for restaurant analytics systems

---

## Profitability Prediction System

The prediction framework uses:

- Ensemble machine learning models
- Feature-engineered restaurant profiles
- Operational analytics
- Cost structure indicators
- Restaurant segmentation intelligence
- PCA-enhanced clustering insights

The system predicts:

- Profitability category
- Operational risk exposure
- Margin sustainability
- Business efficiency potential
- Restaurant performance behaviour

---

## Streamlit Dashboard Features

The project includes an interactive Streamlit dashboard with:

- Executive Overview Dashboard
- Channel Profitability Analytics
- Margin Analysis Engine
- Cost Structure Breakdown
- Cuisine Analytics Dashboard
- Segment-Wise Performance Analysis
- Profit Volatility Insights
- What-If Profitability Simulator
- Restaurant Drilldown Intelligence
- AI Powered ML Prediction Center
- Interactive KPI Dashboard
- Executive Business Intelligence Reports
- Model Accuracy Comparison Charts

---

## Key Performance Indicators (KPIs)

- Total Revenue
- Total Net Profit
- Average Profit Margin
- Revenue by Channel
- Profit by Channel
- Aggregator Dependency Ratio
- Delivery Efficiency Score
- Operational Cost Ratio
- Channel Share Distribution
- Restaurant Profitability Index

---

## Project Structure

```text
Restaurant-Profitability-Analytics/
│
├── Models/
│   ├── lightgbm_model.pkl
│   ├── random_forest.pkl
│   ├── xgboost_model.pkl
│   ├── logistic_regression.pkl
│   ├── kmeans_model.pkl
│   ├── pca_model.pkl
│   └── scaler.pkl
│
├── app.py
├── Restaurant_Profitability_Research_Paper.pdf
├── restaurant_profitability.csv
├── Restaurant_Profitability_Analytics.ipynb
├── Final_Restaurant_Profitability_Dataset.csv
├── Executive_Stakeholder_Report.pdf
├── README.md
└── requirements.txt
```

---

## Running the Project

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Streamlit Dashboard

```bash
streamlit run app.py
```

---

## Research & Academic Notes

- The dataset used in this project contains structured restaurant operational and financial information.
- Results were evaluated within the available operational and profitability feature space.
- Clustering quality demonstrates meaningful separation between restaurant business groups.
- Machine learning performance depends on structured operational, revenue, and cost-related features.
- This work is intended as an educational, research-oriented, and business analytics implementation project.

---

## Future Improvements

- Real-world restaurant dataset validation
- SHAP-based explainability analysis
- Deep learning integration
- Real-time restaurant analytics pipeline
- Live operational monitoring system
- Cloud-based deployment architecture
- Advanced ensemble optimization
- Restaurant recommendation intelligence
- Explainable AI integration
- Dynamic pricing optimization
