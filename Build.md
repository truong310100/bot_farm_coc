pip install pyinstaller

pyinstaller --onefile --noconsole --add-data "config.json;." --add-data "models.py;." --add-data "scenario_manager.py;." main.py
