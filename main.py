from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.network.urlrequest import UrlRequest
from kivy.core.image import Image as CoreImage
from io import BytesIO
import requests
import random
# test
class My(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        
        # 국기 이미지를 표시할 위젯
        self.flag_image = Image(size_hint=(None, None), size=(100, 70),
                                pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.layout.add_widget(self.flag_image)

        # 체크박스들을 담을 리스트
        self.checkboxes = []

        # 체크박스 생성 및 추가
        for i in range(4):
            checkbox = CheckBox()
            checkbox.bind(active=self.on_checkbox_active)
            self.layout.add_widget(checkbox)
            self.checkboxes.append(checkbox)
        
        # 버튼 생성 및 이벤트 핸들링
        self.button = Button(text='Show me')
        self.button.bind(on_release=self.on_button_press)
        self.layout.add_widget(self.button)

        

        url = 'http://apis.data.go.kr/1262000/CountryFlagService2/getCountryFlagList2'
        params = {
            'serviceKey': 'NEbj7uugsb5VWDa/iayAlVNIQifgGpMZ42N38euKpv7DyaR8vCsvkLxoAtvZQSe+0JbRXBSUQCIhKqPGDGwtMA==',
            'returnType': 'JSON',
            'numOfRows': '220',
        }

        response = requests.get(url, params=params)

        # JSON 형식으로 응답 받기
        data = response.json()

        country_list = []

        # 데이터 확인
        for i in range(len(data['data'])):
            country_list.append([data['data'][i]['country_nm'], data['data'][i]['download_url']])
            
        self.country_list = country_list

        return self.layout
    
    def on_button_press(self, instance):
        # API 요청
        problem_list = []
        answer = None
        wrong_answers = []

        num = random.randint(0, 219)
        problem_list.append(num)

        nums = self.random_numbers_except(num, 3, 219)
        problem_list.extend(nums)

        random.shuffle(problem_list)

        url = self.country_list[num][1]
        response = requests.get(url)
        image_data = BytesIO(response.content)
        core_image = CoreImage(image_data, ext='jpg')

        # flag_image 위젯의 텍스처 업데이트
        self.flag_image.texture = core_image.texture

        # 체크박스의 텍스트 설정
        for i in range(4):
            self.checkboxes[i].text = self.country_list[problem_list[i]][0]
            self.checkboxes[i].active = False

    def random_numbers_except(self, exclude_number, count, range_end):
        selected_numbers = []
        
        while len(selected_numbers) < count:
            random_number = random.randint(0, range_end)
            
            if random_number != exclude_number and random_number not in selected_numbers:
                selected_numbers.append(random_number)
        
        return selected_numbers

    def on_checkbox_active(self, checkbox, value):
        if value:
            # 체크박스가 활성화되었을 때 다른 체크박스들의 상태를 비활성화로 설정
            for cb in self.checkboxes:
                if cb != checkbox:
                    cb.active = False

if __name__ == '__main__':
    My().run()
    print("testsetsetset")
