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
    _description = 'Asistente para la Cuadrícula de Variantes'

    purchase_order_line_id = fields.Many2one('purchase.order.line', string="Línea de Pedido de Compra")
    attribute_serie_id = fields.Many2one('attribute.serie', string="Serie de Atributos")
    detail_ids = fields.One2many('variant.grid.wizard.cell', 'wizard_id', string='Detalles')

    @api.onchange('attribute_serie_id')
    def onchange_attribute_serie_id(self):
        details = []
        if self.attribute_serie_id:
            tallas = self.attribute_serie_id.item_ids.mapped('attribute_value_id')
            num_tallas = len(tallas)
            
            # Crear o actualizar la "fila de encabezado" con los nombres de las tallas.
            header_vals = {
                'color_id': False,  # No hay color para la fila de encabezados.
            }
            for i in range(3):
                if i < num_tallas:
                    header_vals[f'talla_{i+1}'] = tallas[i].name
                else:
                    header_vals[f'talla_{i+1}'] = False
            details.append((0, 0, header_vals))
            
            # Añade el resto de tus detalles aquí.
        self.detail_ids = details

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

class VariantGridWizardCell(models.TransientModel):
    _name = 'variant.grid.wizard.cell'
    _description = 'Detalle de Cuadrícula de Variantes'

    wizard_id = fields.Many2one('variant.grid.wizard', string="Wizard de Variantes")
    color_id = fields.Many2one('product.attribute.value', string="Color")
    talla_1 = fields.Char("Talla 1", force_save=True)
    talla_2 = fields.Char("Talla 2", force_save=True)
    talla_3 = fields.Char("Talla 3", force_save=True)
    talla_1_cantidad = fields.Integer("Cantidad Talla 1")
    talla_2_cantidad = fields.Integer("Cantidad Talla 2")
    talla_3_cantidad = fields.Integer("Cantidad Talla 3")

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _open_variant_grid_wizard(self):
        wizard = self.env['variant.grid.wizard'].create({
            'purchase_order_line_id': self.id,
        })
        action = self.env.ref('wsem_attribute_serie.action_variant_grid_wizard').read()[0]
        action['res_id'] = wizard.id
        action['context'] = self.env.context
        return action

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