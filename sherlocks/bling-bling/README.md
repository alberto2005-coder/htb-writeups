---
sherlock: Bling Bling
category: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, neo4j, cypher, fraud, graph-analysis]
---

# Bling Bling — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Durante una campaña de descuentos de Diwali, una tienda usa StoreD y recibe un volumen anómalo de cuentas. Se entrega una base Neo4j y se pide detectar cuentas duplicadas, tarjetas compartidas y direcciones reutilizadas.

## Evidencias

- `opsk-5.zip` con el dump de Neo4j.
- Nodos `Account`, `CreditCard` y relaciones de registro.
- No hay logs web ni PCAP.

```bash
unzip opsk-5.zip
neo4j console
```

## Investigación

### 1. Inventario y triaje

Se importa el dump y se revisan las etiquetas y propiedades. Las claves útiles son `username`, `register_ip_address`, `address`, `created_at` y el número de tarjeta.

```cypher
MATCH (n) RETURN labels(n), count(*);
MATCH (n:Account) RETURN n LIMIT 5;
```

### 2. Línea temporal

Se ordenan las cuentas por `created_at` y se agrupan por IP y dirección física. Un pico de registros en pocas horas es el patrón de abuso.

```cypher
MATCH (a:Account)
RETURN a.register_ip_address, count(*) AS c
ORDER BY c DESC LIMIT 10;
```

### 3. Artefacto clave

La relación `HAS_CREDITCARD` conecta una tarjeta con varias cuentas. Esa reutilización es la evidencia principal de fraude, junto con la dirección física compartida.

## Conclusiones

- La base contiene más de un millar de cuentas.
- Varias cuentas comparten IP, dirección y tarjeta.
- El patrón apunta a creación automatizada de cuentas para abusar de descuentos.
- Las consultas Cypher permiten reproducir el análisis.

## Lecciones

- Las bases de grafos son ideales para fraude relacional.
- La IP sola no basta: la dirección física y la tarjeta confirman.
- Documentar cada consulta hace el informe auditable.

## Referencias

- <https://www.hackthebox.com/sherlocks/Bling%20Bling>
- <https://neo4j.com/docs/cypher-manual/current/>
- <https://attack.mitre.org/techniques/T1136/001/>
