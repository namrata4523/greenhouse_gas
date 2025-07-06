import gradio as gr
import joblib
import pandas as pd

def preprocess_input(df):
    substance_map = {'carbon dioxide': 0, 'methane': 1, 'nitrous oxide': 2, 'other GHGs': 3}
    unit_map = {'kg/2018 USD, purchaser price': 0, 'kg CO2e/2018 USD, purchaser price': 1}
    source_map = {'Commodity': 0, 'Industry': 1}

    df['Substance'] = df['Substance'].map(substance_map)
    df['Unit'] = df['Unit'].map(unit_map)
    df['Source'] = df['Source'].map(source_map)
    return df

# Load from local models folder
model = joblib.load('models/LR_model.pkl')
scaler = joblib.load('models/scaler.pkl')

def predict(substance, unit, source, supply_wo_margin, margin,
            dq_reliability, dq_temporal, dq_geo, dq_tech, dq_data):
    
    input_data = {
        'Substance': substance,
        'Unit': unit,
        'Supply Chain Emission Factors without Margins': supply_wo_margin,
        'Margins of Supply Chain Emission Factors': margin,
        'DQ ReliabilityScore of Factors without Margins': dq_reliability,
        'DQ TemporalCorrelation of Factors without Margins': dq_temporal,
        'DQ GeographicalCorrelation of Factors without Margins': dq_geo,
        'DQ TechnologicalCorrelation of Factors without Margins': dq_tech,
        'DQ DataCollection of Factors without Margins': dq_data,
        'Source': source
    }

    input_df = preprocess_input(pd.DataFrame([input_data]))
    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)[0]
    
    return f"✅ Predicted Emission Factor with Margin: **{prediction:.4f}**"

iface = gr.Interface(
    fn=predict,
    inputs=[
        gr.Dropdown(['carbon dioxide', 'methane', 'nitrous oxide', 'other GHGs'], label="Substance"),
        gr.Dropdown(['kg/2018 USD, purchaser price', 'kg CO2e/2018 USD, purchaser price'], label="Unit"),
        gr.Dropdown(['Commodity', 'Industry'], label="Source"),
        gr.Number(label="Supply Chain Emission Factors without Margins", value=0.0),
        gr.Number(label="Margins of Supply Chain Emission Factors", value=0.0),
        gr.Slider(0.0, 1.0, step=0.01, label="DQ Reliability"),
        gr.Slider(0.0, 1.0, step=0.01, label="DQ Temporal Correlation"),
        gr.Slider(0.0, 1.0, step=0.01, label="DQ Geographical Correlation"),
        gr.Slider(0.0, 1.0, step=0.01, label="DQ Technological Correlation"),
        gr.Slider(0.0, 1.0, step=0.01, label="DQ Data Collection")
    ],
    outputs=gr.Markdown(label="Prediction"),
    title="🌱 GHG Emissions Predictor",
    description="Predict GHG Emission Factors with Margins using DQ metrics"
)

if __name__ == "__main__":
    iface.launch()