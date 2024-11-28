# Dominos---Predictive-Purchase-Order-System

# Problem Statement

Dominoe's Pizza aims to optimize its inventory management by predicting future pizza sales and automating purchase orders for ingredients. This predictive system helps ensure sufficient ingredient stock without overstocking, reducing waste and avoiding stockouts. The project uses historical sales data and ingredient requirements to build a forecasting model that enhances inventory management and operational efficiency.

# Business Use Cases

   **1. Inventory Management:** Maintain optimal stock levels for ingredients to meet demand without overstocking.

   **2. Cost Reduction:** Minimize waste and reduce costs from excess or expired inventory.

   **3. Sales Forecasting:** Predict sales trends to inform promotions and strategies.

   **4. Supply Chain Optimization:** Streamline the ingredient ordering process to align with forecasted sales.

# Skills Takeaway From This Project

   * Data Cleaning and Preprocessing
   * Exploratory Data Analysis (EDA)
   * Multiple Time Series Forecasting
   * Predictive Modeling
   * Business Decision Making
   * Real-world Application of Data Science

# Domain
 Food Service Industry

# Dataset
    * Sales dataset
    * Ingredients dataset
    * Alao at https://www.kaggle.com/datasets/nextmillionaire/pizza-sales-dataset

# Data Explanation

1. **Sales Data:** Historical sales records including date, pizza type, quantity sold, price, category, and ingredients.
 
2. **Ingredient Data:** Ingredient requirements for each pizza type, specifying the amount needed per pizza (pizza type, ingredient, quantity needed).
 
3. **Dated:** Data from 01-01-2015 to 31-12-2015
  
4. **Unique Values:** Contains 91 unique pizzas and 64 unique pizza ingredients

             * Data spans from 01-01-2015 to 31-12-2015
   
             * Data contains 91 unique pizzas

             * Data contains 64 unique pizza ingredients

# Approach

# 1. Data Preprocessing and Exploration

**Data Cleaning:** Handled missing data, outliers, and format inconsistencies.

**Exploratory Data Analysis (EDA):** Analyzed historical trends, seasonality, and patterns in sales data, and visualize to identify important features.

Data of only 4 unique pizzas for visualization

          * Example_graph_for_4_pizzas.png

# 2. Further Data Preparation and Model Selection:

**Feature Engineering:** Extracted features such as day of the week, month, promotions, and holiday effects.

**Model Selection:** Selected time series forecasting models like Linear Regression, Decesion Trees, Random Forest, Gradient boost models, and LSTM(Long Short-Term Memory RNN).

# 3. Model Training Using Classic ML models:

**>> Data Conversion**: Categorical data was one-hot encoded and label encoded before feeding to the machine learning models

**>> Train-Test Split:** Since this is a time series data, we don't randomly split but we split by time as to not lead to data leakage

**>> Model Evaluation:** Evaluation of the classic ml models using metrics such as Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Mean Squared Error(MSE) to ensure accuracy

Although Gradient Boosting gives us the best among them and a good MAE, it's not ideal

                

