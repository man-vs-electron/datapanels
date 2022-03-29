# Overview
Datapanels is an application for displaying a rotating set of independent panels, each of which displays
some useful or entertaining information or something visually interesting. 

# Usage
After installation, the application can be run using

```
python -m datapanels.app [--builder_path path_to_builder_file] [--transition-sec secs] [--full_screen]
```

The --builder_path option lets you specify a configuration file that will 
determine what panels get displayed. The --transition-sec parameter lets 
you specify the number of seconds between transitions. If no parameters are
provided, a simple default set of panels will be created.

## Configuring DataPanels

DataPanels can be configured via a configuration file that specifies 
what panels should be displayed.  This is actually a Kivy ([https://kivy.org/]) 
configuration file.  

The configuration file should take the form:

```
<DataBuilder>:
    PanelType1:
        panel type one parameters
    PanelType2
        panel type two parameters
    PanelType2
        parameters for another instance of PanelType2
```

The following example show a sample configuration.  

```
<DataBuilder>:
    border: 0
    QuotationDisplay:
        update_sec: 5
        quotations: "See https://github.com/man-vs-electron/datapanels for info on how to configure this application.", "Where you go, that's where you'll be", "Thanks for trying this application."
    StockPanel:
        tickers: 'MSFT', 'PSEC', 'TSLA'
        data_update_rate_sec: 60*20
        ticker_change_rate_sec: 5
    GameOfLifePanel:
        update_rate: 0.5
        activated_color: 1, 0, 0, 1
        grid_color: 0, 0, 1, 1

```

## Example Usage

TODO

# Panel Types

Each panel displayed in Datapanels can be configured.  The following
sections describe each panel type and its key parameters.

## QuotationDisplay
The quotation display is a simple panel that displays quotations.  These
quotations change periodically.

The parameters include:
* __update_sec__: The number of seconds before changing the quotation
* __quotations__: assigned as either a list of strings, one per quotation, or a single string that is a path to
  a file with quotations, one per line.

## StockPanel
The StockPanel display information about a list of stocks.  Data about
one stock is shown at a time and the specific stock shown is rotated
around on a regular basis.

The parameters include:
* __data_update_rate_sec__: how many seconds between updating the stock info
* __proxserver__: if not None, a proxy server to use for talking to yfinance
* __ticker_change_rate_sec__: how many seconds between changing the stock being shown
* __tickers__: list of security ticker symbols to track

## GameOfLifePanel
The Kivy panel that displays the Game of Life, along with some controls.

Key Properties:
* __update_rate__: number of seconds between each generation
* __random_cell_count__: Either percentage of cells to make alive or the number of cells to make alive when randomizing.
* __background_color__ - RGBA list for the inactive cell color
* __grid_color__ - RGBA for the grid lines
* __activated_color__ - RGBA for the active cell color
* __cell_length__ - the length of the side of a cell (essentially cell size)

## WeatherPanel
The Kivy panel that displays current weather and weather forecast for a list of provided locations.

Key Properties:
* __owm_key__ - The user's key from https://openweathermap.org/.  IMPORTANT: This panel will not work without this key.*
    It either needs to be specified as a property in the configuration or it needs to be set as an
    environment variable.  You can get a free key by registering at openweathermap.org.
* __temp_units__ - either fahrenheit or celcius (Default - fahrenheit)
* __text_color__ - the rgba color of the text and line components of the interface. (Default - [0,0,0,1])
* __bg_color__ - the background color (Default - [.5, .5, .5, 1])
* __locations__ - a list of WeatherResponse objects, one each for the locations of interest.  This attribute can be
    set by assigning a list in the form of [(lat1, lon1), location_name1, (lat2, lon2), location_name2, ...].
    This is the form to use when assigning locations using the configuration file.  If assigned this way, 
    it will be converted in a list of WeatherResponse objects.  

