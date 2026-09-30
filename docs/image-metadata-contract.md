# Image metadata contract

The minimum publication tuple is `(image_url, image_alt, image_credit, image_rights, image_source_url)`. A Creative Commons record extends the tuple with `image_license_url`.

Treat the tuple atomically. Changing the image without updating its creator, rights, and source record creates a provenance defect even if the page still renders.
