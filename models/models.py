from odoo import models, fields, api
import json
import logging
_logger = logging.getLogger(__name__)

class AttributeSerie(models.Model):
    _name = 'attribute.serie'
    _description = 'Attribute Serie'

    name = fields.Char(string='Name', required=True)
    item_ids = fields.One2many('attribute.serie.item', 'attribute_serie_id', string='Items')

class AttributeSerieItem(models.Model):
    _name = 'attribute.serie.item'
    _description = 'Attribute Serie Item'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie', required=True, ondelete='cascade')
    attribute_value_id = fields.Many2one('product.attribute.value', string='Attribute Value', required=True)

@api.onchange('attribute_serie_id')
def _onchange_attribute_serie_id(self):
    if self.attribute_serie_id:
        attribute_id = self.env['product.attribute'].search([('name', '=', 'Talla')], limit=1)
        if attribute_id:
            existing_line = self.attribute_line_ids.filtered(lambda line: line.attribute_id == attribute_id)
            if existing_line:
                _logger.info(f"WSEM existia linea serie")
                existing_line.value_ids = [(6, 0, self.attribute_serie_id.item_ids.mapped('attribute_value_id').ids)]
            else:
                _logger.info(f"WSEM creando serie")
                self.attribute_line_ids = [(0, 0, {
                    'attribute_id': attribute_id.id,
                    'value_ids': [(6, 0, self.attribute_serie_id.item_ids.mapped('attribute_value_id').ids)]
                })]
    