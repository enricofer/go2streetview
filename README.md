# go2streetview

a QGIS plugin for google Streetview© interaction

## Changelog

#### v10.0 (from QGIS 3.36)

1. Drop Qt WebKit for Qt WebEngine from QGIS 3.36.

2. Digitize on streetview window.

   ![](docs/digitizeOnSV.jpg)

#### v8.8

1. Outdated WebKit message on dockwidget.
2. Direct open streetview on web broser.

#### v8.7

1. Downgrade to last running gmapsjs lib - courtesy of @yvo2m

#### v8.6

1. Avoid using deprecated QgsCoordinateReferenceSystem constructor - courtesy of @nirvn Mathieu Pellerin.
2. Fix once-per-session ballpark transformation warning when panel opens - courtesy of @nirvn Mathieu Pellerin.
3. Fix error when clicking on 'open in external browser' with a non-zero pitch value - courtesy of @nirvn Mathieu Pellerin.

#### v8.5

1. Fix broken view when resizing the panel - courtesy of @nirvn Mathieu Pellerin.
2. Avoid using deprecated QgsCoordinateReferenceSystem constructor - courtesy of @nirvn Mathieu Pellerin.
3. Fix once-per-session ballpark transformation warning when panel opens - courtesy of @nirvn Mathieu Pellerin.
4. Fix error when clicking on 'open in external browser' with a non-zero pitch value - courtesy of @nirvn Mathieu Pellerin.

#### v8.4

1. snapshots issues fixes.
2. fix python 3.9 update - courtesy of https://github.com/denchat.

#### v8.3

1. various bug fixes.

#### v8.2

1. new QGIS expression function to view static images in atlas.

#### v8.1 - QGIS3 fork (23/02/2018)

1. log level api break issue fixed.
2. bing oblique icon not visible issue fixed.

#### v8.0 -QGIS3 fork (26/01/2018)

1. Bing service support discontinued.
2. Full Google maps oblique support.
3. Infolayer projects settings restored at loading.

#### v7.4 -QGIS2 fork (26/01/2018)

1. Bing service support discontinued.
2. Partial Google maps oblique support.

#### v7.3 (04/08/2017)

1. console print trace issues fixed (courtesy of https://github.com/dwsilk).
2. save snapshot url field issue fixed.
3. snapshots layer style issue fixed.

#### v7.2 (10/01/2017. 

1. Google maps API key support.
2. Web inspector dialog.

#### v7.1 (30/8/2016)

1. Google streetview api update.

#### v7.0 (30/3/2016)

1. Streetview Coverage feature.
2. Toggle Panorama controls (date, links, click to go, pan, zoom) feature.
3. links and pan issue fixed.

#### v6.5 (27/7/2015)

1. Map rotation support.
2. Bing bird's eye connection issues fixed.
3. Proxying issues fixed.
4. Proxying subnet exclusions fixed.
5. Line and polygon infolayer support.
6. Select and edit attributes from info layers.
7. A4 keymap pdf printing.
8. Buttons toolbar compacted.
9. Map follows streetview option.
9. Resize behaviour issues fixed.

#### v6.2 (6/4/2015)

1. Poor performance with WGS84 layers issue fixed.
2. Changing default Distance Buffer depending from info layer mapunits.

#### v6.1 (6/4/2015)

1. malformed html blocking script issue fixed.
2. open in browser points always to Bing issue fixed.

#### v6.0 (3/4/2015)

1. info layer overlay in streetview window.
2. info layer overlay in bing window.
3. new gui toolbar.
4. location tracking improvement.
5. resize issue opening view fixed.

#### v5.1 (5/1/2015)

1. terms of service dialog behaviour improved.
2. menu icon toggle on/off dock widget.

#### v5.0 (4/11/2014)

1. Dockable Dialog Window.
2. Reformat dialog Button Position.
3. Click on Dialog to trigger tool.
4. Terms of service agreement.

#### v4.1 (12/06/2014)

1. fixed float conversion bug during window resizing.
2. improved zoom to fov conversion.
3. fixed srs setting.
4. oriented symbol qml style.

#### v4.0 (29/5/2014)

1. Dynamic resizing of Windows with responsive rescaling of contents.
2. CTRL + Click&Drag cursor to open view straight to predifined browser.
3. Added dynamic icon to show on map current Streetview position and field of view.
4. Nominating Geocoding on the fly, to get complete address when taking snapshot of the view.
5. Recording Field of View in the snapshot URL field.

#### v3.01 (21/4/2014)

1. Modified “take a snapshot” procedure to fulfil article 10.1.3 of google maps terms of service.
2. Added action to “Streetview_snapshot_log” layer to view saved snapshots clicking on camera icon (“Webview” layer action activation needed).

#### v3.0 (17/04/2014)

1. Added Streetview position tracking. Plugin detects panorama parameters like coordinates, heading etc. and use them for browser calling or change to Bing.
2. Added "Take a Snapshot" functionality. clicking on button you record a snapshot of current view in snapshots directory located in the plugin folder.
3. Snapshots can be annotated by user with custom notes.
4. Snapshots are annotated in a shapefile log that stores date, point of view, address, notes and file name.
5. Plugin add to project legend a layer called "Streetview snapshots log" where the snapshots stored are visible as html tips hovering with mouse (remember to enable map tips from view menu).

#### v2.1 (11/4/2014)

1. fixed a bug with the procedure for the automatic setting of the proxy service by reading qsetting stored by qgis options.

#### v2.0 (29/3/2014)

1. Revised dialog interface. 
2. Improved user interaction, interactive clicking and dragging cursor to find location and heading of the desidered view.
3. Allowed opening view in external browser.  
4. Interaction with google service to find out if the view for the given point is not available or other server-errors.
5. Minor bug fixes.

