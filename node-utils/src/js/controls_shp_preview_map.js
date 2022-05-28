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


// const controls_geojson = {"type":"FeatureCollection","crs":{"type":"name","properties":{"name":"EPSG:4326"}},"features":[{"type":"Feature","properties":{"beacon":"570889ee-7564-4fac-9ab2-c59c06b83dfa","pk":"cb215246-f63e-446f-8d2e-6fdbdc2dfcf0","name":"1CAC","parcels":["kajiado-lr-no-448067"]},"geometry":{"type":"MultiPoint","coordinates":[[36.654252946020314,-1.363250600037153]]}},{"type":"Feature","properties":{"beacon":"b2eac7ac-b1de-46c6-8ce0-88410045a414","pk":"725d6f9d-39b2-45c2-9612-88452613352b","name":"13FE","parcels":["kajiado-lr-no-448067"]},"geometry":{"type":"MultiPoint","coordinates":[[36.65431166114556,-1.363308441662277]]}},{"type":"Feature","properties":{"beacon":"171af0a7-371a-4387-8d99-74874bd02b6d","pk":"22a350b9-beaf-46ca-b74e-6876bf741593","name":"21DA","parcels":["kajiado-lr-no-448070"]},"geometry":{"type":"MultiPoint","coordinates":[[36.654337687989376,-1.363256924181637]]}},{"type":"Feature","properties":{"beacon":"52ec1879-6c0e-4397-9909-6f0bffaa6e11","pk":"593ad591-6ea0-4833-bfd7-90fdd70a18f5","name":"823E","parcels":["kajiado-lr-no-448070"]},"geometry":{"type":"MultiPoint","coordinates":[[36.654298854944315,-1.363218657179303]]}},{"type":"Feature","properties":{"beacon":"310bdc26-1d8e-434f-b85a-5c605b8e0baa","pk":"37e94298-693a-4f87-a1cd-97c80012b9e3","name":"C002","parcels":["kajiado-lr-no-448069"]},"geometry":{"type":"MultiPoint","coordinates":[[36.654365903631735,-1.363317744149287]]}}]}


const controlsVectorSource = new VectorSource({
    features: new GeoJSON().readFeatures(controls_geojson, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3857",
        extractGeometryName: true,
    }),
});

const pointsStyle = feature => new Style({
    image: new CircleStyle({
        radius: 4.5,
        fill: new Fill({ color: "rgb(0,0,102)" }),
        stroke: new Stroke({ color: "rgb(153, 153, 255)", width: 2.5 }),
    }),
    updateWhileAnimating: true, // optional, for instant visual feedback
    updateWhileInteracting: true, // optional, for instant visual feedback
});

// surveyor location layer
const controlsLayer = new VectorLayer({
    source: controlsVectorSource,
    style: pointsStyle
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
    layers: [OpenStreetMapLayer, controlsLayer],
    view: new View(),
});

sync(parcel_Map);

const layer_extent = controlsLayer.getSource().getExtent()
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
    layers: [controlsLayer],
    style: new Style({
        image: new CircleStyle({
            radius: 6,
            fill: new Fill({ color: "rgb(153, 153, 255)" }),
            stroke: new Stroke({ color: "rgb(0, 0, 102)", width: 1 }),
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
    let name = feat.name ?? ''
    let parcels = feat.parcels ?? ''

    detail_content.innerHTML = `<p class='fs-6 text-center fw-bold'>${name}</p>`

    if (parcels) {
        detail_content.innerHTML += "<p class='fs-6 fw-light lh-1'>Intersecting Parcels:</p>"
        detail_content.innerHTML += '<ol class="list-group list-group-numbered">'
        for (let parcel of parcels) {
            detail_content.innerHTML += `<li class="list-group-item">${parcel}</li>`
        }
        detail_content.innerHTML += '</ol>'
    }else{
        detail_content.innerHTML += '<h5>No intersecting parcels</h5>'
    }


}
