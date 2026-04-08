# Mock HTML fixtures

Archivos locales para testear selectores sin trafico a sitios reales.

## Archivos incluidos

- progresar.html: estructura orientada a `alpha`.
- manuel_belgrano.html: variaciones de clases compatibles con `alpha`.
- oea_list.html: estructura de listado orientada a `beta`.

## Ejemplo de ejecucion local

```bash
SCRAPER_SITES_JSON='[
  {
    "kind": "alpha",
    "name": "Progresar local",
    "url": "file:///app/mocks/progresar.html",
    "source_name": "Progresar",
    "default_country": "Argentina",
    "link_base_url": "https://www.argentina.gob.ar"
  },
  {
    "kind": "alpha",
    "name": "Manuel Belgrano local",
    "url": "file:///app/mocks/manuel_belgrano.html",
    "source_name": "Manuel Belgrano",
    "default_country": "Argentina",
    "link_base_url": "https://www.argentina.gob.ar"
  },
  {
    "kind": "beta",
    "name": "OEA local",
    "url": "file:///app/mocks/oea_list.html",
    "source_name": "OEA",
    "default_country": "Global",
    "link_base_url": "https://www.oas.org"
  }
]'
```

Si corres dentro del contenedor scraper, estos archivos quedan bajo `/app/mocks`.
