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

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # v18: "bien" (type='consu') ya es el default del core. Ofrecemos
        # is_storable marcado por defecto en el formulario nuevo de un bien, para
        # que el usuario lo vea marcado (puede desmarcarlo). No basta con
        # setdefault en create(): la UI envía is_storable=False explícito (default
        # del core), y ahí un setdefault no pisaría nada. is_storable es
        # compute-stored @api.depends('type'): el core lo fuerza a False en
        # service/combo, así que en consu el True persiste; no se toca 'type' ni
        # el difunto 'detailed_type' de v16.
        if 'is_storable' in fields_list and res.get('type', 'consu') == 'consu':
            res['is_storable'] = True
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # Respaldo para creaciones por ORM que no pasan por default_get y omiten
        # is_storable (bien almacenable por defecto). Se hace en este create (el
        # externo, ya que este módulo depende de wsem_pos) para que wsem_pos lo
        # lea y aplique available_in_pos.
        for vals in vals_list:
            if vals.get('type', 'consu') == 'consu':
                vals.setdefault('is_storable', True)
        return super().create(vals_list)

    @api.constrains('is_storable', 'type', 'attribute_serie_id')
    def _check_serie_required(self):
        # Única regla de compra que se queda en este módulo: exigir "Serie de
        # atributos" cuando existen series definidas. El resto de reglas de compra
        # (proveedor, precio, talla+color) viven en wsem_pos. _is_purchase_context
        # se hereda de wsem_pos (product.template).
        has_defined_series = bool(self.env['attribute.serie'].search_count([], limit=1))
        if not has_defined_series or not self._is_purchase_context(self.env):
            return
        for product in self:
            if product.is_storable and not product.attribute_serie_id:
                raise ValidationError(_(
                    "Para los productos almacenables creados desde pedidos de compra, el campo 'Serie de atributos' es obligatorio cuando existen series definidas."
                ))
