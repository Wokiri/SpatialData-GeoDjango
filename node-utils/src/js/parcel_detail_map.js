
import sync from "ol-hashed";
import GeoJSON from "ol/format/GeoJSON";
import VectorSource from "ol/source/Vector";
import { Style, Fill, Stroke } from "ol/style";
import VectorLayer from "ol/layer/Vector";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import { Map, View } from "ol";
import {
    DragRotateAndZoom,
    defaults as defaultInteractions,
} from 'ol/interaction';
import { Attribution, FullScreen, defaults as defaultControls, ZoomSlider } from 'ol/control';

const shapefile_preview_map = document.getElementById("shapefile_preview_map");

let expandedAttribution = new Attribution({
    collapsible: false,
});


// const parcel_geojson = {"type":"FeatureCollection","crs":{"type":"name","properties":{"name":"EPSG:4326"}},"features":[{"type":"Feature","properties":{"parcel":"kajiado-lr-no-4480310","pk":"91f19d86-79a6-4c7a-a87e-f0442c46d5d1","parcel_number":"LR NO 4480/310","fr_datum":"253/32","county":"Kajiado","sub_county":"Ngong","land_use":null,"hold_type":"FREEHOLD","date_created":"2022-05-24T09:05:47.198Z","owners":[]},"geometry":{"type":"MultiPolygon","coordinates":[[[[36.652920260729346,-1.364461222054883],[36.65281196926663,-1.364208929701973],[36.65281271682623,-1.364207683167037],[36.652927924470546,-1.364156871781623],[36.65303778931569,-1.364409394849637],[36.652920260729346,-1.364461222054883]]]]}}]}


const parcelsVectorSource = new VectorSource({
    features: new GeoJSON().readFeatures(parcel_geojson, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3857",
        extractGeometryName: true,
    }),
});


const polygonShapeStyle = feature => new Style({
    fill: new Fill({
        color: "rgba(102, 51, 0, 0.125)",
    }),
    stroke: new Stroke({
        color: "rgb(102, 51, 0)",
        width: 4,
    }),
    updateWhileAnimating: true, // optional, for instant visual feedback
    updateWhileInteracting: true, // optional, for instant visual feedback
});

// surveyor location layer
const parcelsLayer = new VectorLayer({
    source: parcelsVectorSource,
    style: polygonShapeStyle
});

// basemap layer
const OpenStreetMapLayer = new TileLayer({
    opacity: 1,
    type: "base",
    title: "OpenStreetMap Base Map",
    source: new OSM({
        attributions: `<a href="https://www.openstreetmap.org/">OSM Basemap</a>`,
    }),
});

const parcel_Map = new Map({
    controls: defaultControls({
        attribution: false
    }).extend([
        new FullScreen(),
        expandedAttribution,
        new ZoomSlider(),
    ]),
    interactions: defaultInteractions().extend([new DragRotateAndZoom()]),
    target: shapefile_preview_map,
    layers: [OpenStreetMapLayer, parcelsLayer],
    view: new View(),
});

sync(parcel_Map);

const layer_extent = parcelsLayer.getSource().getExtent()
parcel_Map.getView().fit(layer_extent)
parcel_Map.getView().setZoom(parcel_Map.getView().getZoom() - 0.25)

let checkSize = () => {
    let isLess600 = parcel_Map.getSize()[0] < 600;
    expandedAttribution.setCollapsible(isLess600);
    expandedAttribution.setCollapsed(isLess600);
}
checkSize()
window.addEventListener("resize", checkSize);
