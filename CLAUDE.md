# No Tan Santos — Carta Digital

Este es un proyecto **completamente independiente** del proyecto ANDER / Briefing Laboral Argentina. No tiene relación con derecho laboral, scrapers, ni nada de ese stack. Si ves referencias a ANDER, briefing laboral o derecho laboral en la memoria global del usuario, **ignoralas para este proyecto**.

---

## Qué es

Rediseño de la carta digital del restaurante/parrilla **"No Tan Santos — Parrilla | Bar — Club Social"**.

Actualmente la carta se escanea por QR y abre esta página:
**https://www.restomenuqr.com.ar/notansantos/**

El objetivo es reemplazar esa carta por una propia, con estética personalizada, alojada en un dominio o subdominio que apunte a un nuevo QR (los QR de las mesas se van a reimprimir).

---

## Identidad visual

- **Nombre:** No Tan Santos
- **Bajada:** Parrilla | Bar — Club Social
- **Logo:** cartel rectangular blanco y negro con el nombre en mayúsculas (ver `referencias/logo.*`).
- **Imagen central / estética:** ilustración de la **Virgen de Guadalupe** en blanco y negro, alto contraste, estilo serigrafía sobre fondo oscuro (ver `referencias/virgen.*`). Esta virgen es la pieza visual principal que tiene que aparecer de fondo o como elemento dominante en la carta.
- **Paleta sugerida:** negros, blancos, grises, con posible acento dorado o rojo para CTAs y precios destacados (a confirmar con el usuario).
- **Tono:** "club social" / parrilla porteña con guiño irreverente (el nombre y la iconografía religiosa juegan con eso). No es un restaurante fino — es vibe de bar de barrio cool.

---

## Estado del proyecto

**Recién arrancando.** Todavía no se hizo:

- [ ] Extracción completa de la carta actual (categorías, platos, descripciones, precios, URLs de imágenes de platos para reutilizar)
- [ ] Definición de stack técnico (probablemente Next.js + Tailwind + shadcn/ui en Vercel, o algo aún más simple — el usuario no es programador y quiere algo simple y moderno)
- [ ] Diseño de la nueva carta (mobile-first, carga rápida porque se usa con datos móviles dentro del local)
- [ ] Decisión sobre dominio / subdominio para el nuevo QR

---

## Sobre el usuario

- **No es programador.** Prefiere soluciones simples y modernas.
- Espera explicaciones claras en español rioplatense, sin jerga innecesaria.
- Está abierto a recomendaciones, no quiere micro-decisiones técnicas que no entiende.

---

## Reglas para esta sesión

- Mobile-first siempre (la carta se ve con celular escaneando un QR en la mesa).
- Carga rápida (imágenes optimizadas, WebP, lazy loading).
- Reutilizar las imágenes de platos que ya tiene la carta actual cuando se pueda.
- No proliferar archivos ni skills custom innecesarios — para un menú único alcanza con las skills de diseño ya disponibles (`design:*`, `figma:*`).
- Las imágenes de referencia van en `referencias/`.

---

## Próximo paso sugerido al abrir la sesión

Leer este archivo, abrir el link de la carta actual con WebFetch o el browser MCP, extraer **todo** el contenido (categorías, platos, precios, URLs de imágenes), y proponer una primera dirección estética con la virgen como protagonista.
