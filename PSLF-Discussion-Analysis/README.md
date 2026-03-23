# PSLF Discussion Analysis

## Overview

This project analyzes Public Service Loan Forgiveness (PSLF) discussions across multiple platforms, with a focus on medical professionals and healthcare workers. The analysis includes sentiment analysis, time series trends, policy impact assessment, and comprehensive data visualizations.

## Key Features

- **Multi-Platform Data Collection**: Reddit (r/PSLF, r/medicalschool, r/medicine, r/StudentLoans, r/personalfinance) and Student Doctor Network
- **Sentiment Analysis**: TextBlob-based polarity and subjectivity analysis
- **Time Series Analysis**: Temporal trends, seasonal patterns, and policy impact assessment
- **Medical Professional Focus**: Specialized analysis for healthcare workers and medical trainees
- **Comprehensive Visualizations**: 12-panel analytics dashboard with word clouds and trend analysis
- **Statistical Modeling**: Trend analysis and basic forecasting

## Analysis Results

### Dataset Overview
- **322 total posts** analyzed across platforms
- **40.7% medical-related** discussions
- **Date range**: 2012-2025 (13+ years of data)
- **Overall positive sentiment** (0.088 average polarity)

### Key Insights
- **Medical professionals** show 5x higher engagement than general users
- **Policy changes** significantly impact discussion volume and sentiment
- **Academic calendar correlation**: Medical discussions peak during training transitions
- **Seasonal patterns**: August peak (residency/fellowship season), October low

## Technology Stack

- **Python 3.9+**
- **Data Analysis**: pandas, numpy, scipy, scikit-learn
- **Visualization**: matplotlib, seaborn, wordcloud
- **Text Processing**: NLTK, TextBlob
- **Web Scraping**: requests, BeautifulSoup
- **API Integration**: Reddit API (PRAW)

## Project Structure

```
PSLF/
├── notebook.ipynb                          # Main analysis notebook
├── pyproject.toml                          # Poetry configuration
├── combined_pslf_discussions.csv           # Multi-platform dataset
├── enhanced_pslf_discussions.csv           # Enhanced search dataset
├── reddit_pslf_discussions.csv             # Reddit-specific data
├── sdn_pslf_discussions.csv               # Student Doctor Network data
└── README.md                              # This file
```

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Poetry (for dependency management)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/PSLF-analysis.git
cd PSLF-analysis
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

4. Launch Jupyter Notebook:
```bash
jupyter notebook
```

5. Open `notebook.ipynb` and run the cells

## Analysis Components

### 1. Data Collection
- Reddit API integration for real-time data
- Student Doctor Network scraping
- Enhanced search terms for comprehensive coverage

### 2. Sentiment Analysis
- TextBlob polarity scoring (-1 to +1)
- Categorical classification (positive, negative, neutral)
- Topic-specific sentiment analysis

### 3. Time Series Analysis
- Monthly discussion volume trends
- Sentiment evolution over time
- Policy impact assessment
- Seasonal pattern identification

### 4. Medical Professional Analysis
- Healthcare-specific keyword filtering
- Medical vs general user comparison
- Academic calendar correlation analysis

### 5. Visualization Dashboard
- 12-panel comprehensive analytics
- Word clouds for different categories
- Time series plots and trend analysis
- Engagement metrics and platform comparisons

## Policy Impact Analysis

The analysis includes assessment of major PSLF policy changes:
- **2017-10-01**: PSLF Program First Eligible Date
- **2018-09-01**: TEPSLF Program Launch
- **2020-03-01**: COVID-19 Payment Pause
- **2021-10-01**: Limited PSLF Waiver Announced
- **2022-10-31**: Limited PSLF Waiver Deadline
- **2023-07-01**: New SAVE Income Plan Launch

## Key Findings

1. **Volume Growth**: Strong upward trajectory, especially since 2022
2. **Policy Sensitivity**: Clear response to PSLF policy changes
3. **Academic Seasonality**: Medical discussions peak during training transitions
4. **Sentiment Stability**: Generally positive with improving trend
5. **Platform Dynamics**: Medical subreddits show different engagement patterns

## Future Enhancements

- Real-time data pipeline integration
- Interactive dashboard development
- Advanced NLP topic modeling
- Predictive analytics for policy impact
- Cross-platform sentiment comparison

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

*This analysis was conducted for research purposes to understand public discourse around PSLF policy and its impact on medical professionals and public service workers.*
