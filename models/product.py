from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Serie Tallas')  

    @api.onchange('attribute_serie_id')
    def _onchange_attribute_serie_id(self):
        if self.attribute_serie_id:
            attribute_id = self.env['product.attribute'].search([('name', '=', 'Talla')], limit=1)
            if attribute_id:
                existing_line = self.attribute_line_ids.filtered(lambda line: line.attribute_id == attribute_id)

                # Obtener los valores de atributo ordenados por secuencia y nombre
                sorted_attribute_values = self.attribute_serie_id.item_ids.sorted(key=lambda item: (item.sequence or 0, item.attribute_value_id.name))
                attribute_value_ids = sorted_attribute_values.mapped('attribute_value_id').ids

                if existing_line:
                    _logger.info(f"WSEM existia linea serie")
                    existing_line.value_ids = [(6, 0, attribute_value_ids)]
                else:
                    _logger.info(f"WSEM creando serie")
                    self.attribute_line_ids = [(0, 0, {
                        'attribute_id': attribute_id.id,
                        'value_ids': [(6, 0, attribute_value_ids)]
                    })]
    
    @api.constrains('type', 'serie_tallas', 'list_price', 'seller_ids', 'attribute_line_ids')
    def _check_custom_fields(self):
        # Se ejecuta para cada producto
        for product in self:
            if product.type == 'product':  # Solo para productos almacenable
                # Validar que se haya completado el campo serie_tallas
                if not product.attribute_serie_id:
                    raise ValidationError(_("Para los productos almacenable, el campo 'Serie Tallas' es obligatorio."))

                # Validar que se haya ingresado un precio de venta mayor que cero
                if not product.list_price or product.list_price <= 0:
                    raise ValidationError(_("Para los productos almacenable, el precio de venta debe ser mayor que cero."))
                '''
                if not product.seller_ids:
                    raise ValidationError(_(
                        "Para los productos almacenable debe existir al menos un registro de precio de compra en los Proveedores."
                    ))
                # Opcional: verifica que al menos uno de los registros tenga un precio mayor que cero
                if not any(s.price > 0 for s in product.seller_ids):
                    raise ValidationError(_(
                        "Para los productos almacenable, al menos uno de los registros en Proveedores debe tener un precio de compra mayor que cero."
                    ))
                '''
                # Validar que exista al menos una línea de atributo para el Color
                # Suponiendo que tienes un atributo para Color y que puedes obtener su referencia,
                # por ejemplo, mediante un XML ID en tu módulo:
                color_lines = product.attribute_line_ids.filtered(lambda l: l.attribute_id.name.lower() == 'color')
                if not color_lines or not any(line.value_ids for line in color_lines):
                    raise ValidationError(_("Debe agregarse al menos un valor para el atributo 'Color' en el producto."))                   


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        # Llamamos al método original para conservar parte de la lógica (por ejemplo, el código)
        super_res = super(ProductProduct, self).name_get()
        # Convertimos el resultado a diccionario para fácil acceso
        super_names = dict(super_res)
        result = []
        for product in self:
            # Extraemos el nombre base que normalmente incluiría el código y el nombre del producto.
            # Por ejemplo: "[ABC] Producto X"
            base_name = super_names.get(product.id, product.name)
            # Si queremos asegurarnos de no duplicar información (en caso de que ya tenga paréntesis),
            # separamos el nombre base eliminando la parte de la variante que pudiera haber.
            base_name = base_name.split(" (")[0]

            # Obtenemos todos los valores de los atributos, sin filtrar si son únicos o no.
            attribute_values = product.product_template_attribute_value_ids.mapped('name')
            if attribute_values:
                # Concatenamos todos los atributos (puedes cambiar la coma por otro separador si lo deseas)
                combo = ", ".join(attribute_values)
                # Concatenamos el nombre base con los atributos entre paréntesis
                display_name = "%s (%s)" % (base_name, combo)
            else:
                display_name = base_name

            result.append((product.id, display_name))
        return result


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char(string='Code', help="Codigo", readonly=True, default=lambda self: self._generate_code())
    
    @api.model
    def _generate_code(self):
        return self.env['ir.sequence'].next_by_code('product.attribute.value.code')