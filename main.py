from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from io import BytesIO
import requests
import random

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        start_button = Button(
            text='Start',
            size_hint=(0.8, None),  # 80% of the width
            height=50,
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        start_button.bind(on_release=self.start_game)
        
        layout.add_widget(Label(font_size=18, text='Welcome to the Flag Quiz Game!', size_hint=(1, 0.2), halign='center', valign='middle'))
        layout.add_widget(start_button)

        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Flag image widget
        self.flag_image = Image(
            size_hint=(1, 0.5),  # 50% of the height of the screen
            allow_stretch=True,
            keep_ratio=False,
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        self.layout.add_widget(self.flag_image)

        # Checkboxes layout
        self.checkbox_layout = GridLayout(
            cols=2,
            padding=10,
            spacing=10,
            size_hint=(1, 0.3),  # 30% of the height of the screen
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        self.checkbox_layout.bind(minimum_height=self.checkbox_layout.setter('height'))
        self.checkboxes = []

        # Creating checkboxes and adding them to the layout
        for i in range(4):
            box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            checkbox = CheckBox()
            label = Label(text='', size_hint_x=None, width=200, halign='left', valign='middle')
            label.bind(size=label.setter('text_size'))
            checkbox.bind(active=self.on_checkbox_active)
            box.add_widget(checkbox)
            box.add_widget(label)
            self.checkbox_layout.add_widget(box)
            self.checkboxes.append((checkbox, label, box))
        
        self.layout.add_widget(self.checkbox_layout)

        # Button
        self.button = Button(
            text='Next',
            size_hint=(0.8, None),  # 80% of the width
            height=50,
            pos_hint={'center_x': 0.5}  # Center horizontally
        )
        self.button.bind(on_release=self.on_button_press)
        self.layout.add_widget(self.button)

        # API request
        url = 'http://apis.data.go.kr/1262000/CountryFlagService2/getCountryFlagList2'
        params = {
            'serviceKey': 'NEbj7uugsb5VWDa/iayAlVNIQifgGpMZ42N38euKpv7DyaR8vCsvkLxoAtvZQSe+0JbRXBSUQCIhKqPGDGwtMA==',
            'returnType': 'JSON',
            'numOfRows': '220',
        }

        response = requests.get(url, params=params)

        # Receive JSON response
        data = response.json()

        self.country_list = [[item['country_eng_nm'], item['download_url']] for item in data['data']]
        self.add_widget(self.layout)
        self.on_button_press(1)

    def on_button_press(self, instance):
        # Problem list and answer settings
        self.answer_index = random.randint(0, 219)
        problem_list = [self.answer_index]
        problem_list.extend(self.random_numbers_except(self.answer_index, 3, 219))
        random.shuffle(problem_list)

        url = self.country_list[self.answer_index][1]
        response = requests.get(url)
        image_data = BytesIO(response.content)
        core_image = CoreImage(image_data, ext='jpg')

        # Update flag_image widget texture
        self.flag_image.texture = core_image.texture

        # Set checkbox text
        for i in range(4):
            self.checkboxes[i][1].text = self.country_list[problem_list[i]][0]
            self.checkboxes[i][0].active = False
            self.reset_checkbox_background(self.checkboxes[i][0])

    def random_numbers_except(self, exclude_number, count, range_end):
        selected_numbers = []
        while len(selected_numbers) < count:
            random_number = random.randint(0, range_end)
            if random_number != exclude_number and random_number not in selected_numbers:
                selected_numbers.append(random_number)
        return selected_numbers

    def on_checkbox_active(self, checkbox, value):
        if value:
            # Only one checkbox can be active
            for cb, label, box in self.checkboxes:
                if cb != checkbox:
                    cb.active = False
            self.check_answer(checkbox)
        else:
            self.reset_checkbox_background(checkbox)

    def check_answer(self, checkbox):
        for cb, label, box in self.checkboxes:
            if cb == checkbox:
                if self.country_list[self.answer_index][0] == label.text:
                    self.set_checkbox_background(box, (0, 1, 0, 1))  # Green for correct
                else:
                    self.set_checkbox_background(box, (1, 0, 0, 1))  # Red for incorrect

    def set_checkbox_background(self, checkbox, color):
        with checkbox.canvas.before:
            Color(*color)
            checkbox.rect = Rectangle(size=checkbox.size, pos=checkbox.pos)
            checkbox.bind(pos=self.update_rect, size=self.update_rect)

    def reset_checkbox_background(self, checkbox):
        for cb, label, box in self.checkboxes:
            if cb == checkbox:
                with box.canvas.before:
                    Color(0, 0, 0, 1)  # White background
                    box.rect = Rectangle(size=box.size, pos=box.pos)
                    box.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    MyApp().run()
