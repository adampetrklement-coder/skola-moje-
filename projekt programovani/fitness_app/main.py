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
            # Reset workout data (už neukládáme do users.json)
            self.workouts_screen.workout_data = []
            self.workouts_screen.ids.workout_list.text = ""
            self.workouts_screen.ids.note.text = ""
            
        self.manager.current = "login"

from api import ApiClient

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = ApiClient()

    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text

        print(f"[DEBUG] Pokus o přihlášení: {username}")
        error = self.api.login(username, password)
        print(f"[DEBUG] Výsledek login: error={error}, token={self.api.token}")
        
        if error is None:  # přihlášení úspěšné
            print(f"[DEBUG] Přihlášení úspěšné, přepínám na main screen")
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
                workouts_screen.api = self.api  # Sdílej token
                workouts_screen.load_user_data(username)
                # Načtení dat z API
                workouts, api_error = self.api.get_workouts()
                if workouts and not api_error:
                    # TODO: Implementovat zobrazení workoutů z API
                    pass
        else:
            print(f"[DEBUG] Přihlášení selhalo: {error}")
            popup = Popup(title="Chyba",
                          content=Label(text=str(error)),
                          size_hint=(0.5, 0.3))
            popup.open()





class WorkoutsScreen(Screen):
    exercises = ListProperty(["Bench press", "Dřepy", "Mrtvý tah", "Biceps curl", "Kliky"])
    workout_data = ListProperty()
    personal_records = DictProperty()
    progress_data = DictProperty()  # New: Track progress over time
    selected_exercise = StringProperty("")
    show_exercises = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = ApiClient()

    def load_user_data(self, username):
        """Načte data uživatele z API a spočítá PR a progres."""
        workouts, err = self.api.get_workouts()
        if err:
            popup = Popup(title="Chyba",
                          content=Label(text=f"Nepodařilo se načíst tréninky: {err}"),
                          size_hint=(0.6, 0.35))
            popup.open()
            return

        # Reset lokálních agregací
        self.personal_records = {}
        self.progress_data = {}

        # Doplnit seznam cviků dle historie
        seen_exercises = set(self.exercises)

        # Pro každý workout spočítat PR a progres
        for w in workouts:
            ex = w.get('exercise')
            sets = int(w.get('sets', 0) or 0)
            reps = int(w.get('reps', 0) or 0)
            weight = float(w.get('weight', 0) or 0)
            date = w.get('date')

            if ex not in seen_exercises:
                self.exercises.append(ex)
                seen_exercises.add(ex)

            # PR: maximální váha pro daný cvik
            if ex not in self.personal_records or weight > float(self.personal_records.get(ex, 0)):
                self.personal_records[ex] = weight

            # Progres: uložení historie
            if ex not in self.progress_data:
                self.progress_data[ex] = []
            self.progress_data[ex].append({
                'date': date,
                'sets': sets,
                'reps': reps,
                'weight': weight,
                'volume': sets * reps * weight
            })

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

        # Okamžité uložení do DB přes API (včetně aktuální poznámky)
        note = self.ids.note.text
        error = self.api.add_workout(
            exercise=self.selected_exercise,
            sets=int(sets),
            reps=int(reps),
            weight=float(weight),
            note=note or ""
        )
        if error:
            popup = Popup(title="Chyba",
                          content=Label(text=f"Chyba při ukládání: {error}"),
                          size_hint=(0.6, 0.35))
            popup.open()
            return

        # Přidáme do lokálního zobrazení pro přehled
        entry = f"{self.selected_exercise} - {sets}x{reps}, {weight}kg"
        self.workout_data.append((self.selected_exercise, int(sets), int(reps), float(weight)))
        self.ids.workout_list.text += f"{entry}\n"

        # aktualizace osobních rekordů
        if self.selected_exercise not in self.personal_records or float(weight) > self.personal_records[self.selected_exercise]:
            self.personal_records[self.selected_exercise] = float(weight)

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
        # Data se ukládají průběžně při přidání cviku; jen přenačteme data z API a přepočítáme PR/progres
        self.load_user_data(App.get_running_app().root.get_screen("main").username)

        popup = Popup(
            title="Uloženo",
            content=Label(text=f"Trénink průběžně ukládán do DB.\n\n{summary}\n\nPoznámka uložena u záznamů:\n{note if note else '(žádná)'}"),
            size_hint=(0.7, 0.7),
        )
        popup.bind(on_dismiss=self.back_to_dashboard)
        popup.open()

        # reset polí
        self.workout_data = []
        self.ids.workout_list.text = ""
        self.ids.note.text = ""

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
