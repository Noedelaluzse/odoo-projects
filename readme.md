version: '3.1'

services:
  db:
    image: postgres:15
    container_name: odoo-db
    environment:
      POSTGRES_DB: postgres
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - ./data/db:/var/lib/postgresql/data

  odoo:
    image: odoo:18.0
    container_name: odoo-app
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./odoo.conf:/etc/odoo/odoo.conf
      - ./custom_addons:/mnt/extra-addons
      - ./data/filestore:/var/lib/odoo
      - ./odoo:/mnt/odoo-source
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo