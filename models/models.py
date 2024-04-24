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
    
    nombres_tallas = fields.Text(string='Nombres de Tallas', default='["T1", "T2", "T3","T4","T5","T6","T7","T8","T9","T10","T11","T12","T13","T14","T15","T16","T17","T18","T19","T20"]')
    
    @api.model
    def default_get(self, fields):
        res = super(VariantGridWizard, self).default_get(fields)
        purchase_order_line_id = self.env.context.get('purchase_order_line_id')
        if purchase_order_line_id:
            res['purchase_order_line_id'] = purchase_order_line_id
            purchase_order_line = self.env['purchase.order.line'].browse(purchase_order_line_id)
            product_template = purchase_order_line.product_id.product_tmpl_id
            if product_template.attribute_serie_id:
                res['attribute_serie_id'] = product_template.attribute_serie_id.id                

        return res

    @api.onchange('attribute_serie_id')
        serie_id=self.attribute_serie_id.id
        _logger.info(f"WSEM _update_table {serie_id}")
        if serie_id:
            serie = self.env['attribute.serie'].browse(serie_id)
            tallas = serie.item_ids.mapped('attribute_value_id')
            nombres_tallas = [talla.name for talla in tallas]
    
        # Convertir la lista de nombres a un string JSON válido
        nombres_tallas_json = json.dumps(nombres_tallas)

        # Actualizar el campo con el string JSON
        self.nombres_tallas = nombres_tallas_json

                    
    def button_accept(self):
        # Crear las líneas de variantes según las cantidades ingresadas
        _logger.info(f"WSEM Pulsado aceptar")
        if self.purchase_order_line_id:
            _logger.info(f"WSEM existe linea de compra {self.purchase_order_line_id.id}")
            variant_grid = {
                'tallas': json.loads(self.nombres_tallas),  # Convertir de JSON a lista
                'colores': [line.color_id.name for line in self.line_ids if line.color_id],
            }
            self.purchase_order_line_id.product_id.product_tmpl_id.attribute_serie_id = self.attribute_serie_id
            
            for line in self.line_ids:
                if line.color_id:
                    for i, talla in enumerate(variant_grid['tallas'], start=1):
                        _logger.info(f"WSEM itera talla {talla}")
                        cantidad = getattr(line, f'talla_{i}', 0)
                        if cantidad:
                            variant_grid[f'{talla}_{line.color_id.name}'] = int(cantidad)

        
            # Llamar al método create_variant_lines en la línea de pedido de compra
            self.purchase_order_line_id.with_context(variant_grid=variant_grid).create_variant_lines()

        # Devolver la acción de cierre de la ventana emergente
        return {'type': 'ir.actions.act_window_close'}

class VariantGridWizardLine(models.TransientModel):
    _name = 'variant.grid.wizard.line'
    _description = 'Línea de Wizard para Cuadrícula de Variantes'

    wizard_id = fields.Many2one('variant.grid.wizard', string="Wizard de Variantes", required=True, ondelete='cascade')
    color_id = fields.Many2one(
        'product.attribute.value',
        string='Color',
        domain="[('attribute_id.name', '=', 'Color')]"
    )
    
    talla_1 = fields.Char("T1")
    talla_2 = fields.Char("T2")
    talla_3 = fields.Char("T3")
    talla_4 = fields.Char("T4")
    talla_5 = fields.Char("T5")
    talla_6 = fields.Char("T6")
    talla_7 = fields.Char("T7")
    talla_8 = fields.Char("T8")
    talla_9 = fields.Char("T9")
    talla_10 = fields.Char("T10")
    talla_11 = fields.Char("T11")
    talla_12 = fields.Char("T12")
    talla_13 = fields.Char("T13")
    talla_14 = fields.Char("T14")
    talla_15 = fields.Char("T15")
    talla_16 = fields.Char("T16")    
    talla_17 = fields.Char("T17")
    talla_18 = fields.Char("T18")
    talla_19 = fields.Char("T19")
    talla_20 = fields.Char("T20")
    
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def create_variant_lines(self):
        variant_grid = self.env.context.get('variant_grid', {})

        # Obtener la plantilla de producto
        template = self.product_id.product_tmpl_id
        
        # Obtener los atributos de Talla y Color de la plantilla de producto
        talla_attribute = template.attribute_line_ids.filtered(lambda x: x.attribute_id.name == 'Talla')
        color_attribute = template.attribute_line_ids.filtered(lambda x: x.attribute_id.name == 'Color')

        for talla in variant_grid.get('tallas', []):
            _logger.info(f"WSEM dentro crear: itera talla {talla}")
            
            # Obtener el valor de atributo de Talla
            talla_value = self.env['product.attribute.value'].search([
                ('name', '=', talla),
                ('attribute_id', '=', talla_attribute.attribute_id.id)
            ], limit=1)
            
            if not talla_value:
                _logger.info(f"WSEM error no existe talla")
                
            # Verificar si el valor de atributo de Talla está asociado al producto, si no, asociarlo
            if talla_value and talla_value not in talla_attribute.value_ids:
                _logger.info(f"WSEM asociando talla a producto")
                talla_attribute.value_ids |= talla_value

            for color in variant_grid.get('colores', []):
                _logger.info(f"WSEM dentro color: itera color {color} cantidad {variant_grid.get(f'{talla}_{color}', 0)}")
                
                # Obtener el valor de atributo de Color
                color_value = self.env['product.attribute.value'].search([
                    ('name', '=', color),
                    ('attribute_id', '=', color_attribute.attribute_id.id)
                ], limit=1)
                
                if not color_value:
                    _logger.info(f"WSEM error no existe color")
                    
                # Verificar si el valor de atributo de Color está asociado al producto, si no, asociarlo
                if color_value and color_value not in color_attribute.value_ids:
                    _logger.info(f"WSEM asociando color a producto")
                    color_attribute.value_ids |= color_value

                # Verificar si la variante existe, si no, crearla
                variant = template.product_variant_ids.filtered(lambda x: 
                    talla_value in x.product_template_attribute_value_ids.mapped('product_attribute_value_id') and
                    color_value in x.product_template_attribute_value_ids.mapped('product_attribute_value_id'))
                if not variant:
                    variant = template.create_variant_ids([(talla_attribute.attribute_id.id, talla_value.id), (color_attribute.attribute_id.id, color_value.id)])

                # Crear la línea de pedido de compra para la variante
                cantidad = variant_grid.get(f'{talla}_{color}', 0)
                if cantidad > 0:
                    self.env['purchase.order.line'].create({
                        'product_id': variant.id,
                        'product_qty': cantidad,
                        'order_id': self.order_id.id,
                    })