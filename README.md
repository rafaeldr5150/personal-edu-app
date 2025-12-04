# Educational Performance Analysis Dashboard

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.24.0-red)
![Pandas](https://img.shields.io/badge/Pandas-1.5.0-green)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7.0-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Overview

A comprehensive educational data analysis system that analyzes student performance in Portuguese and Mathematics, combining exploratory data analysis with an interactive web dashboard.

## ✨ Features

### 🔍 **Data Analysis Notebook**
- **Exploratory Data Analysis (EDA)**: Student performance analysis
- **Statistical Analysis**: Descriptive statistics and correlation analysis
- **Data Visualization**: Grade distribution plots and correlation graphs
- **Dataset Simulation**: Simulated student response data
- **Performance Categorization**: Automatic classification of performance levels

### 🎨 **Interactive Web Dashboard**
- **Real-time Visualizations**: Interactive charts and graphs
- **Performance Metrics**: Key statistics display
- **Student Explorer**: Individual performance analysis
- **Question Analyzer**: Identify challenging questions
- **Comparative Analysis**: Subject comparison tools

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
```
git clone https://github.com/yourusername/educational-analysis.git
cd educational-analysis

Create virtual environment

python -m venv venv

# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

Install dependencies

pip install -r requirements.txt

Running the Application

Run Jupyter Notebook


jupyter notebook part1_educational_analysis.ipynb

Run Streamlit Dashboard

streamlit run app.py
```


## 📁 Project Structure

text
```
educational-analysis/
├── .streamlit
│   └── secrets.toml
├── EDA
│   ├── desempenho_alunos_questoes.csv 
│   └── main.ipynb     
├── data/
│   ├── desempenho_alunos_questoes    
│   ├── desempenho.csv              
│   └── questoes.csv                  
├── gamefic/                             
│   ├── __init__.py
│   └── game.py
├── graphs/                             
│   ├── __init__.py
│   └── graphss.py
├── helpers/                             
│   ├── __init__.py
│   └── loader.py
├── app.py                            
├── requirements.txt                 
└── README.md   
```

## 🛠️ Technical Details

### Data Processing

- Data Loading: CSV files with student and question data
- Data Cleaning: Percentage conversion and type handling
- Transformation: Simulation of question responses
- Analysis: Statistical calculations
- Visualization: Plot generation

### Key Metrics

- Average Scores: Mean performance per subject
- Standard Deviation: Performance variation
- Correlation: Relationship between subjects
- Question Difficulty: Error rates analysis

## 📈 Visualizations

### Notebook Visualizations

- Grade Distribution: Line plots showing performance
- Box Plots: Statistical distribution
- Scatter Plots: Correlation analysis
- Bar Charts: Question distribution
- Pie Charts: Performance categories

### Dashboard Visualizations

- Interactive Histograms: Dynamic exploration
- Filterable Tables: Real-time data filtering
- Zoomable Plots: Detailed analysis
- Performance Heatmaps: Visual difficulty representation

## 📚 Educational Insights

### Key Findings

- Mathematics Performance: Generally higher than Portuguese
- Positive Correlation: Good performance in one subject relates to good performance in the other
- Content Difficulty: Specific topics show higher error rates
- Normal Distribution: Student performance follows expected patterns

### Recommendations

- Targeted Support: Focus on lower-performing students
- Content Review: Address difficult topics
- Personalized Learning: Custom study plans
- Resource Allocation: Focus on challenging areas

## 🧪 Testing

### Install test dependencies
```
pip install pytest
```

### Run tests
pytest tests/

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

- Fork the repository
- Create a feature branch
- Commit your changes
- Push to the branch
- Open a Pull Request

### Guidelines

- Follow PEP 8 style guide
- Add tests for new features
- Update documentation
- Maintain compatibility

## 🔮 Future Plans

### Features

- Machine Learning: Predictive models
- Real-time Updates: Live data integration
- Advanced Analytics: Clustering algorithms
- Mobile App: Cross-platform dashboard

## 🙏 Acknowledgments

- Data Sources: Educational institutions
- Libraries: Pandas, NumPy, Matplotlib, Streamlit
- Inspiration: Educational research
- Contributors: Project contributors

## 📚 Resources

### Documentation

- Pandas Docs
- Streamlit Docs
- Matplotlib Docs
- Related Projects

Student Performance Prediction
Educational Dashboard Templates
Learning Analytics Toolkit

<div align="center"> <p>Made for educational improvement</p> <p>If this project helps you, please give it a ⭐️</p> </div>
