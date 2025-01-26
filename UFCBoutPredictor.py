import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import base64
import plotly.graph_objects as go


#configures page settings and sets background
st.set_page_config(page_title="UFC Bout Predictor", layout="wide", page_icon="UFC-LOGO.png")
def set_bg_image(image_file):
    with open(image_file, "rb") as img_file:
        base64_img = base64.b64encode(img_file.read()).decode()

    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{base64_img}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
set_bg_image("IMG_20250125_133948.png")

#creates dataframe
df = pd.read_csv("UFC Fighters' Statistics Dataset.csv", index_col=0)
# df.columns=['Name', 'Nickname', "wins", "losses", "draws", ] WORk ON THIS LATER
numeric_cols_for_weighted = [
    'wins', 'losses', 'draws', 'significant_strike_defence',
    'takedown_defense', 'significant_striking_accuracy',
    'takedown_accuracy', 'significant_strikes_landed_per_minute',
    'average_submissions_attempted_per_15_minutes', 'reach_in_cm'
]
df[numeric_cols_for_weighted] = df[numeric_cols_for_weighted].apply(pd.to_numeric, errors='coerce')
df[numeric_cols_for_weighted] = df[numeric_cols_for_weighted].fillna(0)
correlations = df[numeric_cols_for_weighted].corr()['wins']
df['weighted_sum'] = df[numeric_cols_for_weighted].apply(lambda x: (x * correlations).sum(), axis=1)

prettyindexes = {
    'nickname': 'Nickname', 'wins': 'Wins', 'losses': 'Losses',
    'draws': 'Draws', 'height': 'Height (cm)', 'weight_in_kg': 'Weight (kg)',
    'reach_in_cm': 'Reach (cm)', 'stance': 'Stance', 'date_of_birth': 'Date of Birth',
    'significant_strikes_landed_per_minute': 'Strikes per Minute',
    'significant_striking_accuracy': 'Striking Accuracy (%)',
    'significant_strikes_absorbed_per_minute': 'Strikes Absorbed/Min',
    'significant_strike_defence': 'Strike Defense (%)',
    'average_takedowns_landed_per_15_minutes': 'Takedowns per 15 Min',
    'takedown_accuracy': 'Takedown Accuracy (%)',
    'average_submissions_attempted_per_15_minutes': 'Submissions per 15 Min',
    'significant_strikes_absorbed_per_minute': 'Strikes Absorbed/Min',
    'significant_strike_defense': 'Striking Defense (%)',
    'takedown_average_per_15_minutes': 'Takedowns per 15 Min',
    'takedown_defense': 'Takedown Defense (%)', 'weighted_sum': 'Score'
    }
#creates column sections
st.title('_:red[UFC]_ Bout Predictor')
cfighter1, space, cfighter2 = st.columns([1,2.5,1], gap = 'small', vertical_alignment='center')
with cfighter1:
    fighter1 = st.text_input('Enter the name of the first fighter: ') #creates user input box
    if fighter1 in df.index:
        fighter_1= fighter1.replace(" ", "-")
        fighter1url = (f'https://www.ufc.com/athlete/{fighter_1}') #gets specific fighter url
        source = requests.get(fighter1url)
        soup = BeautifulSoup(source.text, 'lxml') #parses page html
        image1 = soup.find("img", class_="hero-profile__image") 
        image1_url = image1["src"]
        row_data = df.loc[fighter1].rename(index=prettyindexes)
        st.image(image1_url) #displays image
        st.dataframe(row_data, use_container_width=True, height=668)
    else:
        print("Row not found in the dataset.")
    
with cfighter2:
    fighter2 = st.text_input('Enter the name of the second fighter: ')
    if fighter2 in df.index:
        fighter_2= fighter2.replace(" ", "-")
        fighter2url = (f'https://www.ufc.com/athlete/{fighter_2}')
        source = requests.get(fighter2url)
        soup = BeautifulSoup(source.text, 'lxml')
        image2 = soup.find("img", class_="hero-profile__image")
        image2_url = image2["src"]
        row_data = df.loc[fighter2].rename(index=prettyindexes)
        st.image(image2_url)
        st.dataframe(row_data, use_container_width=True, height=668)
    else:
        print("Row not found in the dataset.")

#everything to do with the middle section
with space:
    if fighter1 in df.index and fighter2 in df.index:
        columnsneednormal = ["wins", "significant_strikes_landed_per_minute", "significant_striking_accuracy", 
                             "takedown_accuracy", "average_submissions_attempted_per_15_minutes"] #creates radar categories
        nicercategories = {"wins": "Total Wins",
            "significant_strikes_landed_per_minute": "Strikes/Min",
            "significant_striking_accuracy": "Striking Accuracy (%)",
            "takedown_accuracy": "Takedown Accuracy (%)",
            "average_submissions_attempted_per_15_minutes": "Submission Attempts"
        }
        fighter1_score = df.loc[fighter1, 'weighted_sum']
        fighter2_score = df.loc[fighter2, 'weighted_sum']
        if fighter1_score > fighter2_score:
            st.markdown(
                f"<h1 style='text-align: center; color: white; text-decoration: underline;'>"
                f"We predict that <em>{fighter1}</em> Will Win</h1>", 
                unsafe_allow_html=True
            )
        elif fighter2_score > fighter1_score:
            st.markdown(
                f"<h1 style='text-align: center; color: white; text-decoration: underline;'>"
                f"We predict that <em>{fighter2}</em> Will Win</h1>", 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<h1 style='text-align: center; color: white; text-decoration: underline;'>Draw!</h1>", 
                unsafe_allow_html=True
            )


        chartlabels = [nicercategories[col] for col in columnsneednormal]
        max_values = df[columnsneednormal].max()
        fighter1_stats = (df.loc[fighter1][columnsneednormal] / max_values).tolist() #retrieve and normalize fighter stats
        fighter2_stats = (df.loc[fighter2][columnsneednormal] / max_values).tolist()
        fig = go.Figure() #creates the figure
        fig.add_trace(go.Scatterpolar(
            r=fighter1_stats,
            theta=chartlabels,
            fill='toself',
            name=fighter1,
            line=dict(color='#FF0000'),
            fillcolor='rgba(255, 0, 0, 0.32)'
        ))
        fig.add_trace(go.Scatterpolar(
            r=fighter2_stats,
            theta=chartlabels,
            fill='toself',
            name=fighter2,
            line=dict(color='#0000FF'),  
            fillcolor='rgba(0,0,255,0.2)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]  
                )
            ),
            title=f'{fighter1} vs. {fighter2}',
            title_x=0.29,
            showlegend=True,
            title_font=dict(size=18, family='Arial', color='white'),
            height=700, width=975
        )
        st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False}) #displays figure
        st.container(height=500, border=False)

        