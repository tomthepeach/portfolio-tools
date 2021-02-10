from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt

#Lool stole ur shit
def striptonums(string):
    return float(''.join(c for c in string if (c.isdigit() or c == ',')))

source = requests.get("https://www.metoffice.gov.uk/weather/forecast/gcnwpkvps").text

soup = BeautifulSoup(source, "lxml")

# print(soup.prettify())

stuff = soup.find("section", class_="forecast-table")

newstuff = stuff.find("div", class_="sticky-pin")
newerstuff = newstuff.find("div", class_="forecast-content-container scrollable")
dates = []
times = {}
temps = {}
rains = {}
for forecast_day in newerstuff.find_all("div", class_=["forecast-day", "forecast-day print-wide"]):
    
    #Days
    try:
        day = forecast_day.div.div.span.text
    except Exception as e:
        day = "Couldnt find day"
    dates.append(day)
    actualday = day.split()[0]
    
    #Times
    timelist = []
    try:
        table = forecast_day.find("table")
        trthing = table.thead.tr
        for thing in trthing.find_all("th"):
            timelist.append(thing.text)

    except Exception as e:
        timelist.append("Couldnt find time")
    timelist.remove("Time")
    for i in range(len(timelist)):
        newtime = timelist[i].split("\n")
        timelist[i] = newtime[1]
    for i in range(len(timelist)):
        timelist[i] = f"{actualday} {timelist[i]}"
    times[day] = timelist

    #Precipitation
    rainlist = []
    try:
        table = forecast_day.find("table")
        bodyrain = table.tbody.find("tr", class_="step-pop")
        for item in bodyrain.find_all("td"):
            rainlist.append(item.text)
    except Exception as e:
        rainlist.append("Couldnt find rain")
    for i in range(len(rainlist)):
        newrain = rainlist[i].split("\n")
        rainlist[i] = striptonums(newrain[1])
        
    rains[day] = rainlist
 

    #Temperature
    templist = []
    try:
        table = forecast_day.find("table")
        bodytemps = table.tbody.find("tr", class_="step-temp")
        for item in bodytemps.find_all("td"):
            templist.append(item.text)
    except Exception as e:
        templist.append("Couldnt find temp")
    for i in range(len(templist)):
        newtemp = templist[i].split("\n")
        templist[i] = newtemp[1]
    for i in range(len(templist)):
        newtemp = templist[i].split("°")
        templist[i] = int(newtemp[0])

    temps[day] = templist
days = []
for i in range(len(dates)):
    day = dates[i].split()
    days.append(day[0])

fulltimes = []
fulltemps = []
fullrains = []
for timelist in times.values():
    fulltimes.extend(timelist)
for templist in temps.values():
    fulltemps.extend(templist)
for rainlist in rains.values():
    fullrains.extend(rainlist)


fig, ax1 = plt.subplots()
ax1.plot(fulltimes, fulltemps, color="r")
ax1.set_xlabel("Day/Time")
ax1.set_ylabel("Temperature / Degrees C", color="r")

ax2 = ax1.twinx()
ax2.plot(fulltimes, fullrains, color="b")
ax2.set_ylabel("Precipitation Chance / %", color="b")
ax1.tick_params("x", rotation=60)
plt.show()
