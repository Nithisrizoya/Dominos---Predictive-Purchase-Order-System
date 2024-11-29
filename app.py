import streamlit as st
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model # type: ignore
from sklearn.preprocessing import MinMaxScaler
from io import BytesIO

# Add custom CSS for background and fonts
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f4f9;
        font-family: 'Roboto', sans-serif;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        padding: 10px;
    }
    .stSlider>.css-14xtw13 {
        background-color: #007bff;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load your data and model
@st.cache_resource
def load_data():
    # Load your data here (adjust path as needed)
    dfs = pd.read_excel('Pizza_Sale_Cleaned.xlsx')
    dfs['order_date'] = pd.to_datetime(dfs['order_date'])
    df_agg = dfs.groupby(['order_date', 'pizza_name_id']).agg({'quantity': 'sum', }).reset_index()
    df_agg['order_date'] = pd.to_datetime(df_agg['order_date'], format='%Y-%m-%d')
    data = pd.pivot_table(
        data=df_agg,
        values='quantity',
        index='order_date',
        columns='pizza_name_id'
    )
    data.columns.name = None
    data.columns = [f"{col}" for col in data.columns]
    data = data.asfreq('1D')
    data = data.sort_index()
    data.fillna(0, inplace=True)
    return data

@st.cache_resource
def load_lstm_model():
    # Load the pre-trained LSTM model
    loaded_model = load_model("lstm_pizza_model.keras")
    return loaded_model

# Initialize Streamlit app
st.title("Domino's Pizza Demand Forecast and Ingredient Planner 🍕")
st.write("This interactive app predicts daily pizza sales and calculates the required ingredients for each day. It uses historical pizza order data and an LSTM model to forecast future demand. Users can select the number of days to forecast, and the app generates a detailed pizza order list along with the corresponding ingredient quantities for each day. Perfect for streamlining supply chain planning and inventory management in a pizza business!")

# Load data and model
data = load_data()
model = load_lstm_model()

# Section 1: Data Summary
with st.expander('Dataset Summary'):
    st.subheader('Dataset Overview')
    data = load_data()
    model = load_lstm_model()
    min_date = data.index.min()
    max_date = data.index.max()
    st.write(f"Data spans from **{min_date.strftime('%Y-%m-%d')}** to **{max_date.strftime('%Y-%m-%d')}**")
    st.write(f"Data contains **{len(data.columns)} unique pizzas**")
    st.write("Data contains **64 unique ingredients**")


# Select number of days to forecast
days_to_forecast = st.slider('Select number of days to forecast', min_value=1, max_value=365, value=7)

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

sequence_length = 7

def predict_next_n_days(model, data, sequence_length, scaler, n):
    predictions = []
    recent_data = data[-sequence_length:]

    for _ in range(n):
        input_sequence = np.expand_dims(recent_data, axis=0)  # Shape: (1, sequence_length, number_of_features)
        pred_scaled = model.predict(input_sequence)
        pred = scaler.inverse_transform(pred_scaled.reshape(-1, pred_scaled.shape[-1]))  # Reshape for inverse_transform
        predictions.append(pred[-1])  # Append the last prediction

        # Update the recent data with the new prediction
        recent_data = np.append(recent_data[1:], np.expand_dims(pred_scaled[0], axis=0), axis=0)

    return np.array(predictions)

# Predict button
if st.button('Predict 🚀'):
    # Ensure the model is compatible with the forecast period
    if days_to_forecast <= 0:
        st.error('Number of days to forecast must be greater than 0')
    else:
        test_predictions = predict_next_n_days(model, scaled_data, sequence_length, scaler, days_to_forecast)
        rounded_predictions = np.round(test_predictions).astype(int)
        pizza_names = data.columns
        df_forecasted = pd.DataFrame(rounded_predictions, columns=pizza_names)
        next_1_day = max_date + pd.Timedelta(days=1)
        next_n_days = max_date + pd.Timedelta(days=days_to_forecast)
        st.success(f"Data predicted for **{next_1_day.strftime('%Y-%m-%d')}** to **{next_n_days.strftime('%Y-%m-%d')}**")
        df_ing = pd.read_excel('Pizza_ingredients_cleaned.xlsx')
        file_name_pizza_order = f"output/pizza_order_forecast_{next_1_day.strftime('%b%d')}_to_{next_n_days.strftime('%b%d')}.xlsx"
        file_name_pizza_quantities = f"output/pizza_quantities_{next_1_day.strftime('%b%d')}_to_{next_n_days.strftime('%b%d')}.xlsx"

        # Calculating quantity amount in grams of each ingredient per day
        num_rows = len(df_forecasted)
        df_forecasted['day'] = [(i % num_rows) + 1 for i in range(num_rows)]
        df_forecast_long = df_forecasted.melt(id_vars=['day'], var_name='pizza_name_id', value_name='forecast_qty')
        df_merged = pd.merge(df_forecast_long, df_ing, on='pizza_name_id')
        df_merged['total_qty'] = df_merged['forecast_qty'] * df_merged['Items_Qty_In_Grams']
        df_total_qty_by_day_ingredient = df_merged.groupby(['day', 'pizza_ingredients'])['total_qty'].sum().reset_index()

        # Create order lists for each day
        all_orders = {}
        for day, quantities in enumerate(rounded_predictions):
            order_list = []
            for i, quantity in enumerate(quantities):
                if quantity > 0:
                    pizza_code = pizza_names[i]
                    pizza_info = df_ing[df_ing['pizza_name_id'] == pizza_code]
                    if not pizza_info.empty:
                        pizza_name = pizza_info['pizza_name'].values[0]
                        pizza_size = pizza_info['pizza_size'].values[0]
                        order_list.append({
                            'Code': pizza_code,
                            'Pizza Name': pizza_name,
                            'Size': pizza_size,
                            'Quantity': quantity
                        })
            all_orders[f'Day_{day + 1}'] = pd.DataFrame(order_list)

        # Display results side-by-side
        st.title('Pizza Demand Forecast and Ingredient Requirements in Grams')
        for day in range(days_to_forecast):
            # Create two columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader(f'Pizza Demand Forecast for Day {day + 1}')
                if f'Day_{day + 1}' in all_orders:
                    st.dataframe(all_orders[f'Day_{day + 1}'])

            with col2:
                st.subheader(f'Ingredient Requirements for Day {day + 1}')
                df_day_ingredient = df_total_qty_by_day_ingredient[df_total_qty_by_day_ingredient['day'] == day + 1]
                st.dataframe(df_day_ingredient[['pizza_ingredients', 'total_qty']])

        # Create a Pandas Excel writer object
        with pd.ExcelWriter(file_name_pizza_order, engine='openpyxl') as writer:
            # Loop through each day's pizza quantities
            for day, quantities in enumerate(rounded_predictions):
                order_list = []

                for i, quantity in enumerate(quantities):
                    if quantity > 0:
                        pizza_code = pizza_names[i]

                        # Get pizza name and size from df_ing
                        pizza_info = df_ing[df_ing['pizza_name_id'] == pizza_code]

                        if not pizza_info.empty:
                            pizza_name = pizza_info['pizza_name'].values[0]
                            pizza_size = pizza_info['pizza_size'].values[0]

                            # Add to order list
                            order_list.append({
                                'Code': pizza_code,
                                'Pizza Name': pizza_name,
                                'Size': pizza_size,
                                'Quantity': quantity
                            })

                # Convert the list of orders to a DataFrame for this day
                df_order = pd.DataFrame(order_list)

                # Write the DataFrame to a sheet in the Excel file
                df_order.to_excel(writer, sheet_name=f'Day_{day + 1}', index=False)

        st.write(f"File saved as: **{file_name_pizza_order}**📥")

        with pd.ExcelWriter(file_name_pizza_quantities, engine='openpyxl') as writer:
            # Iterate through each unique day
            for day in df_total_qty_by_day_ingredient['day'].unique():
                # Filter data for the current day
                df_day = df_total_qty_by_day_ingredient[df_total_qty_by_day_ingredient['day'] == day]

                # Write the DataFrame to a new sheet in the Excel file
                df_day[['pizza_ingredients', 'total_qty']].to_excel(writer, sheet_name=f'Day_{day}', index=False)

        st.write(f"File saved as: **{file_name_pizza_quantities}** 📥")