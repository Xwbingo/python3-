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

#������ͼģʽ��PhantomJS
SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
driver = webdriver.PhantomJS(service_args=SERVICE_ARGS)
driver.maximize_window()

#������ͼģʽ��chrome
#options = webdriver.ChromeOptions()
#prefs = {'profile.default_content_setting_values': {'images': 2}}
#options.add_experimental_option('prefs', prefs)
#driver = webdriver.Chrome(chrome_options=options)

timeout = WebDriverWait(driver, 10)#�������ʱ��Ϊ10s
table_list = []#������Ʒ��Ϣ���б�

#������Ʒ����
def search_item(item, tm, rq, xl, jg):
    try:
        url = 'https://www.taobao.com/'
        driver.get(url)
        #��Ʒ�����
        input_frame = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#q')))
        #����ȷ�ϰ���
        search_submit = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input_frame.clear()
        input_frame.send_keys(item)
        search_submit.click()
        #����Ϊ����������ʾ
        time.sleep(2)
        driver.find_element_by_css_selector('span.icon.icon-btn-switch-grid').click()
        #���ü�����������
        search_condition(tm=tm, rq=rq, xl=xl, jg=jg)
        #�ȴ��׶�ҳ��������
        timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        #��ü�����ҳ����������
        total_page = int(re.findall(r'��\s*(\d+)\s*ҳ', driver.page_source)[0])
        print('һ��������{}ҳ��Ʒ��Ϣ....'.format(total_page))
        return total_page
    except TimeoutException:
        print('����ʱ��������������....')
        return search_item(item)

#������������
def search_condition(tm, rq, xl, jg):
    time.sleep(2)
    #��è
    if tm == 1:
        tianmao = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-key="filter_tianmao"] > span.icon.icon-btn-check-big')))
        tianmao.click()
        timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-key="filter_tianmao"] > span.icon.icon-btn-check-big')))
        time.sleep(2)
    #�����Ӹߵ���
    if rq == 1:
        renqi = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="renqi-desc"]')))
        renqi.click()
        timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="renqi-desc"]')))
        time.sleep(2)
    #�����Ӹߵ���
    if xl == 1:
        xiaoliang = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="sale-desc"]')))
        xiaoliang.click()
        timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > ul > li > a[data-value="sale-desc"]')))
        time.sleep(2)
    #�۸���������
    if jg == 1:
        min_price = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > div.prices > div.inputs.J_LaterHover > div > ul > li:nth-child(1) > input')))
        #������ͣ
        ActionChains(driver).move_to_element(min_price).perform()
        max_price = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > div.prices > div.inputs.J_LaterHover > div > ul > li:nth-child(3) > input')))
        price_submit = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_relative > div.sort-row > div > div.prices > div.inputs.J_LaterHover > div > ul > li.submit > button')))
        time.sleep(2)
        min_price.clear()
        min_price.send_keys(str(price_min.get()))
        max_price.clear()
        max_price.send_keys(str(price_max.get()))
        price_submit.click()

#����һҳ����
def each_page(page):
    try:
        page_frame = timeout.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        page_submit = timeout.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        page_frame.clear()
        page_frame.send_keys(str(page))
        page_submit.click()
        print('���ڴ򿪵�{}ҳ....'.format(page))
        time.sleep(2)
    except:
        print('���´򿪵�{}ҳ....'.format(page))
        return each_page(page)

#�����Ʒ��Ϣ
def get_item_info(page):
    print('�����ռ���{}ҳ��Ʒ��Ϣ.....'.format(page))
    soup = BeautifulSoup(driver.page_source, 'lxml')
    all_div = soup.select('div[class*="J_MouserOnverReq"]')
    for div in all_div:
        #ͼƬ��ַ
        pic_url = 'https:' + div.select('a.pic-link.J_ClickStat.J_ItemPicA > img.J_ItemPic.img')[0]['data-src']
        #��Ʒ�۸�
        price = div.select('div.price.g_price.g_price-highlight > strong')[0].text
        #��Ʒ����
        title = div.select('a.J_ClickStat img')[0]['alt']
        #��Ʒ��ַ
        item_url = div.select('a.J_ClickStat')[0]['href']
        if item_url[0:4] == 'http':
            title = '(�ƹ���)' + title
        else:
            item_url = 'https:' + div.select('a.J_ClickStat')[0]['href']
        #������
        location = div.select('div.row.row-3.g-clearfix > div.location')[0].text
        #������
        shopname = div.select('a.shopname.J_MouseEneterLeave.J_ShopInfo > span:nth-of-type(2)')[0].text
        #�������
        baoyou = '����' if div.select('span.baoyou-intitle.icon-service-free') else '������'
        #�Ƿ���è
        tianmao = '��è' if div.select('span.icon-service-tianmao') else ''
        #�����������ջ�����
        deal_cnt = div.select('div.deal-cnt')[0].text
        print([title, price, location, shopname, baoyou, tianmao, deal_cnt, pic_url, item_url])
        table_list.append([title, price, location, shopname, baoyou, tianmao, deal_cnt, pic_url, item_url])
    print('��{}ҳ��Ʒ��Ϣ�ռ����....'.format(page))

#csv���溯��
def csv_write():
    tableheader = ['����', '�۸�', '������', '�������', '�ʷ�', '�̵�����', '��������', '����ͼƬ', '��Ʒ��ַ']
    with open('item.csv', 'w', newline='', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow(tableheader)
        for row in table_list:
            writer.writerow(row)

#������
def main_fun():
    try:
        #���ؼ���������ҳ����������Ʒ�ؼ��ʡ���è���������������۸񣬵õ���ʼ��ҳ
        total_page = search_item(item.get(), tm.get(), rq.get(), xl.get(), jg.get())
        #������Ҫ������ҳ������ÿһҳ����ȡ��Ʒ��Ϣ�����浽�б��У�����csv��
        for page in range(1, spage.get()+1):
            each_page(page)
            get_item_info(page)
        print('��Ʒ��Ϣȫ���ռ���ɣ�')
        csv_write()
        print('��Ʒ��Ϣcsv�ļ�����ɹ���')
    finally:
        driver.quit()

if __name__ == '__main__':
    try:
        root = Tk()
        root.title('�Ա���������')
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

        Label(root, text='�Ա���������').place(relx=0.6, rely=0.1, anchor=SE)
        Label(root, text='�������ݣ�').place(relx=0.5, rely=0.2, anchor=SE)
        Entry(root, textvariable=item, width=8).place(relx=0.65, rely=0.2, anchor=SE)
        Checkbutton(root, variable=tm, text='��è').place(relx=0.48, rely=0.3, anchor=SE)
        Checkbutton(root, variable=rq, text='�����Ӹߵ���').place(relx=0.6, rely=0.4, anchor=SE)
        Checkbutton(root, variable=xl, text='�����Ӹߵ���').place(relx=0.6, rely=0.5, anchor=SE)
        Checkbutton(root, variable=jg, text='�۸���������').place(relx=0.5, rely=0.6, anchor=SE)
        Entry(root, textvariable=price_min, width=4).place(relx=0.6, rely=0.6, anchor=SE)
        Label(root, text='~').place(relx=0.65, rely=0.6, anchor=SE)
        Entry(root, textvariable=price_max, width=4).place(relx=0.75, rely=0.6, anchor=SE)
        Label(root, text='����ҳ����').place(relx=0.55, rely=0.7, anchor=SE)
        Entry(root, textvariable=spage, width=4).place(relx=0.65, rely=0.7, anchor=SE)
        Button(root, text='��ʼ����', command=main_fun).place(relx=0.6, rely=0.85, anchor=SE)
        root.mainloop()
    finally:
        driver.quit()
        print('������ѹرգ�')