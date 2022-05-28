
import sync from "ol-hashed";
import GeoJSON from "ol/format/GeoJSON";
import VectorSource from "ol/source/Vector";
import { Circle as CircleStyle, Style, Fill, Stroke } from "ol/style";
import VectorLayer from "ol/layer/Vector";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import { Map, View } from "ol";
import {
    DragRotateAndZoom,
    defaults as defaultInteractions,
} from 'ol/interaction';
import { Attribution, FullScreen, defaults as defaultControls, ZoomSlider } from 'ol/control';
import Select from "ol/interaction/Select";

const shapefile_preview_map = document.getElementById("shapefile_preview_map");

const detail_content = document.getElementById('detail_content');

let expandedAttribution = new Attribution({
    collapsible: false,
});


// const existing_parcels_geojson = {"type":"FeatureCollection","crs":{"type":"name","properties":{"name":"EPSG:4326"}},"features":[{"type":"Feature","properties":{"parcel":"kajiado-lr-no-448048","pk":"5bcf0cec-f67a-4bab-957f-fd53001b4929","parcel_number":"LR NO 4480/48","fr_datum":"76/78","county":"Kajiado","sub_county":"Ngong","land_use":null,"hold_type":"FREEHOLD","date_created":"2022-05-24T09:05:46.738Z","owners":[]},"geometry":{"type":"MultiPolygon","coordinates":[[[[36.65716779957811,-1.362313862745647],[36.65741904282,-1.36220412722422],[36.65752847154055,-1.362457523565383],[36.65727729568316,-1.362567396139325],[36.65716779957811,-1.362313862745647]]]]}},{"type":"Feature","properties":{"parcel":"kajiado-lr-no-448059","pk":"32385ea1-6239-4a18-b36e-138fd10eef38","parcel_number":"LR NO 4480/59","fr_datum":"76/78","county":"Kajiado","sub_county":"Ngong","land_use":null,"hold_type":"FREEHOLD","date_created":"2022-05-24T09:05:46.756Z","owners":[]},"geometry":{"type":"MultiPolygon","coordinates":[[[[36.65609370095147,-1.361375831136438],[36.65613904970416,-1.361647699970802],[36.65581533500067,-1.361700135022282],[36.655771821833326,-1.361427968925704],[36.65609370095147,-1.361375831136438]]]]}},{"type":"Feature","properties":{"parcel":"kajiado-lr-no-4480314","pk":"be05dcfa-23a2-4db0-9355-1a228390ca10","parcel_number":"LR NO 4480/314","fr_datum":"253/32","county":"Kajiado","sub_county":"Ngong","land_use":null,"hold_type":"FREEHOLD","date_created":"2022-05-24T09:05:47.153Z","owners":[]},"geometry":{"type":"MultiPolygon","coordinates":[[[[36.65338991707519,-1.363953253261391],[36.653498220348276,-1.364206462858439],[36.65338362421257,-1.364256970380918],[36.65327308850057,-1.364004744281277],[36.65338991707519,-1.363953253261391]]]]}},{"type":"Feature","properties":{"parcel":"kajiado-lr-no-4480315","pk":"73c961ab-2375-4981-9299-764e4572f713","parcel_number":"LR NO 4480/315","fr_datum":"253/32","county":"Kajiado","sub_county":"Ngong","land_use":null,"hold_type":"FREEHOLD","date_created":"2022-05-24T09:05:47.159Z","owners":[]},"geometry":{"type":"MultiPolygon","coordinates":[[[[36.65350396681801,-1.363902986971042],[36.65361413053294,-1.364155376164338],[36.653498220348276,-1.364206462858439],[36.65338991707519,-1.363953253261391],[36.65350396681801,-1.363902986971042]]]]}}]}


const parcelsVectorSource = new VectorSource({
    features: new GeoJSON().readFeatures(existing_parcels_geojson, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3857",
        extractGeometryName: true,
    }),
});


const polygonShapeStyle = feature => new Style({
    fill: new Fill({
        color: "rgba(102, 51, 0, 0.25)",
    }),
    stroke: new Stroke({
        color: "rgb(102, 51, 0)",
        width: 2,
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


// selection option
const singleMapClick = new Select({
    layers: [parcelsLayer],
    style: new Style({
        fill: new Fill({
            color: "rgba(255, 204, 153)",
        }),
        stroke: new Stroke({
            color: "rgb(102, 51, 0)",
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

        populate_popup_content(selected_feature)
        selected = null;
    } else {
        detail_content.innerHTML = ''
    }
})

function populate_popup_content(feat) {
    let parcel_number = feat.parcel_number ?? ''
    let fr_datum = feat.fr_datum ?? ''
    let county = feat.county ?? ''
    let sub_county = feat.sub_county ?? ''
    let land_use = feat.land_use ?? ''
    let hold_type = feat.hold_type ?? ''
    let owners = feat.owners ?? ''

    detail_content.innerHTML = `
        <p class='fs-6 text-center fw-bold' mb-3>${parcel_number}</p>
        <p class='fs-6 fw-light lh-1'>FR Datum: ${fr_datum}</p>
        <p class='fs-6 fw-light lh-1'>County: ${county}</p>
        <p class='fs-6 fw-light lh-1'>Sub county: ${sub_county}</p>
        <p class='fs-6 fw-light lh-1'>Hold type: ${hold_type}</p>
        <p class='fs-6 fw-light lh-1'>Land use: ${land_use}</p>
    `
    
    if (owners.length > 1) {
        detail_content.innerHTML += "<p class='fs-6 fw-light lh-1'>Parcel owner(s):</p>"
        detail_content.innerHTML += '<ol class="list-group list-group-numbered">'
        for (let owner of owners) {
            detail_content.innerHTML += `<li class="list-group-item">${owner}</li>`
        }
        detail_content.innerHTML += '</ol>'
    }else{
        detail_content.innerHTML += '<p class="h6">No owner(s) listed for this parcel</p>'
    }
}
