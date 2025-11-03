from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, DictProperty, ListProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView

class GradientBackground(Widget):
    gradient_texture = ObjectProperty(None)
    
    def create_gradient_texture(self):
        texture = Texture.create(size=(1, 64), colorfmt='rgba')
        buf = bytes()
        for i in range(64):
            r = int(10 + i * 0.5)
            g = int(60 + i * 2)
            b = int(30 + i * 1)
            buf += bytes([r, g, b, 255])
        texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        texture.wrap = 'repeat'
        texture.uvsize = (1, -1)
        return texture

# Nastavení velikosti a základní barvy okna
Window.size = (1200, 700)
Window.clearcolor = (0.07, 0.07, 0.07, 1)
Window.minimum_width = 800
Window.minimum_height = 600


# ======== OBRAZOVKY ========

class MainScreen(Screen):
    username = StringProperty("")
    current_view = StringProperty("workouts")
    workouts_screen = ObjectProperty(None)
    stats_screen = ObjectProperty(None)
    
    def on_kv_post(self, *args):
        """Called after kv file is loaded"""
        # Store references to our child screens
        for widget in self.walk():
            if isinstance(widget, WorkoutsScreen):
                self.workouts_screen = widget
            elif isinstance(widget, StatsScreen):
                self.stats_screen = widget
    
    def switch_view(self, view):
        self.current_view = view
        
        if view == "stats" and self.stats_screen:
            self.stats_screen.on_enter()
    
    def logout(self):
        if self.workouts_screen:
            # Save any remaining data before logout
            self.workouts_screen.save_to_file(
                "\n".join([f"{ex} - {s}x{r}, {w}kg" for ex, s, r, w in self.workouts_screen.workout_data]),
                self.workouts_screen.ids.note.text
            )
            # Reset workout data
            self.workouts_screen.workout_data = []
            self.workouts_screen.ids.workout_list.text = ""
            self.workouts_screen.ids.note.text = ""
            
        self.manager.current = "login"

class LoginScreen(Screen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        if username == "admin" and password == "1234":
            self.manager.current = "main"
            main_screen = self.manager.get_screen("main")
            main_screen.username = username
            
            # Load saved data for the user
            workouts_screen = None
            for widget in main_screen.walk():
                if isinstance(widget, WorkoutsScreen):
                    workouts_screen = widget
                    break
            
            if workouts_screen:
                workouts_screen.load_user_data(username)
        else:
            popup = Popup(title="Chyba",
                          content=Label(text="Špatné jméno nebo heslo!"),
                          size_hint=(0.5, 0.3))
            popup.open()





class WorkoutsScreen(Screen):
    exercises = ListProperty(["Bench press", "Dřepy", "Mrtvý tah", "Biceps curl", "Kliky"])
    workout_data = ListProperty()
    personal_records = DictProperty()
    progress_data = DictProperty()  # New: Track progress over time
    selected_exercise = StringProperty("")
    show_exercises = BooleanProperty(False)

    def load_user_data(self, username):
        """Load saved data for the user from JSON file."""
        import json
        import os
        
        if os.path.exists("data/users.json"):
            try:
                with open("data/users.json", "r") as f:
                    data = json.load(f)
                    if username in data:
                        user_data = data[username]
                        self.personal_records.update(user_data.get("personal_records", {}))
                        self.progress_data.update(user_data.get("progress_data", {}))
                        
                        # Update exercises list with any custom exercises
                        custom_exercises = set()
                        for workout in user_data.get("workouts", []):
                            for ex, _, _, _ in workout["exercises"]:
                                custom_exercises.add(ex)
                        
                        # Add any new exercises to the list
                        for exercise in custom_exercises:
                            if exercise not in self.exercises:
                                self.exercises.append(exercise)
            except (json.JSONDecodeError, KeyError):
                pass  # Use default data if file is corrupted or empty

    def on_exercises(self, instance, value):
        self.update_exercise_list()

    def update_exercise_list(self):
        exercise_list = self.ids.get('exercise_list', None)
        if exercise_list:
            exercise_list.clear_widgets()
            for exercise in self.exercises:
                btn = Button(
                    text=exercise,
                    size_hint_y=None,
                    height=48,
                    background_color=(0.2, 0.2, 0.2, 1)
                )
                btn.bind(on_release=lambda b: self.select_exercise(b.text))
                exercise_list.add_widget(btn)

    def toggle_exercise_list(self):
        """Show or hide the right-side exercise panel."""
        # Toggle flag; kv bindings handle visibility/disabled state
        self.show_exercises = not self.show_exercises
        if self.show_exercises:
            # populate list when opening
            self.update_exercise_list()

    def select_exercise(self, exercise_name):
        self.selected_exercise = exercise_name
        self.show_exercises = False

    def add_custom_exercise(self):
        name = self.ids.new_exercise.text.strip()
        if name and name not in self.exercises:
            self.exercises.append(name)
            self.ids.new_exercise.text = ""
        else:
            popup = Popup(title="Chyba",
                          content=Label(text="Cvik už existuje nebo je prázdný."),
                          size_hint=(0.5, 0.3))
            popup.open()

    def add_exercise(self):
        sets = self.ids.sets.text
        reps = self.ids.reps.text
        weight = self.ids.weight.text

        if not (self.selected_exercise and sets and reps and weight):
            popup = Popup(title="Chyba",
                          content=Label(text="Vyplň všechny údaje!"),
                          size_hint=(0.5, 0.3))
            popup.open()
            return

        entry = f"{self.selected_exercise} - {sets}x{reps}, {weight}kg"
        self.workout_data.append((self.selected_exercise, int(sets), int(reps), int(weight)))
        self.ids.workout_list.text += f"{entry}\n"

        # aktualizace osobních rekordů
        if self.selected_exercise not in self.personal_records or int(weight) > self.personal_records[self.selected_exercise]:
            self.personal_records[self.selected_exercise] = int(weight)

        # vyčištění polí
        self.ids.sets.text = ""
        self.ids.reps.text = ""
        self.ids.weight.text = ""



    def remove_last(self):
        if self.workout_data:
            self.workout_data.pop()
            lines = self.ids.workout_list.text.strip().split("\n")
            self.ids.workout_list.text = "\n".join(lines[:-1])
        else:
            popup = Popup(title="Chyba",
                          content=Label(text="Žádné cviky k odstranění."),
                          size_hint=(0.5, 0.3))
            popup.open()

    def save_workout(self):
        if not self.workout_data:
            popup = Popup(title="Chyba",
                          content=Label(text="Nejdřív přidej alespoň jeden cvik!"),
                          size_hint=(0.5, 0.3))
            popup.open()
            return

        note = self.ids.note.text
        summary = "\n".join([f"{ex} - {s}x{r}, {w}kg" for ex, s, r, w in self.workout_data])

        # Update progress data
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
        for exercise, sets, reps, weight in self.workout_data:
            if exercise not in self.progress_data:
                self.progress_data[exercise] = []
            self.progress_data[exercise].append({
                'date': date,
                'sets': sets,
                'reps': reps,
                'weight': weight,
                'volume': sets * reps * weight
            })

        # tady později přidáme ukládání do databáze
        self.save_to_file(summary, note)

        popup = Popup(
            title="Uloženo",
            content=Label(text=f"Trénink byl úspěšně uložen!\n\n{summary}\n\nPoznámka:\n{note if note else '(žádná)'}"),
            size_hint=(0.7, 0.7),
        )
        popup.bind(on_dismiss=self.back_to_dashboard)
        popup.open()

        # reset polí
        self.workout_data = []
        self.ids.workout_list.text = ""
        self.ids.note.text = ""

    def save_to_file(self, summary, note):
        """Saves workout data, personal records and progress to JSON file."""
        import json
        import os
        from datetime import datetime

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Load existing data
        data = {}
        if os.path.exists("data/users.json"):
            try:
                with open("data/users.json", "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        
        # Get current user
        username = App.get_running_app().root.get_screen("main").username
        if username not in data:
            data[username] = {
                "workouts": [],
                "personal_records": {},
                "progress_data": {}
            }
        
        # Update user data
        workout_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exercises": self.workout_data,
            "note": note,
            "summary": summary
        }
        
        data[username]["workouts"].append(workout_entry)
        data[username]["personal_records"] = dict(self.personal_records)
        data[username]["progress_data"] = dict(self.progress_data)
        
        # Save updated data
        with open("data/users.json", "w") as f:
            json.dump(data, f, indent=4)

    def back_to_dashboard(self, *_):
        """Vrátí uživatele zpět na hlavní obrazovku."""
        # Find the MainScreen instance and switch to workouts view
        main_screen = App.get_running_app().root.get_screen('main')
        main_screen.switch_view('workouts')



class StatsScreen(Screen):
    user_weight = NumericProperty(0)
    personal_records = DictProperty()
    progress_data = DictProperty()

    def update_weight(self):
        try:
            new_weight = int(self.ids.weight_input.text)
            self.user_weight = new_weight
            self.ids.weight_label.text = f"Aktuální váha: {self.user_weight} kg"
            self.ids.weight_input.text = ""
        except ValueError:
            popup = Popup(title="Chyba", content=Label(text="Zadej číslo!"), size_hint=(0.5, 0.3))
            popup.open()

    def on_enter(self):
        # Find the WorkoutsScreen instance inside the MainScreen
        main_screen = App.get_running_app().root.get_screen('main')
        for widget in main_screen.walk():
            if isinstance(widget, WorkoutsScreen):
                self.personal_records = widget.personal_records
                self.progress_data = widget.progress_data
                break
        
        # Update PR display
        self.ids.pr_label.text = ""
        if self.personal_records:
            for ex, w in self.personal_records.items():
                self.ids.pr_label.text += f"{ex}: {w} kg\n"
        else:
            self.ids.pr_label.text = "(zatím žádné PR)"

        # Update progress display
        self.ids.progress_label.text = ""
        if self.progress_data:
            for exercise, data in self.progress_data.items():
                latest = data[-1]
                first = data[0]
                progress = latest['weight'] - first['weight']
                progress_text = "🔺" if progress > 0 else "🔻" if progress < 0 else "="
                
                self.ids.progress_label.text += f"\n{exercise}:\n"
                self.ids.progress_label.text += f"  Poslední trénink: {latest['sets']}x{latest['reps']} @ {latest['weight']}kg\n"
                self.ids.progress_label.text += f"  Progress: {abs(progress)}kg {progress_text}\n"
                self.ids.progress_label.text += f"  Celkový objem: {latest['volume']}kg\n"
        else:
            self.ids.progress_label.text = "(zatím žádný progress)"


# ======== APLIKACE ========

class FitnessApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))
        return sm


if __name__ == "__main__":
    FitnessApp().run()
