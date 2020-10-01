import kivy
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget

Builder.load_string("""

<YowieScreen4>:

    canvas:
        Color: 
            rgba: [1, 1, 1, 1]
        Rectangle: 
            size: self.size
            pos: self.pos

    BoxLayout:
        orientation: 'horizontal'
        padding: 0
        spacing: 0
        size_hint: (None, None)
        height: dp(480)
        width: dp(800)

        # SCREEN BUTTONS
	    BoxLayout:
	        orientation: 'horizontal'
	        size_hint: (None, None)
	        height: dp(480)
	        width: dp(180)

	        GridLayout:
		        size: self.parent.size
		        pos: self.parent.pos
		        cols: 2

		        # Top right
	        	Button:
	        		on_press: root.go_s2()
	        		Label:
	        			center: self.parent.center
	        			color: [1,1,1,1]
		        		height: self.parent.width
				        canvas.before:
				            PushMatrix
				            Rotate:
				                angle: 90
				                origin: self.center
				        canvas.after:
				            PopMatrix
		        		text: 'Scan Settings'

		        # Bottom right
	        	Button:
	        		on_press: root.go_s4()
	        		Label:
	        			center: self.parent.center
	        			color: [1,1,1,1]
		        		height: self.parent.width
				        canvas.before:
				            PushMatrix
				            Rotate:
				                angle: 90
				                origin: self.center
				        canvas.after:
				            PopMatrix
		        		text: 'Scan Output'

		        # Top left
	        	Button:
	        		on_press: root.go_s1()
	        		Label:
	        			center: self.parent.center
	        			color: [1,1,1,1]
		        		height: self.parent.width
				        canvas.before:
				            PushMatrix
				            Rotate:
				                angle: 90
				                origin: self.center
				        canvas.after:
				            PopMatrix
		        		text: 'Levelling'

		        # Bottom left
	        	Button:
	        		on_press: root.go_s3()
	        		Label:
	        			center: self.parent.center
	        			color: [1,1,1,1]
		        		height: self.parent.width
				        canvas.before:
				            PushMatrix
				            Rotate:
				                angle: 90
				                origin: self.center
				        canvas.after:
				            PopMatrix
		        		text: 'Scan'

	    BoxLayout:
	        orientation: 'horizontal'
	        size_hint: (None, None)
	        height: dp(480)
	        width: dp(200)


		Button:
	        size_hint: (None, None)
	        height: dp(480)
	        width: dp(200)
	        on_press: root.save_output()
			Label:
    			center: self.parent.center
    			color: [1,1,1,1]
        		height: self.parent.width
        		width: self.parent.height
		        canvas.before:
		            PushMatrix
		            Rotate:
		                angle: 90
		                origin: self.center
		        canvas.after:
		            PopMatrix
		        markup: True
		        font_size: '22sp'
		        text: "Save"




""")

class YowieScreen4(Screen):

	def __init__(self, **kwargs):

		self.sm = kwargs['screen_manager']
		self.name = kwargs['name']
		# self.s = kwargs['scanner']

		super(YowieScreen4, self).__init__()

# SCREEN BUTTONS
	def go_s1(self):
		self.sm.current = 's1'

	def go_s2(self):
		self.sm.current = 's2'

	def go_s3(self):
		self.sm.current = 's3'

	def go_s4(self):
		self.sm.current = 's4'


# SAVE OUTPUT

	save_path = ''

	def save_output(self):
		pass

		# INSERT SAVE FUNCTION