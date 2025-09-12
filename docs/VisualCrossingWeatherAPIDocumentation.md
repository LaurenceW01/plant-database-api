Example call to get weather for my location using lat, long
https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/29.827119%2C%20-95.472232?unitGroup=us&key=API_KEY&contentType=json

Response JSON
{
 "queryCost": 1,
 "latitude": 29.827119,
 "longitude": -95.472232,
 "resolvedAddress": "29.827119, -95.472232",
 "address": "29.827119, -95.472232",
 "timezone": "America/Chicago",
 "tzoffset": -5,
 "description": "Similar temperatures continuing with no rain expected.",
 "days": [
  {
   "datetime": "2025-09-12",
   "datetimeEpoch": 1757653200,
   "tempmax": 94.9,
   "tempmin": 75.3,
   "temp": 83.9,
   "feelslikemax": 98.2,
   "feelslikemin": 75.3,
   "feelslike": 86.4,
   "dew": 69.8,
   "humidity": 65.6,
   "precip": 0,
   "precipprob": 2,
   "precipcover": 0,
   "preciptype": null,
   "snow": 0,
   "snowdepth": 0,
   "windgust": 12.8,
   "windspeed": 8.1,
   "winddir": 114,
   "pressure": 1018.1,
   "cloudcover": 17.2,
   "visibility": 9.9,
   "solarradiation": 262.4,
   "solarenergy": 22.5,
   "uvindex": 9,
   "severerisk": 30,
   "sunrise": "07:05:06",
   "sunriseEpoch": 1757678706,
   "sunset": "19:30:35",
   "sunsetEpoch": 1757723435,
   "moonphase": 0.68,
   "conditions": "Clear",
   "description": "Clear conditions throughout the day.",
   "icon": "clear-day",
   "stations": [
    "KHOU",
    "KSGR",
    "E6288",
    "KAXH",
    "KIAH",
    "KDWH",
    "KMCJ"
   ],
   "source": "comb",
   "hours": [
    {
     "datetime": "04:00:00",
     "datetimeEpoch": 1757667600,
     "temp": 75.7,
     "feelslike": 75.7,
     "humidity": 87.24,
     "dew": 71.6,
     "precip": 0,
     "precipprob": 0,
     "snow": 0,
     "snowdepth": 0,
     "preciptype": null,
     "windgust": 3.4,
     "windspeed": 2.5,
     "winddir": 59,
     "pressure": 1018.4,
     "visibility": 9.7,
     "cloudcover": 40.2,
     "solarradiation": 0,
     "solarenergy": 0,
     "uvindex": 0,
     "severerisk": 30,
     "conditions": "Partially cloudy",
     "icon": "partly-cloudy-night",
     "stations": [
      "KHOU",
      "KSGR",
      "E6288",
      "KIAH",
      "KDWH",
      "KMCJ"
     ],
     "source": "obs",
     "datetimeInstance": "2025-09-12T09:00:00.000Z"
    },
    {
     "datetime": "05:00:00",
     "datetimeEpoch": 1757671200,
     "temp": 76.2,
     "feelslike": 76.2,
     "humidity": 85.75,
     "dew": 71.6,
     "precip": 0,
     "precipprob": 0,
     "snow": 0,
     "snowdepth": 0,
     "preciptype": null,
     "windgust": 3.4,
     "windspeed": 4,
     "winddir": 59,
     "pressure": 1018.4,
     "visibility": 9.8,
     "cloudcover": 24,
     "solarradiation": 0,
     "solarenergy": 0,
     "uvindex": 0,
     "severerisk": 30,
     "conditions": "Partially cloudy",
     "icon": "partly-cloudy-night",
     "stations": [
      "KHOU",
      "KSGR",
      "E6288",
      "KIAH",
      "KDWH",
      "KMCJ"
     ],
     "source": "obs",
     "datetimeInstance": "2025-09-12T10:00:00.000Z"
    }
   ],
   "precipsum": 0,
   "precipsumnormal": 0,
   "snowsum": 0,
   "datetimeInstance": "2025-09-12T05:00:00.000Z"
  }
 ],
 "alerts": [
  {
   "event": "Air Quality Alert",
   "headline": "Air Quality Alert issued September 11 at 2:54PM CDT by NWS Houston/Galveston TX",
   "ends": "2025-09-12T19:00:00",
   "endsEpoch": 1757721600,
   "onset": "2025-09-11T14:54:00",
   "onsetEpoch": 1757620440,
   "id": "urn:oid:2.49.0.1.840.0.5fd040f3cd4edbea42d3d91877adc9e2c9de80fe.001.1",
   "language": "en",
   "link": "http://www.weather.gov",
   "description": "AQAHGX\n\nThe Texas Commission on Environmental Quality (TCEQ) has issued an\nOzone Action Day for the Houston, Galveston, and Brazoria area for\nFriday, September 12, 2025.\n\nAtmospheric conditions are expected to be favorable for producing\nhigh levels of ozone pollution in the Houston, Galveston, and\nsurrounding areas on Friday. You can help prevent ozone pollution by\nsharing a ride, walking, riding a bicycle, taking your lunch to work,\navoiding drive through lanes, conserving energy and keeping your vehicle\nproperly tuned.\n\nFor more information on ozone:\nOzone: The Facts www.tceq.texas.gov/airquality/monops/ozonefacts.html\nEPA AirNow: www.airnow.gov/?city=Houston&state=TX&country=USA\nTake Care of Texas:\nwww.takecareoftexas.org/conservation-tips/keep-our-air-clean\n"
  }
 ],
 "stations": {
  "KHOU": {
   "distance": 28754,
   "latitude": 29.63,
   "longitude": -95.28,
   "useCount": 0,
   "id": "KHOU",
   "name": "KHOU",
   "quality": 100,
   "contribution": 0
  },
  "KSGR": {
   "distance": 29344,
   "latitude": 29.62,
   "longitude": -95.66,
   "useCount": 0,
   "id": "KSGR",
   "name": "KSGR",
   "quality": 100,
   "contribution": 0
  },
  "TNST2": {
   "distance": 5862,
   "latitude": 29.783,
   "longitude": -95.44,
   "useCount": 0,
   "id": "TNST2",
   "name": "1000 Houston Transtar TX US HCFCD",
   "quality": 0,
   "contribution": 0
  },
  "E6288": {
   "distance": 7760,
   "latitude": 29.766,
   "longitude": -95.51,
   "useCount": 0,
   "id": "E6288",
   "name": "EW6288 Houston TX US",
   "quality": 0,
   "contribution": 0
  },
  "KAXH": {
   "distance": 35310,
   "latitude": 29.51,
   "longitude": -95.48,
   "useCount": 0,
   "id": "KAXH",
   "name": "KAXH",
   "quality": 98,
   "contribution": 0
  },
  "KIAH": {
   "distance": 19802,
   "latitude": 29.97,
   "longitude": -95.35,
   "useCount": 0,
   "id": "KIAH",
   "name": "KIAH",
   "quality": 100,
   "contribution": 0
  },
  "F3809": {
   "distance": 7243,
   "latitude": 29.796,
   "longitude": -95.406,
   "useCount": 0,
   "id": "F3809",
   "name": "FW3809 Houston TX US",
   "quality": 0,
   "contribution": 0
  },
  "KDWH": {
   "distance": 28059,
   "latitude": 30.07,
   "longitude": -95.55,
   "useCount": 0,
   "id": "KDWH",
   "name": "KDWH",
   "quality": 100,
   "contribution": 0
  },
  "AT039": {
   "distance": 6438,
   "latitude": 29.818,
   "longitude": -95.538,
   "useCount": 0,
   "id": "AT039",
   "name": "W5HRH Houston TX US",
   "quality": 0,
   "contribution": 0
  },
  "KMCJ": {
   "distance": 14788,
   "latitude": 29.71,
   "longitude": -95.4,
   "useCount": 0,
   "id": "KMCJ",
   "name": "KMCJ",
   "quality": 99,
   "contribution": 0
  }
 },
 "currentConditions": {
  "datetime": "08:31:00",
  "datetimeEpoch": 1757683860,
  "temp": 79.2,
  "feelslike": 79.2,
  "humidity": 85.1,
  "dew": 74.3,
  "precip": 0,
  "precipprob": 0,
  "snow": 0,
  "snowdepth": 0,
  "preciptype": null,
  "windgust": 3.8,
  "windspeed": 0.8,
  "winddir": 32,
  "pressure": 1020,
  "visibility": 8.7,
  "cloudcover": 0,
  "solarradiation": 4,
  "solarenergy": 0,
  "uvindex": 0,
  "conditions": "Clear",
  "icon": "clear-day",
  "stations": [
   "TNST2",
   "F3809",
   "AT039",
   "KMCJ"
  ],
  "source": "obs",
  "sunrise": "07:05:06",
  "sunriseEpoch": 1757678706,
  "sunset": "19:30:35",
  "sunsetEpoch": 1757723435,
  "moonphase": 0.68
 },
 "isProcessed": true
}

API Documentation
Introduction
The Timeline Weather API is a versatile and powerful tool for retrieving weather data globally. You can request data over any time window including windows that span the past, present, and future. The API will take care of the combining historical observations, current 15-day forecasts, and statistical weather forecasts to create a single, consolidated dataset via a single API call. By leveraging advanced data sources, this API offers superior features like:

GET Request Simplicity: All queries use straightforward HTTP GET requests.
Timeline-Based Queries: Retrieve data for any date range, including past, present, and future.
Location-Based Flexibility: Use addresses, latitude/longitude, or ZIP codes for pinpoint weather data.
Comprehensive Coverage: Includes hourly, daily, and statistical weather details, as well as alerts and astronomical data.
Customizable Output: Get data in JSON or CSV format.
Dynamic Periods: Use dynamic keywords like last30days, today, or yesterday for queries.
The Timeline API offers complete, global weather data coverage both geographically and chronologically. It always picks the best available data sources to answer any weather API query. These sources include:

Current weather conditions
Daily historical, forecast and statistical forecast data (depending on dates requested)
Hourly historical observations and 15-day forecast
Weather alerts
Astronomical observations including sunrise, sunset and moon phase.
Result data is provided in a common JSON format allowing you to ignore to complex underlying data sources and focus entirely on your weather data use case. You can also request the result in CSV text format if you prefer.

Generate Code with AI
Our new AI-powered code generator instantly creates working code tailored to your requirements. Try the AI code generator tool today and start building faster.

Latest features and recent changes
We continue to invest heavily in enhancing the Timeline Weather API and expanding its underlying data sources. Recent improvements include:

Radar-Based Precipitation Estimates
You can now include radar-derived precipitation data directly in your datasets, providing improved estimates of precipitation amount and intensity.
New Programmatic Dataset APIs
New APIs have been added to enable programmatic submission, modification, and download of stored datasets, streamlining automated workflows.
Sub-Hourly Data Support
The Timeline Weather API now supports sub-hourly data with minute-level granularity, offering more precise short-term forecasts and observations.
For a full list of additions to the Timeline Weather API, please see the changelog.

Timeline Weather API Query Builder
The Weather Query Builder page includes a full, interactive query builder so you can create queries and see the live results directly in your browser.

Creating a weather API request
Base URL
https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/
Endpoints
The possible endpoints of the Timeline Weather API requests are as follows:

/timeline/[location] – forecast queries.
/timeline/[location]/[date1]/[date2] – queries for a specific date range.
Main Format of the URL
All requests to the Timeline Weather API use the following the form:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/[location]/[date1]/[date2]?key=YOUR_API_KEY
Request Parameters
Main Parameters (Path Parameters)
location (required) – is the address, partial address or latitude,longitude location for which to retrieve weather data. You can also use US ZIP Codes. If you would like to submit multiple locations in the same request, consider our Multiple Location Timeline Weather API.

date1 (optional) – is the start date for which to retrieve weather data. If a date2 value is also given, then it represents the first date for which to retrieve weather data. If no date2 is specified then weather data for a single day is retrieved, and that date is specified in date1. All dates and times are in local time of the location specified. Dates should be in the format yyyy-MM-dd. For example 2020-10-19 for October 19th, 2020 or 2017-02-03 for February 3rd, 2017.

Instead of an exact date, you can specify a dynamic date period. See below for more details. You may also supply the in “UNIX time”. In this case provide the number of seconds since 1st January 1970 UTC. For example 1612137600 for Midnight on 1st February 2021.

You can also request the information for a specific time for a single date by including time into the date1 field using the format yyyy-MM-ddTHH:mm:ss. For example 2020-10-19T13:00:00.

The results are returned in the ‘currentConditions’ field and are truncated to the hour requested (i.e. 2020-10-19T13:59:00 will return data at 2020-10-19T13:00:00).

date2 (optional) – is the end date for which to retrieve weather data. This value may only be used when a date1 value is given. When both date1 and date2 values are given, the query is inclusive of date2 and the weather data request period will end on midnight of the date2 value. All dates and times are in local time of the specified location and should be in the format yyyy-MM-dd.

When no date1 or date2 is specified, the request will retrieve the forecast at the requested location for the next 15 days.

Additional Parameters (QueryParameters)
The following are specified as HTTP query parameters (they may also be passed in a POST query).

key (required) – your API key. Sign up for a free account using our Weather Data Services page.

unitGroup (optional) – The system of units used for the output data.
Supported values are us, uk, metric, and base. See Unit groups and measurement units for more information. Defaults to US system of units.

lang (optional) – Sets the language of the translatable parts of the output such as the conditions field. Available languages include: ar (Arabic), bg (Bulgiarian), cs (Czech), da (Danish), de (German), el (Greek Modern), en (English), es (Spanish) ), fa (Farsi), fi (Finnish), fr (French), he Hebrew), hu, (Hungarian), it (Italian), ja (Japanese), ko (Korean), nl (Dutch), pl (Polish), pt (Portuguese), ru (Russian), sk (Slovakian), sr (Serbian), sv (Swedish), tr (Turkish), uk (Ukranian), vi (Vietnamese) and zh (Chinese). In addition passing in ‘id’ will result in the raw descriptor IDs.See How to create or modify language files for more information on how to help add additional languages.

include (optional) – Specifies the sections you would like to include in the result data. This allows you to reduce query cost and latency. Specify this as a comma separated list. For example: &include=obs,fcst to include the historical observations and forecast data. The options are:

days – daily data
hours – hourly data
minutes – minutely data (beta). See Requesting sub-hourly data in the Timeline Weather API. 
alerts – weather alerts
current – current conditions or conditions at requested time.
events – historical events such as a hail, tornadoes, wind damage and earthquakes (not enabled by default)
obs – historical observations from weather stations
remote – historical observations from remote source such as satellite or radar
fcst – forecast based on 16 day models.
stats – historical statistical normals and daily statistical forecast
statsfcst – use the full statistical forecast information for dates in the future beyond the current model forecast. Permits hourly statistical forecast.
elements (optional) – Specifies the specific weather elements you would like to include in the response as a comma separated list. For example, &elements=tempmax,tempmin,temp will request the only the tempmax, tempmin and temp response elements. For the full list of available elements, see the response below.

options (optional) – Specifies additional options on the requests to either indicate the type of data or format of the output. Supported values include:

nonulls – remove all null values from the JSON response
noheaders – removes the header row from the CSV response
contentType (optional) – indicates the output format for the API. By default the output is formated in JSON. You can also set contentType=csv to retrieve CSV formatted data.Note that CSV format does not support the full JSON output due to the format limitations. You must use the include parameter to indicate which section you would like to retrieve. CSV include parameters support are days, hours, alerts, events and current.

iconSet (optional) – used to choose which icons IDs are populated. For more information see Defining the icon set parameter in the Weather API.

timezone (optional) – specifies the timezone of the input and result dates and times. When not specified, all date times are considered local times. If you would like to specify that all dates are entered as UTC dates and times, use timezone=Z parameter.

maxDistance (optional) The maximum distance in meters used to search for local weather stations ( By default, 50 miles or approximately 80km (80,467m). This setting is combined with the maxStations parameter to find local weather stations.

maxStations (optional) The maximum number of weather stations used to calculate a weather record (default 3). Closer weather stations are weighted significantly more heavily than farther stations.

elevationDifference (optional) The maximum elevation difference in meters between the requested location and weather stations. Any weather station that is either lower or higher than more than this setting will be excluded. Default is turned off.

locationNames (optional) provides alternative name for the location requested. This is typically used by users who need to be able to join the API results back to a dataset. For example, you may pass a store database ID in this parameter so that you can populate the weather forecast for that store.

forecastBasisDate (optional, requires historical forecast license) – specifies the date when the weather forecast model was run. For example, if you specify 2021-06-01, then the data from 2021-06-01 to 2021-06-15 will use the weather forecast produced on June 1st, 2021. For more information see How to query weather forecasts from the past.

forecastBasisDay (optional, requires historical forecast license) – specifies the forecast day for the date1 parameter above. For example, if you specify the start date as 2021-06-05 and a forecastBasisDay value of 5, then the value for 2021-06-06 will be the 5th day forecast (i.e. it will be based on the weather forecast produced five days earlier (2021-06-01). You can use this parameter to quickly find the forecast that was predicted for a particular day on multiple days (for example the 5, 3 and 1 day forecast). For more information see How to query weather forecasts from the past.

Degree days parameters (Query Parameters)
degreeDayTempFix – The temperature at which to start the degree day season if no season start and end dates are specified. For example, if the fix temperature is 32F (OC), then the cumulative degree days will reset to zero on the last 32F temperature of the winter. This defines the growing season for growing degree days.

degreeDayStartDate – Fixes the start of the degree day season based on fixed dates of the format yyyy-M-d (eg 1990-3-1 for 1st March). Default=not specified.

degreeDayTempMaxThreshold – Defines the maximum temperature that is considered for the calculation. Any temperature above this temperature will be set to the maximum threshold temperature. Default value=not set.

degreeDayTempBase – The degree day base temperature. Default value is set to 10C/50F

degreeDayInverse – Calculate the inverse degree days so colder temperatures contribute more degree days. Used for heating degree days. Default=false.

degreeDayMethod (beta) – The method used for calculating the degree days. Values include average, sine, doublesine, triangle and doubletriangle. Default value is set to average.

Request Examples
Forecast Request Example
The following will retrieve the weather forecast for London, United Kingdom for the next 15 days, starting at midnight at the start of the current day (local time of the requested location).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK?key=YOUR_API_KEY
Forecast Request Example using longitude and latitude
You may also pass the location as a “latitude,longitude” value. For example: 38.9697,-77.385

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/38.9697,-77.385?key=YOUR_API_KEY
Date Range Request Example
The following will retrieve the weather data for London, UK from October 1st, 2020 to December 31st, 2020 (inclusive).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/2020-10-01/2020-12-31?key=YOUR_API_KEY
Assuming the current date is November 1st, 2020, the result will include historical observations from October 1st to 31st, then 15 days of weather forecast and finally the remaining days will include the statistical forecast based on processing years of historical observations.

Date Range Request Example using UNIX Time (Epoch Time)
The following shows the same query using UNIX format of seconds since the 1970 UNIX time epoch. Note that these times are seconds in the UTC (GMT/Z) time zone.

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/1601510400/1609372800?key=YOUR_API_KEY
Specific Time Request Example
The following will retrieve the weather data for London, UK for the 15th December 2020 and will request the current conditions property be populated using the conditions at 13:00 local time (1pm local time).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/2020-12-15T13:00:00?key=YOUR_API_KEY
The above example will include the daily and hourly detail for the day of the current conditions (2020-12-15 in this case). This query cost will therefore be 24. If you only need the specific time data, and don’t need the hourly detail, you can reduce the query costing using the include parameter:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/2020-12-15T13:00:00?key=YOUR_API_KEY&include=current
This query cost will be one.

Dynamic period Request Example
Rather the specify and date range, you can also specify and dynamic period. A request based on a dynamic period will automatically adjust based on the period. In this example, we will use the dynamic period value “last30days” to retrieve data for the most recent 30 days.

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?key=YOUR_API_KEY
Other dynamic period values include “today”, “yesterday”, and “lastyear”. For a complete list of options and additional example, please see the dynamic period article.

Using elements list and options parameter to request only daily with limited elements
By default both daily and hourly data is included in the response along with all the response weather data elements (see below). To reduce the size of the result JSON for lower query cost, reduced network transfer and faster client processing, the options and elements parameters may be used.

This example requests only the daily data:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?key=YOUR_API_KEY
This example requests the daily data with only temperature elements:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?key=YOUR_API_KEY&include=days&elements=tempmax,tempmin,temp
Degree day elements list example
The following includes the daily ‘degree days’ information for the requested location and date range (in this case the last 30 days).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?
unitGroup=us&key=YOUR_API_KEY&include=days&elements=datetime,tempmax,tempmin,degreedays,accdegreedays&degreeDayTempMaxThreshold=86&degreeDayTempBase=50
For more information on our growing, cooling and heating degree day options, please see our degree day page.

Industry elements
The Timeline API can be extended to include advanced agriculture, horticulture and energy elements. These include evapotranspiration, soil temperature & moisture, advanced solar radiation and higher altitude wind speeds and directions.

To include these advanced industry elements, please see our Agriculture and Horticulture and Wind and Solar Energy pages.

Weather API Response Structure
Typical JSON response format
All Timeline Weather API requests return response JSON in the same format. Here is an example for Reston, VA on 11/12/2020:

{
    "latitude" : 38.9697,
    "longitude" : -77.385,
    "resolvedAddress" : "Reston, VA, United States",
    "address" : " Reston,VA",
    "timezone" : "America/New_York",
    "tzoffset" : -5,
    "description":"Cooling down with a chance of rain on Friday.",
    "days" : [{ //array of days of weather data objects
        "datetime":"2020-11-12",
        "datetimeEpoch":1605157200,
        "temp" : 59.6,
        "feelslike" : 59.6,
        ...
        "stations" : {
        },
        "source" : "obs",
        "hours" : [{  //array of hours of weather data objects
            "datetime" : "01:00:00",
            ...
        },...]
    },...],
    "alerts" : [{
            "event" : "Flash Flood Watch",
            "description" : "...",
            ...
        }
    ],
    "currentConditions" : {
        "datetime" : "2020-11-11T22:48:35",
        "datetimeEpoch" : 160515291500,
        "temp" : 67.9,
        ...
    }
}
The response starts with a set of properties describing the location and request including the specific location requested, the resolved address, the latitude and longitude, a text based time zone and a time zone offset in hours. Note that the time zone offset can change within a dataset (based on daylight savings). If this occurs, the a tzoffset property will be found in the day, hour or current conditions weather data object.

The days array is an array of weather data objects for each day requested.

Within each day may be an hours array for the hourly information. Statistical forecast days will not include an hourly array. Typically the hours array will be length 24 but day light savings may cause the array to be 23 or 25 hours long.

If the request includes the current date, the current conditions and any weather alerts available for the location will be included.

Response Elements
Response weather data elements
cloudcover – how much of the sky is covered in cloud ranging from 0-100%

conditions – textual representation of the weather conditions. See Weather Data Conditions.

description – longer text descriptions suitable for displaying in weather displays. The descriptions combine the main features of the weather for the day such as precipitation or amount of cloud cover. Daily descriptions are provided for historical and forecast days. When the timeline request includes the model forecast period, a seven day outlook description is provided at the root response level.

datetime – ISO 8601 formatted date, time or datetime value indicating the date and time of the weather data in the local time zone of the requested location. See Dates and Times in the Weather API for more information.

datetimeEpoch – number of seconds since 1st January 1970 in UTC time

tzoffset – the time zone offset in hours. This will only occur in the data object if it is different from the global time zone offset.

dew – dew point temperature

feelslike – what the temperature feels like accounting for heat index or wind chill. Daily values are average values (mean) for the day.

feelslikemax (day only) – maximum feels like temperature at the location.

feelslikemin (day only) – minimum feels like temperature at the location.

hours – array of hourly weather data objects. This is a child of each of the daily weather object when hours are selected.

humidity – relative humidity in %

icon – a fixed, machine readable summary that can be used to display an icon

moonphase –  represents the fractional portion through the current moon lunation cycle ranging from 0 (the new moon) to 0.5 (the full moon) and back to 1 (the next new moon). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

normal – array of normal weather data values – Each weather data normal is an array of three values representing, in order, the minimum value over the statistical period, the mean value, and the maximum value over the statistical period.

offsetseconds (hourly only) – time zone offset for this weather data object in seconds – This value may change for a location based on daylight saving time observation.

precip – the amount of liquid precipitation that fell or is predicted to fall in the period. This includes the liquid-equivalent amount of any frozen precipitation such as snow or ice.

precipremote – radar estimated precipitation amount. See How to Include Weather Radar Data in Weather Datasets for more information.

precipcover (days only) – the proportion of hours where there was non-zero precipitation

precipprob (forecast only) – the likelihood of measurable precipitation ranging from 0% to 100%

preciptype – an array indicating the type(s) of precipitation expected or that occurred. Possible values include rain, snow, freezingrain and ice.

reflectivity – (minutes only) estimates of the radar-based reflectivity values indicating precipitation intensity. See How to Include Weather Radar Data in Weather Datasets for more information.

pressure – the sea level atmospheric or barometric pressure in millibars (or hectopascals)

snow – the amount of snow that fell or is predicted to fall

snowdepth – the depth of snow on the ground

source –  the type of weather data used for this weather object. – Values include historical observation (“obs”), forecast (“fcst”), historical forecast (“histfcst”) or statistical forecast (“stats”). If multiple types are used in the same day, “comb” is used. Today a combination of historical observations and forecast data.

stations (historical only) – the weather stations used when collecting an historical observation record

sunrise (day only) – The formatted time of the sunrise (For example “2022-05-23T05:50:40”). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

sunriseEpoch – sunrise time specified as number of seconds since 1st January 1970 in UTC time

sunset – The formatted time of the sunset (For example “2022-05-23T20:22:29”). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

sunsetEpoch – sunset time specified as number of seconds since 1st January 1970 in UTC time

moonrise (day only, optional) – The formatted time of the moonrise (For example “2022-05-23T02:38:10”). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

moonriseEpoch (day only, optional) – moonrise time specified as number of seconds since 1st January 1970 in UTC time

moonset (day only, optional) – The formatted time of the moonset (For example “2022-05-23T13:40:07”)

moonsetEpoch (day only, optional) – moonset time specified as number of seconds since 1st January 1970 in UTC time

temp – temperature at the location. Daily values are average values (mean) for the day.

tempmax (day only) – maximum temperature at the location.

tempmin (day only) – minimum temperature at the location.

uvindex – a value between 0 and 10 indicating the level of ultra violet (UV) exposure for that hour or day. 10 represents high level of exposure, and 0 represents no exposure. The UV index is calculated based on amount of short wave solar radiation which in turn is a level the cloudiness, type of cloud, time of day, time of year and location altitude. Daily values represent the maximum value of the hourly values.

uvindex2 (optional, 5 day forecast only) – an alternative UV index element that uses the algorithms and models used by the US National Weather Service. In order to maintain backwards compatibility, this UV index element is deployed as a new, optional element ‘uvindex2’ and may be requested using the elements parameter.

visibility – distance at which distant objects are visible

winddir – direction from which the wind is blowing

windgust – instantaneous wind speed at a location – May be empty if it is not significantly higher than the wind speed. Daily values are the maximum hourly value for the day.

windspeed – the sustained wind speed measured as the average windspeed that occurs during the preceding one to two minutes. Daily values are the maximum hourly value for the day.

windspeedmax (day only, optional)– maximum wind speed over the day.

windspeedmean (day only , optional ) – average (mean) wind speed over the day.

windspeedmin (day only , optional ) – minimum wind speed over the day.

solarradiation – (W/m2) the solar radiation power at the instantaneous moment of the observation (or forecast prediction). See the full solar radiation data documentation and Wind and Solar Energy pages .

solarenergy – (MJ /m2 ) indicates the total energy from the sun that builds up over an hour or day. See the full solar radiation data documentation and Wind and Solar Energy pages .

severerisk (forecast only) – a value between 0 and 100 representing the risk of convective storms (e.g. thunderstorms, hail and tornadoes). Severe risk is a scaled measure that combines a variety of other fields such as the convective available potential energy (CAPE) and convective inhibition (CIN), predicted rain and wind. Typically, a severe risk value less than 30 indicates a low risk, between 30 and 70 a moderate risk and above 70 a high risk.

cape (forecast only) – convective available potential energy. This is a numbering indicating amount of energy available to produce thunderstorms. A higher values indicates a more unstable atmosphere capable of creating stronger storms. Values lower than 1000 J/kg indicate generally low instability, between 1000-2500 J/kg medium instability and 2500-4000 J/kg high instability. Values greater than 4000 J/kg indicating an extremely unstable atmosphere.

cin (forecast only) – convective inhibition. A number representing the level of atmospheric tendency to prevent instability and therefore prevent thunderstorms.

degreedays (day only) – optional elements indicating the number of degree days for this date. See the degree days API for more information on degree days. To turn degree days and degree day accumulation on, use the elements parameter. For example, elements=datetime,tempmax,tempmin,degreedays,accdegreedays.

To convert existing Dark Sky API parameters to the Timeline Weather API, see How to replace the Dark Sky API with the Timeline Weather API.

Location and station elements
The following are available in the JSON response type to provide information about the requested location:

queryCost – The record cost of this query. See what is a record for more information.

latitude,longitude – the latitude and longitude of the requested location. This is provided in decimal degrees.

resolvedAddress – if the requested location was made by address, the address that is found using our internal geocoding engine.

address – the requested location text from the request.

timezone – the timezone of the location. See Date and Times in the Weather API for more information.

tzoffset – the timezone offset from UTC time for the first record of the data. This may change throughout the dataset if there is a daylight savings change during the requested date range.

elevation (optional) – the elevation of the requested location. This is an optional element requested by including the elements parameter: (see Adding and Removing Elements).

HTTP Response Code and Error Handling
The API communicates error codes through the HTTP response code. In addition, the body the response will normally include additional error information indicating the cause of the error. The possible HTTP response status codes include:

200 OK – a successfully processed request

400 BAD_REQUEST – The format of the API is incorrect or an invalid parameter or combination of parameters was supplied

401 UNAUTHORIZED – There is a problem with the API key, account or subscription. May also be returned if a feature is requested for which the account does not have access to.

404 NOT_FOUND – The request cannot be matched to any valid API request endpoint structure.

429 TOO_MANY_REQUESTS – The account has exceeded their assigned limits. See What is the cause of “Maximum concurrent jobs has been exceeded”, HTTP response 429

500 INTERNAL_SERVER_ERROR – A general error has occurred processing the request.

For general information on debugging API queries, please see: How to debug problems when running weather API queries in code

Accessing the Timelime Weather API using the OpenAPI Description
The OpenAPI Initiative standardizes the description of APIs such as the Visual Crossing Weather API. If you are using a tool that supports the OpenAPI standard or Swagger, you can more easily use our API by importing the the specification document below.

https://www.visualcrossing.com/weather/specs/visualcrossing-weather-api-openapi.json
https://www.visualcrossing.com/weather/specs/visualcrossing-weather-api-openapi.yaml
https://www.visualcrossing.com/weather/specs/visualcrossing-weather-api-swagger.json
Questions or need help?
If you have a question or need help, please post on our actively monitored forum for the fastest replies. You can also contact us via our support site

Introduction
The Timeline Weather API is a versatile and powerful tool for retrieving weather data globally. You can request data over any time window including windows that span the past, present, and future. The API will take care of the combining historical observations, current 15-day forecasts, and statistical weather forecasts to create a single, consolidated dataset via a single API call. By leveraging advanced data sources, this API offers superior features like:

The Timeline API offers complete, global weather data coverage both geographically and chronologically. It always picks the best available data sources to answer any weather API query. These sources include:

Result data is provided in a common JSON format allowing you to ignore to complex underlying data sources and focus entirely on your weather data use case. You can also request the result in CSV text format if you prefer.

Latest features and recent changes
We continue to invest heavily in enhancing the Timeline Weather API and expanding its underlying data sources. Recent improvements include:

For a full list of additions to the Timeline Weather API, please see the changelog.

Timeline Weather API Query Builder
The Weather Query Builder page includes a full, interactive query builder so you can create queries and see the live results directly in your browser.

Creating a weather API request
Base URL
https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/
Endpoints
The possible endpoints of the Timeline Weather API requests are as follows:

Main Format of the URL
All requests to the Timeline Weather API use the following the form:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/[location]/[date1]/[date2]?key=YOUR_API_KEY
Request Parameters
Main Parameters (Path Parameters)
location (required) – is the address, partial address or latitude,longitude location for which to retrieve weather data. You can also use US ZIP Codes. If you would like to submit multiple locations in the same request, consider our Multiple Location Timeline Weather API.

date1 (optional) – is the start date for which to retrieve weather data. If a date2 value is also given, then it represents the first date for which to retrieve weather data. If no date2 is specified then weather data for a single day is retrieved, and that date is specified in date1. All dates and times are in local time of the location specified. Dates should be in the format yyyy-MM-dd. For example 2020-10-19 for October 19th, 2020 or 2017-02-03 for February 3rd, 2017.

Instead of an exact date, you can specify a dynamic date period. See below for more details. You may also supply the in “UNIX time”. In this case provide the number of seconds since 1st January 1970 UTC. For example 1612137600 for Midnight on 1st February 2021.

You can also request the information for a specific time for a single date by including time into the date1 field using the format yyyy-MM-ddTHH:mm:ss. For example 2020-10-19T13:00:00.

The results are returned in the ‘currentConditions’ field and are truncated to the hour requested (i.e. 2020-10-19T13:59:00 will return data at 2020-10-19T13:00:00).

date2 (optional) – is the end date for which to retrieve weather data. This value may only be used when a date1 value is given. When both date1 and date2 values are given, the query is inclusive of date2 and the weather data request period will end on midnight of the date2 value. All dates and times are in local time of the specified location and should be in the format yyyy-MM-dd.

When no date1 or date2 is specified, the request will retrieve the forecast at the requested location for the next 15 days.

Additional Parameters (QueryParameters)
The following are specified as HTTP query parameters (they may also be passed in a POST query).

key (required) – your API key. Sign up for a free account using our Weather Data Services page.

unitGroup (optional) – The system of units used for the output data.
Supported values are us, uk, metric, and base. See Unit groups and measurement units for more information. Defaults to US system of units.

lang (optional) – Sets the language of the translatable parts of the output such as the conditions field. Available languages include: ar (Arabic), bg (Bulgiarian), cs (Czech), da (Danish), de (German), el (Greek Modern), en (English), es (Spanish) ), fa (Farsi), fi (Finnish), fr (French), he Hebrew), hu, (Hungarian), it (Italian), ja (Japanese), ko (Korean), nl (Dutch), pl (Polish), pt (Portuguese), ru (Russian), sk (Slovakian), sr (Serbian), sv (Swedish), tr (Turkish), uk (Ukranian), vi (Vietnamese) and zh (Chinese). In addition passing in ‘id’ will result in the raw descriptor IDs.See How to create or modify language files for more information on how to help add additional languages.

include (optional) – Specifies the sections you would like to include in the result data. This allows you to reduce query cost and latency. Specify this as a comma separated list. For example: &include=obs,fcst to include the historical observations and forecast data. The options are:

elements (optional) – Specifies the specific weather elements you would like to include in the response as a comma separated list. For example, &elements=tempmax,tempmin,temp will request the only the tempmax, tempmin and temp response elements. For the full list of available elements, see the response below.

options (optional) – Specifies additional options on the requests to either indicate the type of data or format of the output. Supported values include:

contentType (optional) – indicates the output format for the API. By default the output is formated in JSON. You can also set contentType=csv to retrieve CSV formatted data.Note that CSV format does not support the full JSON output due to the format limitations. You must use the include parameter to indicate which section you would like to retrieve. CSV include parameters support are days, hours, alerts, events and current.

iconSet (optional) – used to choose which icons IDs are populated. For more information see Defining the icon set parameter in the Weather API.

timezone (optional) – specifies the timezone of the input and result dates and times. When not specified, all date times are considered local times. If you would like to specify that all dates are entered as UTC dates and times, use timezone=Z parameter.

maxDistance (optional) The maximum distance in meters used to search for local weather stations ( By default, 50 miles or approximately 80km (80,467m). This setting is combined with the maxStations parameter to find local weather stations.

maxStations (optional) The maximum number of weather stations used to calculate a weather record (default 3). Closer weather stations are weighted significantly more heavily than farther stations.

elevationDifference (optional) The maximum elevation difference in meters between the requested location and weather stations. Any weather station that is either lower or higher than more than this setting will be excluded. Default is turned off.

locationNames (optional) provides alternative name for the location requested. This is typically used by users who need to be able to join the API results back to a dataset. For example, you may pass a store database ID in this parameter so that you can populate the weather forecast for that store.

forecastBasisDate (optional, requires historical forecast license) – specifies the date when the weather forecast model was run. For example, if you specify 2021-06-01, then the data from 2021-06-01 to 2021-06-15 will use the weather forecast produced on June 1st, 2021. For more information see How to query weather forecasts from the past.

forecastBasisDay (optional, requires historical forecast license) – specifies the forecast day for the date1 parameter above. For example, if you specify the start date as 2021-06-05 and a forecastBasisDay value of 5, then the value for 2021-06-06 will be the 5th day forecast (i.e. it will be based on the weather forecast produced five days earlier (2021-06-01). You can use this parameter to quickly find the forecast that was predicted for a particular day on multiple days (for example the 5, 3 and 1 day forecast). For more information see How to query weather forecasts from the past.

Degree days parameters (Query Parameters)
degreeDayTempFix – The temperature at which to start the degree day season if no season start and end dates are specified. For example, if the fix temperature is 32F (OC), then the cumulative degree days will reset to zero on the last 32F temperature of the winter. This defines the growing season for growing degree days.

degreeDayStartDate – Fixes the start of the degree day season based on fixed dates of the format yyyy-M-d (eg 1990-3-1 for 1st March). Default=not specified.

degreeDayTempMaxThreshold – Defines the maximum temperature that is considered for the calculation. Any temperature above this temperature will be set to the maximum threshold temperature. Default value=not set.

degreeDayTempBase – The degree day base temperature. Default value is set to 10C/50F

degreeDayInverse – Calculate the inverse degree days so colder temperatures contribute more degree days. Used for heating degree days. Default=false.

degreeDayMethod (beta) – The method used for calculating the degree days. Values include average, sine, doublesine, triangle and doubletriangle. Default value is set to average.

Request Examples
Forecast Request Example
The following will retrieve the weather forecast for London, United Kingdom for the next 15 days, starting at midnight at the start of the current day (local time of the requested location).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK?key=YOUR_API_KEY
Forecast Request Example using longitude and latitude
You may also pass the location as a “latitude,longitude” value. For example: 38.9697,-77.385

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/38.9697,-77.385?key=YOUR_API_KEY
Date Range Request Example
The following will retrieve the weather data for London, UK from October 1st, 2020 to December 31st, 2020 (inclusive).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/2020-10-01/2020-12-31?key=YOUR_API_KEY
Assuming the current date is November 1st, 2020, the result will include historical observations from October 1st to 31st, then 15 days of weather forecast and finally the remaining days will include the statistical forecast based on processing years of historical observations.

Date Range Request Example using UNIX Time (Epoch Time)
The following shows the same query using UNIX format of seconds since the 1970 UNIX time epoch. Note that these times are seconds in the UTC (GMT/Z) time zone.

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/1601510400/1609372800?key=YOUR_API_KEY
Specific Time Request Example
The following will retrieve the weather data for London, UK for the 15th December 2020 and will request the current conditions property be populated using the conditions at 13:00 local time (1pm local time).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/2020-12-15T13:00:00?key=YOUR_API_KEY
The above example will include the daily and hourly detail for the day of the current conditions (2020-12-15 in this case). This query cost will therefore be 24. If you only need the specific time data, and don’t need the hourly detail, you can reduce the query costing using the include parameter:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/2020-12-15T13:00:00?key=YOUR_API_KEY&include=current
This query cost will be one.

Dynamic period Request Example
Rather the specify and date range, you can also specify and dynamic period. A request based on a dynamic period will automatically adjust based on the period. In this example, we will use the dynamic period value “last30days” to retrieve data for the most recent 30 days.

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?key=YOUR_API_KEY
Other dynamic period values include “today”, “yesterday”, and “lastyear”. For a complete list of options and additional example, please see the dynamic period article.

Using elements list and options parameter to request only daily with limited elements
By default both daily and hourly data is included in the response along with all the response weather data elements (see below). To reduce the size of the result JSON for lower query cost, reduced network transfer and faster client processing, the options and elements parameters may be used.

This example requests only the daily data:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?key=YOUR_API_KEY
This example requests the daily data with only temperature elements:

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?key=YOUR_API_KEY&include=days&elements=tempmax,tempmin,temp
Degree day elements list example
The following includes the daily ‘degree days’ information for the requested location and date range (in this case the last 30 days).

https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/London,UK/last30days?
unitGroup=us&key=YOUR_API_KEY&include=days&elements=datetime,tempmax,tempmin,degreedays,accdegreedays&degreeDayTempMaxThreshold=86&degreeDayTempBase=50
For more information on our growing, cooling and heating degree day options, please see our degree day page.

Industry elements
The Timeline API can be extended to include advanced agriculture, horticulture and energy elements. These include evapotranspiration, soil temperature & moisture, advanced solar radiation and higher altitude wind speeds and directions.

To include these advanced industry elements, please see our Agriculture and Horticulture and Wind and Solar Energy pages.

Weather API Response Structure
Typical JSON response format
All Timeline Weather API requests return response JSON in the same format. Here is an example for Reston, VA on 11/12/2020:

{
    "latitude" : 38.9697,
    "longitude" : -77.385,
    "resolvedAddress" : "Reston, VA, United States",
    "address" : " Reston,VA",
    "timezone" : "America/New_York",
    "tzoffset" : -5,
    "description":"Cooling down with a chance of rain on Friday.",
    "days" : [{ //array of days of weather data objects
        "datetime":"2020-11-12",
        "datetimeEpoch":1605157200,
        "temp" : 59.6,
        "feelslike" : 59.6,
        ...
        "stations" : {
        },
        "source" : "obs",
        "hours" : [{  //array of hours of weather data objects
            "datetime" : "01:00:00",
            ...
        },...]
    },...],
    "alerts" : [{
            "event" : "Flash Flood Watch",
            "description" : "...",
            ...
        }
    ],
    "currentConditions" : {
        "datetime" : "2020-11-11T22:48:35",
        "datetimeEpoch" : 160515291500,
        "temp" : 67.9,
        ...
    }
}
The response starts with a set of properties describing the location and request including the specific location requested, the resolved address, the latitude and longitude, a text based time zone and a time zone offset in hours. Note that the time zone offset can change within a dataset (based on daylight savings). If this occurs, the a tzoffset property will be found in the day, hour or current conditions weather data object.

The days array is an array of weather data objects for each day requested.

Within each day may be an hours array for the hourly information. Statistical forecast days will not include an hourly array. Typically the hours array will be length 24 but day light savings may cause the array to be 23 or 25 hours long.

If the request includes the current date, the current conditions and any weather alerts available for the location will be included.

Response Elements
Response weather data elements
cloudcover – how much of the sky is covered in cloud ranging from 0-100%

conditions – textual representation of the weather conditions. See Weather Data Conditions.

description – longer text descriptions suitable for displaying in weather displays. The descriptions combine the main features of the weather for the day such as precipitation or amount of cloud cover. Daily descriptions are provided for historical and forecast days. When the timeline request includes the model forecast period, a seven day outlook description is provided at the root response level.

datetime – ISO 8601 formatted date, time or datetime value indicating the date and time of the weather data in the local time zone of the requested location. See Dates and Times in the Weather API for more information.

datetimeEpoch – number of seconds since 1st January 1970 in UTC time

tzoffset – the time zone offset in hours. This will only occur in the data object if it is different from the global time zone offset.

dew – dew point temperature

feelslike – what the temperature feels like accounting for heat index or wind chill. Daily values are average values (mean) for the day.

feelslikemax (day only) – maximum feels like temperature at the location.

feelslikemin (day only) – minimum feels like temperature at the location.

hours – array of hourly weather data objects. This is a child of each of the daily weather object when hours are selected.

humidity – relative humidity in %

icon – a fixed, machine readable summary that can be used to display an icon

moonphase –  represents the fractional portion through the current moon lunation cycle ranging from 0 (the new moon) to 0.5 (the full moon) and back to 1 (the next new moon). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

normal – array of normal weather data values – Each weather data normal is an array of three values representing, in order, the minimum value over the statistical period, the mean value, and the maximum value over the statistical period.

offsetseconds (hourly only) – time zone offset for this weather data object in seconds – This value may change for a location based on daylight saving time observation.

precip – the amount of liquid precipitation that fell or is predicted to fall in the period. This includes the liquid-equivalent amount of any frozen precipitation such as snow or ice.

precipremote – radar estimated precipitation amount. See How to Include Weather Radar Data in Weather Datasets for more information.

precipcover (days only) – the proportion of hours where there was non-zero precipitation

precipprob (forecast only) – the likelihood of measurable precipitation ranging from 0% to 100%

preciptype – an array indicating the type(s) of precipitation expected or that occurred. Possible values include rain, snow, freezingrain and ice.

reflectivity – (minutes only) estimates of the radar-based reflectivity values indicating precipitation intensity. See How to Include Weather Radar Data in Weather Datasets for more information.

pressure – the sea level atmospheric or barometric pressure in millibars (or hectopascals)

snow – the amount of snow that fell or is predicted to fall

snowdepth – the depth of snow on the ground

source –  the type of weather data used for this weather object. – Values include historical observation (“obs”), forecast (“fcst”), historical forecast (“histfcst”) or statistical forecast (“stats”). If multiple types are used in the same day, “comb” is used. Today a combination of historical observations and forecast data.

stations (historical only) – the weather stations used when collecting an historical observation record

sunrise (day only) – The formatted time of the sunrise (For example “2022-05-23T05:50:40”). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

sunriseEpoch – sunrise time specified as number of seconds since 1st January 1970 in UTC time

sunset – The formatted time of the sunset (For example “2022-05-23T20:22:29”). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

sunsetEpoch – sunset time specified as number of seconds since 1st January 1970 in UTC time

moonrise (day only, optional) – The formatted time of the moonrise (For example “2022-05-23T02:38:10”). See How to include sunrise, sunset, moon phase, moonrise and moonset data into your API requests

moonriseEpoch (day only, optional) – moonrise time specified as number of seconds since 1st January 1970 in UTC time

moonset (day only, optional) – The formatted time of the moonset (For example “2022-05-23T13:40:07”)

moonsetEpoch (day only, optional) – moonset time specified as number of seconds since 1st January 1970 in UTC time

temp – temperature at the location. Daily values are average values (mean) for the day.

tempmax (day only) – maximum temperature at the location.

tempmin (day only) – minimum temperature at the location.

uvindex – a value between 0 and 10 indicating the level of ultra violet (UV) exposure for that hour or day. 10 represents high level of exposure, and 0 represents no exposure. The UV index is calculated based on amount of short wave solar radiation which in turn is a level the cloudiness, type of cloud, time of day, time of year and location altitude. Daily values represent the maximum value of the hourly values.

uvindex2 (optional, 5 day forecast only) – an alternative UV index element that uses the algorithms and models used by the US National Weather Service. In order to maintain backwards compatibility, this UV index element is deployed as a new, optional element ‘uvindex2’ and may be requested using the elements parameter.

visibility – distance at which distant objects are visible

winddir – direction from which the wind is blowing

windgust – instantaneous wind speed at a location – May be empty if it is not significantly higher than the wind speed. Daily values are the maximum hourly value for the day.

windspeed – the sustained wind speed measured as the average windspeed that occurs during the preceding one to two minutes. Daily values are the maximum hourly value for the day.

windspeedmax (day only, optional)– maximum wind speed over the day.

windspeedmean (day only , optional ) – average (mean) wind speed over the day.

windspeedmin (day only , optional ) – minimum wind speed over the day.

solarradiation – (W/m2) the solar radiation power at the instantaneous moment of the observation (or forecast prediction). See the full solar radiation data documentation and Wind and Solar Energy pages .

solarenergy – (MJ /m2 ) indicates the total energy from the sun that builds up over an hour or day. See the full solar radiation data documentation and Wind and Solar Energy pages .

severerisk (forecast only) – a value between 0 and 100 representing the risk of convective storms (e.g. thunderstorms, hail and tornadoes). Severe risk is a scaled measure that combines a variety of other fields such as the convective available potential energy (CAPE) and convective inhibition (CIN), predicted rain and wind. Typically, a severe risk value less than 30 indicates a low risk, between 30 and 70 a moderate risk and above 70 a high risk.

cape (forecast only) – convective available potential energy. This is a numbering indicating amount of energy available to produce thunderstorms. A higher values indicates a more unstable atmosphere capable of creating stronger storms. Values lower than 1000 J/kg indicate generally low instability, between 1000-2500 J/kg medium instability and 2500-4000 J/kg high instability. Values greater than 4000 J/kg indicating an extremely unstable atmosphere.

cin (forecast only) – convective inhibition. A number representing the level of atmospheric tendency to prevent instability and therefore prevent thunderstorms.

degreedays (day only) – optional elements indicating the number of degree days for this date. See the degree days API for more information on degree days. To turn degree days and degree day accumulation on, use the elements parameter. For example, elements=datetime,tempmax,tempmin,degreedays,accdegreedays.

To convert existing Dark Sky API parameters to the Timeline Weather API, see How to replace the Dark Sky API with the Timeline Weather API.

Location and station elements
The following are available in the JSON response type to provide information about the requested location:

queryCost – The record cost of this query. See what is a record for more information.

latitude,longitude – the latitude and longitude of the requested location. This is provided in decimal degrees.

resolvedAddress – if the requested location was made by address, the address that is found using our internal geocoding engine.

address – the requested location text from the request.

timezone – the timezone of the location. See Date and Times in the Weather API for more information.

tzoffset – the timezone offset from UTC time for the first record of the data. This may change throughout the dataset if there is a daylight savings change during the requested date range.

elevation (optional) – the elevation of the requested location. This is an optional element requested by including the elements parameter: (see Adding and Removing Elements).

HTTP Response Code and Error Handling
The API communicates error codes through the HTTP response code. In addition, the body the response will normally include additional error information indicating the cause of the error. The possible HTTP response status codes include:

200 OK – a successfully processed request

400 BAD_REQUEST – The format of the API is incorrect or an invalid parameter or combination of parameters was supplied

401 UNAUTHORIZED – There is a problem with the API key, account or subscription. May also be returned if a feature is requested for which the account does not have access to.

404 NOT_FOUND – The request cannot be matched to any valid API request endpoint structure.

429 TOO_MANY_REQUESTS – The account has exceeded their assigned limits. See What is the cause of “Maximum concurrent jobs has been exceeded”, HTTP response 429

500 INTERNAL_SERVER_ERROR – A general error has occurred processing the request.

For general information on debugging API queries, please see: How to debug problems when running weather API queries in code

Accessing the Timelime Weather API using the OpenAPI Description
The OpenAPI Initiative standardizes the description of APIs such as the Visual Crossing Weather API. If you are using a tool that supports the OpenAPI standard or Swagger, you can more easily use our API by importing the the specification document below.