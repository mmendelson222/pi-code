import time
import terminalio
import displayio
import adafruit_imageload
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from secrets import secrets
import sys
import alarm
import board
import adafruit_sht4x

# Debug settings
fetch_data = True

# User config
METRIC = False  # set to True for metric units

EXTENDED_FORECAST = False # set to false for today.
FONT = terminalio.FONT

i2c = board.I2C()
sht = adafruit_sht4x.SHT4x(i2c)  # temp and humidity
sht.mode = adafruit_sht4x.Mode.NOHEAT_HIGHPRECISION

buttons = (board.BUTTON_A, board.BUTTON_B)# pick any two
pin_alarms = [alarm.pin.PinAlarm(pin=pin, value=False, pull=True) for pin in buttons]

# ----------------------------
# Define various assets
# ----------------------------
BACKGROUND_BMP = "/bmps/weather_bg4.bmp"
ICONS_LARGE_FILE = "/bmps/weather_icons_70px.bmp"
ICONS_SMALL_FILE = "/bmps/weather_icons_20px.bmp"
ICON_MAP = ("01", "02", "03", "04", "09", "10", "11", "13", "50")

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MONTHS = (    "January",    "February",    "March",    "April",    "May",    "June",    "July",    "August",    "September",    "October",    "November",    "December",)
#DAYS = ("Mon", "Tue", "Weds", "Thurs", "Fri", "Sat", "Sun")
#MONTHS = (    "Jan",    "Feb",    "Mar",    "Apr",    "May",    "Jun",    "Jul",    "Aug",    "Sep",    "Oct",    "Nov",    "Dec",)

magtag = MagTag()

# ----------------------------
# Backgrounnd bitmap
# ----------------------------
magtag.graphics.set_background(BACKGROUND_BMP)

# ----------------------------
# Weather icons sprite sheet
# ----------------------------
icons_large_bmp, icons_large_pal = adafruit_imageload.load(ICONS_LARGE_FILE)
icons_small_bmp, icons_small_pal = adafruit_imageload.load(ICONS_SMALL_FILE)

# /////////////////////////////////////////////////////////////////////////


def get_data_source_url(api="onecall", location=None):
    """Build and return the URL for the OpenWeather API."""
    if api.upper() == "FORECAST5":
        URL = "https://api.openweathermap.org/data/2.5/forecast?"
        URL += "q=" + location
    elif api.upper() == "ONECALL":
        URL = "https://api.openweathermap.org/data/2.5/onecall?exclude=minutely,hourly,alerts"
        URL += "&lat={}".format(location[0])
        URL += "&lon={}".format(location[1])
    else:
        raise ValueError("Unknown API type: " + api)

    return URL + "&appid=" + secrets["openweather_token"]


def get_latlon():
    """Use the Forecast5 API to determine lat/lon for given city."""
    #magtag.url = get_data_source_url(api="forecast5", location=secrets["openweather_location"])
    #magtag.json_path = ["city"]
    #raw_data = magtag.fetch()  # could have set auto_refresh=False
    #print(raw_data)
    #return raw_data["coord"]["lat"], raw_data["coord"]["lon"]

    resp = magtag.network.fetch(get_data_source_url(api="forecast5", location=secrets["openweather_location"]))
    json_data = resp.json()
    city = json_data["city"]
    return city["coord"]["lat"], city["coord"]["lon"], json_data["list"]



def get_forecast(location):
    """Use OneCall API to fetch forecast and timezone data."""
    resp = magtag.network.fetch(get_data_source_url(api="onecall", location=location))
    json_data = resp.json()
    #print(json_data)
    return json_data["daily"], json_data["current"]["dt"], json_data["timezone_offset"]


def fmt_temp(tempK):
    if METRIC:
        return "{:.0f}C".format(tempK - 273.15)
    else:
        return "{:.0f}F".format(32.0 + 1.8 * (tempK - 273.15))


def fmt_wind(speedms):
    if METRIC:
        return "{:.0f}m/s".format(speedms)
    else:
        return "{:.0f}mph".format(2.23694 * speedms)

def fmt_humidity(hum):
    return "%0.0f%%" % hum

def fmt_time(time, hour_only=False):
    H = time.tm_hour if time.tm_hour <= 12 else time.tm_hour - 12
    H = 12 if H == 0 else H
    if hour_only:
        AP = "A" if time.tm_hour < 12 else "P"
        return "{:2d}{}".format(H, AP)
    else:
        AP = "AM" if time.tm_hour < 12 else "PM"
        return "{:2d}:{:02d} {}".format(H, time.tm_min, AP)
        
def make_banner(x=0, y=0):
    """Make a single future forecast info banner group."""
    day_of_week = label.Label(FONT, text="DAY", color=0x000000)
    day_of_week.anchor_point = (0, 0.5)
    day_of_week.anchored_position = (0, 10)

    icon = displayio.TileGrid(
        icons_small_bmp,
        pixel_shader=icons_small_pal,
        x=25,
        y=0,
        width=1,
        height=1,
        tile_width=20,
        tile_height=20,
    )

    day_temp = label.Label(FONT, text="100F", color=0x000000)
    day_temp.anchor_point = (0, 0.5)
    day_temp.anchored_position = (50, 10)

    group = displayio.Group(x=x, y=y)
    group.append(day_of_week)
    group.append(icon)
    group.append(day_temp)

    return group

def update_banner_extended(banner, data):
    """Update supplied forecast banner with supplied data."""
    banner[0].text = DAYS[time.localtime(data["dt"]).tm_wday][:3].upper()
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = fmt_temp(data["temp"]["day"])

def update_banner_todayforecast(banner, data):
    banner[0].text = fmt_time(time.localtime(data["dt"]), True)
    banner[1][0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    banner[2].text = fmt_temp(data["main"]["temp"])


def update_from_sensor(temp_label, humidity_label):
    temperature, relative_humidity = sht.measurements
    if METRIC:
        temp = "{:.0f}C".format(temperature)
    else:
        temp = "{:.0f}F".format((temperature * 9/5)+32)
    temp_label.text = temp
    humidity_label.text = fmt_humidity(relative_humidity)


def update_today(data, now_dt, tz_offset=0):
    """Update today info banner."""
    now = time.localtime(now_dt + local_tz_offset)
    date = time.localtime(data["dt"])
    sunrise = time.localtime(data["sunrise"] + tz_offset)
    sunset = time.localtime(data["sunset"] + tz_offset)

    today_date.text = "{} {} {} {}".format(
        DAYS[date.tm_wday].upper(),
        MONTHS[date.tm_mon - 1].upper(),
        date.tm_mday,
        fmt_time(now)
    )
    today_icon[0] = ICON_MAP.index(data["weather"][0]["icon"][:2])
    today_morn_temp.text = fmt_temp(data["temp"]["morn"])
    today_day_temp.text = fmt_temp(data["temp"]["day"])
    today_night_temp.text = fmt_temp(data["temp"]["night"])
    today_humidity.text = fmt_humidity(data["humidity"]))
    today_wind.text = fmt_wind(data["wind_speed"])
    today_sunrise.text = fmt_time(sunrise)
    today_sunset.text = fmt_time(sunset)


def go_to_sleep(current_time):
    """Enter deep sleep for time needed."""
    # compute current time offset in seconds
    hour, minutes, seconds = time.localtime(current_time)[3:6]
    seconds_since_midnight = 60 * (hour * 60 + minutes) + seconds
    # wake up 15 minutes after midnite
    seconds_to_sleep = (24 * 60 * 60 - seconds_since_midnight) + 15 * 60
    print(
        "Sleeping for {} hours, {} minutes".format(
            seconds_to_sleep // 3600, (seconds_to_sleep // 60) % 60
        )
    )
    magtag.exit_and_deep_sleep(seconds_to_sleep)


# ===========
# U I
# ===========
today_date = label.Label(FONT, text="1234567890" * 3, color=0x000000)
today_date.anchor_point = (0, 0)
today_date.anchored_position = (15, 13)

city_name = label.Label(
    FONT, text=secrets["openweather_location"], color=0x000000
)
city_name.anchor_point = (0, 0)
city_name.anchored_position = (15, 24)

today_icon = displayio.TileGrid(
    icons_large_bmp,
    pixel_shader=icons_small_pal,
    x=10,
    y=40,
    width=1,
    height=1,
    tile_width=70,
    tile_height=70,
)

y = 50
today_morn_temp = label.Label(FONT, text="100F", color=0x000000)
today_morn_temp.anchor_point = (0, 0)
today_morn_temp.anchored_position = (105, y)

today_day_temp = label.Label(FONT, text="100F", color=0x000000)
today_day_temp.anchor_point = (0.5, 0)
today_day_temp.anchored_position = (144, y)

today_night_temp = label.Label(FONT, text="100F", color=0x000000)
today_night_temp.anchor_point = (1, 0)
today_night_temp.anchored_position = (182, y)

y += 30
today_humidity = label.Label(FONT, text="100%", color=0x000000)
today_humidity.anchor_point = (0, 0.5)
today_humidity.anchored_position = (105, y)

today_wind = label.Label(FONT, text="99mph", color=0x000000)
today_wind.anchor_point = (1, 0.5)
today_wind.anchored_position = (182, y)

y += 20
indoor_temp = label.Label(FONT, text="100F", color=0x000000)
indoor_temp.anchor_point = (0, 0.5)
indoor_temp.anchored_position = (105, y)

indoor_humidity = label.Label(FONT, text="100%", color=0x000000)
indoor_humidity.anchor_point = (1, 0.5)
indoor_humidity.anchored_position = (182, y)

today_sunrise = label.Label(FONT, text="12:12 PM", color=0x000000)
today_sunrise.anchor_point = (0, 0.5)
today_sunrise.anchored_position = (45, 117)

today_sunset = label.Label(FONT, text="12:12 PM", color=0x000000)
today_sunset.anchor_point = (0, 0.5)
today_sunset.anchored_position = (130, 117)

today_banner = displayio.Group()
today_banner.append(today_date)
today_banner.append(city_name)
today_banner.append(today_icon)
today_banner.append(today_morn_temp)
today_banner.append(today_day_temp)
today_banner.append(today_night_temp)
today_banner.append(today_humidity)
today_banner.append(today_wind)
today_banner.append(indoor_temp)
today_banner.append(indoor_humidity)
today_banner.append(today_sunrise)
today_banner.append(today_sunset)

X=210
Y=18
future_banners = []
for i in range(5):
    future_banners.append(make_banner(x=X, y=Y))
    Y += 21

magtag.splash.append(today_banner)
for future_banner in future_banners:
    magtag.splash.append(future_banner)

# ===========
#  M A I N
# ===========

if fetch_data:
    print("Getting Lat/Lon...")
    lat, long, list = get_latlon()
    print(secrets["openweather_location"])
    print(lat, long)

    print("Fetching forecast...")
    forecast_data, utc_time, local_tz_offset = get_forecast((lat, long))

    print("Updating...")
    update_today(forecast_data[0], utc_time, local_tz_offset)
    update_from_sensor(indoor_temp, indoor_humidity)
    
    if EXTENDED_FORECAST:
        for day, forecast in enumerate(forecast_data[1:6]):
            update_banner_extended(future_banners[day], forecast)
    else:
        # list all the forecasts available.
        for forecast in list:
            dt = time.localtime(forecast["dt"])
            print("dt: {} {} {} {}".format(dt.tm_mday, fmt_time(dt), forecast["dt_txt"], forecast["main"]["humidity"]))
            
        for day, forecast in enumerate(list[0:5]):
            update_banner_todayforecast(future_banners[day], forecast)

print("Refreshing...")
#time.sleep(magtag.display.time_to_refresh + 1)
magtag.display.refresh()
time.sleep(magtag.display.time_to_refresh + 1)

print("Sleeping...")
#go_to_sleep(utc_time + local_tz_offset)

# sleep until button is pressed.
alarm.exit_and_deep_sleep_until_alarms(*pin_alarms)

#  entire code will run again after deep sleep cycle
#  similar to hitting the reset button

