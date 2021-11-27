# Overview
Datapanels is an application for displaying a rotating set of independent panels, each of which displays
some useful or entertaining information or something visually interesting. 

# Usage
After installation, the application can be run using

```
python -m datapanels.app [--builder_path path_to_builder_file] [--transition-sec secs]
```

The --builder_path option lets you specify a configuration file that will 
determine what panels get displayed. The --transition-sec parameter lets 
you specify the number of seconds between transitions. If no parameters are
provided, a simple default set of panels will be created.

# Configuring Datapanels

Datapanels can be configured via a configuration file that specifies 
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
    QuotationDisplay:
        update_sec: 5
        quotations: "Quote 1", "Quote 2", "Quote 3"
    StockPanel:
        ticker: 'MSFT'
    StockPanel:
        ticker: 'PSEC'
    StockPanel:
        ticker: 'DOCN'
```



# Panel Types

Each panel displayed in Datapanels can be configured.  The following
sections describe each panel type and its key parameters.

## QuotationDisplay
The quotation display is a simple panel that displays quotations.  These
quotations change periodically.

The parameters include:
* update_sec - how often to choose a new quotation
* quotations - either a list of strings, each of which is a quotation, or 
  the path to a text file with one line per quotation

## StockPanel
The StockPanel display information about a single stock.  This information
is downloaded using the yfinance library.  

The parameters include:
* ticker - The symbol for the stock of interest
* update_rate_sec - How many seconds to wait before updating the data.
