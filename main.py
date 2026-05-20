# Copyright (c) 2025 Omer Kemal
# Proprietary and confidential. All rights reserved.
# Unauthorized copying, modification, or distribution is prohibited.

import sqlite3
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock

from PhantomGate import main, targetData

# ===================== THREAD MANAGEMENT ======================
# Create an event to signal thread shutdown
thread_stop_event = threading.Event()

create_all_target_table = targetData(command="create_all_table")

def run_main_with_stop():
    """Wrapper function to run main with stop event"""
    # Pass the stop event to main function if it accepts it
    # If not, we'll need to modify PhantomGate.main() to check for stop signal
    main()  # Assuming main runs in a loop, it needs to check for stop condition


# ===================== DATABASE HANDLER ======================
class MyDatabase:
    def __init__(self, db_name='people.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.lock = threading.Lock()
        self.create_table()

    def create_table(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS people (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            self.conn.commit()

    def add_person(self, name):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO people (name) VALUES (?)', (name,))
            self.conn.commit()

    def get_all_people(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, name FROM people')
            return cursor.fetchall()

    def delete_person(self, person_id):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM people WHERE id = ?', (person_id,))
            self.conn.commit()

    def close(self):
        with self.lock:
            self.conn.close()

# ===================== CARD COMPONENT ======================
class Card(BoxLayout):
    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.padding = 10
        self.spacing = 10
        self.size_hint_y = None
        self.height = 60
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg = RoundedRectangle(radius=[10], pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

# ===================== MAIN UI ======================
class MobileUI(BoxLayout):
    def __init__(self, **kwargs):
        super(MobileUI, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 10
        self.db = MyDatabase()
        self.cleanup_done = False

        # Header
        header = Label(text="📱 My SQLite App", font_size=24, size_hint_y=None, height=50, bold=True)
        self.add_widget(header)

        # Input section
        self.input_card = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.input_name = TextInput(hint_text='Enter name', multiline=False)
        self.input_name.bind(on_touch_down=self.force_focus)

        self.add_button = Button(text='Add', size_hint_x=None, width=80)
        self.add_button.bind(on_press=self.add_name)
        self.input_card.add_widget(self.input_name)
        self.input_card.add_widget(self.add_button)
        self.add_widget(self.input_card)

        # Scrollable list
        self.scroll = ScrollView()
        self.names_layout = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=[0, 5])
        self.names_layout.bind(minimum_height=self.names_layout.setter('height'))
        self.scroll.add_widget(self.names_layout)
        self.add_widget(self.scroll)

        self.update_name_list()

    def force_focus(self, instance, touch):
        if instance.collide_point(*touch.pos):
            instance.focus = True

    def add_name(self, instance):
        name = self.input_name.text.strip()
        if name:
            self.db.add_person(name)
            self.input_name.text = ''
            self.update_name_list()

    def delete_name(self, person_id):
        self.db.delete_person(person_id)
        self.update_name_list()

    def update_name_list(self):
        self.names_layout.clear_widgets()
        people = self.db.get_all_people()
        for person_id, name in people:
            name_card = Card()
            name_label = Label(text=name, font_size=18, color=(0, 0, 0, 1), halign='left', valign='middle')
            delete_button = Button(text='Delete', size_hint_x=None, width=80)
            delete_button.bind(on_press=lambda btn, pid=person_id: self.delete_name(pid))
            name_card.add_widget(name_label)
            name_card.add_widget(delete_button)
            self.names_layout.add_widget(name_card)

    def cleanup(self):
        """Clean up resources before app closes"""
        if not self.cleanup_done:
            print("Starting cleanup...")
            
            # Close database
            self.db.close()
            print("Database closed.")
            
            # Signal thread to stop
            try:
                # Try multiple times to ensure thread gets the message
                for i in range(3):
                    targetData(command='setPermission', threadPermisstion='Deny', ID=123)
                    print(f"Permission revocation attempt {i+1}")
                    time.sleep(0.1)  # Small delay between attempts
            except Exception as e:
                print(f"Error while revoking permission: {e}")
            
            self.cleanup_done = True
            print("Cleanup completed.")

# ===================== KIVY APP ======================
class MyApp(App):
    def build(self):
        self.ui = MobileUI()
        return self.ui

    def on_start(self):
        """Start background work and ensure DB/tables are initialized."""
        try:
            self.bg_thread = threading.Thread(target=run_main_with_stop, daemon=True)
            self.bg_thread.start()
        except Exception as e:
            print("Failed to start background thread:", e)

        try:
            targetData(command="create_all_table")
            targetData(command='setPermission', ID=123)
            targetData(command='setProxci', proxci_status='NoteAllow', ID=123)
        except Exception as e:
            print("Error initializing target data:", e)

    def on_stop(self):
        """Called when the app is stopping"""
        print("App is stopping...")
        if hasattr(self, 'ui'):
            # Schedule cleanup in the main thread
            Clock.schedule_once(lambda dt: self.ui.cleanup(), 0)
        
        # Give cleanup time to complete
        Clock.schedule_once(lambda dt: self.force_exit(), 1)

    def force_exit(self):
        """Force exit after cleanup"""
        print("Forcing exit...")
        # One final attempt to stop the thread
        try:
            print("Final permission revocation attempt")
            targetData(command='setPermission', threadPermisstion='Deny', ID=123)
        except:
            pass

# ===================== ENTRY POINT ======================
if __name__ == '__main__':
    try:
        app = MyApp()
        app.run()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received")
        # Try to stop the thread
        print("Attempting to stop background thread...")
        targetData(command='setPermission', threadPermisstion='Deny', ID=123)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Application exiting")
        # Final cleanup
        print("Final cleanup...")
        targetData(command='setPermission', threadPermisstion='Deny', ID=123)