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


class VariantGridWizard(models.TransientModel):
    _name = 'variant.grid.wizard'
    _description = 'Wizard para Cuadrícula de Variantes'

    _logger.info("WSEM VariantGridWizard")
    attribute_serie_id = fields.Many2one('attribute.serie', string="Serie de Atributos")
    purchase_order_line_id = fields.Many2one('purchase.order.line', string="Línea de Pedido de Compra")
    # Asumiendo que `attribute.serie` es tu modelo de serie de atributos
    # y que contiene referencias a las tallas (p.ej., mediante un campo One2many hacia `attribute.serie.item`)
    
    line_ids = fields.One2many('variant.grid.wizard.line', 'wizard_id', string="Líneas")
    
    @api.model
    def default_get(self, fields_list):
        res = super(VariantGridWizard, self).default_get(fields_list)
        color_ids = self.env['product.attribute.value'].search([('attribute_id.name', '=', 'Color')])
        
        line_vals = []
        for color in color_ids:
            line_vals.append((0, 0, {
                'color_id': color.id,
                'talla_1': 'Talla 1',
                'talla_2': 'Talla 2',
                'talla_3': 'Talla 3',
            }))
        
        res['line_ids'] = line_vals
        return res

    

    @api.onchange('attribute_serie_id')
    def _onchange_attribute_serie_id(self):
        if self.attribute_serie_id:
            tallas = self.attribute_serie_id.item_ids.mapped('attribute_value_id')
            
            # Asumimos que siempre hay 3 tallas como máximo.
            nombres_tallas = [talla.name for talla in tallas[:3]]
            
            # Rellenar con nombres genéricos si hay menos de 3 tallas
            while len(nombres_tallas) < 3:
                nombres_tallas.append("Talla {}".format(len(nombres_tallas) + 1))
            
            for line in self.line_ids:
                line.talla_1 = nombres_tallas[0] if len(nombres_tallas) > 0 else 'Talla 1'
                line.talla_2 = nombres_tallas[1] if len(nombres_tallas) > 1 else 'Talla 2'
                line.talla_3 = nombres_tallas[2] if len(nombres_tallas) > 2 else 'Talla 3'

                    
    def button_accept(self):
        # Crear las líneas de variantes según las cantidades ingresadas
        if self.purchase_order_line_id:
            variant_grid = {
                'tallas': [detail.talla_1 for detail in self.detail_ids if detail.talla_1],
                'colores': [detail.color_id.name for detail in self.detail_ids if detail.color_id],
            }
            for detail in self.detail_ids:
                if detail.color_id:
                    for talla in variant_grid['tallas']:
                        cantidad = getattr(detail, f'{talla}_cantidad', 0)
                        if cantidad > 0:
                            variant_grid[f'{talla}_{detail.color_id.name}'] = cantidad

            # Llamar al método create_variant_lines en la línea de pedido de compra
            self.purchase_order_line_id.with_context(variant_grid=variant_grid).create_variant_lines()

        # Devolver la acción de cierre de la ventana emergente
            return {'type': 'ir.actions.act_window_close'}

class VariantGridWizardLine(models.TransientModel):
    _name = 'variant.grid.wizard.line'
    _description = 'Línea de Wizard para Cuadrícula de Variantes'

    wizard_id = fields.Many2one('variant.grid.wizard', string="Wizard de Variantes", required=True, ondelete='cascade')
    color_id = fields.Many2one('product.attribute.value', string="Color", required=True)
    talla_1 = fields.Char("Talla 1")
    talla_2 = fields.Char("Talla 2")
    talla_3 = fields.Char("Talla 3")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

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