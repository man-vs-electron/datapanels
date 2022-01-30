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

# Configuring DataPanels

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

The following example show a sample configuration.  Notice how three
StockPanel types are created, one for each stock ticker of interest.

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

# Panel Types

Each panel displayed in Datapanels can be configured.  The following
sections describe each panel type and its key parameters.

## QuotationDisplay
The quotation display is a simple panel that displays quotations.  These
quotations change periodically.

The parameters include:
* update_sec: The number of seconds before changing the quotation
* quotations: assigned as either a list of strings, one per quotation, or a single string that is a path to
  a file with quotations, one per line.

## StockPanel
The StockPanel display information about a list of stocks.  Data about
one stock is shown at a time and the specific stock shown is rotated
around on a regular basis.

The parameters include:
* data_update_rate_sec: how many seconds between updating the stock info
* proxserver: if not None, a proxy server to use for talking to yfinance
* ticker_change_rate_sec: how many seconds between changing the stock being shown
* tickers: list of security ticker symbols to track

## GameOfLifePanel
The Kivy panel that displays the Game of Life, along with some controls.

Key Properties:
* update_rate: number of seconds between each generation
* random_cell_count: Either percentage of cells to make alive or the number of cells to make alive when randomizing.
* background_color - RGBA list for the inactive cell color
* grid_color - RGBA for the grid lines
* activated_color - RGBA for the active cell color
* cell_length - the length of the side of a cell (essentially cell size)
