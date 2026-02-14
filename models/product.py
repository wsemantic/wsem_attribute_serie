# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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

                # Get attribute values sorted by sequence and name
                sorted_attribute_values = self.attribute_serie_id.item_ids.sorted(key=lambda item: (item.sequence or 0, item.attribute_value_id.name))
                attribute_value_ids = sorted_attribute_values.mapped('attribute_value_id').ids

                if existing_line:
                    _logger.info(f"WSEM existed as a series line")
                    existing_line.value_ids = [(6, 0, attribute_value_ids)]
                else:
                    _logger.info(f"WSEM creating series")
                    self.attribute_line_ids = [(0, 0, {
                        'attribute_id': attribute_id.id,
                        'value_ids': [(6, 0, attribute_value_ids)]
                    })]
    
    @api.constrains('is_storable', 'type', 'serie_tallas', 'list_price', 'seller_ids', 'attribute_line_ids')
    def _check_custom_fields(self):
        # Runs for each product
        for product in self:
            if product.is_storable:  # Only for storable products (in v18, is_storable replaces type == 'product')
                # Validate that the size_series field has been completed.
                if not product.attribute_serie_id:
                    raise ValidationError(_("Para los productos almacenable, el campo 'Serie Tallas' es obligatorio."))

                # Validate that a sale price greater than zero has been entered.
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
                # Validate that at least one attribute line exists for Color
                # Assuming you have an attribute for Color and that you can obtain its reference,
                # for example, using an XML ID in your module:
                color_lines = product.attribute_line_ids.filtered(lambda l: l.attribute_id.name.lower() == 'color')
                if not color_lines or not any(line.value_ids for line in color_lines):
                    raise ValidationError(_("Debe agregarse al menos un valor para el atributo 'Color' en el producto."))                   


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('name', 'default_code', 'product_template_attribute_value_ids')
    @api.depends_context('display_default_code')
    def _compute_display_name(self):
        # Migrado de name_get() (v16) a _compute_display_name() (v18)
        for product in self:
            # We extract the base name that would normally include the code and product name.
            # For example: "[ABC] Product X"
            name = product.name or ''

            # Add product code if it should be displayed
            if self._context.get('display_default_code', True) and product.default_code:
                name = "[%s] %s" % (product.default_code, name)

            # Get all attribute values, without filtering if they are unique or not.
            attribute_values = product.product_template_attribute_value_ids.mapped('name')
            if attribute_values:
                # Concatenate all attributes (you can change the comma to another separator if you want)
                combo = ", ".join(attribute_values)
                # Concatenate the base name with the attributes between parentheses
                product.display_name = "%s (%s)" % (name, combo)
            else:
                product.display_name = name


