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
        return res

    @api.onchange('attribute_serie_id')
    def _onchange_attribute_serie_id(self):
        if self.attribute_serie_id:
            # Obtener los nombres de las tallas de la serie seleccionada
            tallas = self.attribute_serie_id.item_ids.mapped('attribute_value_id')
            nombres_tallas = [talla.name for talla in tallas][:3]

            # Asegurarse de que hay al menos 3 nombres (rellenar con vacío si es necesario)

            # Convertir la lista de nombres a un string JSON válido
            nombres_tallas_json = json.dumps(nombres_tallas)
            _logger.info(f"WSEM talla 1 {nombres_tallas_json}")

            # Actualizar el campo con el string JSON
            self.nombres_tallas = nombres_tallas_json

            # Actualizar la fila de encabezado (asumiendo que siempre es la primera línea)
            
            #Esto era si la primera fila era el encabezado
            #for i, nombre_talla in enumerate(nombres_tallas[:3], start=1):
            #    setattr(self.line_ids[0], f'talla_{i}', nombre_talla)

        else:
            # Si no hay serie seleccionada, reiniciar a los valores predeterminados
            self.nombres_tallas = '["Talla 1", "Talla 2", "Talla 3","Talla 4","Talla 5","Talla 6","Talla 7","Talla 8","Talla 9","Talla 10","Talla 11","Talla 12","Talla 13","Talla 14","Talla 15","Talla 16","Talla 17","Talla 18","Talla 19","Talla 20"]'



                    
    def button_accept(self):
        # Crear las líneas de variantes según las cantidades ingresadas
        _logger.info(f"WSEM Pulsado aceptar")
        if self.purchase_order_line_id:
            _logger.info(f"WSEM existe linea de compra {self.purchase_order_line_id.id}")
            variant_grid = {
                'tallas': [detail.talla_1 for detail in self.detail_ids if detail.talla_1],
                'colores': [detail.color_id.name for detail in self.detail_ids if detail.color_id],
            }
            for detail in self.detail_ids:
                if detail.color_id:
                    for talla in variant_grid['tallas']:
                        _logger.info(f"WSEM itera talla {talla}")
                        cantidad = getattr(detail, f'{talla}', 0)
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

        for talla in variant_grid.get('tallas', []):
            _logger.info(f"WSEM dentro crear: itera talla {talla}")
            for color in variant_grid.get('colores', []):
                
                cantidad = variant_grid.get(f'{talla}_{color}', 0)
                _logger.info(f"WSEM dentro color: itera color {color} cantidad {cantidad}")
                
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