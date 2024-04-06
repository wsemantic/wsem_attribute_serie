from odoo import models, fields, api
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

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie')
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    #attribute_serie_id = fields.Many2one('attribute.serie', string='Attribute Serie', related='product_id.attribute_serie_id')

    @api.onchange('product_id')
    def onchange_product_id(self):
        _logger.info("WSEM onchange_product_id")
        if self.product_id:
            self.attribute_serie_id = self.product_id.attribute_serie_id
            # Lógica para abrir el wizard con datos pre-cargados
            wizard = self.env['variant.grid.wizard'].create({
                'purchase_order_line_id': self.id,
                'attribute_serie_id': self.attribute_serie_id.id,
                # Aquí deberías pre-cargar los nombres de las tallas y cualquier otra información necesaria
            })
            return {
                'name': 'Cuadrícula de Variantes',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'variant.grid.wizard',
                'res_id': wizard.id,
                'target': 'new',
                'context': self.env.context,
            }

    def create(self, vals):
        if vals.get('product_id'):
            product_id = self.env['product.product'].browse(vals['product_id'])
            vals['attribute_serie_id'] = product_id.attribute_serie_id.id
        return super(PurchaseOrderLine, self).create(vals)
        
    def create_variant_lines(self):
        variant_grid = self.env.context.get('variant_grid', {})

        for talla in variant_grid.get('tallas', []):
            for color in variant_grid.get('colores', []):
                cantidad = variant_grid.get(f'{talla}_{color}', 0)
                if cantidad > 0:
                    variante = self.product_id.product_variant_ids.filtered(lambda x: 
                        x.attribute_value_ids.filtered(lambda y: y.name == talla) and 
                        x.attribute_value_ids.filtered(lambda y: y.name == color))
                    if variante:
                        self.env['purchase.order.line'].create({
                            'product_id': variante.id,
                            'product_qty': cantidad,
                            'order_id': self.order_id.id,
                        })

        return {'type': 'ir.actions.act_window_close'}
        

class VariantGridWizardCell(models.TransientModel):
    _name = 'variant.grid.wizard.cell'
    _description = 'Detalle de Cuadrícula de Variantes'

    wizard_id = fields.Many2one('variant.grid.wizard', string="Wizard de Variantes")
    color_id = fields.Many2one('product.attribute.value', string="Color")
    talla_1 = fields.Char("Talla 1")
    talla_2 = fields.Char("Talla 2")
    talla_3 = fields.Char("Talla 3")

    # Asume que estos campos son para mostrar los nombres de tallas y no para editar cantidades.
    # Las cantidades se gestionarían en otros campos o en lógica adicional.

class VariantGridWizard(models.TransientModel):
    _name = 'variant.grid.wizard'
    _description = 'Asistente para la Cuadrícula de Variantes'

    attribute_serie_id = fields.Many2one('attribute.serie', string="Serie de Atributos")
    detail_ids = fields.One2many('variant.grid.wizard.cell', 'wizard_id', string='Detalles')

    @api.onchange('attribute_serie_id')
    def onchange_attribute_serie_id(self):
        details = []
        if self.attribute_serie_id:
            tallas = self.attribute_serie_id.talla_ids[:3]  # Asume que este campo devuelve las tallas relevantes.
            # Crear o actualizar la "fila de encabezado" con los nombres de las tallas.
            details.append((0, 0, {
                'color_id': False,  # No hay color para la fila de encabezados.
                'talla_1': tallas[0].name if len(tallas) > 0 else "",
                'talla_2': tallas[1].name if len(tallas) > 1 else "",
                'talla_3': tallas[2].name if len(tallas) > 2 else "",
            }))
            # Añade el resto de tus detalles aquí.
        self.detail_ids = details
