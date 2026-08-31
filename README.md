# Natal Chart Explorer
A Streamlit-based interactive natal chart application built with Python and Kerykeion.
Hosted on https://natal-chart.streamlit.app/.

# Overview
Natal Chart Explorer lets you enter birth data, generate a natal chart, explore planetary positions and aspects interactively, and use AI-powered tools to interpret the chart.

# Features
## 1. Enter Birth Data & Generate Chart
Enter the birth date, time, and location to generate the natal chart. The application then displays the calculated chart along with the relevant planetary and house information.

![Natal chart generation demo](https://i.imgur.com/c0YWQFO.gif)

## 2. Interactive Chart & AI Summary
The chart is interactive - clicking zoom, and then planets or signs provides additional information on the placements, as well as an opportunity to get an AI-generated interpretation of the selected position.

![Interactive chart and AI summary demo](https://i.imgur.com/Mv1mKCv.gif)

## 3. SVG Chart Generation & Download
Generate a high-quality SVG version of the natal chart and download it for use outside the application. This is generated via [Kerykeion](https://kerykeion.net/python-library/docs/v5).

![SVG chart generation example](https://i.imgur.com/qrcAjjI.png)

## 4. Aspect Table
View the calculated planetary aspects in a dedicated table for easier inspection of the relationships between chart elements. Hover over relevant aspect to show more detailed data.

![Aspect table example](https://i.imgur.com/kgszkIQ.png)

## 5. Additional Tables
The application provides additional tabular views of the calculated chart data, making it easier to inspect planetary positions, houses, aspects etc.

![Additional chart tables demo](https://i.imgur.com/PkyOCrU.png)

## 6. AI Chat
Interact with the chart through an AI chat interface. Ask questions about specific placements, aspects, houses, or broader patterns in the chart and receive contextual responses based on the calculated chart.

![AI chat demo](https://i.imgur.com/ZOmzsoX.gif)

# Using the repository
If you want to use, edit or build the repository on your own machine, you can do the following steps to recreate the development enviroment.

1. Clone the repository and install the required dependencies:
```
git clone https://github.com/pipstur/natal-chart-visualizer.git
cd natal-chart-visualizer
uv venv
source venv/bin/activate # or on Windows, source venv/Scripts/activate
uv pip install -r requirements.txt
```
2. Configure `.streamlit/secrets.toml.example` with your credentials (GROQ_API_KEY, get it from [here](https://console.groq.com/keys), GEOAPIFY_API_KEY, get it from [here](https://myprojects.geoapify.com/api)) and rename it to `secrets.toml`. This is how Streamlit knows which environment variables to load.

3. Then start the Streamlit application:
```
streamlit run app.py
```
The application should open in your browser!
