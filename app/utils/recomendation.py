def get_calorie_burn_recommendation(calories_burned, calories_consumed):
    recommendation = []

    # Net calories = consumed - burned
    net_calories = calories_consumed - calories_burned

    if net_calories > 300:
        recommendation.append("⚠️ You’re in a calorie surplus. This may lead to weight gain. Consider reducing intake or increasing activity.")
    elif net_calories < -300:
        recommendation.append("⚠️ You’re in a calorie deficit. Good for weight loss, but make sure you’re not under-eating.")
    else:
        recommendation.append("✅ Your energy balance is healthy. Great job maintaining it!")

    recommendation.append(f"Calories Burned (Predicted): {int(calories_burned)} kcal")
    recommendation.append(f"Calories Consumed: {int(calories_consumed)} kcal")
    recommendation.append(f"Net Calories: {int(net_calories)} kcal")

    return recommendation
