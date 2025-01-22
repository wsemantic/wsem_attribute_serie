from odoo import models, fields

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char(string='Code', help='Unique code for the attribute value')