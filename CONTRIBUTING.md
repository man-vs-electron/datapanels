# Contributing

This application is intended to be a set of independent data visualization 
panels. This is amenable to multiple independent contributors.  Contributions 
are welcome via merge requests.  New panels should be added via it own python 
file inside the datapanels package.  For example, the stock display is in 
datapanels.stockpanel.

Issues posted in the issues tracker are also welcome.

Generally usable widgets that are written in support of panels in this
application are welcome in the kwidgets library.

# Versioning

DataPanels uses a form of the standard Semantic Versioning methodology 
(https://semver.org/spec/v2.0.0.html) for naming versions.  All versions 
will take the form X.Y.Z.  All X.*.* versions will maintain backward 
compatibility starting with 1.0.0.  An increment in a MINOR (Y) version 
indicates new functionality. An increment in a PATCH (Z) version 
indicates a bug fix.  PATCHES may also contain simple changes like 
exposing options that were hard coded before.  Development versions 
(X.Y.Z.devD) may be released as well. These version may be tagged on 
branches that are eventually collapsed when merged back into master.  
All X.Y.Z versions will be found on master.  