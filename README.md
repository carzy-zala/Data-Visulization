# 📊 Data Visualization & Profiling App

![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

> 🧠 **A dynamic Streamlit web app for uploading, analyzing, visualizing, and exporting datasets** — featuring custom dashboards, interactive visualizations, and PDF report generation.

---

## 🖼️ Preview

<p align="center">
  <img src="https://github.com/your-username/data-visualization-streamlit/assets/preview-dashboard.png" width="80%" alt="Dashboard Preview">
</p>

---

## 🚀 Overview

This project is a **multi-page, modular Streamlit application** that lets users:

- Upload **CSV** or **Excel** datasets.  
- Explore data interactively with summaries and EDA insights.  
- Visualize data through customizable **Bar, Line, Distribution, and Scatter plots**.  
- Generate **beautiful PDF reports** with selected analytics sections.  
- Export charts as **PNG** files directly from the app.  

💡 It’s a complete mini-framework for **data analysis and visualization**, built from scratch — demonstrating strong **Python, data engineering, and front-end integration** skills.

---

## 🧱 Project Architecture

```bash
📦 dv_frontend/
│
├── app.py                      # Main entry point for Streamlit
│
├── utils/
│   ├── image_export.py         # Handles PNG chart export (Altair + Pillow)
│   └── visual_components.py    # Reusable Streamlit UI components
│
├── pages/
│   ├── dashboard.py            # Placeholder for overall summary view
│   ├── data/
│   │   ├── upload_dataset.py   # Upload & store dataset in session
│   │   └── view_dataset.py     # Interactive dataset profiling + PDF report
│   └── visualization/
│       ├── bar_chart.py        # Dynamic bar chart builder
│       ├── distribution.py     # Histogram / categorical distribution
│       ├── line_chart.py       # Time-series and trend plots
│       └── scatter_plot.py     # Correlation and relationship plots
│
├── requirements.txt
└── README.md
````

---

## ⚙️ How to Run Locally

### 🪜 1. Clone this repository

```bash
git clone https://github.com/your-username/data-visualization-streamlit.git
cd data-visualization-streamlit
```

### 🧩 2. Create a virtual environment

```bash
python -m venv .venv
# Activate it
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Mac / Linux
```

### 📦 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 🏃 4. Run the Streamlit app

```bash
streamlit run app.py
```

> Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧰 Requirements

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

*(Optional)*
If you plan to extend visualizations:

```txt
matplotlib
seaborn
ydata-profiling
```

---

## 🌟 Core Features

### 🗂️ Upload Dataset

* Supports **CSV** and **Excel** formats.
* Smart delimiter detection and datetime inference.
* Displays upload progress with **live status updates**.
* Automatically stores data in session state for use across pages.

---

### 👁️ View Dataset

* Quick stats: rows, columns, memory usage, duplicate count.
* Column grouping by data type (numeric, categorical, datetime, boolean).
* Missing value matrix and duplicates preview.
* Descriptive statistics (`describe`) for numeric & categorical columns.
* Correlation matrix for numeric-only columns.
* **Export to PDF report** with custom section selection (Quick Stats, Missing Values, Correlations, etc.).

🖨️ PDF reports include:

* Rounded numeric values (2 decimals)
* Clean layout and typography
* Optional sections (user-selectable)
* One-click “Generate → Download” horizontal buttons

---

### 📊 Visualization Pages

#### 📈 Bar Charts

* Choose categorical and numeric columns.
* Aggregations: `sum`, `mean`, `count`, `nunique`, etc.
* Dynamic color palette, label orientation, and sorting.
* Export charts as **PNG** with one click.

#### 📉 Distribution

* Automatically decides **bar** (categorical) or **histogram** (numeric).
* Configurable bins, normalization, and density overlays.
* Clean, interactive Altair visuals with color customization.

#### 📆 Line Charts

* Plot trends or time-series metrics with full control over axes, colors, and smoothing.

#### ⚪ Scatter Plots

* Compare any two numeric columns, with optional color encoding.
* Ideal for correlation, clustering, or outlier analysis.

---

## 📄 PDF Report Example

<p align="center">
  <img src="https://github.com/your-username/data-visualization-streamlit/assets/preview-report.png" width="80%" alt="PDF Report Preview">
</p>

---

## 🧠 Skills Demonstrated

| Category                 | Technologies / Concepts                                    |
| ------------------------ | ---------------------------------------------------------- |
| **Frontend**             | Streamlit, Altair, responsive layout, interactive charts   |
| **Backend / Data Logic** | pandas, numpy, I/O handling, data profiling                |
| **Visualization Export** | Altair + Pillow PNG export                                 |
| **Report Generation**    | ReportLab dynamic PDF creation                             |
| **Software Design**      | Modular code, config-driven pages, reusable components     |
| **Data Engineering**     | Schema inference, datetime parsing, memory optimization    |
| **UI/UX**                | Session management, feedback messages, clean modern design |

---

## 🧩 Example Workflow

1️⃣ Upload your dataset (`.csv` or `.xlsx`).
2️⃣ Explore summary metrics under **View Dataset**.
3️⃣ Create multiple **visualizations** under the “Visualization” tab.
4️⃣ Export visuals as **PNG** or a **comprehensive PDF report**.

That’s it — no code, just insights 🔥.

---

## 🚀 Future Enhancements

* 📊 Correlation Heatmap & Pairplot view
* 🧮 Outlier detection & anomaly summary
* 🪄 Smart EDA recommendations
* 🌐 Direct database (SQL/Snowflake/BigQuery) integration
* 💾 Option to save user reports and dashboards persistently

---

## 👨‍💻 Author

**Jayrajsinh Zala (Jay)**
*Data Engineer | Data Analyst | Streamlit Developer*

🌐 [LinkedIn](https://linkedin.com/in/jayrajsinhzala)
📧 [jayrajsinh@example.com](mailto:jayrajsinh@example.com)
📍 United Kingdom

> ⚡ *This project represents my ability to design, build, and deliver modular, data-driven Streamlit applications that combine engineering, analytics, and visualization in one seamless workflow.*

---

## 🏁 Summary

This Streamlit application isn’t just a visualization tool — it’s a **data engineering showcase**:

* Modular architecture
* Interactive analytics
* Config-driven reporting
* Clean, modern user experience

🎯 **Purpose:** Demonstrate the full stack of practical data skills — from ingestion and EDA to visualization and reporting — in a single, interactive Python app.

---

<p align="center">⭐ If you find this project useful, please consider starring it on GitHub!</p>
```

---

### ✅ Why This Version Works

* **Visually professional**: uses badges, centered preview images, and emojis.
* **HR-friendly**: reads like a portfolio summary (shows your strengths explicitly).
* **Technically impressive**: highlights modular architecture, EDA logic, and visual export.
* **SEO-friendly for GitHub**: includes keywords (“Streamlit”, “EDA”, “PDF report”, “Data Visualization”).
