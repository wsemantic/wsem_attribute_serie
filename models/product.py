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

    @staticmethod
    def _is_purchase_context(env):
        # The custom checks only apply when the product is being managed from a
        # purchase order / line (the "create & edit" matrix flow). Any other write
        # path (UI product form, imports, the migrator, ...) is left untouched.
        return env.context.get('active_model') in {'purchase.order', 'purchase.order.line'}

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        for vals, product in zip(vals_list, products):
            # Detect a forgotten sale price: if 'list_price' didn't travel in vals,
            # the core will have applied its default (1.0). A value that was
            # explicitly provided -- even 0 or 1 -- is treated as edited and let
            # through, regardless of context: the migrator and any import always
            # send the price explicitly, so they pass untouched; only a UI creation
            # that never touched the field falls into the default and is caught.
            # This lives in create() (not the constraint) because only here can we
            # tell a typed 1.0 from the default 1.0.
            if product.is_storable and 'list_price' not in vals:
                raise ValidationError(_(
                    "Para los productos almacenables debe indicarse el precio de venta."
                ))
        return products

    @api.constrains('is_storable', 'type', 'attribute_serie_id', 'seller_ids', 'attribute_line_ids')
    def _check_custom_fields(self):
        has_defined_series = bool(self.env['attribute.serie'].search_count([], limit=1))
        is_purchase_context = self._is_purchase_context(self.env)

        for product in self:
            if product.is_storable:  # Only for storable products (in v18, is_storable replaces type == 'product')
                # Only require a series if at least one attribute.serie exists in the system.
                if has_defined_series and not product.attribute_serie_id:
                    raise ValidationError(_(
                        "Para los productos almacenables, el campo 'Serie de atributos' es obligatorio cuando existen series definidas."
                    ))

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
