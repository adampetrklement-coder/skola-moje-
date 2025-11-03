import requests
import json
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

# Načti .env proměnné (pokud existují)
load_dotenv()

# Konfigurace API
API_URL = os.getenv('API_URL', 'http://localhost:5001')

class ApiClient:
    def __init__(self):
        self.token = None
    
    def login(self, username: str, password: str) -> Optional[str]:
        """Přihlášení uživatele přes API"""
        print(f"[API] Přihlášení uživatele: {username}")
        print(f"[API] URL: {API_URL}/login")
        try:
            response = requests.post(f"{API_URL}/login", json={
                "username": username,
                "password": password
            }, timeout=5)
            
            print(f"[API] Status kód: {response.status_code}")
            print(f"[API] Odpověď: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                print(f"[API] Token získán: {self.token[:20]}..." if self.token else "[API] Token nebyl vrácen!")
                return None  # úspěch
            else:
                error_msg = response.json().get('error', 'Neznámá chyba při přihlášení')
                print(f"[API] Chyba: {error_msg}")
                return error_msg
                
        except requests.RequestException as e:
            error_msg = f"Chyba připojení k serveru: {str(e)}"
            print(f"[API] Exception: {error_msg}")
            return error_msg
    
    def register(self, username: str, password: str, email: Optional[str] = None) -> Optional[str]:
        """Registrace nového uživatele"""
        try:
            response = requests.post(f"{API_URL}/register", json={
                "username": username,
                "password": password,
                "email": email
            })
            
            if response.status_code == 201:
                return None  # úspěch
            else:
                return response.json().get('error', 'Neznámá chyba při registraci')
                
        except requests.RequestException as e:
            return f"Chyba připojení k serveru: {str(e)}"
    
    def add_workout(self, exercise: str, sets: int, reps: int, weight: float, note: str = "") -> Optional[str]:
        """Přidání nového tréninku"""
        if not self.token:
            return "Nejste přihlášeni"
            
        try:
            response = requests.post(f"{API_URL}/add_workout", json={
                "token": self.token,
                "exercise": exercise,
                "sets": sets,
                "reps": reps,
                "weight": weight,
                "note": note
            })
            
            if response.status_code == 201:
                return None  # úspěch
            else:
                return response.json().get('error', 'Neznámá chyba při ukládání tréninku')
                
        except requests.RequestException as e:
            return f"Chyba připojení k serveru: {str(e)}"
    
    def get_workouts(self) -> tuple[Optional[List[Dict]], Optional[str]]:
        """Získání historie tréninků"""
        if not self.token:
            return None, "Nejste přihlášeni"
            
        try:
            response = requests.get(
                f"{API_URL}/get_workouts",
                headers={"Authorization": self.token}
            )
            
            if response.status_code == 200:
                return response.json().get('workouts', []), None
            else:
                return None, response.json().get('error', 'Neznámá chyba při načítání tréninků')
                
        except requests.RequestException as e:
            return None, f"Chyba připojení k serveru: {str(e)}"