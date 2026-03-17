import streamlit as st
import pandas as pd

st.set_page_config(page_title="Macro Meal Builder", layout="centered")

st.title("🍽 Macro Meal Builder")

# -------------------------
# LOAD DATA
# -------------------------
try:
    df = pd.read_csv("menu_data.csv")
    df.columns = df.columns.str.strip().str.lower()

    required_cols = ["restaurant", "name", "calories", "protein", "carbs", "fat", "category"]

    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing column: {col}")
            st.stop()

    for col in ["calories", "protein", "carbs", "fat"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

except Exception as e:
    st.error("Error loading CSV")
    st.exception(e)
    st.stop()

# -------------------------
# USER GOALS
# -------------------------
calorie_goal = 1700
protein_goal = 150
carb_goal = 170
fat_goal = 60

# -------------------------
# USER INPUT
# -------------------------
st.subheader("What Have You Eaten Today?")

calories_eaten = st.number_input("Calories eaten", min_value=0)
protein_eaten = st.number_input("Protein eaten", min_value=0)
carbs_eaten = st.number_input("Carbs eaten", min_value=0)
fat_eaten = st.number_input("Fat eaten", min_value=0)

remaining_calories = calorie_goal - calories_eaten
remaining_protein = protein_goal - protein_eaten
remaining_carbs = carb_goal - carbs_eaten
remaining_fat = fat_goal - fat_eaten

# -------------------------
# SCORING FUNCTION
# -------------------------
def meal_score(meal):
    if meal["calories"] > remaining_calories:
        return float("inf")

    return (
        abs(remaining_protein - meal["protein"]) * 3
        + abs(remaining_carbs - meal["carbs"])
        + abs(remaining_fat - meal["fat"])
    )

# -------------------------
# GLOBAL TOP 5 (ENTREES + SIDES ONLY)
# -------------------------
st.subheader("🔥 Top 5 Entrees & Sides (All Restaurants)")

global_filtered = df[df["category"].isin(["entree", "side"])]
global_ranked = sorted(global_filtered.to_dict("records"), key=meal_score)

top_5 = [m for m in global_ranked if m["calories"] <= remaining_calories][:5]

for i, meal in enumerate(top_5, 1):
    st.write(f"#{i} {meal['restaurant']} - {meal['name']} | {int(meal['calories'])} cal")

# -------------------------
# RESTAURANT SELECT
# -------------------------
restaurants = sorted(df["restaurant"].unique())
selected_restaurant = st.selectbox("Choose Restaurant", restaurants)

restaurant_df = df[df["restaurant"] == selected_restaurant]

# -------------------------
# TOGGLE: TOP 5 OR ALL
# -------------------------
view_option = st.radio(
    "View Entrees & Sides",
    ["Top 5", "Show All"]
)

# -------------------------
# SHOW ENTREE + SIDES
# -------------------------
st.subheader("🍔 Entrees & Sides")

main_items = restaurant_df[
    restaurant_df["category"].isin(["entree", "side"])
].to_dict("records")

ranked = sorted(main_items, key=meal_score)

if view_option == "Top 5":
    display_items = ranked[:5]
else:
    display_items = ranked

for i, meal in enumerate(display_items, 1):
    st.write(f"#{i} {meal['name']} | {int(meal['calories'])} cal")

# -------------------------
# DRINKS + SAUCES
# -------------------------
st.subheader("🥤 Drinks & Sauces")

extras = restaurant_df[
    restaurant_df["category"].isin(["drink", "sauce"])
]

selected_extras = st.multiselect(
    "Select Drinks/Sauces",
    extras["name"].tolist()
)

# -------------------------
# MEAL BUILDER
# -------------------------
st.subheader("🍽 Build Your Meal")

entree_choices = restaurant_df[
    restaurant_df["category"] == "entree"
]["name"].tolist()

side_choices = restaurant_df[
    restaurant_df["category"] == "side"
]["name"].tolist()

entree_choice = st.selectbox("Select Entree", entree_choices)
selected_sides = st.multiselect("Select Sides", side_choices)

# -------------------------
# CALCULATE TOTAL
# -------------------------
selected_items = restaurant_df[
    restaurant_df["name"].isin(
        [entree_choice] + selected_sides + selected_extras
    )
]

total_calories = selected_items["calories"].sum()
total_protein = selected_items["protein"].sum()
total_carbs = selected_items["carbs"].sum()
total_fat = selected_items["fat"].sum()

st.subheader("📊 Total Meal Macros")

st.write(f"Calories: {int(total_calories)}")
st.write(f"Protein: {int(total_protein)}")
st.write(f"Carbs: {int(total_carbs)}")
st.write(f"Fat: {int(total_fat)}")

# -------------------------
# REMAINING AFTER MEAL
# -------------------------
st.subheader("Remaining After This Meal")

st.write(f"Calories Left: {int(remaining_calories - total_calories)}")
st.write(f"Protein Left: {int(remaining_protein - total_protein)}")
