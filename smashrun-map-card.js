/**
 * Smashrun Extended Map Card
 * Wraps hui-map-card and draws a polyline + km markers using MapLibre GL.
 */
class SmashrunMapCard extends HTMLElement {

  static IDS = {
    ROUTE_SOURCE: 'smashrun-route',
    ROUTE_LAYER: 'smashrun-route-layer'
  };

  constructor() {
    super();

    this._hass = null;
    this._config = null;
    this._mapCardElement = null;

    this._lastPolyline = null;
    this._lastMarkers = null;

    this._mlMarkers = [];
    this._updateTimer = null;
  }

  connectedCallback() {
    this._mount();

    this._lastPolyline = null;
    this._lastMarkers = null;

    if (this._hass && this._config) {
      this._updateMap();
    }
  }

  disconnectedCallback() {
    clearTimeout(this._updateTimer);
  }

  async setConfig(config) {
    if (!config.entity) {
      throw new Error('smashrun-map-card: devi definire entity');
    }

    this._config = {
      entity: config.entity,
      polyline_attr: config.polyline_attr || 'polyline',
      markers_attr: config.markers_attr || 'markers',
      color: config.color || '#3388ff',
      weight: config.weight || 4,
      ...config
    };

    const entitiesConfig =
      config.entities &&
      Array.isArray(config.entities) &&
      config.entities.length > 0
        ? config.entities
        : [config.entity];

    const cardConfig = {
      type: 'map',
      title: config.title,
      hours_to_show: config.hours_to_show ?? 0,
      entities: entitiesConfig,
      dark_mode: config.dark_mode,
      aspect_ratio: config.aspect_ratio,
    };

    if (!this._mapCardElement) {
      if (window.loadCardHelpers) {
        const helpers = await window.loadCardHelpers();
        this._mapCardElement = helpers.createCardElement(cardConfig);
      } else {
        this._mapCardElement = document.createElement('hui-map-card');
        this._mapCardElement.setConfig(cardConfig);
      }
    } else {
      this._mapCardElement.setConfig(cardConfig);
    }

    if (this._hass) {
      this._mapCardElement.hass = this._hass;
    }

    this._mount();
    this._injectMarkerHideStyles();
  }

  set hass(hass) {
    this._hass = hass;

    if (!this._config || !this._mapCardElement) {
      return;
    }

    this._mapCardElement.hass = hass;

    clearTimeout(this._updateTimer);

    this._updateTimer = setTimeout(() => {
      this._updateMap();
    }, 50);
  }

  _updateMap() {
    const stateObj = this._hass?.states?.[this._config.entity];

    if (!stateObj) {
      return;
    }

    const polylineData =
      stateObj.attributes[this._config.polyline_attr];

    const markerData =
      stateObj.attributes[this._config.markers_attr];

    if (
      polylineData === this._lastPolyline &&
      markerData === this._lastMarkers
    ) {
      return;
    }

    this._lastPolyline = polylineData;
    this._lastMarkers = markerData;

    this._drawOverlays(polylineData, markerData);
  }

  _mount() {
    if (
      this._mapCardElement &&
      !this.contains(this._mapCardElement)
    ) {
      this.innerHTML = '';
      this.appendChild(this._mapCardElement);
      this._injectMarkerHideStyles();
    }
  }

  _injectMarkerHideStyles() {
    if (this.querySelector('[data-smashrun-style]')) {
      return;
    }

    const style = document.createElement('style');
    style.dataset.smashrunStyle = 'true';

    style.textContent = `
      ha-map,
      maplibre-gl-map {
        --map-marker-color: transparent !important;
      }

      .marker {
        display: none !important;
      }
    `;

    this.appendChild(style);
  }

  async _waitForMap(timeout = 5000) {
    const start = Date.now();

    while (Date.now() - start < timeout) {
      const map =
        this._mapCardElement
          ?.shadowRoot
          ?.querySelector('ha-map')
          ?._engine
          ?._map;

      if (map?.loaded?.() && map?.isStyleLoaded?.()) {
        return map;
      }

      await new Promise(resolve => setTimeout(resolve, 100));
    }

    return null;
  }

  _clearMarkers() {
    this._mlMarkers.forEach(marker => marker.remove());
    this._mlMarkers = [];
  }

  _removeOverlays(mlMap) {
    const routeLayer =
      mlMap.getLayer(SmashrunMapCard.IDS.ROUTE_LAYER);

    if (routeLayer) {
      mlMap.removeLayer(SmashrunMapCard.IDS.ROUTE_LAYER);
    }

    const routeSource =
      mlMap.getSource(SmashrunMapCard.IDS.ROUTE_SOURCE);

    if (routeSource) {
      mlMap.removeSource(SmashrunMapCard.IDS.ROUTE_SOURCE);
    }

    this._clearMarkers();
  }

  async _drawOverlays(polylineData, markerData) {
    const mlMap = await this._waitForMap();

    if (!mlMap) {
      console.warn(
        'smashrun-map-card: MapLibre non trovato o non pronto'
      );
      return;
    }

    const haMapEl =
      this._mapCardElement.shadowRoot?.querySelector('ha-map');

    const ML = haMapEl?._engine?._maplibre;

    if (!ML) {
      return;
    }

    this._removeOverlays(mlMap);

    if (!Array.isArray(polylineData) || !polylineData.length) {
      return;
    }

    const coords = polylineData
      .filter(p => p.lat != null && p.lon != null)
      .map(p => [p.lon, p.lat]);

    if (!coords.length) {
      return;
    }

    this._drawRoute(mlMap, coords);
    this._drawStartFinishMarkers(ML, mlMap, coords);
    this._drawDistanceMarkers(ML, mlMap, markerData);

    const bounds = this._fitRouteBounds(mlMap, coords);

    if (haMapEl) {
      haMapEl.fitMap = () => {
        this._applyBounds(mlMap, bounds);
      };
    }
  }

  _drawRoute(mlMap, coords) {
    mlMap.addSource(
      SmashrunMapCard.IDS.ROUTE_SOURCE,
      {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: coords
          }
        }
      }
    );

    mlMap.addLayer({
      id: SmashrunMapCard.IDS.ROUTE_LAYER,
      type: 'line',
      source: SmashrunMapCard.IDS.ROUTE_SOURCE,
      paint: {
        'line-color': this._config.color,
        'line-width': this._config.weight,
        'line-opacity': 0.8
      }
    });
  }

  _drawStartFinishMarkers(ML, mlMap, coords) {
    const startEl =
      this._markerEl('S', '#4CAF50');

    const finishEl =
      this._markerEl('F', '#F44336');

    this._mlMarkers.push(
      new ML.Marker({ element: startEl })
        .setLngLat(coords[0])
        .addTo(mlMap)
    );

    this._mlMarkers.push(
      new ML.Marker({ element: finishEl })
        .setLngLat(coords[coords.length - 1])
        .addTo(mlMap)
    );
  }

  _drawDistanceMarkers(ML, mlMap, markerData) {
    if (!Array.isArray(markerData)) {
      return;
    }

    markerData.forEach(marker => {
      if (marker.lat == null || marker.lon == null) {
        return;
      }

      const el = this._markerEl(
        String(marker.label ?? ''),
        this._config.color
      );

      const mapMarker =
        new ML.Marker({ element: el })
          .setLngLat([marker.lon, marker.lat])
          .addTo(mlMap);

      this._mlMarkers.push(mapMarker);
    });
  }

  _fitRouteBounds(mlMap, coords) {
    const lons = coords.map(c => c[0]);
    const lats = coords.map(c => c[1]);

    const bounds = [
      [Math.min(...lons), Math.min(...lats)],
      [Math.max(...lons), Math.max(...lats)]
    ];

    this._applyBounds(mlMap, bounds);

    return bounds;
  }

  _applyBounds(mlMap, bounds) {
    const singlePoint =
      bounds[0][0] === bounds[1][0] &&
      bounds[0][1] === bounds[1][1];

    if (singlePoint) {
      mlMap.flyTo({
        center: bounds[0],
        zoom: 15
      });
      return;
    }

    mlMap.fitBounds(bounds, {
      padding: 30,
      duration: 300
    });
  }

  _markerEl(label, bg, size = 24) {
    const div = document.createElement('div');

    div.style.cssText = `
      width:${size}px;
      height:${size}px;
      border-radius:50%;
      background:${bg};
      color:white;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:11px;
      font-weight:bold;
      border:2px solid white;
      box-sizing:border-box;
      box-shadow:0 2px 5px rgba(0,0,0,0.4);
      cursor:default;
    `;

    div.textContent = label;

    return div;
  }

  getCardSize() {
    return typeof this._mapCardElement?.getCardSize === 'function'
      ? this._mapCardElement.getCardSize()
      : 4;
  }

  static getStubConfig() {
    return {
      type: 'custom:smashrun-map-card',
      entity: 'sensor.smashrun_activity_id',
      polyline_attr: 'polyline',
      markers_attr: 'markers',
    };
  }
}

if (!customElements.get('smashrun-map-card')) {
  customElements.define(
    'smashrun-map-card',
    SmashrunMapCard
  );

  window.customCards = window.customCards || [];

  window.customCards.push({
    type: 'smashrun-map-card',
    name: 'Smashrun Map Card',
    description:
      'Native HA card extended with Smashrun polyline e km markers',
  });

  console.info(
    '%c SMASHRUN-MAP-CARD %c loaded ',
    'background:#FF5722;color:white;',
    ''
  );
}