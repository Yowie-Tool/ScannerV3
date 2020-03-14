import kivy
kivy.require('1.10.1')
from kivy.app import App
from kivy.uix.label import label

class MyApp(App):

	def build(self):
		return Label(test='Hello world')
		
if __name__ == "__main__":
	MyApp().run()