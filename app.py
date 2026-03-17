import streamlit as st
import pandas as pd

st.set_page_config(page_title="Macro Restaurant Finder", layout="centered")

st.title("🍔 Macro-Based Restaurant Finder")

# -------------------------
# LOAD DATA FROM CSV
# -------------------------
df = pd.read_csv("menu_data.csv")
menu_items = df.to_dict("records")

# -------------------------
# USER GOALS (hardcoded)
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
# SEARCH FEATURE
# -------------------------
search = st.text_input("Search for a food (optional)")

if search:
    menu_items = [
        m for m in menu_items
        if search.lower() in m["name"].lower()
    ]

# -------------------------
# SCORING FUNCTION
# PRIORITY:
# 1. Do NOT exceed calories
# 2. Protein
# 3. Carbs
# 4. Fat
# -------------------------
def meal_score(meal):

    # HARD FILTER: cannot exceed calories
    if meal["calories"] > remaining_calories:
        return float("inf")

    protein_diff = abs(remaining_protein - meal["protein"])
    carb_diff = abs(remaining_carbs - meal["carbs"])
    fat_diff = abs(remaining_fat - meal["fat"])

    score = (protein_diff * 3) + carb_diff + fat_diff
    return score

# -------------------------
# GLOBAL RECOMMENDATIONS
# -------------------------
st.subheader("🔥 Best Meals Across All Restaurants")

global_ranked = sorted(menu_items, key=meal_score)

count = 0
for meal in global_ranked:
    if meal["calories"] <= remaining_calories and count < 10:
        st.write(
            f"{meal['restaurant']} — {meal['name']} | "
            f"{meal['calories']} cal | "
            f"P:{meal['protein']} C:{meal['carbs']} F:{meal['fat']}"
        )
        count += 1

# -------------------------
# RESTAURANT FILTER
# -------------------------
restaurants = sorted(list(set(item["restaurant"] for item in menu_items)))

selected_restaurant = st.selectbox("Choose a Restaurant", restaurants)

restaurant_items = [
    i for i in menu_items
    if i["restaurant"] == selected_restaurant
]

st.subheader(f"📍 Best Options at {selected_restaurant}")

ranked = sorted(restaurant_items, key=meal_score)

for meal in ranked:
    if meal["calories"] <= remaining_calories:
        st.write(
            f"{meal['name']} | "
            f"{meal['calories']} cal | "
            f"P:{meal['protein']} C:{meal['carbs']} F:{meal['fat']}"
        )