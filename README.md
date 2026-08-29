# Natal Chart Explorer
A Streamlit-based interactive natal chart application built with Python and Kerykeion.
Hosted on https://natal-chart.streamlit.app/.

# Overview
Natal Chart Explorer lets you enter birth data, generate a natal chart, explore planetary positions and aspects interactively, and use AI-powered tools to interpret the chart.

# Features
## 1. Enter Birth Data & Generate Chart
Enter the birth date, time, and location to generate the natal chart. The application then displays the calculated chart along with the relevant planetary and house information.

![Natal chart generation demo](https://i.imgur.com/imSpbpM.gif)

## 2. Interactive Chart & AI Summary
The chart is interactive - clicking planets and signs, the relevant elements and provides additional information.
An AI-generated summary is also available to provide a high-level interpretation of the selected.

![Interactive chart and AI summary demo](https://i.imgur.com/Ptw5eZW.gif)

## 3. SVG Chart Generation & Download
Generate a high-quality SVG version of the natal chart and download it for use outside the application.

![SVG chart generation example](https://i.imgur.com/qrcAjjI.png)

## 4. Aspect Table
View the calculated planetary aspects in a dedicated table for easier inspection of the relationships between chart elements. Hover over relevant aspect to show more detailed data.

![Aspect table example](https://i.imgur.com/KJtJmv9.png)

## 5. Additional Tables
The application provides additional tabular views of the calculated chart data, making it easier to inspect planetary positions, houses, aspects etc.

![Additional chart tables demo](https://i.imgur.com/x7SsVy4.gif)

## 6. AI Chat
Interact with the chart through an AI chat interface. Ask questions about specific placements, aspects, houses, or broader patterns in the chart and receive contextual responses based on the calculated chart.

![AI chat demo](https://i.imgur.com/MA94rdf.gif)

# Using the repository
Clone the repository and install the required dependencies:
```
git clone <repository-url>
cd <repository-folder>
pip install -r requirements.txt
```
Then start the Streamlit application:
```
streamlit run app.py
```
The application will open in your browser.
