<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.22.4-Białowieża" styleCategories="LayerConfiguration|Symbology|Actions|MapTips" readOnly="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <renderer-v2 forceraster="0" type="singleSymbol" referencescale="-1" symbollevels="0" enableorderby="0">
    <symbols>
      <symbol alpha="1" name="0" type="marker" clip_to_extent="1" force_rhr="0">
        <data_defined_properties>
          <Option type="Map">
            <Option name="name" type="QString" value=""/>
            <Option name="properties"/>
            <Option name="type" type="QString" value="collection"/>
          </Option>
        </data_defined_properties>
        <layer locked="0" pass="0" enabled="1" class="SvgMarker">
          <Option type="Map">
            <Option name="angle" type="QString" value="0"/>
            <Option name="color" type="QString" value="0,170,255,255"/>
            <Option name="fixedAspectRatio" type="QString" value="0"/>
            <Option name="horizontal_anchor_point" type="QString" value="1"/>
            <Option name="name" type="QString" value="gpsicons/camera.svg"/>
            <Option name="offset" type="QString" value="0,0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="outline_color" type="QString" value="0,170,255,0"/>
            <Option name="outline_width" type="QString" value="1"/>
            <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="outline_width_unit" type="QString" value="MM"/>
            <Option name="parameters"/>
            <Option name="scale_method" type="QString" value="diameter"/>
            <Option name="size" type="QString" value="5"/>
            <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="size_unit" type="QString" value="MM"/>
            <Option name="vertical_anchor_point" type="QString" value="1"/>
          </Option>
          <prop v="0" k="angle"/>
          <prop v="0,170,255,255" k="color"/>
          <prop v="0" k="fixedAspectRatio"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="gpsicons/camera.svg" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,170,255,0" k="outline_color"/>
          <prop v="1" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="" k="parameters"/>
          <prop v="diameter" k="scale_method"/>
          <prop v="5" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="angle" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="field" type="QString" value="heading"/>
                  <Option name="type" type="int" value="2"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" enabled="1" class="SimpleMarker">
          <Option type="Map">
            <Option name="angle" type="QString" value="90"/>
            <Option name="cap_style" type="QString" value="square"/>
            <Option name="color" type="QString" value="0,170,255,255"/>
            <Option name="horizontal_anchor_point" type="QString" value="1"/>
            <Option name="joinstyle" type="QString" value="bevel"/>
            <Option name="name" type="QString" value="arrowhead"/>
            <Option name="offset" type="QString" value="0,0"/>
            <Option name="offset_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="offset_unit" type="QString" value="MM"/>
            <Option name="outline_color" type="QString" value="0,170,255,255"/>
            <Option name="outline_style" type="QString" value="solid"/>
            <Option name="outline_width" type="QString" value="0"/>
            <Option name="outline_width_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="outline_width_unit" type="QString" value="MM"/>
            <Option name="scale_method" type="QString" value="area"/>
            <Option name="size" type="QString" value="10"/>
            <Option name="size_map_unit_scale" type="QString" value="3x:0,0,0,0,0,0"/>
            <Option name="size_unit" type="QString" value="MM"/>
            <Option name="vertical_anchor_point" type="QString" value="1"/>
          </Option>
          <prop v="90" k="angle"/>
          <prop v="square" k="cap_style"/>
          <prop v="0,170,255,255" k="color"/>
          <prop v="1" k="horizontal_anchor_point"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="arrowhead" k="name"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="0,170,255,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0" k="outline_width"/>
          <prop v="3x:0,0,0,0,0,0" k="outline_width_map_unit_scale"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="area" k="scale_method"/>
          <prop v="10" k="size"/>
          <prop v="3x:0,0,0,0,0,0" k="size_map_unit_scale"/>
          <prop v="MM" k="size_unit"/>
          <prop v="1" k="vertical_anchor_point"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties" type="Map">
                <Option name="angle" type="Map">
                  <Option name="active" type="bool" value="true"/>
                  <Option name="expression" type="QString" value="heading + 90"/>
                  <Option name="type" type="int" value="3"/>
                </Option>
              </Option>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <attributeactions>
    <defaultAction key="Canvas" value="{9a4f4db7-222c-42ae-8f2b-f43e6946a61c}"/>
    <actionsetting icon="" capture="0" name="Webview" type="1" notificationMessage="" isEnabledOnlyWhenEditable="0" shortTitle="" action="from PyQt5.QtWebKitWidgets import QWebView&#xa;view = QWebView()&#xa;view.resize(480, 300)&#xa;view.setWindowTitle(&quot;Streetview snapshot&quot;)&#xa;html='&lt;html>&lt;body style=&quot;margin:0&quot;>&lt;div>&lt;img width=100% height=100% src=&quot;[% &quot;url&quot; %]&quot;/>&lt;/div>&lt;div style=&quot;position:fixed; top:5px;left:5px;color:white&quot;>&lt;small>&lt;b>[% &quot;lon&quot; %]E [% &quot;lat&quot; %]N&lt;br/>address: [% &quot;address&quot; %]&lt;br>notes: [% &quot;notes&quot; %]&lt;/b>&lt;/small>&lt;/div>&lt;/body>&lt;/html>'&#xa;view.setHtml(html)&#xa;view.show()" id="{9a4f4db7-222c-42ae-8f2b-f43e6946a61c}">
      <actionScope id="Feature"/>
      <actionScope id="Field"/>
      <actionScope id="Canvas"/>
    </actionsetting>
  </attributeactions>
  <previewExpression>"date"</previewExpression>
  <mapTip>&lt;b>Google Streetview snapshot: [% "date" %] [% "lon" %]E [% "lat" %]N &lt;/b>&lt;br/>&lt;b>Address: [% "address" %]&lt;/b>&lt;br/>&lt;b>Note:  [%notes%]&lt;/b></mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
