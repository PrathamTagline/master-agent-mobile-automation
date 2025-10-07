import random
from birthday_app import run_birthday_app
from nail_app import run_nail_app
from fitness_app import run_fitness_app
from session_tracker import update_session

GAMES = {
    "nail_app": {"name": "Nail App", "function": run_nail_app, "needs_chrome": False},
    "birthday_app": {"name": "Birthday App", "function": run_birthday_app, "needs_chrome": True},
    "fitness_app": {"name": "Fitness App", "function": run_fitness_app, "needs_chrome": False}
}

def run_specific_game(device, appium_port, system_port, chrome_port, app_name="random"):
    """Run specific game or random game"""
    
    if app_name == "random":
        selected_game = random.choice(list(GAMES.values()))
    elif app_name in GAMES:
        selected_game = GAMES[app_name]
    else:
        print(f"[{device}] Unknown app: {app_name}, using random")
        selected_game = random.choice(list(GAMES.values()))
    
    print(f"[{device}] 🎲 Selected: {selected_game['name']}")

    try:
        if selected_game["needs_chrome"]:
            selected_game["function"](device, appium_port, system_port, chrome_port)
        else:
            selected_game["function"](device, appium_port, system_port)
        
        print(f"[{device}] ✅ {selected_game['name']} completed")
        update_session(device, selected_game["name"], success=True)

    except Exception as e:
        print(f"[{device}] ❌ Error in {selected_game['name']}: {e}")
        update_session(device, selected_game["name"], success=False)
        raise

# Legacy function for backward compatibility
def run_random_game(device, appium_port, system_port, chrome_port):
    return run_specific_game(device, appium_port, system_port, chrome_port, "random")