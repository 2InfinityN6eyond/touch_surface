#pyautogui 설치 pip install pyautogui
import pyautogui
'''
#moveTo (x,y 좌표 기준으로 마우스 이동) x,y,duration
pyautogui.moveTo(50,30) #마우스를 (50,30)으로 이동
pyautogui.moveTo(150, None, 1) #마우스의 x좌표가 150으로 1초동안 이동하도록 움직임 (y는 현재위치)
pyautogui.moveTo(None,70) #마우스의 y좌표가 70으로 이동하도록 움직임 (x는 현재위치)

#move (현재 x,y 좌표 기준으로 마우스 이동) x,y,duration
pyautogui.moveTo(100,100)
pyautogui.move(0,100)
pyautogui.move(100,30,3)

#dragTo (x,y 좌표로 기준으로 마우스를 button을 누른 상태로 duration동안 움직임 /duration은 default있음, button은 right left middle)
pyautogui.dragTo(1000,300, button='middle')

#dragTo (현재위치를 기준으로 마우스를 button을 누른 상태로 x,y만큼 duration동안 움직임 /duration은 default있음, button은 right left middle)
pyautogui.drag(100,30, button='middle')


#click (x,y 위치를 button으로 누름 /interval동안 click만큼 누름)
pyautogui.click() #현재 위치 클릭 기본left


#마우스 버튼 누르기, 떼기 mouseDown, Up
pyautogui.mouseDown() #현재위치에서 마우스 왼쪽 버튼 누름
pyautogui.mouseDown(button="right") #현재 오른쪽 누름
pyautogui.mouseUp(100,100,button="right") #x,y 위치에서 마우스 오른쪽버튼 뗌
'''

#scroll x,y로 이동후 click 만큼 스크롤 이동 click,x,y
pyautogui.scroll(2,1000,300)