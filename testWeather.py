import pyowm

owm = pyowm.OWM('74be88781b6c233e202169c47b6bf892')  # You MUST provide a valid API key

# Have a pro subscription? Then use:

observation = owm.weather_at_place("Les Sables d'Olonne")
w = observation.get_weather()
print(w.get_temperature('celsius').get("temp"))

w.get_wind()
w.get_humidity()
w.get_temperature('celsius')
