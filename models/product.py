from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Supongamos que ya existe el campo serie_tallas, de lo contrario lo defines:
    # serie_tallas = fields.Selection([...], string="Serie Tallas")

    @api.constrains('type', 'serie_tallas', 'list_price', 'standard_price', 'attribute_line_ids')
    def _check_custom_fields(self):
        # Se ejecuta para cada producto
        for product in self:
            if product.type == 'product':  # Solo para productos almacenable
                # Validar que se haya completado el campo serie_tallas
                if not product.serie_tallas:
                    raise ValidationError(_("Para los productos almacenable, el campo 'Serie Tallas' es obligatorio."))

                # Validar que se haya ingresado un precio de venta mayor que cero
                if not product.list_price or product.list_price <= 0:
                    raise ValidationError(_("Para los productos almacenable, el precio de venta debe ser mayor que cero."))

                # Validar que se haya ingresado un precio de compra mayor que cero
                if not product.standard_price or product.standard_price <= 0:
                    raise ValidationError(_("Para los productos almacenable, debe asignarse un precio de compra mayor que cero."))

                # Validar que exista al menos una línea de atributo para el Color
                # Suponiendo que tienes un atributo para Color y que puedes obtener su referencia,
                # por ejemplo, mediante un XML ID en tu módulo:
                color_lines = product.attribute_line_ids.filtered(lambda l: l.attribute_id.name.lower() == 'color')
                if not color_lines or not any(line.value_ids for line in color_lines):
                    raise ValidationError(_("Debe agregarse al menos un valor para el atributo 'Color' en el producto."))
