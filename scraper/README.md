# Scraper Module

El scraper soporta multiples sitios mediante un patron Adapter.

## Configuracion

### Un solo sitio

```bash
SCRAPER_SOURCE_URL=https://example.com/becas
SCRAPER_SOURCE_NAME="Portal Ejemplo"
```

### Varios sitios

```bash
SCRAPER_SITES_JSON='[
	{"kind": "alpha", "name": "Portal A", "url": "https://site-a.com/becas", "source_name": "Portal A"},
	{"kind": "beta", "name": "Portal B", "url": "https://site-b.com/listado", "source_name": "Portal B"}
]'
```

Tipos soportados:

- `alpha`: cards tipo `article` o bloques similares.
- `beta`: listados tipo `li`, `.card` o layouts alternativos.
- `demo`: fallback local cuando no se configura ningun sitio.

## Google Dorking para encontrar fuentes

Usa busquedas avanzadas para encontrar paginas faciles de procesar:

```text
site:.edu "scholarships" filetype:html
inurl:scholarships "2026"
site:.gob.ar becas convocatoria
site:.gov scholarships application
```

## Flujo recomendado para testeo local

1. Guardar la pagina objetivo como HTML local.
2. Apuntar `url` a un archivo local (`file:///...` o ruta absoluta).
3. Definir `link_base_url` para resolver links relativos al dominio real.
4. Ajustar selectores sin pegarle al sitio real.
5. Pasar a URL real cuando el parsing sea estable.

Ejemplo local con multiples sitios:

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
		"kind": "beta",
		"name": "OEA local",
		"url": "/app/mocks/oea.html",
		"source_name": "OEA",
		"default_country": "Global",
		"link_base_url": "https://www.oas.org"
	}
]'
```

Tambien puedes usar modo simple para un solo sitio local:

```bash
SCRAPER_SOURCE_URL=file:///app/mocks/progresar.html
SCRAPER_LINK_BASE_URL=https://www.argentina.gob.ar
```
