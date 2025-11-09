# 📊 Data Visualization & Profiling App

![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Deployed-success)

> 🧠 **A dynamic Streamlit web app for uploading, analyzing, visualizing, and exporting datasets** — featuring custom dashboards, interactive visualizations, and professional PDF report generation.

---

## 🌐 Live Demo

🎯 **Try it here → [data-visulization.streamlit.app](https://data-visulization.streamlit.app/)**  

*(No setup needed — runs directly in your browser)*

---

## 🧭 Overview

This project is a **multi-page, modular Streamlit application** that allows you to:

- 📤 Upload CSV or Excel datasets (up to 150 MB).  
- 🧮 Perform automatic EDA (Exploratory Data Analysis).  
- 📈 Create rich, interactive **Bar, Distribution, Line, and Scatter** visualizations.  
- 📄 Generate **custom PDF reports** with the sections you choose.  
- 🖼️ Export visuals as **PNG** directly from the interface.  

💡 Designed to demonstrate end-to-end **data engineering, analytics, and visualization** workflows — fully coded from scratch using Streamlit and Python.

---

## 🧱 Project Structure

```bash
📦 dv_frontend/
│
├── app.py                      # Main Streamlit app entry point
│
├── utils/
│   ├── image_export.py         # Handles PNG export for Altair charts
│   └── visual_components.py    # Reusable Streamlit components for exports/UI
│
├── pages/
│   ├── dashboard.py            # (Reserved for summary dashboard)
│   ├── data/
│   │   ├── upload_dataset.py   # Upload, parse, and cache datasets
│   │   └── view_dataset.py     # Profile datasets and export PDF reports
│   └── visualization/
│       ├── bar_chart.py        # Multi-config bar charts
│       ├── distribution.py     # Histograms / categorical distributions
│       ├── line_chart.py       # Trend & time-series plots
│       └── scatter_plot.py     # Numeric correlation plots
│
├── requirements.txt
└── README.md
````

---

## ⚙️ Run Locally

### 🪜 1. Clone the repo

```bash
git clone https://github.com/carzy-zala/data-visualization-streamlit.git
cd data-visualization-streamlit
```

### 🧩 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# or
source .venv/bin/activate   # macOS/Linux
```

### 📦 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 🏃 4. Launch the app

```bash
streamlit run app.py
```

Then open 👉 [http://localhost:8501](http://localhost:8501)

---

## 📦 Dependencies

```txt
streamlit
pandas
numpy
altair
vl-convert-python
pillow
reportlab
openpyxl
```

*(Optional)* for extended analytics:

```txt
matplotlib
seaborn
ydata-profiling
```

---

## 🌟 Core Features

### 🗂️ Upload Dataset

* Accepts **CSV/XLSX** up to 150 MB.
* Auto-detects delimiters and datetime columns.
* Displays upload progress with **real-time feedback**.
* Automatically stores dataset in Streamlit session state.

---

### 📊 View Dataset

Explore dataset characteristics instantly:

* ✅ Summary: rows, columns, memory, duplicates
* 📦 Dtypes grouped by category (numeric, categorical, datetime, boolean)
* 🧮 Descriptive statistics & correlations
* 🚫 Missing and duplicate value analysis
* 📄 **PDF report generation** with customizable sections

💾 PDF exports include:

* Rounded numeric values (2 decimals)
* Clean tables (max 12 columns per table)
* Section selection
* Horizontal **Generate → Download** flow

---

### 🎨 Visualization Hub

#### 📊 Bar Chart

* Choose X/Y columns and aggregation (`sum`, `mean`, `count`, `nunique`, etc.)
* Customizable color, orientation, sorting, and labels
* Add up to 10 charts dynamically
* Export each as **PNG**

#### 📈 Distribution

* Detects numeric vs. categorical automatically
* Displays **Histogram** or **Bar Chart** accordingly
* Density overlays, normalization, and color control

#### 📆 Line Chart

* Ideal for time-based or continuous data trends
* Interactive zoom and label control

#### ⚪ Scatter Plot

* Explore relationships between numeric columns
* Optional color encoding, regression overlay

---

## 📄 PDF Report Example

<p align="center">
  <img src="https://github.com/carzy-zala/data-visualization-streamlit/assets/preview-report.png" width="80%" alt="PDF Report Preview">
</p>

---

## 🧠 Skills Demonstrated

| Skill Area           | Tools & Concepts                                      |
| -------------------- | ----------------------------------------------------- |
| **Data Engineering** | Schema inference, type detection, memory optimization |
| **Data Analysis**    | pandas, numpy, descriptive statistics, correlation    |
| **Visualization**    | Altair, Streamlit charts, dynamic chart configuration |
| **Automation**       | Custom PDF reports (ReportLab), PNG chart exports     |
| **Software Design**  | Modular architecture, reusable components             |
| **Frontend Logic**   | Streamlit navigation, state management, UI feedback   |

---

## 🧩 Example Workflow

1️⃣ **Upload** your dataset (`.csv` / `.xlsx`)
2️⃣ **Explore** summary metrics in "View Dataset"
3️⃣ **Visualize** data with charts (Bar, Distribution, Line, Scatter)
4️⃣ **Export** visuals as PNG or full report as PDF

That’s it — zero code, maximum insights ⚡

---

## 🚀 Future Enhancements

* 📊 Correlation heatmaps & pair plots
* 🧮 Outlier detection and auto-profiling
* 🪄 AI-powered EDA insights (auto-summary)
* 🌐 Database integration (SQL / BigQuery / Snowflake)
* 🧱 Persistent dashboard saving & sharing

---

## 👨‍💻 Author

**Jayrajsinh Zala (Jay)**
*Data Engineer | Data Analyst | Streamlit Developer*

🌐 [Live App](https://data-visulization.streamlit.app/)
🔗 [LinkedIn](https://linkedin.com/in/jayrajsinhzala)
📧 [jayrajsinh@example.com](mailto:jayrajsinh@example.com)
📍 United Kingdom

> ⚡ *This project demonstrates my ability to design and implement complete data workflows — from ingestion and analysis to visualization and reporting — using Python and Streamlit.*

---

## 🏁 Summary

This isn’t just a visualization tool — it’s a **data engineering showcase**:

* Modular Streamlit architecture
* Dynamic visual generation
* Automated EDA reporting
* Clean, deployable UI

🎯 **Purpose:** Demonstrate end-to-end practical data skills through an interactive web-based platform.
⭐ **Deployed Live:** [https://data-visulization.streamlit.app/](https://data-visulization.streamlit.app/)

---

<p align="center">⭐ If you find this project useful, please consider giving it a star on GitHub!</p>
```

---
