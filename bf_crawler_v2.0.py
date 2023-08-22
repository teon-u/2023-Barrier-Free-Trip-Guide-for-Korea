"""
무장애 여행 데이터 크롤러 v2.0 by teon-u
Last update : 2023.08.11 16:30
Update Log :
    2.0 : 주요기능 함수화를 통한 코드 안정성 및 유지보수성 개선, 이미지 데이터 및 조회수 데이터 수집 기능 추가

Description:
    한국관광공사에서 서비스중인 "대한민국구석구석" 플랫폼의 무장애 여행 데이터를 크롤링하는 코드입니다.
    해당 크롤러를 통해 수집한 데이터의 금전적 목적의 사용은 법적 문제가 될 수 있습니다.
    또한 크롤러 작동시 "대한민국구석구석" 서버의 부하를 불러일으킬 수 있으니 유의하여 사용해주시기 바랍니다.
    (실제로 서버 다운된적 있음 ...)

Requirements:
    - Program
    Chromedirver.exe
    - Library
    urllib
    regex
    selenium
    BeautifulSoup
    pandas
"""


# Modules
import time
import urllib.request
import os
import re
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd


# Functions
def action_select_type(type_text):
    '''
    목록 페이지에서 음식, 숙박, 관광의 세가지 타입 중 하나를 선택하는 함수

    Parameters:
    type_text(string) : 음식, 숙박, 관광 의 세 값 중 하나를 문자열으로 받음

    Returns:
    None : 정상동작
    0 : 오류발생    
    '''
    sitecode = {'음식':39,'숙박':32,'관광':12}
    wait = WebDriverWait(driver, 2)
    for i in range(10):
        try:
            print("-Select Type Try :",i+1,": ",end="")
            time.sleep(1)
            wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="'+str(sitecode[type_text])+'"]/button'))).click()
            print("Success")
            return
        except Exception as error:
            print("Failed :",type(error).__name__)
            action_scrup()
            if i == 9:
                print("action_select_type_Err")
                return 0

def action_select_site(site_num):
    '''
    목록 페이지에서 변수에 따라 장소를 선택하는 함수

    Parameters:
        site_num(int) : 0~9 사이의 정수로, 목록 페이지의 각 장소에 할당된 번호

    Returns:
        None : 정상작동
        0 : 오류발생
    '''
    wait = WebDriverWait(driver, 2)
    for i in range(10):
        try:
            print("-Select Site Try :",i+1,": ",end="")
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
            "#contents > div.wrap_contView.clfix > div.box_leftType1 > ul > li:nth-child(" + str(site_num+1) + ") > div.area_txt > div > a"))).click()
            print("Success")
            return
        except Exception as error:
            print("Failed :",type(error).__name__)
            action_scrup()
            if i == 9:
                print("-Select Site Try : action_select_site_Err")
                return 0

def extract_info_type(type_text):
    '''
    여행지 분류정보를 추출해 딕셔너리로 반환하는 함수

    Parameters:
        type_text(string) : 음식, 숙박, 관광 의 세 값 중 하나를 문자열으로 받음

    Returns:
        temp_dict(dictionary) : 해당 여행지의 분류(문자열)을 딕셔너리로 반환
    '''
    time.sleep(1)
    temp_dict = {}
    temp_dict['분류'] = type_text
    return temp_dict

def extract_info_base():
    '''
    여행지 페이지의 기본정보를 추출하는 함수

    Returns:
        temp_dict(dictionary) : 해당 페이지의 "장소", "위치", "소개", "설명" 등 데이터를 딕셔너리로 반환
    '''
    try:
        temp_dict = {}
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.ID,"topTitle")))
        time.sleep(1)
        temp_dict['장소'] = driver.find_element(By.ID,"topTitle").text
        temp_dict['위치'] = driver.find_element(By.ID,"topAddr").text
        temp_dict['소개'] = driver.find_element(By.ID,"topCp").text
        temp_dict['설명'] = driver.find_element(By.CSS_SELECTOR,'#detailGo > div:nth-child(2) > div > div.inr_wrap > div > p').text

        if (temp_dict['장소'] is None) or temp_dict['장소']=="":
            action_refresh()
            print("-Extract Info Base : ERR : None value at data")
            time.sleep(5)
            return extract_info_base()

        return temp_dict
    except Exception as error:
        print("-Extract Info Base : ERR :",type(error).__name__,"| Result : Failed")
        return temp_dict

def action_html_parser():
    '''
    여행지 페이지를 파싱해 반환하는 함수

    Returns:
        BeautifulSoup(html,'html.parser) : 해당 페이지의 소스를 Bs4로 파싱해 반환
    '''
    html = driver.page_source
    return BeautifulSoup(html,'html.parser')

def action_return():
    '''
    이전 페이지로 이동하는 함수
    '''
    driver.back()

def extract_info_disable(soup):
    '''
    무장애정보 데이터를 추출해 반환하는 함수

    parameters :
        soup(Bs4.soup) : action_html_parser()를 이용해 추출한 페이지 소스

    Return :
        temp_dict(dictionary) : 해당 페이지의 무장애정보 데이터를 딕셔너리로 반환
    '''
    temp_dict = {}
    for item in soup.select('#bfreeinfoB > div > div > ul > li'):
        key = item.text[3:-2]
        value = 'active' in str(item)
        temp_dict[key] = value
    return temp_dict

def extract_info_text(soup):
    '''
    여행지 세부사항을 추출해 반환하는 함수

    parameters :
        soup(Bs4.soup) : action_html_parser()를 이용해 추출한 페이지 소스
    
    Return :
        temp_dict(dictionary) : 해당 페이지의 무장애정보 데이터를 딕셔너리로 반환
    '''
    temp_dict = {}
    for item in soup.select('#detailinfoview > div > div.inr_wrap > div > ul > li'):
        key = item.find('strong').text
        value = item.find('span').text
        temp_dict[key] = value
    return temp_dict

def action_nextpage():
    '''
    목록 페이지에서 다음 페이지로 이동하는 함수

    Return :
        None : 정상작동
        0 : 오류발생    
    '''
    for i in range(10):
        try:
            print("-Next Page  Try :",i+1,": ",end='')
            wait = WebDriverWait(driver, 5)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME,"on")))
            time.sleep(0.5)
            page = int(driver.find_element(By.CLASS_NAME,"on").text)
            if page % 5 == 0:
                driver.find_element(By.LINK_TEXT,"다음").click()
            else:
                driver.find_element(By.LINK_TEXT,str(page+1)).click()
            action_scrup()
            print("Success")
            return page
        except Exception as error:
            print("Failed :",type(error).__name__)
            if i == 9:
                print("-Next Page Try : Err :",type(error).__name__)
                return 0

def action_refresh():
    '''
    페이지를 새로고침 하는 함수
    '''
    driver.execute_script("location.reload()")

def action_scrup():
    '''
    페이지 맨 위로 스크롤을 올리는 함수
    '''
    driver.execute_script('window.scrollTo(0,0)')

def extract_info_view():
    '''
    여행지 페이지의 조회수를 추출하는 함수

    Return :
        info(int) : 조회수(정수) 값을 반환
    '''
    wait = WebDriverWait(driver, 5)
    for i in range(5):
        try:
            wait.until(EC.presence_of_element_located((By.ID,"conRead")))
            info = driver.find_element(By.ID,"conRead").text
            if info[-1] == 'K':
                return int(float(info[:-1])*1000)
            else:
                try:
                    return int(float(info))
                except:
                    print(info)
                    return info
        except:
            time.sleep(1)

def extract_info_imageurl(index,title,img_folder='download_img'):
    '''
    이미지 URL을 추출하는 함수

    Parameter :
        index(int) : 현재 페이지의 인덱스 (데이터 Join 위함)
        title(str) : 여행지명
        img_folder(str) : 이미지를 받을 폴더명

    Return :
        temp_df(pd.DataFrame) : 이미지 URL과 저장할 경로를 포함한 데이터프레임 반환
            row : 인덱스, 여행지명, 사진번호, 링크, 저장경로
                저장경로 : /저장경로/인덱스_사진번호_여행지명.jpg
    '''
    url_list = []
    element = driver.find_element(By.CSS_SELECTOR,"#pImgList")
    elements = element.find_elements(By.TAG_NAME, 'img')
   
    for e in elements:
        url_list.append(e.get_attribute("src"))# 1,2 img attribute
        url_list.append(e.get_attribute("data-src"))# 3~ img attribute
    url_list = [x for x in url_list if x]# Delete None from list
    
    temp_df = pd.DataFrame(columns=['Index','Title','Num','Link','Location'])
    
    for num, link in enumerate(url_list):# 딕셔너리에 이미지 경로 저장
        title_santitized = re.sub(r'[<>:"/\\|?*]', '_', title)
        filename = f'{index}_{num + 1}_{title_santitized}.jpg'
        filepath = os.path.join(img_folder, filename)
        temp_df.loc[num] = [index, title, num+1, link, filepath]
    return temp_df

def download_info_image(image_df,img_folder='download_img'):
    '''
    이미지를 다운로드하는 함수

    Parameter :
        image_df(pd.DataFrame) : 다운로드 할 이미지 정보가 담긴 데이터프레임
        img_folder(str) : 이미지 폴더 경로  
    '''
    if not os.path.isdir(img_folder):# 세이브폴더 존재 확인
        os.mkdir(img_folder)# 없으면 하나 만듬
    for row in image_df.iterrows():
        if not os. path.exists(row[1][3]):# 중복파일은 다운로드 X
            print("-Image Downloaded :", row[1][3])
            urllib.request.urlretrieve(row[1][2], row[1][3])
        else:
            print("-Image Not Downloaded :", row[1][3])

# Driver
# 0. 웹드라이버 옵션 설정
options = Options()
options.add_argument('--blink-settings=imagesEnabled=false') # 이미지 로딩 안함
#user_agent = "Mozilla/5.0 (Linux; Android 9; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36"
#options.add_argument('user-agent=' + user_agent) # 임의 User Agent로 설정
#options.add_argument('headless') # 헤드리스 모드로 실행
#options.add_argument('incognito') # 시크릿 모드

# 1. 웹드라이버 생성
driver = webdriver.Chrome(options=options)

# 2. URL 접속 (대한민국 구석구석 - 열린관광 : 모두의 여행 페이지)
driver.get('https://korean.visitkorea.or.kr/other/other_list.do?otdid=b55ffe10-84c3-11e8-8165-020027310001#0^All^All^All^1^10^All^Null^All^b55ffe10-84c3-11e8-8165-020027310001^All^#%EC%A0%84%EC%B2%B4^All^All^All^All')

# 3. 드라이버 화면 최대화
driver.maximize_window()

# Crawling
# 0. 필요변수 설정
starttime = time.time()
type_list = ['관광','숙박','음식']
spec_df = pd.DataFrame()
image_df = pd.DataFrame()
count_num = 0
page_num = 0

# 1. Type 반복문 실행 (관광, 숙박, 음식 3회 반복)
for t in type_list:
    action_select_type(t)
    infoType = extract_info_type(t)

# 2. Page 반복문 실행 (1~n 까지 오류날때까지 반복)
    while True:

# 3. List 반복문 실행 (0~9 까지 10회 반복)
        for i in range(10):
            breaker = action_select_site(i)
            if breaker == 0:
                break
            infoBase = extract_info_base()
            soup = action_html_parser()

            infoView = extract_info_view()
            infoBase['조회수'] = infoView

            image_temp_df = extract_info_imageurl(count_num,infoBase.get(next(iter(infoBase))))
            image_df = pd.concat([image_df, image_temp_df])
            
            action_return()

            infoDisable = extract_info_disable(soup)
            infoText = extract_info_text(soup)
            append_dict = {**infoType,**infoBase,**infoDisable,**infoText}
            spec_df = pd.concat([spec_df, pd.DataFrame(append_dict,index=[count_num])])
            count_num += 1
            print("DataCount:",count_num,"| TimePerCount:",
                  round((time.time()-starttime)/count_num,4),
                  "| Title:",infoBase.get(next(iter(infoBase))))
        if breaker == 0:# List가 도중에 끝난경우
            break

        print("END  : Type:",t,"| Page:",page_num+1)
        page_num = action_nextpage()
        print("START : Type:",t,"| Page:",page_num+1)


# Save
spec_df.to_csv("spec_table.csv") # CSV 저장
image_df.to_csv("img_table.csv") # CSV 저장

# Image
# image_df = pd.read_csv("img_table.csv")
image_df = image_df[['Title','Num','Link','Location']]
download_info_image(image_df)