from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from tkinter import *
from tkinter.ttk import *
import re, time, csv

#设置无图模式的PhantomJS
SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
driver = webdriver.PhantomJS(service_args=SERVICE_ARGS)
driver.maximize_window()

#设置无图模式的chrome
#options = webdriver.ChromeOptions()
#prefs = {'profile.default_content_setting_values': {'images': 2}}
#options.add_experimental_option('prefs', prefs)
#driver = webdriver.Chrome(chrome_options=options)

timeout = WebDriverWait(driver, 10)#设置溢出时间为10s
table_list = []#保存商品信息的列表

#搜索商品函数
def search_item(item, tm, rq, xl, jg):
    try:
        url = 'https://www.taobao.com/'
        driver.get(url)
        #商品输入框
        input_frame = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        #搜索确认按键
        search_submit = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input_frame.clear()
        input_frame.send_keys(item)
        search_submit.click()
        #设置为网格区间显示
        time.sleep(2)
        driver.find_element_by_css_selector('span.icon.icon-btn-switch-grid').click()
        #调用检索条件函数
        search_condition(tm=tm, rq=rq, xl=xl, jg=jg)
        #等待底端页码加载完毕
        timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        #获得检索总页数，并返回
        total_page = int(re.findall(r'共\s*(\d+)\s*页', driver.page_source)[0])
        print('一共检索到{}页商品信息....'.format(total_page))
        return total_page
    except TimeoutException:
        print('请求超时，正在重新连接....')
        return search_item(item)

#检索条件函数
def search_condition(tm, rq, xl, jg):
    time.sleep(2)
    #天猫
    if tm == 1:
        tianmao = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-key="filter_tianmao"] > span.icon.icon-btn-check-big')))
        tianmao.click()
        timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-key="filter_tianmao"] > span.icon.icon-btn-check-big')))
        time.sleep(2)
    #人气从高到低
    if rq == 1:
        renqi = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="renqi-desc"]')))
        renqi.click()
        timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="renqi-desc"]')))
        time.sleep(2)
    #销量从高到低
    if xl == 1:
        xiaoliang = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="sale-desc"]')))
        xiaoliang.click()
        timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="sale-desc"]')))
        time.sleep(2)
    #价格区间设置
    if jg == 1:
        min_price = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > div.prices > div.inputs.J_LaterHover > div > ul > li:nth-child(1) > input')))
        #设置悬停
        ActionChains(driver).move_to_element(min_price).perform()
        max_price = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > div.prices > div.inputs.J_LaterHover > div > ul > li:nth-child(3) > input')))
        price_submit = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > div.prices > div.inputs.J_LaterHover > div > ul > li.submit > button')))
        time.sleep(2)
        min_price.clear()
        min_price.send_keys(str(price_min.get()))
        max_price.clear()
        max_price.send_keys(str(price_max.get()))
        price_submit.click()

#打开下一页函数
def each_page(page):
    try:
        page_frame = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        page_submit = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        page_frame.clear()
        page_frame.send_keys(str(page))
        page_submit.click()
        print('正在打开第{}页....'.format(page))
        time.sleep(2)
    except:
        print('重新打开第{}页....'.format(page))
        return each_page(page)

#获得商品信息
def get_item_info(page):
    print('正在收集第{}页商品信息.....'.format(page))
    soup = BeautifulSoup(driver.page_source, 'lxml')
    all_div = soup.select('div[class*="J_MouserOnverReq"]')
    for div in all_div:
        #图片地址
        pic_url = 'https:' + div.select('a.pic-link.J_ClickStat.J_ItemPicA > img.J_ItemPic.img')[0]['data-src']
        #商品价格
        price = div.select('div.price.g_price.g_price-highlight > strong')[0].text
        #商品标题
        title = div.select('a.J_ClickStat img')[0]['alt']
        #商品地址
        item_url = div.select('a.J_ClickStat')[0]['href']
        if item_url[0:4] == 'http':
            title = '(推广广告)' + title
        else:
            item_url = 'https:' + div.select('a.J_ClickStat')[0]['href']
        #发货地
        location = div.select('div.row.row-3.g-clearfix > div.location')[0].text
        #店铺名
        shopname = div.select('a.shopname.J_MouseEneterLeave.J_ShopInfo > span:nth-of-type(2)')[0].text
        #包邮情况
        baoyou = '包邮' if div.select('span.baoyou-intitle.icon-service-free') else '不包邮'
        #是否天猫
        tianmao = '天猫' if div.select('span.icon-service-tianmao') else ''
        #购买人数或收货人数
        deal_cnt = div.select('div.deal-cnt')[0].text
        print([title, price, location, shopname, baoyou, tianmao, deal_cnt, pic_url, item_url])
        table_list.append([title, price, location, shopname, baoyou, tianmao, deal_cnt, pic_url, item_url])
    print('第{}页商品信息收集完成....'.format(page))

#csv保存函数
def csv_write():
    tableheader = ['标题', '价格', '发货地', '店家名称', '邮费', '商店性质', '购买人数', '封面图片', '商品网址']
    with open('item.csv', 'w', newline='', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow(tableheader)
        for row in table_list:
            writer.writerow(row)

#主函数
def main_fun():
    try:
        #返回检索到的总页数，输入商品关键词、天猫、人气、销量、价格，得到初始网页
        total_page = search_item(item.get(), tm.get(), rq.get(), xl.get(), jg.get())
        #定义需要检索的页数，打开每一页，获取商品信息，保存到列表中，存入csv中
        for page in range(1, spage.get()+1):
            each_page(page)
            get_item_info(page)
        print('商品信息全部收集完成！')
        csv_write()
        print('商品信息csv文件保存成功！')
    finally:
        driver.quit()

if __name__ == '__main__':
    try:
        root = Tk()
        root.title('淘宝检索工具')
        root.geometry('400x300+0+0')

        item = StringVar()
        tm = IntVar()
        rq = IntVar()
        xl = IntVar()
        jg = IntVar()
        spage = IntVar()
        price_max = DoubleVar()
        price_min = DoubleVar()
        item.set('')
        tm.set(0)
        rq.set(0)
        xl.set(0)
        jg.set(0)
        spage.set(5)
        price_max.set(0.0)
        price_min.set(0.0)

        Label(root, text='淘宝检索工具').place(relx=0.6, rely=0.1, anchor=SE)
        Label(root, text='搜索内容：').place(relx=0.5, rely=0.2, anchor=SE)
        Entry(root, textvariable=item, width=8).place(relx=0.65, rely=0.2, anchor=SE)
        Checkbutton(root, variable=tm, text='天猫').place(relx=0.48, rely=0.3, anchor=SE)
        Checkbutton(root, variable=rq, text='人气从高到低').place(relx=0.6, rely=0.4, anchor=SE)
        Checkbutton(root, variable=xl, text='销量从高到低').place(relx=0.6, rely=0.5, anchor=SE)
        Checkbutton(root, variable=jg, text='价格区间设置').place(relx=0.5, rely=0.6, anchor=SE)
        Entry(root, textvariable=price_min, width=4).place(relx=0.6, rely=0.6, anchor=SE)
        Label(root, text='~').place(relx=0.65, rely=0.6, anchor=SE)
        Entry(root, textvariable=price_max, width=4).place(relx=0.75, rely=0.6, anchor=SE)
        Label(root, text='检索页数：').place(relx=0.55, rely=0.7, anchor=SE)
        Entry(root, textvariable=spage, width=4).place(relx=0.65, rely=0.7, anchor=SE)
        Button(root, text='开始搜索', command=main_fun).place(relx=0.6, rely=0.85, anchor=SE)
        root.mainloop()
    finally:
        driver.quit()
        print('浏览器已关闭！')