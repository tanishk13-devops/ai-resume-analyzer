import os
import json

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "applications.json")

class DBHandler:
    """Handles persistence of job applications in a local JSON database."""
    
    @staticmethod
    def _init_db():
        """Ensure data directory and database file exist."""
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)

    @classmethod
    def get_applications(cls):
        """Fetch all applications from the database."""
        cls._init_db()
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def save_applications(cls, applications):
        """Save a list of applications to the database."""
        cls._init_db()
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(applications, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    @classmethod
    def add_application(cls, app_data):
        """Add a single application to the database."""
        apps = cls.get_applications()
        
        # Calculate new id
        new_id = 1
        if apps:
            new_id = max(app.get("id", 0) for app in apps) + 1
            
        app_data["id"] = new_id
        
        # Default empty fields if not provided
        if "status" not in app_data:
            app_data["status"] = "Wishlist"
        if "date_applied" not in app_data:
            app_data["date_applied"] = ""
        if "salary" not in app_data:
            app_data["salary"] = ""
        if "contacts" not in app_data:
            app_data["contacts"] = []
        if "notes" not in app_data:
            app_data["notes"] = ""
        if "checklist" not in app_data:
            app_data["checklist"] = []
            
        apps.append(app_data)
        cls.save_applications(apps)
        return app_data

    @classmethod
    def update_application(cls, app_id, updated_fields):
        """Update fields on an existing application."""
        apps = cls.get_applications()
        updated = False
        for app in apps:
            if app.get("id") == app_id:
                for k, v in updated_fields.items():
                    app[k] = v
                updated = True
                break
        if updated:
            cls.save_applications(apps)
        return updated

    @classmethod
    def delete_application(cls, app_id):
        """Delete an application by ID."""
        apps = cls.get_applications()
        filtered_apps = [app for app in apps if app.get("id") != app_id]
        if len(filtered_apps) < len(apps):
            cls.save_applications(filtered_apps)
            return True
        return False
