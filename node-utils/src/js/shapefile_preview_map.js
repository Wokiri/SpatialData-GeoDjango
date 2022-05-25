import sync from "ol-hashed";
import GeoJSON from "ol/format/GeoJSON";
import VectorSource from "ol/source/Vector";
import { Text, Style, Fill, Stroke } from "ol/style";
import VectorLayer from "ol/layer/Vector";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import { Map, View } from "ol";
import Overlay from "ol/Overlay";
import {
    DragRotateAndZoom,
    defaults as defaultInteractions,
} from 'ol/interaction';
import { Attribution, FullScreen, defaults as defaultControls, ZoomSlider } from 'ol/control';
import Select from "ol/interaction/Select";

const shapefile_preview_map = document.getElementById("shapefile_preview_map");

const container = document.getElementById('popup');
const closer = document.getElementById('popup-closer');
const content = document.getElementById('popup-content');

const parcels_overlay = new Overlay({
    element: container,
    autoPan: true,
    autoPanAnimation: {
        duration: 250,
    },
});

closer.addEventListener('click', () => {
    parcels_overlay.setPosition(undefined)
    closer.blur()
})

let expandedAttribution = new Attribution({
    collapsible: false,
});

// let parcel_json = { "type": "FeatureCollection", "features": [{ "id": "0", "type": "Feature", "properties": { "county": "Machakos", "fr_datum": "76/78", "hold_type": null, "land_use": null, "parcel_number": "LR NO 4480/48", "sub_county": "Ngong" }, "geometry": { "type": "Polygon", "coordinates": [[[36.65716779957811, -1.3623138627456475], [36.65741904282, -1.3622041272242196], [36.65752847154055, -1.3624575235653829], [36.65727729568316, -1.3625673961393248], [36.65716779957811, -1.3623138627456475]]] } }] }

const parcel_location_VectorSource = new VectorSource({
    features: new GeoJSON().readFeatures(parcel_json, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3857",
        extractGeometryName: true,
    }),
});


// Parcels visual style
const getPolyText = feature => `${feature.get('parcel_number')}`

const labelStyle = feature => new Text({
    textAlign: "center",
    textBaseline: "middle",
    font: `bold 12px sans-serif`,
    text: getPolyText(feature),
    placement: "polygon",
    fill: new Fill({
        color: "rgb(0, 0, 51)",
    }),
})

const polygonShapeStyle = feature => new Style({
    text: labelStyle(feature),
    fill: new Fill({
        color: "rgba(0, 0, 102, 0.25)",
    }),
    stroke: new Stroke({
        color: "rgb(0, 0, 102)",
        width: 2,
    })
});

// surveyor location layer
const parcel_Layer = new VectorLayer({
    source: parcel_location_VectorSource,
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
    layers: [OpenStreetMapLayer, parcel_Layer],
    overlays: [parcels_overlay],
    view: new View(),
});

sync(parcel_Map);

const layer_extent = parcel_Layer.getSource().getExtent()
parcel_Map.getView().fit(layer_extent)
parcel_Map.getView().setZoom(parcel_Map.getView().getZoom() - 0.25)

let checkSize = () => {
    let isLess600 = parcel_Map.getSize()[0] < 600;
    expandedAttribution.setCollapsible(isLess600);
    expandedAttribution.setCollapsed(isLess600);
}
checkSize()
window.addEventListener("resize", checkSize);


// selection option
const singleMapClick = new Select({
    layers: [parcel_Layer],
    style: new Style({
        fill: new Fill({
            color: "rgba(204, 204, 255, 0.5)",
        }),
        stroke: new Stroke({
            color: "rgb(0, 0, 0)",
            width: 2.5,
        }),
    })
}); //By default, this is module:ol/events/condition~singleClick. Other defaults are exactly what I need

parcel_Map.addInteraction(singleMapClick);


let selected = null
parcel_Map.on("singleclick", evt => {
    parcel_Map.forEachFeatureAtPixel(evt.pixel, feature => {
        selected = feature
    });
    if (selected) {
        let selected_feature = selected.getProperties()

        let click_coords = evt.coordinate;
        parcels_overlay.setPosition(click_coords);

        populate_popup_content(selected_feature)
        selected = null;
    } else {
        parcels_overlay.setPosition(undefined);
        closer.blur();
    }
})

function populate_popup_content(feat) {
    let parcel_number = feat.parcel_number ?? ''
    let fr_datum = feat.fr_datum ?? ''
    let county = feat.county ?? ''
    let hold_type = feat.hold_type ?? ''
    let land_use = feat.land_use ?? ''
    
    content.innerHTML = `
    <p class='fs-6 text-center fw-bold'>${parcel_number}</p>
    <p class='fs-6 fw-light lh-1'>FR Datum: ${fr_datum}</p>
    <p class='fs-6 fw-light lh-1'>County: ${county}</p>
    <p class='fs-6 fw-light lh-1'>Hold type: ${hold_type}</p>
    <p class='fs-6 fw-light lh-1'>Land use: ${land_use}</p>
    `
}