import streamlit as st
import pandas as pd

st.set_page_config(page_title="Macro Restaurant Finder", layout="centered")

st.title("🍔 Macro-Based Restaurant Finder")

# -------------------------
# LOAD & CLEAN CSV DATA (SAFE VERSION)
# -------------------------
try:
    df = pd.read_csv("menu_data.csv")

    # Clean column names (fixes spaces/capitalization issues)
    df.columns = df.columns.str.strip().str.lower()

    # Ensure required columns exist
    required_cols = ["restaurant", "name", "calories", "protein", "carbs", "fat"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing column in CSV: {col}")
            st.stop()

    # Convert numeric columns safely
    for col in ["calories", "protein", "carbs", "fat"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with bad/missing data
    df = df.dropna(subset=required_cols)

    menu_items = df.to_dict("records")

except Exception as e:
    st.error("Error loading menu_data.csv")
    st.write(e)
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
st.subheader("Enter What You've Eaten Today")

calories_eaten = st.number_input("Calories eaten", min_value=0)
protein_eaten = st.number_input("Protein eaten (g)", min_value=0)
carbs_eaten = st.number_input("Carbs eaten (g)", min_value=0)
fat_eaten = st.number_input("Fat eaten (g)", min_value=0)

# -------------------------
# REMAINING MACROS
# -------------------------
remaining_calories = calorie_goal - calories_eaten
remaining_protein = protein_goal - protein_eaten
remaining_carbs = carb_goal - carbs_eaten
remaining_fat = fat_goal - fat_eaten

st.subheader("Remaining Macros")
st.write(f"Calories: {remaining_calories}")
st.write(f"Protein: {remaining_protein}")
st.write(f"Carbs: {remaining_carbs}")
st.write(f"Fat: {remaining_fat}")

# -------------------------
# SCORING FUNCTION
# -------------------------
def meal_score(meal):

    # Hard rule: do not exceed calories
    if meal["calories"] > remaining_calories:
        return float("inf")

    protein_diff = abs(remaining_protein - meal["protein"])
    carb_diff = abs(remaining_carbs - meal["carbs"])
    fat_diff = abs(remaining_fat - meal["fat"])

    return (protein_diff * 3) + carb_diff + fat_diff

# -------------------------
# GLOBAL TOP 5
# -------------------------
st.subheader("🔥 Best Overall Options (Top 5)")

global_ranked = sorted(menu_items, key=meal_score)

top_5_global = [
    m for m in global_ranked
    if m["calories"] <= remaining_calories
][:5]

if len(top_5_global) == 0:
    st.write("No meals fit within your remaining calories.")
else:
    for i, meal in enumerate(top_5_global, start=1):
        st.write(
            f"#{i} {meal['restaurant']} — {meal['name']} | "
            f"{int(meal['calories'])} cal | "
            f"P:{int(meal['protein'])} C:{int(meal['carbs'])} F:{int(meal['fat'])}"
        )

# -------------------------
# RESTAURANT VIEW
# -------------------------
restaurants = sorted(df["restaurant"].unique())

selected_restaurant = st.selectbox("Choose a Restaurant", restaurants)

restaurant_items = df[df["restaurant"] == selected_restaurant].to_dict("records")

ranked = sorted(restaurant_items, key=meal_score)

# Toggle view
view_option = st.radio(
    "View Options",
    ["Top 5 Best Options", "Show Full Ranked Menu"]
)

st.subheader(f"📍 {selected_restaurant} Options")

# -------------------------
# TOP 5 RESTAURANT
# -------------------------
if view_option == "Top 5 Best Options":

    top_5_restaurant = [
        m for m in ranked
        if m["calories"] <= remaining_calories
    ][:5]

    if len(top_5_restaurant) == 0:
        st.write("No meals fit within your remaining calories.")
    else:
        for i, meal in enumerate(top_5_restaurant, start=1):
            st.write(
                f"#{i} {meal['name']} | "
                f"{int(meal['calories'])} cal | "
                f"P:{int(meal['protein'])} C:{int(meal['carbs'])} F:{int(meal['fat'])}"
            )

# -------------------------
# FULL RANKED MENU
# -------------------------
else:

    for i, meal in enumerate(ranked, start=1):

        over_calories = meal["calories"] > remaining_calories
        label = "❌ OVER CALORIES" if over_calories else ""

        st.write(
            f"#{i} {meal['name']} | "
            f"{int(meal['calories'])} cal | "
            f"P:{int(meal['protein'])} C:{int(meal['carbs'])} F:{int(meal['fat'])} {label}"
        )