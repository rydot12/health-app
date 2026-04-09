import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Macro Meal Builder", layout="centered")
st.title("🍽 Macro Meal Builder (API Driven)")

# -------------------------
# API SETTINGS
# -------------------------
API_KEY = "ef30787de3ea4fcc8e455dad1ecfaa0d"  # Free tier
DEFAULT_CHAINS = [
    "McDonald's", "Burger King", "Wendy's", "Chick-fil-A", "Taco Bell",
    "Subway", "KFC", "Panda Express", "Pizza Hut", "Domino's"
]

@st.cache_data
def get_chain_menu(chain_name):
    """Fetch menu items for a restaurant using Spoonacular API"""
    url = "https://api.spoonacular.com/food/menuItems/search"
    params = {"query": chain_name, "number": 500, "apiKey": API_KEY}
    r = requests.get(url, params=params)
    data = r.json()
    
    items = []
    for item in data.get("menuItems", []):
        nutrition = item.get("nutrition", {})
        items.append({
            "restaurant": chain_name,
            "name": item.get("title"),
            "calories": nutrition.get("calories", 0),
            "protein": nutrition.get("protein", 0),
            "carbs": nutrition.get("carbs", 0),
            "fat": nutrition.get("fat", 0),
            "category": "entree"  # Default; can refine later
        })
    return items

# -------------------------
# SELECT RESTAURANT
# -------------------------
st.subheader("Select or Add Restaurant")
new_restaurant = st.text_input("Type a restaurant name to add (or leave blank for default list):")

if new_restaurant:
    restaurant_list = [new_restaurant]
else:
    restaurant_list = DEFAULT_CHAINS

# -------------------------
# LOAD MENUS
# -------------------------
st.subheader("Loading Menus...")
all_menus = []
for chain in restaurant_list:
    menu = get_chain_menu(chain)
    all_menus.extend(menu)

df = pd.DataFrame(all_menus)
if df.empty:
    st.error("No menu data loaded. Check API key or network.")
    st.stop()

# -------------------------
# USER GOALS
# -------------------------
calorie_goal = 1700
protein_goal = 150
carb_goal = 170
fat_goal = 60

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
view_option = st.radio("View Entrees & Sides", ["Top 5", "Show All"])
main_items = restaurant_df[restaurant_df["category"].isin(["entree", "side"])].to_dict("records")
ranked = sorted(main_items, key=meal_score)
display_items = ranked[:5] if view_option == "Top 5" else ranked
st.subheader("🍔 Entrees & Sides")
for i, meal in enumerate(display_items, 1):
    st.write(f"#{i} {meal['name']} | {int(meal['calories'])} cal")

# -------------------------
# DRINKS + SAUCES
# -------------------------
st.subheader("🥤 Drinks & Sauces")
extras = restaurant_df[restaurant_df["category"].isin(["drink", "sauce"])]
selected_extras = st.multiselect("Select Drinks/Sauces", extras["name"].tolist())

# -------------------------
# MEAL BUILDER
# -------------------------
st.subheader("🍽 Build Your Meal")
entree_choices = restaurant_df[restaurant_df["category"] == "entree"]["name"].tolist()
side_choices = restaurant_df[restaurant_df["category"] == "side"]["name"].tolist()
entree_choice = st.selectbox("Select Entree", entree_choices)
selected_sides = st.multiselect("Select Sides", side_choices)

# -------------------------
# CALCULATE TOTAL
# -------------------------
selected_items = restaurant_df[restaurant_df["name"].isin([entree_choice] + selected_sides + selected_extras)]
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
st.write(f"Carbs Left: {int(remaining_carbs - total_carbs)}")
st.write(f"Fat Left: {int(remaining_fat - total_fat)}")
