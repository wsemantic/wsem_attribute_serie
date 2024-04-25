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
    _order = 'sequence'


    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie', required=True, ondelete='cascade')
    attribute_value_id = fields.Many2one('product.attribute.value', string='Attribute Value', required=True)
    sequence = fields.Integer(string='Sequence')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie')
    
    @api.model
    def create(self, vals):
        if not vals.get('default_code'):
            vals['default_code'] = self.env['ir.sequence'].next_by_code('product.template.ref')
        return super(ProductTemplate, self).create(vals)

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
    
    
 
class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char(string='Code', help="Codigo", readonly=True, default=lambda self: self._generate_code())
    
    @api.model
    def _generate_code(self):
        return self.env['ir.sequence'].next_by_code('product.attribute.value.code')