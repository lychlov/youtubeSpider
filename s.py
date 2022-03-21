
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By #按照什么方式查找，By.ID,By.CSS_SELECTOR
from selenium.webdriver.common.keys import Keys #键盘按键操作
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait #等待页面加载某些元素
browser=webdriver.Chrome()
#隐式等待:在查找所有元素时，如果尚未被加载，则等10秒
browser.implicitly_wait(10)
browser.get('https://youtube.com')
input_tag=browser.find_element_by_id('kw')
input_tag.send_keys('美女')
input_tag.send_keys(Keys.ENTER)
contents=browser.find_element_by_id('content_left') #没有等待环节而直接查找，找不到则会报错
print(contents)
browser.close()