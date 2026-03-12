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
                sorted_attribute_values = self.attribute_serie_id.item_ids.sorted(
                    key=lambda item: (item.sequence or 0, item.attribute_value_id.name)
                )
                attribute_value_ids = sorted_attribute_values.mapped('attribute_value_id').ids

                if existing_line:
                    _logger.info("WSEM existed as a series line")
                    existing_line.value_ids = [(6, 0, attribute_value_ids)]
                else:
                    _logger.info("WSEM creating series")
                    self.attribute_line_ids = [(0, 0, {
                        'attribute_id': attribute_id.id,
                        'value_ids': [(6, 0, attribute_value_ids)]
                    })]

    @api.constrains('is_storable', 'type', 'attribute_serie_id', 'list_price', 'seller_ids', 'attribute_line_ids')
    def _check_custom_fields(self):
        has_defined_series = bool(self.env['attribute.serie'].search_count([], limit=1))
        purchase_context_models = {'purchase.order', 'purchase.order.line'}
        is_purchase_context = self.env.context.get('active_model') in purchase_context_models

        for product in self:
            if product.is_storable:  # Only for storable products (in v18, is_storable replaces type == 'product')
                # Only require a series if at least one attribute.serie exists in the system.
                if has_defined_series and not product.attribute_serie_id:
                    raise ValidationError(_(
                        "Para los productos almacenables, el campo 'Serie de atributos' es obligatorio cuando existen series definidas."
                    ))

                # Validate that a sale price greater than zero has been entered.
                if not product.list_price or product.list_price <= 0:
                    raise ValidationError(_("Para los productos almacenables, el precio de venta debe ser mayor que cero."))

                # Validate vendors only when the product is managed from purchase orders or their lines.
                if is_purchase_context:
                    if not product.seller_ids:
                        raise ValidationError(_(
                            "Para los productos almacenables creados desde pedidos de compra debe existir al menos un proveedor."
                        ))
                    if not any(s.price > 0 for s in product.seller_ids):
                        raise ValidationError(_(
                            "Para los productos almacenables creados desde pedidos de compra, al menos un proveedor debe tener precio de compra mayor que cero."
                        ))

                    color_lines = product.attribute_line_ids.filtered(lambda l: l.attribute_id.name.lower() == 'color')
                    if not color_lines or not any(line.value_ids for line in color_lines):
                        raise ValidationError(_("Debe agregarse al menos un valor para el atributo 'Color' en el producto."))
           


