odoo.define('variant_grid_wizard.form', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var viewRegistry = require('web.view_registry');

    var VariantGridFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            field_changed: '_onFieldChanged',
            // Considera añadir otros eventos si son necesarios para tu lógica
        }),

        _onFieldChanged: function (event) {
            var changes = event.data.changes || {};
            if ('attribute_serie_id' in changes || 'line_ids' in changes) {
                // No es necesario llamar a reload aquí si la actualización de los encabezados
                // se maneja a través de _updateTableHeader, que ya maneja la carga.
                this._updateTableHeader();
            }
            this._super.apply(this, arguments);
        },

        // Asegúrate de llamar a _updateTableHeader después de cualquier acción que requiera una actualización
		_updateTableHeader: function() {
			var self = this;
			this.model.reload(this.handle).then(function() {
				var record = self.model.get(self.handle, {raw: true});
				var nombresTallas = JSON.parse(record.data.nombres_tallas || "[]");
				console.log("Nombres de Tallas:", nombresTallas);

				var numTallasVisibles = 0;
				$('table.o_list_table thead tr th[data-name^="talla_"]').each(function(index) {
					if (index < nombresTallas.length) {
						$(this).text(nombresTallas[index]);
						$(this).show();
						numTallasVisibles++;						         
					} else {
						$(this).hide();						
					}
				});

				// Ajustar el ancho de las columnas visibles
				var anchoColumna = 100 / numTallasVisibles;
				$('table.o_list_table thead tr th[data-name^="talla_"]:visible').css('width', anchoColumna + '%');
				$('table.o_list_table thead tr th[data-name="color_id"]').css('width', anchoColumna + '%');  // Ajustar el ancho de la columna de color
				self._disableExtraSizeInputs(nombresTallas.length);
			});
		},		
		
		_disableExtraSizeInputs: function(numTallas) {
            $('table.o_list_table tbody tr').each(function() {
                $(this).find('td[data-field^="talla_"]').each(function(index) {
                    if (index >= numTallas) {
						console.log("Deshabilitando:", index);
                        $(this).find('input').prop('disabled', true); // Deshabilita el input
                    }
                });
            });
        }

    });

    var VariantGridFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: VariantGridFormController,
        }),
    });

    viewRegistry.add('variant_grid_wizard_form', VariantGridFormView);
});
