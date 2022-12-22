from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from pathlib import Path
from datetime import date, timedelta
import shutil
import fnmatch
import os


temp = Path.cwd().joinpath("temp", "temp20")
try:
	shutil.rmtree(temp)
except:
	pass
temp.mkdir(parents=True, exist_ok=True)
options=Options()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", str(temp))
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
options.headless = True
service = Service(str(Path.cwd().joinpath('geckodriver')))
driver = Firefox(service=service, options=options)


start = date(2020, 1, 1)
end = date(2020, 12, 31)
current = start


units = [ \
"AHMEDNAGAR", \
"AKOLA", \
"AMRAVATI CITY", \
"AMRAVATI RURAL", \
"AURANGABAD CITY", \
"AURANGABAD RURAL", \
"BEED", \
"BHANDARA", \
"BRIHAN MUMBAI CITY", \
"BULDHANA", \
"CHANDRAPUR", \
"DHULE", \
"GADCHIROLI", \
"GONDIA", \
"HINGOLI", \
"JALGAON", \
"JALNA", \
"KOLHAPUR", \
"LATUR", \
"Mira-Bhayandar, Vasai-Virar Police Commissioner", \
"NAGPUR CITY", \
"NAGPUR RURAL", \
"NANDED", \
"NANDURBAR", \
"NASHIK CITY", \
"NASHIK RURAL", \
"NAVI MUMBAI", \
"OSMANABAD", \
"PALGHAR", \
"PARBHANI", \
"PIMPRI-CHINCHWAD", \
"PUNE CITY", \
"PUNE RURAL", \
"RAIGAD", \
"RAILWAY AURANGABAD", \
"RAILWAY MUMBAI", \
"RAILWAY NAGPUR", \
"RAILWAY PUNE", \
"RATNAGIRI", \
"SANGLI", \
"SATARA", \
"SINDHUDURG", \
"SOLAPUR CITY", \
"SOLAPUR RURAL", \
"THANE CITY", \
"THANE RURAL", \
"WARDHA", \
"WASHIM", \
"YAVATMAL" \
]


# returns fromdate and todate
def calc_date():
	global current
	if current.day < 10:
		fromdate = "0" + str(current.day)
	else:
		fromdate = str(current.day)
	if current.month < 10:
		fromdate+= "0"+ str(current.month)
	else:
		fromdate+= str(current.month)
	fromdate+= str(current.year)
	
	if current.month == 12:
		current = current.replace(month=1, year=current.year+1)
	else:
		current = current.replace(month=current.month+1)
	
	todate = str((current-timedelta(days=1)).day) 
	if olddate.month < 10:
		todate+= "0"+str(olddate.month)
	else:
		todate+=str(olddate.month)
	todate+=str(olddate.year)

	return fromdate, todate


# loads page, refreshes, fills information and clicks search
def load_page(fromdate, todate, unit):
	while(True):
		try:
			driver.get("https://citizen.mahapolice.gov.in/Citizen/MH/PublishedFIRs.aspx")
			driver.refresh()
			frombtn = driver.find_element(By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$txtDateOfRegistrationFrom'][@id='ContentPlaceHolder1_txtDateOfRegistrationFrom']")
			frombtn.send_keys(Keys.ARROW_LEFT*10)
			frombtn.send_keys(fromdate)
			tobtn = driver.find_element(By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$txtDateOfRegistrationTo'][@id='ContentPlaceHolder1_txtDateOfRegistrationTo']")
			tobtn.send_keys(Keys.ARROW_LEFT*10)
			tobtn.send_keys(todate)
			select_unit = Select(driver.find_element(By.XPATH, "//select[@name='ctl00$ContentPlaceHolder1$ddlDistrict'][@id='ContentPlaceHolder1_ddlDistrict']"))
			select_unit.select_by_visible_text(unit)
			driver.find_element(By.XPATH, "//input[@name='ctl00$ContentPlaceHolder1$btnSearch'][@value='Search']").click()
			select_page_capacity = Select(driver.find_element(By.XPATH, "//select[@name='ctl00$ContentPlaceHolder1$ucRecordView$ddlPageSize'][@id='ContentPlaceHolder1_ucRecordView_ddlPageSize']"))
			select_page_capacity.select_by_visible_text("50")
			break
		except:
			continue

def check_server_error():
	errorpage = False
	try:
		errorpage = driver.find_element(By.XPATH, "//*[contains(text(), 'Source Error:')]")
	except:
		pass

	return bool(errorpage)

def move_files(olddate, unit):
		target_dir = Path.cwd().joinpath("data", str(olddate.year), olddate.strftime("%B"), unit)
		target_dir.mkdir(parents=True, exist_ok=True)
		file_names = os.listdir(temp)
		for file_name in file_names:
  		  shutil.move(os.path.join(temp, file_name), os.path.join(target_dir,file_name))

while(current <= end):

	olddate = current
	fromdate, todate = calc_date()

	print(f'\n\n{fromdate} {todate}\n')

	for unit in units:
		print(unit)

		count = len(fnmatch.filter(os.listdir(temp), '*.*'))
		load_page(fromdate, todate, unit)

		i=1
		while(True):
			try:
				if i > 1:
					time.sleep(2)
					if(i%10==1):
						nav_button = driver.find_elements(By.LINK_TEXT, "...")[-1]
						driver.execute_script("arguments[0].click();", nav_button)
					else:
						nav_button = driver.find_element(By.LINK_TEXT, str(i))
						driver.execute_script("arguments[0].click();", nav_button)
					
				for j in range(50):
					try:
						print(f"{olddate.strftime('%B')} {olddate.year} {unit} Page {i} PDF no. {j}")
						for k in range(2):
							dl_button = driver.find_element(By.XPATH, "//input[@id='ContentPlaceHolder1_gdvDeadBody_btnDownload_"+str(j)+"']")
							driver.execute_script("arguments[0].click();", dl_button)
							time.sleep(2)
							if len(fnmatch.filter(os.listdir(temp), '*.*')) > count:
								count+=1
								break
					except Exception as e:
						print("breaking within page\t" + str(e))
						break
				
				server_error = check_server_error()
				if server_error:
					print("breaking in server error")
					move_files(olddate, unit)
					break
					
				move_files(olddate, unit) #moving every page
			except Exception as e:
				print("breaking from shifting pages\t" + str(e))
				break

			i+=1
		
		move_files(olddate, unit) #move any remaining files

driver.quit()